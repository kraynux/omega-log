# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Sauvegardes planifiees EXECUTEES (porte d'omega-serv 2.6.0 le 2026-11-07, application/logs/
rotation_automation.py) : la tache quotidienne et ce qu'elle fait.

- `run_due_automations` : appelee par `omega-log rotate run-automations` (timer systemd ou ligne crontab).
  Chaque automatisation arrivee a echeance sauvegarde son log comme « Sauvegarder » dans Rotate (archive +
  retention), sans sudo : un log protege echoue, l'echec est note (Sante des logs le signale).
- `install_rotation_schedule` / `remove_rotation_schedule` / `rotation_schedule_status` : la tache elle-meme,
  une par compte. systemd -> timer (sudo, authentification faite par l'ecran avant l'appel) ; OpenRC, runit
  ou aucun gestionnaire -> ligne de votre crontab (aucun privilege) ; sans crontab -> instructions."""
from __future__ import annotations

import shutil
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from omega_log.domain.logs.rotation_schedule import (
    build_rotation_cron_line,
    build_rotation_service_unit,
    build_rotation_timer_unit,
    is_due,
    render_manual_rotation_instructions,
    rotation_cron_marker,
    rotation_unit_base_name,
    without_marked_line,
)
from omega_log.shared.i18n import _

if TYPE_CHECKING:
    from omega_log.infrastructure.storage.rotation_automation_store import RotationAutomationStore
    from omega_log.ports.process_runner_port import ProcessRunnerPort

SYSTEMD_UNIT_DIR = Path("/etc/systemd/system")
_CRONTAB_MISSING = 127
_TIMEOUT_SECONDS = 15.0


@dataclass(frozen=True)
class AutomationRun:
    path: str
    success: bool
    message: str


def run_due_automations(
    store: RotationAutomationStore, now: datetime, backup: Callable[[str], tuple[bool, str]],
) -> list[AutomationRun]:
    """`backup(chemin)` -> (reussi, message) : RotateLogsCommand sans sudo. Une automatisation en echec reste
    due : elle sera retentee la nuit suivante."""
    runs: list[AutomationRun] = []
    automations = store.list_all()
    for automation in automations:
        if not is_due(automation, now):
            continue
        path = str(automation.get("path", ""))
        try:
            success, message = backup(path)
        except Exception as exc:  # noqa: BLE001 - une automatisation en echec ne bloque jamais les suivantes
            success, message = False, str(exc)
        runs.append(AutomationRun(path, success, message))
        automation["last_result"], automation["last_success"] = message, success
        if success:
            automation["last_run_at"] = now.isoformat()
    if runs:
        store.save_all(automations)
    return runs


# ---- tache planifiee -----------------------------------------------------------------

@dataclass(frozen=True)
class ScheduleResult:
    mechanism: Literal["systemd", "cron", "manual", "error"]
    success: bool
    message: str


def uses_systemd() -> bool:
    """systemd est le gestionnaire du systeme (pas seulement installe) : l'ecran demande alors sudo."""
    return shutil.which("systemctl") is not None and Path("/run/systemd/system").is_dir()


def _timer(user: str) -> str:
    return f"{rotation_unit_base_name(user)}.timer"


def rotation_schedule_status(user: str, runner: ProcessRunnerPort) -> ScheduleResult:
    if uses_systemd():
        timer = _timer(user)
        enabled = runner.run(["systemctl", "is-enabled", timer], timeout=_TIMEOUT_SECONDS)
        if enabled.ok:
            return ScheduleResult("systemd", True, _("Exécution : timer systemd {timer} actif (chaque nuit).").format(timer=timer))
        return ScheduleResult("systemd", False, _("Exécution : timer systemd {timer} non installé.").format(timer=timer))
    listing = runner.run(["crontab", "-l"], timeout=_TIMEOUT_SECONDS)
    if listing.returncode == _CRONTAB_MISSING:
        return ScheduleResult("manual", False, _("Exécution : aucun planificateur (ni systemd, ni crontab)."))
    marker = rotation_cron_marker(user)
    if any(line.rstrip().endswith(marker) for line in listing.stdout.splitlines()):
        return ScheduleResult("cron", True, _("Exécution : ligne crontab installée (chaque nuit)."))
    return ScheduleResult("cron", False, _("Exécution : aucune ligne crontab pour ce compte."))


def _write_root_file(runner: ProcessRunnerPort, path: Path, content: str) -> str | None:
    """`sudo -n tee` puis `chmod 644` : None si reussi, sinon le message d'erreur."""
    written = runner.run(["sudo", "-n", "tee", "--", str(path)], input_text=content, timeout=_TIMEOUT_SECONDS)
    if not written.ok:
        return written.stderr.strip() or _("code {returncode}").format(returncode=written.returncode)
    mode = runner.run(["sudo", "-n", "chmod", "644", "--", str(path)], timeout=_TIMEOUT_SECONDS)
    return None if mode.ok else (mode.stderr.strip() or _("code {returncode}").format(returncode=mode.returncode))


def _sudo(runner: ProcessRunnerPort, *args: str) -> str | None:
    result = runner.run(["sudo", "-n", *args], timeout=_TIMEOUT_SECONDS)
    return None if result.ok else (result.stderr.strip() or _("code {returncode}").format(returncode=result.returncode))


def install_rotation_schedule(
    user: str, var_dir: Path, python_executable: str, runner: ProcessRunnerPort,
    unit_dir: Path = SYSTEMD_UNIT_DIR,
) -> ScheduleResult:
    var = str(var_dir.resolve())
    if uses_systemd():
        base = rotation_unit_base_name(user)
        error = (
            _write_root_file(runner, unit_dir / f"{base}.service",
                             build_rotation_service_unit(python_executable=python_executable, var_dir=var, user=user))
            or _write_root_file(runner, unit_dir / f"{base}.timer", build_rotation_timer_unit())
            or _sudo(runner, "systemctl", "daemon-reload")
            or _sudo(runner, "systemctl", "enable", "--now", f"{base}.timer")
        )
        if error is not None:
            return ScheduleResult("error", False, _("Timer systemd non installé : {error}").format(error=error))
        return ScheduleResult("systemd", True, _("Timer systemd {timer} installé : les automatisations "
                                                 "s'exécutent chaque nuit.").format(timer=f"{base}.timer"))

    line = build_rotation_cron_line(python_executable=python_executable, var_dir=var, user=user)
    listing = runner.run(["crontab", "-l"], timeout=_TIMEOUT_SECONDS)
    if listing.returncode == _CRONTAB_MISSING:
        return ScheduleResult("manual", False, render_manual_rotation_instructions(cron_line=line))
    kept = without_marked_line(listing.stdout if listing.returncode == 0 else "", user)
    written = runner.run(["crontab", "-"], input_text="\n".join([*kept, line]) + "\n", timeout=_TIMEOUT_SECONDS)
    if not written.ok:
        return ScheduleResult("error", False, _("Échec de l'écriture de la crontab : {value}").format(
            value=(written.stderr or written.stdout).strip()))
    return ScheduleResult("cron", True, _("Ligne crontab installée : les automatisations s'exécutent chaque nuit."))


def remove_rotation_schedule(user: str, runner: ProcessRunnerPort, unit_dir: Path = SYSTEMD_UNIT_DIR) -> ScheduleResult:
    if uses_systemd():
        base = rotation_unit_base_name(user)
        if not (unit_dir / f"{base}.timer").exists():
            return ScheduleResult("systemd", True, "")
        error = (
            _sudo(runner, "systemctl", "disable", "--now", f"{base}.timer")
            or _sudo(runner, "rm", "-f", "--", str(unit_dir / f"{base}.timer"), str(unit_dir / f"{base}.service"))
            or _sudo(runner, "systemctl", "daemon-reload")
        )
        if error is not None:
            return ScheduleResult("error", False, _("Timer systemd non retiré : {error}").format(error=error))
        return ScheduleResult("systemd", True, _("Plus aucune automatisation : timer systemd retiré."))
    listing = runner.run(["crontab", "-l"], timeout=_TIMEOUT_SECONDS)
    if listing.returncode != 0:
        return ScheduleResult("cron", True, "")
    kept = without_marked_line(listing.stdout, user)
    if len(kept) == len(listing.stdout.splitlines()):
        return ScheduleResult("cron", True, "")
    written = runner.run(["crontab", "-"], input_text="\n".join(kept) + "\n" if kept else "", timeout=_TIMEOUT_SECONDS)
    if not written.ok:
        return ScheduleResult("error", False, _("Échec de l'écriture de la crontab : {value}").format(
            value=(written.stderr or written.stdout).strip()))
    return ScheduleResult("cron", True, _("Plus aucune automatisation : ligne crontab retirée."))
