# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat de la Bibliotheque (plan_omega_log.md §3/§10) : hub central
referencant tous les logs a traiter, alimente par le Registre (import au
detail/en totalite, Phase 4) ou manuellement (cette phase)."""
from __future__ import annotations

from typing import Protocol

from omega_log.domain.entities.favorite import LibraryRecord


class LogRepository(Protocol):
    def list_all(self) -> list[LibraryRecord]: ...

    def add(self, record: LibraryRecord) -> None: ...

    def remove(self, path: str) -> None: ...

    def contains(self, path: str) -> bool: ...
