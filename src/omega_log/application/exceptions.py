# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Racine des erreurs de la couche application (use cases, pipeline)."""
from __future__ import annotations

from omega_log.core.exceptions import OmegaLogError
from omega_log.shared.i18n import _


class ApplicationError(OmegaLogError):
    """Racine des echecs techniques inattendus survenant dans application/
    — jamais utilisee pour un echec metier attendu (voir domain/exceptions.py)."""


class UnknownThemeError(ApplicationError):
    """Nom de theme demande absent du catalogue omega_lib.theme.policies.TUI_THEMES."""

    def __init__(self, theme_name: str) -> None:
        super().__init__(_("Thème inconnu : '{theme_name}'").format(theme_name=theme_name))
        self.theme_name = theme_name
