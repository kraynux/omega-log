# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat des Favoris (plan_omega_log.md §3) : combinaisons logs+viewer
nommees, source = Bibliotheque, lancement direct depuis l'ecran Favoris."""
from __future__ import annotations

from typing import Protocol

from omega_log.domain.entities.favorite import Favorite


class FavoriteRepository(Protocol):
    def list_all(self) -> list[Favorite]: ...

    def add(self, favorite: Favorite) -> None: ...

    def remove(self, name: str) -> None: ...
