# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Persistence adapter — file-based implementation of PersistencePort.

ADAPTE depuis omega-fire (infrastructure/storage/files/persistence_adapter.py) :
porte uniquement la partie BackupInfo (create/restore/list/delete_backup,
via ArchiveStore pour le tar.gz reel) — la partie Snapshot (etat complet
pare-feu : IP bannies/regles/jails) est entierement absente ici, pas
seulement non implementee, puisque ports/persistence.py de LOG ne la
declare meme pas (voir plan_omega_log.md §2 : adapte depuis omega-fire
en retirant ce qui est specifique au pare-feu, pas copie sans
discernement)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from omega_log.infrastructure.exceptions import StorageError
from omega_log.infrastructure.storage.files.archive_store import ArchiveStore, ArchiveStoreError
from omega_log.ports.persistence import BackupInfo


class FileBackupAdapter:
    """Implemente PersistencePort via ArchiveStore (tar.gz)."""

    def __init__(self, archive_store: ArchiveStore) -> None:
        self._archive_store = archive_store

    def create_backup(
        self,
        backup_dir: Path,
        *,
        source_paths: list[Path],
        components: list[str] | None = None,
        metadata: dict[str, str] | None = None,
        archive_name: str | None = None,
    ) -> BackupInfo:
        if not source_paths:
            raise StorageError("create_backup: source_paths must not be empty")

        if archive_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = source_paths[0].stem
            archive_name = f"backup_{stem}_{timestamp}"

        try:
            archive_path = self._archive_store.create_archive(archive_name=archive_name, source_paths=source_paths)
            info = self._archive_store.get_archive_info(archive_path)
        except ArchiveStoreError as e:
            raise StorageError(f"Failed to create backup: {e}") from e

        return BackupInfo(
            path=archive_path,
            created_at=datetime.fromisoformat(info["created_at"]),
            size_bytes=info["size_bytes"],
            components=components or [],
            metadata=metadata,
        )

    def restore_backup(self, backup: BackupInfo, *, dest_dir: Path) -> None:
        try:
            self._archive_store.extract_archive(backup.path, dest_dir)
        except ArchiveStoreError as e:
            raise StorageError(f"Failed to restore backup {backup.path}: {e}") from e

    def list_backups(self, backup_dir: Path) -> list[BackupInfo]:
        try:
            infos = []
            for path in self._archive_store.list_archives():
                raw = self._archive_store.get_archive_info(path)
                infos.append(BackupInfo(
                    path=path,
                    created_at=datetime.fromisoformat(raw["created_at"]),
                    size_bytes=raw["size_bytes"],
                    components=[],
                    metadata=None,
                ))
        except ArchiveStoreError as e:
            raise StorageError(f"Failed to list backups in {backup_dir}: {e}") from e

        return sorted(infos, key=lambda b: b.created_at, reverse=True)

    def delete_backup(self, backup: BackupInfo) -> None:
        self._archive_store.delete_archive(backup.path)
