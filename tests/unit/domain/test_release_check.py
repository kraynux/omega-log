# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Verification manuelle des mises a jour et version du splash (portees d'omega-serv 2.6.0, 2026-11-07)."""
from __future__ import annotations

from omega_log.domain.updates.release_check import (
    DOWNLOAD_BASE_URL,
    UpdateStatus,
    compare_with_published,
)
from omega_log.interfaces.tui.widgets.splash_hero import version_bar

_SHA = "version 1.6.0 :\n\naa  omega-log-1.6.0.tar.gz\n\nversion 1.5.0 :\n\nbb  omega-log-1.5.0.tar.gz\n"


def test_compare_with_published() -> None:
    newer = compare_with_published("1.5.0", _SHA)
    assert newer.status is UpdateStatus.UPDATE_AVAILABLE and newer.latest == "1.6.0"
    assert newer.archive_url == DOWNLOAD_BASE_URL + "omega-log-1.6.0.tar.gz"
    assert newer.notes_url == DOWNLOAD_BASE_URL + "omega-log-1.6.0-nouveautes.txt"
    assert compare_with_published("1.6.0", _SHA).status is UpdateStatus.UP_TO_DATE
    assert compare_with_published("1.7.0", _SHA).status is UpdateStatus.AHEAD
    assert compare_with_published("1.6.0", None).status is UpdateStatus.UNKNOWN
    assert compare_with_published("1.6.0", "aa  omega-serv-9.0.0.tar.gz").status is UpdateStatus.UNKNOWN


def test_version_bar_keeps_the_hand_written_form() -> None:
    assert version_bar("1.5.0") == "▒V1.50▒"
    assert version_bar("1.6.0") == "▒V1.60▒"
    assert version_bar("2.0.0-dev") == "▒V2.0.0-dev▒"
