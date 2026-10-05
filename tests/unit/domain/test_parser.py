# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests du parseur generique de logs (domain/logs/parser.py)."""
from __future__ import annotations

import time

from omega_log.domain.logs.models import LogLevel, LogSource
from omega_log.domain.logs.parser import (
    detect_log_source,
    extract_http_fields,
    extract_ip,
    extract_log_level,
    extract_timestamp,
    parse_log_line,
    parse_log_lines,
)


def test_extract_ip_finds_first_ipv4() -> None:
    assert extract_ip("10.0.0.1 - - request") == "10.0.0.1"


def test_extract_ip_returns_none_without_ip() -> None:
    assert extract_ip("no ip here") is None


def test_extract_timestamp_apache_combined_format() -> None:
    ts = extract_timestamp('10.0.0.1 - - [10/Oct/2026:10:30:45] "GET / HTTP/1.1" 200 100')
    assert ts is not None
    assert (ts.day, ts.month, ts.year, ts.hour, ts.minute, ts.second) == (10, 10, 2026, 10, 30, 45)


def test_extract_timestamp_iso_format() -> None:
    ts = extract_timestamp("2026-10-03T14:22:01 some message")
    assert ts is not None
    assert (ts.year, ts.month, ts.day, ts.hour, ts.minute, ts.second) == (2026, 10, 3, 14, 22, 1)


def test_extract_timestamp_syslog_format() -> None:
    ts = extract_timestamp("Oct 10 13:56:01 host sshd[123]: message")
    assert ts is not None
    assert (ts.month, ts.day, ts.hour, ts.minute, ts.second) == (10, 10, 13, 56, 1)


def test_extract_timestamp_returns_none_without_timestamp() -> None:
    assert extract_timestamp("no timestamp in this line") is None


def test_extract_log_level_defaults_to_info() -> None:
    assert extract_log_level("a plain message") == LogLevel.INFO


def test_extract_log_level_detects_error() -> None:
    assert extract_log_level("an ERROR occurred") == LogLevel.ERROR


def test_detect_log_source_auth() -> None:
    assert detect_log_source("sshd: Failed password for root") == LogSource.AUTH


def test_detect_log_source_fail2ban() -> None:
    assert detect_log_source("fail2ban.actions: Ban 10.0.0.1") == LogSource.FAIL2BAN


def test_detect_log_source_access() -> None:
    assert detect_log_source('10.0.0.1 - - "GET / HTTP/1.1" 200') == LogSource.ACCESS


def test_detect_log_source_kernel() -> None:
    assert detect_log_source("kernel: nftables rule matched") == LogSource.KERN


def test_detect_log_source_defaults_to_syslog() -> None:
    assert detect_log_source("a plain generic message") == LogSource.SYSLOG


def test_parse_log_line_skips_empty_lines() -> None:
    assert parse_log_line("") is None
    assert parse_log_line("   ") is None


def test_parse_log_line_builds_entry() -> None:
    entry = parse_log_line(
        '10.0.0.1 - - [10/Oct/2026:10:30:45] "GET / HTTP/1.1" 200 100',
        line_number=1,
        log_path="/var/log/access.log",
    )
    assert entry is not None
    assert entry.ip == "10.0.0.1"
    assert entry.source == LogSource.ACCESS
    assert entry.line_number == 1
    assert entry.log_path == "/var/log/access.log"


def test_parse_log_lines_filters_empty_lines() -> None:
    entries = parse_log_lines(["line one\n", "\n", "line two\n"])
    assert len(entries) == 2


def test_extract_http_fields_combined_format() -> None:
    method, path, status, latency = extract_http_fields(
        '10.0.0.1 - - [10/Oct/2026:10:30:45] "GET /index.html HTTP/1.1" 200 1024'
    )
    assert (method, path, status) == ("GET", "/index.html", 200)
    assert latency is None  # Common Log Format standard : pas de duree


def test_extract_http_fields_with_trailing_latency() -> None:
    # certains formats personnalises (directive Apache %D/%T) ajoutent la
    # duree en fin de ligne, apres les champs Combined standard
    _, _, status, latency = extract_http_fields(
        '10.0.0.1 - - [10/Oct/2026:10:30:45] "GET / HTTP/1.1" 404 512 "-" "curl/8.0" 237'
    )
    assert status == 404
    assert latency == 237


def test_extract_http_fields_non_http_line_returns_all_none() -> None:
    assert extract_http_fields("Oct 10 13:56:01 host sshd[123]: Failed password for root") == (None, None, None, None)


def test_parse_log_line_populates_http_fields_for_access_log() -> None:
    entry = parse_log_line('10.0.0.1 - - [10/Oct/2026:10:30:45] "GET /x HTTP/1.1" 404 100')
    assert entry is not None
    assert entry.http_method == "GET"
    assert entry.http_path == "/x"
    assert entry.http_status == 404


def test_parse_log_line_upgrades_level_from_http_status_when_no_keyword() -> None:
    # un 404/500 Combined standard ne contient jamais le mot "error" en
    # toutes lettres — le niveau doit refleter le code HTTP quand meme
    not_found = parse_log_line('10.0.0.1 - - [10/Oct/2026:10:30:45] "GET /x HTTP/1.1" 404 100')
    server_error = parse_log_line('10.0.0.1 - - [10/Oct/2026:10:30:45] "GET /x HTTP/1.1" 500 100')
    ok = parse_log_line('10.0.0.1 - - [10/Oct/2026:10:30:45] "GET /x HTTP/1.1" 200 100')
    assert not_found is not None and not_found.level == LogLevel.WARNING
    assert server_error is not None and server_error.level == LogLevel.ERROR
    assert ok is not None and ok.level == LogLevel.INFO


def test_parse_log_line_never_downgrades_an_already_detected_level() -> None:
    # une ligne qui contient deja "CRITICAL" explicitement ne doit jamais
    # etre ecrasee par la deduction du code HTTP (ici 404 -> WARNING
    # serait une regression du niveau reellement signale)
    entry = parse_log_line('10.0.0.1 - - [10/Oct/2026:10:30:45] "GET /x HTTP/1.1" 404 100 CRITICAL')
    assert entry is not None
    assert entry.level == LogLevel.CRITICAL


def test_parse_log_line_is_fast_enough_for_a_real_access_log() -> None:
    """Regression de performance (2026-10-04, retour utilisateur : "bug
    severe dans statistique... aucun resultat ne sort" sur un access.log
    reel) — mesure reelle AVANT correctif : 23s pour 34811 lignes d'un
    access.log reel (cProfile a l'appui, re-compilation de regex a
    chaque ligne dans extract_log_level notamment). Ce test ne rejoue
    pas ce fichier exact (couteux a chaque run de la suite) mais fixe un
    seuil large (2.5s pour 5000 lignes synthetiques, mesure reelle
    post-correctif ~0.9s) : largement depasse par toute regression du
    meme ordre de grandeur (~3.3s attendues avec le bug), jamais
    atteint par le comportement normal."""
    lines = [
        f'10.0.0.{i % 5} - - [04/Oct/2026:10:{i % 60:02d}:00 +0200] "GET /x HTTP/1.1" 200 100'
        for i in range(5000)
    ]
    start = time.monotonic()
    for i, line in enumerate(lines):
        parse_log_line(line, line_number=i)
    elapsed = time.monotonic() - start
    assert elapsed < 2.5, f"parse_log_line trop lent : {elapsed:.2f}s pour 5000 lignes (seuil 2.5s)"
