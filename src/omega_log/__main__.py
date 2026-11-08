# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Point d'entree du package (`python -m omega_log` et le script console
`omega-log`). Dispatche vers le TUI (aucun argument) ou le CLI (au moins
un argument) — meme patron que le reste de la suite omega-.

CLI limite pour l'instant a `scan` (interfaces/cli/main.py, Phase 2 du
plan) : les autres commandes (favoris, rotate, purge...) arriveront avec
leurs phases respectives."""
from __future__ import annotations

import sys


def install_language() -> None:
    """Langue de l'interface installee AVANT d'importer la TUI (meme patron que la suite
    omega) : les textes traduits au chargement d'un module sont deja dans la bonne langue.
    Jamais pour la ligne de commande (elle reste en francais)."""
    import os

    from omega_lib.infrastructure.terminal.detector import SystemTerminalDetector

    from omega_log.infrastructure.config import paths
    from omega_log.infrastructure.storage.files.json_settings_store import JsonSettingsStore
    from omega_log.shared.i18n import LANGUAGE

    LANGUAGE.install(
        settings_store=JsonSettingsStore(paths.default_settings_path(paths.resolve_var_dir())),
        environ=os.environ,
        terminal_family=SystemTerminalDetector().detect().family,
    )

    # Hindi (repris d'omega-serv / omega-fire via omega-lib, 2026-11-07) : Rich compte les voyelles
    # devanagari espacantes pour 0 colonne, le terminal pour 1 - aligne avant tout rendu,
    # sans effet sur les autres langues.
    from omega_lib.i18n.terminal_cell_widths import align_spacing_marks_with_terminal

    align_spacing_marks_with_terminal()


def restart_for_language(code: str) -> None:  # pragma: no cover - remplace le processus
    """Meme Python, meme module : seule l'interface redemarre, dans la langue choisie."""
    import os

    from omega_log.shared.i18n import LANGUAGE

    LANGUAGE.prepare_restart_environment(os.environ, code)
    os.execv(sys.executable, [sys.executable, "-m", "omega_log"])


def _run_with_text_direction(app) -> None:  # type: ignore[no-untyped-def]
    """Arabe (repris d'omega-serv / omega-fire via omega-lib, 2026-11-07) : omega-log ordonne lui-meme
    le texte droite-a-gauche, le terminal passe en mode bidi explicite le temps de la TUI pour ne
    plus rien deplacer. Toute autre langue : lancement normal."""
    from omega_lib.i18n.policies import text_direction
    from omega_lib.i18n.terminal_bidi import (
        ENTER_EXPLICIT_MODE,
        LEAVE_EXPLICIT_MODE,
        install_visual_reordering,
    )

    from omega_log.shared.i18n import STATE

    if text_direction(STATE.language.code) != "rtl" or not install_visual_reordering():
        app.run()
        return
    sys.stdout.write(ENTER_EXPLICIT_MODE)
    sys.stdout.flush()
    try:
        app.run()
    finally:
        sys.stdout.write(LEAVE_EXPLICIT_MODE)
        sys.stdout.flush()


def main(argv: list[str] | None = None) -> int:
    effective_argv = sys.argv[1:] if argv is None else argv
    is_tui = not effective_argv
    if is_tui:
        install_language()

    from omega_log.app.bootstrap import bootstrap

    container = bootstrap(console_logging=not is_tui)
    pending_language: str | None = None
    try:
        if is_tui:
            from omega_log.interfaces.tui.app import OmegaLogApp

            app = OmegaLogApp(container)
            _run_with_text_direction(app)
            pending_language = app.pending_language
        else:
            from omega_log.interfaces.cli.main import run as run_cli

            return run_cli(container, effective_argv)
    finally:
        container.close()
    if pending_language is not None:
        restart_for_language(pending_language)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
