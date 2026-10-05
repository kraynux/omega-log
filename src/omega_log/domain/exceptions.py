# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Racine des erreurs du domaine (entites/value objects propres a LOG,
hors sous-domaine logs qui a sa propre racine : voir domain/logs/exceptions.py)."""
from __future__ import annotations

from omega_log.core.exceptions import OmegaLogError


class DomainError(OmegaLogError):
    """Racine des violations de regles metier dans domain/."""
