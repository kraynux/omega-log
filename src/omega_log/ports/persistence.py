# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Contrat pour la persistance (sauvegarde/restauration/suppression
d'archives). Adapte depuis omega-fire (ports/persistence.py) — la partie
Snapshot/banned_ips/rules/jails de la version source est specifique a
l'etat pare-feu de FIRE, sans equivalent pour des fichiers de logs, donc
delibrement pas portee (voir plan_omega_log.md §2 : "porter et adapter",
pas "copier sans discernement"). BackupInfo/PersistencePort restent
identiques — c'est le port reellement utilise pour rotate/purge/restore,
PAS ports/logs.py/LogsPort (confirme code mort chez FIRE)."""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True, slots=True)
class BackupInfo:
    path: Path
    created_at: datetime
    size_bytes: int
    components: list[str]
    metadata: dict[str, str] | None = None


class PersistencePort(Protocol):

    @abstractmethod
    def create_backup(
        self,
        backup_dir: Path,
        *,
        source_paths: list[Path],
        components: list[str] | None = None,
        metadata: dict[str, str] | None = None,
    ) -> BackupInfo:
        ...

    @abstractmethod
    def restore_backup(self, backup: BackupInfo, *, dest_dir: Path) -> None:
        ...

    @abstractmethod
    def list_backups(self, backup_dir: Path) -> list[BackupInfo]:
        ...

    @abstractmethod
    def delete_backup(self, backup: BackupInfo) -> None:
        ...
