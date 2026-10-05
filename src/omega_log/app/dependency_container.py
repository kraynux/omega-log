# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Cablage des adaptateurs concrets derriere les ports — consomme
uniquement par app/bootstrap.py (racine de composition) et par
interfaces/ (sous TYPE_CHECKING uniquement, jamais a l'execution).

Etendu Phase 6 (Rotate/Purger/Restaurer, voir plan_omega_log.md §6) :
Exporter/Statistiques des logs d'acces restent a ajouter (Phase 7)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from omega_log.ports.favorite_repository import FavoriteRepository
from omega_log.ports.log_repository import LogRepository
from omega_log.ports.persistence import PersistencePort
from omega_log.ports.process_runner_port import ProcessRunnerPort
from omega_log.ports.settings_store import SettingsStore
from omega_log.ports.terminal_detector import TerminalDetector


@dataclass
class DependencyContainer:
    settings_store: SettingsStore
    terminal_detector: TerminalDetector
    log_repository: LogRepository
    favorite_repository: FavoriteRepository
    persistence_port: PersistencePort
    backup_dir: Path
    restore_temp_dir: Path
    default_exports_dir: Path
    default_screenshots_dir: Path
    process_runner: ProcessRunnerPort
    elevated_tmp_dir: Path
    """process_runner/elevated_tmp_dir : elevation sudo ponctuelle pour
    l'acces aux logs proteges de /var/log (plan §5.1, 2026-10-03) — voir
    infrastructure/privileged/."""

    def close(self) -> None:
        """Rien a liberer pour l'instant (pas de connexion ouverte) —
        present pour que __main__.py puisse deja appeler
        `container.close()` sans condition, meme convention que le
        reste de la suite."""
