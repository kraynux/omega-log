# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Archive file storage (tar.gz) — porte verbatim depuis omega-fire
(infrastructure/storage/files/archive_store.py) : pur I/O fichier/tar,
aucune dependance firewall, rien a adapter."""
import tarfile
from datetime import datetime
from pathlib import Path

from omega_log.core.exceptions import CoreError


class ArchiveStoreError(CoreError):
    """Exception raised when archive operations fail."""


class ArchiveStore:
    """Archive file storage for tar.gz files."""

    def __init__(self, base_dir: Path):
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def create_archive(
        self, archive_name: str, source_paths: list[Path], base_path: Path | None = None,
    ) -> Path:
        try:
            archive_path = self._base_dir / f"{archive_name}.tar.gz"
            with tarfile.open(archive_path, "w:gz") as tar:
                for source in source_paths:
                    if not source.exists():
                        continue
                    arcname = source.name if base_path is None else str(source.relative_to(base_path))
                    tar.add(source, arcname=arcname)
            return archive_path
        except OSError as e:
            raise ArchiveStoreError(f"Failed to create archive {archive_name}: {e}") from e

    def extract_archive(self, archive_path: Path, dest_dir: Path) -> None:
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(dest_dir)
        except (OSError, tarfile.TarError) as e:
            raise ArchiveStoreError(f"Failed to extract archive {archive_path}: {e}") from e

    def list_archives(self, pattern: str = "*.tar.gz") -> list[Path]:
        return list(self._base_dir.glob(pattern))

    def get_archive_info(self, archive_path: Path) -> dict:
        try:
            stat = archive_path.stat()
            return {
                "path": str(archive_path),
                "name": archive_path.name,
                "size_bytes": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            }
        except OSError as e:
            raise ArchiveStoreError(f"Failed to get info for {archive_path}: {e}") from e

    def delete_archive(self, archive_path: Path) -> bool:
        if archive_path.exists():
            archive_path.unlink()
            return True
        return False
