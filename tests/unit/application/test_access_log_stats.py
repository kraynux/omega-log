# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de application/use_cases/access_log_stats.py — couvre
explicitement le bug du timestamp Apache/Nginx trouve et corrige en
Phase 7 (domain/logs/parser.py::extract_timestamp)."""
from __future__ import annotations

from pathlib import Path

from omega_log.application.use_cases.access_log_stats import compute_access_log_stats

_LOG_CONTENT = (
    '10.0.0.1 - - [10/Oct/2026:10:00:00] "GET / HTTP/1.1" 200 100\n'
    '10.0.0.2 - - [10/Oct/2026:10:00:01] "GET / HTTP/1.1" 404 100\n'
    '10.0.0.1 - - [10/Oct/2026:11:00:02] "GET /x HTTP/1.1" 500 50\n'
)


def test_compute_access_log_stats(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text(_LOG_CONTENT)

    result = compute_access_log_stats([str(log_path)])

    assert result.report.total == 3
    assert result.report.unique_ips == 2


def test_hourly_distribution_respects_apache_timestamp(tmp_path: Path) -> None:
    """Sans la correction du parseur (Phase 7), les 3 lignes tombaient
    toutes sur l'heure courante au lieu de 10h/11h."""
    log_path = tmp_path / "access.log"
    log_path.write_text(_LOG_CONTENT)

    result = compute_access_log_stats([str(log_path)])
    hourly = {hour: count for hour, count in enumerate(result.report.hourly) if count > 0}

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
    assert result.report.total == 0


def test_report_summary_statuses_and_rankings(tmp_path: Path) -> None:
    """Rapport complet (2026-11-06) : synthese, statuts, tops, tendance par jour, jamais de valeur inventee."""
    log_path = tmp_path / "access.log"
    log_path.write_text(_LOG_CONTENT + '10.0.0.3 - - [11/Oct/2026:09:00:00] "GET /x?a=1 HTTP/1.1" 404 -\n')

    report = compute_access_log_stats([str(log_path)]).report

    assert (report.total, report.http_total, report.unique_ips) == (4, 4, 3)
    assert report.error_rate == 75.0                       # 404, 500, 404 sur 4 requetes
    assert report.bytes_total == 250                       # « - » jamais estime
    assert report.statuses == {"2xx": 1, "3xx": 0, "4xx": 2, "5xx": 1, "403": 0, "429": 0}
    assert (report.peak_hour, report.peak_count) == (10, 2)
    assert report.daily == [("2026-10-10", 3), ("2026-10-11", 1)]
    assert [(i.value, i.count, i.errors) for i in report.top_paths] == [("/", 2, 1), ("/x", 2, 2)]  # egalite : ordre d apparition
    assert [(i.value, i.count) for i in report.top_not_found] == [("/", 1), ("/x", 1)]
    assert (report.top_ips[0].value, report.top_ips[0].count, report.top_ips[0].errors) == ("10.0.0.1", 2, 1)


def test_report_of_non_http_log_has_no_statuses(tmp_path: Path) -> None:
    log_path = tmp_path / "auth.log"
    log_path.write_text("Oct 10 10:00:00 host sshd[1]: error: Failed password for root from 1.2.3.4 port 22\n"
                        "Oct 10 10:05:00 host sshd[1]: Accepted password for bob from 1.2.3.5 port 22\n")
    report = compute_access_log_stats([str(log_path)]).report
    assert report.statuses == {} and report.top_paths == [] and report.bytes_total is None
    assert report.error_rate == 50.0 and report.unique_ips == 2
