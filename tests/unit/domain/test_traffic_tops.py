# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Barre du viewer Simple : refus 403/429 et tops, repris d'omega-serv (2026-11-06)."""
from datetime import datetime, timezone

from omega_log.domain.logs.analytics import compute_traffic_stats
from omega_log.domain.logs.models import LogEntry, LogLevel, LogSource


def _entry(ip: str | None = "1.2.3.4", **overrides) -> LogEntry:
    defaults = {
        "timestamp": datetime(2026, 10, 10, 10, 0, 0, tzinfo=timezone.utc),
        "source": LogSource.ACCESS,
        "level": LogLevel.INFO,
        "ip": ip,
    }
    defaults.update(overrides)
    return LogEntry(**defaults)


def test_refusals_top_ips_and_paths_without_query_string() -> None:
    entries = [
        _entry(ip="1.1.1.1", http_path="/a?x=1", http_status=200),
        _entry(ip="1.1.1.1", http_path="/a?x=2", http_status=200),
        _entry(ip="2.2.2.2", http_path="/wp-login.php", http_status=404),
        _entry(ip="3.3.3.3", http_path="/admin", http_status=403),
        _entry(ip="3.3.3.3", http_path="/a", http_status=429),
    ]
    stats = compute_traffic_stats(entries)
    assert (stats.status_403, stats.status_429) == (1, 1)
    assert stats.top_ips[0] in {("1.1.1.1", 2), ("3.3.3.3", 2)}
    assert stats.top_paths[0] == ("/a", 3)
    assert stats.top_not_found == [("/wp-login.php", 1)]


def test_log_without_http_fields_has_no_path_tops() -> None:
    stats = compute_traffic_stats([_entry(), _entry(ip="9.9.9.9")])
    assert stats.top_paths == [] and stats.top_not_found == []
