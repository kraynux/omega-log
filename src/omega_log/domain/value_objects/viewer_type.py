# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""ViewerType — les 3 viewers du plan (plan_omega_log.md §2/§3) :
SIMPLE (tail -f + stats generiques, omega-fire adapte), CLASSIC
(lecture+suivi thematise, omega-serv adapte), LNAV (fusion multi-logs,
PTY). Regle de selection (plan §5) : 1 log -> les 3 disponibles ; 2+
logs -> LNAV uniquement."""
from __future__ import annotations

from enum import Enum


class ViewerType(Enum):
    SIMPLE = "simple"
    CLASSIC = "classic"
    LNAV = "lnav"


def allowed_viewers(log_count: int) -> tuple[ViewerType, ...]:
    """1 log -> les 3 viewers ; 2+ logs -> LNAV uniquement (seul capable
    de fusionner plusieurs fichiers)."""
    if log_count <= 1:
        return (ViewerType.SIMPLE, ViewerType.CLASSIC, ViewerType.LNAV)
    return (ViewerType.LNAV,)
