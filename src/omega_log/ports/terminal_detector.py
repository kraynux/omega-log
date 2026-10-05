# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Re-export depuis omega_lib (plan_omega_log.md §1), meme raisonnement
que ports/settings_store.py."""
from __future__ import annotations

from omega_lib.ports.terminal_detector import TerminalDetector

__all__ = ["TerminalDetector"]
