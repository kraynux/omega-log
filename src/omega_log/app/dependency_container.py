# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Cablage des adaptateurs concrets derriere les ports — consomme
uniquement par app/bootstrap.py (racine de composition) et par
interfaces/ (sous TYPE_CHECKING uniquement, jamais a l'execution).

Etendu Phase 6 (Rotate/Purger/Restaurer, voir plan_omega_log.md §6) :
Exporter/Statistiques des logs d'acces restent a ajouter (Phase 7)."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from omega_log.ports.declaration_port import DeclarationSenderPort, DeclarationStorePort
from omega_log.ports.favorite_repository import FavoriteRepository
from omega_log.ports.log_repository import LogRepository
from omega_log.ports.persistence import PersistencePort
from omega_log.ports.process_runner_port import ProcessRunnerPort
from omega_log.ports.release_source_port import ReleaseSourcePort
from omega_log.ports.remote_log_source_repository import RemoteLogSourceRepositoryPort
from omega_log.ports.settings_store import SettingsStore
from omega_log.ports.terminal_detector import TerminalDetector

if TYPE_CHECKING:
    from omega_log.infrastructure.probe.omega_serv_locator import OmegaServScan
    from omega_log.infrastructure.storage.rotation_automation_store import RotationAutomationStore


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
    remote_source_repository: RemoteLogSourceRepositoryPort
    remote_cache_dir: Path
    """Sources distantes SSH (portees d'omega-serv, 2026-11-06) : definitions nommees et dossier des copies
    recuperees par scp (une copie par source, remplacee a chaque recuperation)."""
    find_omega_serv_logs: Callable[[], OmegaServScan]
    """« Ajouter les logs connus d'Omega-Serv » : recherche locale en lecture seule, appelee sur clic."""
    app_version: str
    declaration_store: DeclarationStorePort
    declaration_sender: DeclarationSenderPort
    open_url: Callable[[str], bool]
    """Aide -> Contact et support (repris d'omega-serv, 2026-11-06) : declaration anonyme « une seule
    fois » et ouverture d'une adresse dans le navigateur (False sans session graphique : l'ecran
    affiche alors l'adresse)."""

    var_dir: Path
    """Racine var/ de cette session (absolue) : la tache planifiee des sauvegardes la recoit (OMEGA_LOG_VAR_DIR)."""
    rotation_automation_store: RotationAutomationStore
    """Sauvegardes planifiees (portees d'omega-serv 2.6.0, 2026-11-07), executees chaque nuit."""
    release_source: ReleaseSourcePort
    """Aide -> Contact et support -> « Verifier les mises a jour » : lit download/sha.txt, seulement sur clic."""

    def close(self) -> None:
        """Rien a liberer pour l'instant (pas de connexion ouverte) —
        present pour que __main__.py puisse deja appeler
        `container.close()` sans condition, meme convention que le
        reste de la suite."""
