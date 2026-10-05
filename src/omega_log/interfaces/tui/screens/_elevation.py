# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Point d'entree UNIQUE pour demander l'elevation sudo depuis un ecran
(plan §5.1, 2026-10-03) — chaque ecran qui en a besoin (viewers,
process_ip, rotate, purge) appelle `request_elevation()` plutot que de
re-cabler lui-meme `_maybe_suspend()` + `authenticate_sudo()`."""
from __future__ import annotations

from typing import TYPE_CHECKING

from omega_log.infrastructure.privileged.elevation import authenticate_sudo

if TYPE_CHECKING:
    from omega_log.interfaces.tui.screens._base import OmegaScreen
    from omega_log.ports.process_runner_port import ProcessRunnerPort


def request_elevation(screen: OmegaScreen, runner: ProcessRunnerPort) -> bool:
    """Suspend l'ecran, authentifie sudo sur le vrai terminal, reprend
    la main. Retourne True si l'elevation est maintenant disponible
    (deja root ou authentification reussie) — notifie l'utilisateur et
    retourne False sinon (jamais une exception : l'appelant decide quoi
    faire d'un refus, typiquement retomber sur le message d'erreur
    normal de permission)."""
    with screen._maybe_suspend():
        result = authenticate_sudo(runner)
    if not result.success:
        screen.app.notify(result.message or "Authentification sudo echouee ou annulee.", severity="error")
        return False
    return True
