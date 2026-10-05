# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Chargement des feuilles de style selon le profil de rendu deja decide.
Meme patron que le reste de la suite omega-."""
from __future__ import annotations

from pathlib import Path

from omega_lib.terminal.models import RenderProfile

_STYLES_DIR = Path(__file__).parent.parent / "styles"

_PROFILE_STYLESHEETS: dict[RenderProfile, str] = {
    RenderProfile.COMPLETE: "complete.tcss",
    RenderProfile.STANDARD: "standard.tcss",
    RenderProfile.REDUCED: "reduced.tcss",
    RenderProfile.MONO: "mono.tcss",
}


def stylesheet_paths_for(profile: RenderProfile) -> tuple[Path, Path, Path]:
    """Retourne (base.tcss, terminal_frame.tcss, <profil>.tcss) — base
    toujours chargee en premier, `terminal_frame.tcss` ensuite (fichier
    isole et portable a dessein, copie tel quel depuis le reste de la
    suite), le fichier du profil vient enfin affiner/surcharger."""
    return (
        _STYLES_DIR / "base.tcss", _STYLES_DIR / "terminal_frame.tcss",
        _STYLES_DIR / _PROFILE_STYLESHEETS[profile],
    )


def load_paths_for(profile: RenderProfile) -> list[str]:
    """Format attendu par `textual.app.App.CSS_PATH` (liste de chaines)."""
    return [str(path) for path in stylesheet_paths_for(profile)]
