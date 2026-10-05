# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de domain/value_objects/viewer_type.py — regle de compatibilite
du plan_omega_log.md §5 (1 log -> les 3 viewers, 2+ logs -> lnav seul)."""
from __future__ import annotations

from omega_log.domain.value_objects.viewer_type import ViewerType, allowed_viewers


def test_single_log_allows_all_three_viewers() -> None:
    allowed = allowed_viewers(1)
    assert set(allowed) == {ViewerType.SIMPLE, ViewerType.CLASSIC, ViewerType.LNAV}


def test_zero_logs_allows_all_three_viewers() -> None:
    assert set(allowed_viewers(0)) == {ViewerType.SIMPLE, ViewerType.CLASSIC, ViewerType.LNAV}


def test_multiple_logs_only_allow_lnav() -> None:
    assert allowed_viewers(2) == (ViewerType.LNAV,)
    assert allowed_viewers(5) == (ViewerType.LNAV,)
