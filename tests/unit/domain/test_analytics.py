# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de domain/logs/analytics.py."""
from __future__ import annotations

from datetime import datetime

from omega_log.domain.logs.analytics import (
    compute_hourly_stats,
    compute_stats,
    compute_top_ips,
    filter_entries_by_ip,
    filter_error_entries,
)
from omega_log.domain.logs.models import LogEntry, LogLevel, LogSource


def _entry(ip: str, hour: int, level: LogLevel = LogLevel.INFO) -> LogEntry:
    return LogEntry(
        timestamp=datetime(2026, 10, 3, hour, 0, 0),
        source=LogSource.ACCESS,
        level=level,
        ip=ip,
    )


def test_compute_top_ips_counts_occurrences_descending() -> None:
    entries = [_entry("10.0.0.1", 10), _entry("10.0.0.2", 10), _entry("10.0.0.1", 11)]
    top = compute_top_ips(entries, n=10)
    assert top[0].ip == "10.0.0.1"
    assert top[0].count == 2
    assert top[1].ip == "10.0.0.2"
    assert top[1].count == 1


def test_compute_top_ips_ignores_entries_without_ip() -> None:
    entries = [LogEntry(timestamp=datetime(2026, 10, 3), source=LogSource.SYSLOG, ip=None)]
    assert compute_top_ips(entries) == []


def test_compute_hourly_stats_covers_all_24_hours() -> None:
    entries = [_entry("10.0.0.1", 10), _entry("10.0.0.1", 10)]
    hourly = compute_hourly_stats(entries)
    assert len(hourly) == 24
    assert hourly[10].count == 2
    assert hourly[0].count == 0


def test_compute_stats_aggregates_unique_ips_and_errors() -> None:
    entries = [
        _entry("10.0.0.1", 10),
        _entry("10.0.0.2", 10, level=LogLevel.ERROR),
        _entry("10.0.0.1", 11),
    ]
    stats = compute_stats(entries)
    assert stats.unique_ips == 2
    assert stats.parsed_lines == 3
    assert stats.error_rate() > 0


def test_filter_entries_by_ip() -> None:
    entries = [_entry("10.0.0.1", 10), _entry("10.0.0.2", 10)]
    filtered = filter_entries_by_ip(entries, "10.0.0.1")
    assert len(filtered) == 1
    assert filtered[0].ip == "10.0.0.1"


def test_filter_error_entries() -> None:
    entries = [_entry("10.0.0.1", 10), _entry("10.0.0.2", 10, level=LogLevel.CRITICAL)]
    errors = filter_error_entries(entries)
    assert len(errors) == 1
    assert errors[0].level == LogLevel.CRITICAL
