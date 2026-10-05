# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de application/use_cases/_log_reading.py — en particulier la
lecture inversee avec arret anticipe (regression du bug reel 2026-10-04 :
"aucun changement... j'ai attendu 2 minutes, rien ne s'affiche" sur un
access.log reel de 136 Mo/415 614 lignes couvrant ~3 mois — une requete
"7 jours" parsait l'integralite du fichier avant de filtrer en memoire,
plus de 90% du travail jete). Mesure reelle post-correctif sur ce meme
fichier : 7 jours en 7,65s au lieu de plusieurs minutes."""
from __future__ import annotations

import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from omega_log.application.use_cases._log_reading import read_entries_for_paths
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError

_NOW = datetime(2026, 10, 4, 12, 0, 0)


def _line(dt: datetime, ip: str = "10.0.0.1") -> str:
    return f'{ip} - - [{dt.strftime("%d/%b/%Y:%H:%M:%S")}] "GET /x HTTP/1.1" 200 100'


def test_period_filter_returns_only_recent_entries(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    old = _NOW - timedelta(days=60)
    recent = _NOW - timedelta(hours=1)
    log_path.write_text("\n".join([_line(old), _line(recent)]) + "\n")

    entries = read_entries_for_paths([str(log_path)], period="7d", now=_NOW)

    assert len(entries) == 1
    assert entries[0].timestamp == datetime(recent.year, recent.month, recent.day, recent.hour, recent.minute, recent.second)


def test_period_filter_handles_a_large_old_prefix_quickly(tmp_path: Path) -> None:
    """Le coeur de la regression : un GROS prefixe de lignes anciennes
    (simule les mois d'historique du fichier reel) ne doit jamais etre
    integralement parse quand une periode courte est demandee — l'arret
    anticipe doit s'en charger bien avant la fin du fichier."""
    log_path = tmp_path / "access.log"
    old = _NOW - timedelta(days=90)
    recent_lines = [_line(_NOW - timedelta(hours=h)) for h in range(5)]
    with log_path.open("w") as f:
        for i in range(50_000):
            f.write(_line(old - timedelta(seconds=i)) + "\n")
        for line in recent_lines:
            f.write(line + "\n")

    start = time.monotonic()
    entries = read_entries_for_paths([str(log_path)], period="24h", now=_NOW)
    elapsed = time.monotonic() - start

    assert len(entries) == 5
    assert elapsed < 3.0, f"lecture trop lente ({elapsed:.2f}s) — l'arret anticipe ne fonctionne plus"


def test_period_none_reads_the_whole_file(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    old = _NOW - timedelta(days=400)
    recent = _NOW - timedelta(hours=1)
    log_path.write_text("\n".join([_line(old), _line(recent)]) + "\n")

    entries = read_entries_for_paths([str(log_path)], period=None, now=_NOW)

    assert len(entries) == 2


def test_period_filter_on_protected_file_without_runner_raises(tmp_path: Path) -> None:
    log_path = tmp_path / "protected.log"
    log_path.write_text(_line(_NOW - timedelta(hours=1)) + "\n")
    log_path.chmod(0)
    try:
        with pytest.raises(PermissionRequiredError):
            read_entries_for_paths([str(log_path)], period="24h", now=_NOW)
    finally:
        log_path.chmod(0o644)


def test_period_filter_combines_multiple_paths(tmp_path: Path) -> None:
    a = tmp_path / "a.log"
    b = tmp_path / "b.log"
    recent = _NOW - timedelta(hours=1)
    a.write_text(_line(recent, ip="10.0.0.1") + "\n")
    b.write_text(_line(recent, ip="10.0.0.2") + "\n")

    entries = read_entries_for_paths([str(a), str(b)], period="24h", now=_NOW)

    assert {e.ip for e in entries} == {"10.0.0.1", "10.0.0.2"}
