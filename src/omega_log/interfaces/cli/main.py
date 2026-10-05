# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Interface CLI de test pour le Registre (plan_omega_log.md §6 Phase 2,
§12). Non-interactif, pensee pour verifier scan_logs reellement sur une
machine cible — pas encore le CLI complet de la suite (favoris, rotate,
purge... viendront avec leurs phases)."""
from __future__ import annotations

import argparse
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


def run(container: DependencyContainer, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="omega-log")
    subparsers = parser.add_subparsers(dest="command")

    scan_parser = subparsers.add_parser("scan", help="Detecter les services actifs et leurs logs")
    scan_parser.add_argument(
        "--path", default=None,
        help="Dossier supplementaire a scanner manuellement (non recursif)",
    )

    args = parser.parse_args(argv)

    if args.command == "scan":
        return _run_scan(args.path)

    parser.print_help()
    return 1
