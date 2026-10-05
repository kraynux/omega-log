# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Point d'entree du package (`python -m omega_log` et le script console
`omega-log`). Dispatche vers le TUI (aucun argument) ou le CLI (au moins
un argument) — meme patron que le reste de la suite omega-.

CLI limite pour l'instant a `scan` (interfaces/cli/main.py, Phase 2 du
plan) : les autres commandes (favoris, rotate, purge...) arriveront avec
leurs phases respectives."""
from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> int:
    from omega_log.app.bootstrap import bootstrap

    effective_argv = sys.argv[1:] if argv is None else argv
    is_tui = not effective_argv
    container = bootstrap(console_logging=not is_tui)
    try:
        if is_tui:
            from omega_log.interfaces.tui.app import OmegaLogApp

            OmegaLogApp(container).run()
            return 0

        from omega_log.interfaces.cli.main import run as run_cli

        return run_cli(container, effective_argv)
    finally:
        container.close()


if __name__ == "__main__":
    raise SystemExit(main())
