# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Entite Favorite (plan_omega_log.md §3) : un ou plusieurs logs +
viewer, enregistres sous un nom pour un lancement direct depuis l'ecran
Favoris."""
from __future__ import annotations

from dataclasses import dataclass

from omega_log.domain.value_objects.viewer_type import ViewerType


@dataclass(frozen=True, slots=True)
class Favorite:
    name: str
    paths: tuple[str, ...]
    viewer: ViewerType


@dataclass(frozen=True, slots=True)
class LibraryRecord:
    """Entree persistee de la Bibliotheque — identite seule (path/
    access/service_id), jamais l'etat au moment du scan (taille/mtime) :
    la fraicheur est toujours recalculee a l'affichage
    (application/use_cases/library.py::refresh_log_file), jamais
    figee dans le stockage (voir annuaire §0 sur les fichiers morts)."""
    path: str
    access: str
    service_id: str | None = None
