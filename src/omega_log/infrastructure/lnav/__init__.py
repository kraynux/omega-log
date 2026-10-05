# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Infrastructure lnav subsystem — porte depuis omega-fire.

Encapsule lnav en tant que moteur d'analyse externe : sous-processus
dans un pty, et le repondeur minimal de capacites terminal requis pour
que lnav (notcurses) demarre sans bloquer. Ne modifie jamais lnav
lui-meme."""
from omega_log.infrastructure.lnav.pty_session import (
    CONFIG_DIR,
    TerminalResponder,
    kill_lnav,
    relay_osc52,
    resize_pty,
    spawn_lnav,
    wait_dead,
)

__all__ = [
    "CONFIG_DIR",
    "TerminalResponder",
    "kill_lnav",
    "relay_osc52",
    "resize_pty",
    "spawn_lnav",
    "wait_dead",
]
