# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Sauvegardes planifiees EXECUTEES (porte d'omega-serv 2.6.0 le 2026-11-07, OMEGA-LOG_PLAN_PORTAGE_SERV.md,
portage n°2 lot 6 ; decision utilisateur : « oui, comme omega-serv »).

Une seule tache planifiee par compte, une fois par jour : `python -m omega_log rotate run-automations`, qui
sauvegarde chaque log de la Bibliotheque dont l'automatisation est arrivee a echeance (meme geste que
« Sauvegarder » dans Rotate). Timer systemd, sinon ligne crontab de votre compte (OpenRC, runit, sans
gestionnaire), sinon ligne a ajouter soi-meme. Gabarits purs, aucune I/O ici.

`var_dir` : la racine var/ d'omega-log depend du dossier de lancement (infrastructure/config/paths.py) ; la
tache planifiee la recoit donc en clair (OMEGA_LOG_VAR_DIR), pour retrouver la meme Bibliotheque."""
from __future__ import annotations

import shlex
from datetime import datetime, timedelta

from omega_log.shared.i18n import _

FREQUENCY_DAYS: tuple[int, ...] = (1, 7, 30)
"""Choix proposes : tous les jours, toutes les semaines, tous les mois."""


def is_due(automation: dict, now: datetime) -> bool:
    """Echeance = derniere execution (ou creation) + intervalle en jours. Donnee illisible : jamais due."""
    due = next_run(automation)
    return due is not None and now >= due


def next_run(automation: dict) -> datetime | None:
    try:
        reference = datetime.fromisoformat(str(automation.get("last_run_at") or automation["created_at"]))
        return reference + timedelta(days=int(automation["days_interval"]))
    except (KeyError, TypeError, ValueError):
        return None


def rotation_unit_base_name(user: str) -> str:
    return f"omega-log-rotation-{user}"


def rotation_command(python_executable: str) -> str:
    return f"{shlex.quote(python_executable)} -m omega_log rotate run-automations"


def build_rotation_service_unit(*, python_executable: str, var_dir: str, user: str) -> str:
    """Lance sous VOTRE compte, jamais root : les sauvegardes restent lisibles par l'interface. Un log protege
    (/var/log/...) ne peut pas etre sauvegarde la nuit sans mot de passe : l'echec est note, Sante des logs
    le signale."""
    return (
        "[Unit]\n"
        "Description=Sauvegardes planifiées des logs (OMEGA-LOG, généré - ne pas éditer à la main)\n"
        "\n"
        "[Service]\n"
        "Type=oneshot\n"
        f"User={user}\n"
        f"Environment=OMEGA_LOG_VAR_DIR={var_dir}\n"
        f"WorkingDirectory={var_dir}\n"
        f"ExecStart={rotation_command(python_executable)}\n"
    )


def build_rotation_timer_unit() -> str:
    return (
        "[Unit]\n"
        "Description=Timer des sauvegardes planifiées des logs (OMEGA-LOG, généré - ne pas éditer à la main)\n"
        "\n"
        "[Timer]\n"
        "OnCalendar=*-*-* 03:45:00\n"
        "RandomizedDelaySec=1800\n"
        "Persistent=true\n"
        "\n"
        "[Install]\n"
        "WantedBy=timers.target\n"
    )


def rotation_cron_marker(user: str) -> str:
    return f"# omega-log-rotation:{user}"


def build_rotation_cron_line(*, python_executable: str, var_dir: str, user: str) -> str:
    """Sortie ajoutee a var/rotation-automations.log : cron n'envoie jamais de courriel pour rien."""
    var = shlex.quote(var_dir)
    log = shlex.quote(f"{var_dir}/rotation-automations.log")
    command = f"OMEGA_LOG_VAR_DIR={var} {rotation_command(python_executable)} >> {log} 2>&1"
    return f"45 3 * * * {command}  {rotation_cron_marker(user)}"


def without_marked_line(existing_crontab: str, user: str) -> list[str]:
    """Lignes de la crontab sauf celle d'omega-log pour ce compte."""
    marker = rotation_cron_marker(user)
    return [line for line in existing_crontab.splitlines() if not line.rstrip().endswith(marker)]


def render_manual_rotation_instructions(*, cron_line: str) -> str:
    return _("Aucun planificateur détecté (ni systemd, ni crontab). Ajoutez cette ligne vous-même à votre "
             "planificateur (crontab -e, /etc/cron.d/, tâche OpenRC ou runit équivalente) :\n\n{cron_line}").format(
        cron_line=cron_line)
