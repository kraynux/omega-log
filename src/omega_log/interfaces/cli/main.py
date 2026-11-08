# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Interface CLI de test pour le Registre (plan_omega_log.md §6 Phase 2,
§12). Non-interactif, pensee pour verifier scan_logs reellement sur une
machine cible — pas encore le CLI complet de la suite (favoris, rotate,
purge... viendront avec leurs phases)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from omega_log.application.use_cases.scan_logs import scan_directory, scan_logs
from omega_log.domain.entities.log_file import LogFile

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer


def _format_log_file(log_file: LogFile) -> str:
    size = f"{log_file.size_bytes}o" if log_file.size_bytes is not None else "?"
    stale = " [SUSPECT: vide]" if log_file.is_stale else ""
    service = f" ({log_file.service_id})" if log_file.service_id else ""
    return f"  {log_file.path}{service} — {log_file.access}, {size}{stale}"


def _run_scan(path: str | None) -> int:
    result = scan_logs()

    print("=== Registre des capacites ===")
    print(
        f"{result.capabilities_registered} capacites sondees : "
        f"{result.capabilities_available} disponibles, "
        f"{result.capabilities_degraded} degradees, "
        f"{result.capabilities_missing} manquantes, "
        f"{result.capabilities_disqualified} disqualifiees"
    )
    for error in result.errors:
        print(f"  ! {error}")

    print()
    print(f"=== Logs decouverts ({len(result.discovered)}) ===")
    for log_file in result.discovered:
        print(_format_log_file(log_file))

    if result.stale:
        print()
        print(f"=== Suspects ({len(result.stale)}) — fichier present mais vide, probable routage journald ===")
        for log_file in result.stale:
            print(_format_log_file(log_file))

    if path:
        directory = Path(path)
        manual = scan_directory(directory)
        print()
        print(f"=== Scan manuel de {directory} ({len(manual)}) ===")
        for log_file in manual:
            print(_format_log_file(log_file))

    return 0


def _run_version(container: DependencyContainer, *, check: bool) -> int:
    """Meme verification que Aide → Contact et support → « Vérifier les mises à jour » (portee d'omega-serv
    2.6.0, 2026-11-07). Code 1 si le site est injoignable ou la liste illisible."""
    from omega_log.application.use_cases.check_updates import check_for_update
    from omega_log.domain.updates.release_check import UpdateStatus

    installed = container.app_version
    if not check:
        print(installed)
        return 0
    result = check_for_update(container.release_source, installed)
    if result.status is UpdateStatus.UPDATE_AVAILABLE:
        print(f"Nouvelle version disponible : {result.latest} (installée : {result.installed}).")
        print(f"Archive : {result.archive_url}")
        print(f"Nouveautés : {result.notes_url}")
    elif result.status is UpdateStatus.UP_TO_DATE:
        print(f"Vous avez la dernière version publiée ({result.installed}).")
    elif result.status is UpdateStatus.AHEAD:
        print(f"Votre version ({result.installed}) est plus récente que la dernière publiée ({result.latest}) : "
              "version en cours, pas encore publiée.")
    else:
        print(f"Version installée : {result.installed}. Site injoignable ou liste des versions illisible : "
              "réessayez plus tard.", file=sys.stderr)
        return 1
    return 0


def _run_rotation_automations(container: DependencyContainer) -> int:
    """Tache de nuit (portee d'omega-serv 2.6.0, 2026-11-07). Sans sudo : un log protege echoue et l'echec est
    note. Code 1 si au moins une sauvegarde a echoue."""
    from datetime import datetime

    from omega_log.application.commands.rotate_logs import RotateLogsCommand, RotateLogsRequest
    from omega_log.application.use_cases.rotation_automation import run_due_automations
    from omega_log.infrastructure.privileged.elevation import PermissionRequiredError

    command = RotateLogsCommand(container.persistence_port, container.backup_dir, container.elevated_tmp_dir)
    keep_by_path = {str(item.get("path")): item.get("keep", 7) for item in container.rotation_automation_store.list_all()}

    def backup(path: str) -> tuple[bool, str]:
        keep = keep_by_path.get(path, 7)
        try:
            result = command.execute(RotateLogsRequest(source_path=path, keep=int(keep) if isinstance(keep, int) else 7))
        except PermissionRequiredError:
            return False, "log protégé : sauvegarde impossible sans sudo la nuit, faites-la depuis Rotate"
        return result.success, result.message

    runs = run_due_automations(container.rotation_automation_store, datetime.now().astimezone(), backup)
    stamp = datetime.now().astimezone().isoformat(timespec="seconds")
    for item in runs:
        print(f"{stamp} {'OK' if item.success else 'ÉCHEC'} {item.path} : {item.message}")
    if not runs:
        print(f"{stamp} " + "Aucune sauvegarde planifiée à échéance.")
    return 0 if all(item.success for item in runs) else 1


def run(container: DependencyContainer, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="omega-log")
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan", help="Detecter les services actifs et leurs logs")
    scan_parser.add_argument(
        "--path", default=None,
        help="Dossier supplementaire a scanner manuellement (non recursif)",
    )

    rotate_parser = subparsers.add_parser("rotate", help="Sauvegardes planifiées des logs")
    rotate_sub = rotate_parser.add_subparsers(dest="rotate_command")
    rotate_sub.add_parser("run-automations", help=(
        "Sauvegarde chaque log dont l'automatisation est arrivée à échéance (lancée chaque nuit par le timer "
        "systemd ou la ligne crontab)."))

    version_parser = subparsers.add_parser("version", help=(
        "Affiche la version installée ; --check la compare à la dernière version publiée sur le site."))
    version_parser.add_argument("--check", action="store_true", help=(
        "Lit la liste des versions publiées (download/sha.txt du site) ; rien n'est envoyé."))

    args = parser.parse_args(argv)

    if args.command == "scan":
        return _run_scan(args.path)
    if args.command == "version":
        return _run_version(container, check=args.check)
    if args.command == "rotate" and args.rotate_command == "run-automations":
        return _run_rotation_automations(container)

    parser.print_help()
    return 1
