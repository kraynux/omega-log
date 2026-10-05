# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Purge backups command — porte verbatim depuis omega-fire
(application/commands/purge_backups.py) : entierement generique, rien
a adapter. La SELECTION des archives a supprimer reste la responsabilite
de l'appelant (ecran) — ce cas d'usage ne fait qu'executer la
suppression via le port."""
from __future__ import annotations

from dataclasses import dataclass, field

from omega_log.ports.persistence import BackupInfo, PersistencePort


@dataclass
class PurgeBackupsResult:
    deleted_count: int = 0
    error_count: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.error_count == 0


class PurgeBackupsCommand:
    def __init__(self, persistence_port: PersistencePort):
        self._port = persistence_port

    def execute(self, backups_to_delete: list[BackupInfo]) -> PurgeBackupsResult:
        deleted_count = 0
        errors: list[str] = []

        for backup in backups_to_delete:
            try:
                self._port.delete_backup(backup)
                deleted_count += 1
            except OSError as e:
                errors.append(f"{backup.path.name} : {e}")

        return PurgeBackupsResult(deleted_count=deleted_count, error_count=len(errors), errors=errors)
