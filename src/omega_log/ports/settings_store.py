# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Re-export depuis omega_lib (plan_omega_log.md §1, corrige D-013) : garde
la convention 'importer depuis omega_log.ports.X' uniforme dans tout le
reste du code, meme principe que le reste de la suite omega-."""
from __future__ import annotations

from omega_lib.ports.settings_store import SettingsStore

__all__ = ["SettingsStore"]
