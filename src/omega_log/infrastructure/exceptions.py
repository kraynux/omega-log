# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Racine des erreurs techniques de infrastructure/ — meme patron que
le reste de la suite omega-."""
from __future__ import annotations

from omega_log.core.exceptions import OmegaLogError


class InfrastructureError(OmegaLogError):
    """Racine des pannes techniques (I/O, archive, reseau...)."""


class StorageError(InfrastructureError):
    """Echec d'une operation de stockage (fichier, archive)."""
