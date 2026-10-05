# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Racine de composition : construit un DependencyContainer avec les
adaptateurs concrets de production. Seul module autorise a importer a la
fois infrastructure/ ET app/dependency_container.py."""
from __future__ import annotations

from pathlib import Path

from omega_lib.infrastructure.terminal.detector import SystemTerminalDetector

from omega_log.app.dependency_container import DependencyContainer
from omega_log.infrastructure.config import paths
from omega_log.infrastructure.logging.config import APP_LOG_FILENAME, configure_logging
from omega_log.infrastructure.process.subprocess_runner import SubprocessRunner
from omega_log.infrastructure.storage.files.archive_store import ArchiveStore
from omega_log.infrastructure.storage.files.json_favorite_repository import JsonFavoriteRepository
from omega_log.infrastructure.storage.files.json_log_repository import JsonLogRepository
from omega_log.infrastructure.storage.files.json_settings_store import JsonSettingsStore
from omega_log.infrastructure.storage.files.persistence_adapter import FileBackupAdapter


def bootstrap(*, var_dir: Path | None = None, console_logging: bool = True) -> DependencyContainer:
    """`console_logging=False` pour le TUI (voir __main__.py) : Textual
    prend le controle exclusif de l'ecran, une ecriture de log directe sur
    stderr pendant l'usage corromprait son rendu. Le CLI garde
    `console_logging=True` par defaut."""
    base = var_dir if var_dir is not None else paths.resolve_var_dir()
    configure_logging(log_path=base / APP_LOG_FILENAME, console=console_logging)

    backup_dir = paths.default_backup_dir(base)

    return DependencyContainer(
        settings_store=JsonSettingsStore(paths.default_settings_path(base)),
        terminal_detector=SystemTerminalDetector(),
        log_repository=JsonLogRepository(paths.default_library_path(base)),
        favorite_repository=JsonFavoriteRepository(paths.default_favorites_path(base)),
        persistence_port=FileBackupAdapter(ArchiveStore(backup_dir)),
        backup_dir=backup_dir,
        restore_temp_dir=paths.default_restore_temp_dir(base),
        default_exports_dir=paths.default_exports_dir(base),
        default_screenshots_dir=paths.default_screenshots_dir(base),
        process_runner=SubprocessRunner(),
        elevated_tmp_dir=paths.default_elevated_tmp_dir(base),
    )
