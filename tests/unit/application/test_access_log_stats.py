# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de application/use_cases/access_log_stats.py — couvre
explicitement le bug du timestamp Apache/Nginx trouve et corrige en
Phase 7 (domain/logs/parser.py::extract_timestamp)."""
from __future__ import annotations

from pathlib import Path

from omega_log.application.use_cases.access_log_stats import (
    compute_access_log_stats,
    hourly_stats_for_export,
)

_LOG_CONTENT = (
    '10.0.0.1 - - [10/Oct/2026:10:00:00] "GET / HTTP/1.1" 200 100\n'
    '10.0.0.2 - - [10/Oct/2026:10:00:01] "GET / HTTP/1.1" 404 100\n'
    '10.0.0.1 - - [10/Oct/2026:11:00:02] "GET /x HTTP/1.1" 500 50\n'
)


def test_compute_access_log_stats(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text(_LOG_CONTENT)

    result = compute_access_log_stats([str(log_path)])

    assert result.stats.parsed_lines == 3
    assert result.stats.unique_ips == 2


def test_hourly_distribution_respects_apache_timestamp(tmp_path: Path) -> None:
    """Sans la correction du parseur (Phase 7), les 3 lignes tombaient
    toutes sur l'heure courante au lieu de 10h/11h."""
    log_path = tmp_path / "access.log"
    log_path.write_text(_LOG_CONTENT)

    result = compute_access_log_stats([str(log_path)])
    hourly = {h["hour"]: h["count"] for h in hourly_stats_for_export(result.stats) if h["count"] > 0}

    assert hourly == {10: 2, 11: 1}


def test_compute_access_log_stats_empty_without_matching_period(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    # 2020, loin dans le PASSE par rapport a "maintenant" quelle que soit
    # la date d'execution du test — contrairement a _LOG_CONTENT (2026),
    # dont les dates peuvent se retrouver dans le futur proche selon la
    # date systeme et donc passer trivialement un filtre "depuis 24h"
    # (qui ne verifie qu'une borne basse, jamais une borne haute).
    log_path.write_text(_LOG_CONTENT.replace("2026", "2020"))

    result = compute_access_log_stats([str(log_path)], period="24h")
    assert result.stats.parsed_lines == 0
