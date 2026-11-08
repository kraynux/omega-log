# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Sante des logs (portee d'omega-serv 2.6.0, 2026-11-07) : regles, collecte, textes, exports."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from omega_log.application.use_cases.health_presentation import (
    finding_text,
    html_arguments,
    render_text,
    report_to_dict,
)
from omega_log.application.use_cases.log_health import (
    archive_facts,
    collect_log_health,
    fix_world_writable,
)
from omega_log.domain.logs.health import HealthLevel, evaluate_automations
from omega_log.infrastructure.exporters.html_exporter import export_log_health_html

_NOW = datetime.now(timezone.utc)


def _codes(report, path: str) -> set[str]:
    log = next(item for item in report.logs if item.facts.path == path)
    return {finding.code for finding in log.findings}


def test_collect_flags_missing_empty_world_writable_and_duplicates(tmp_path: Path) -> None:
    good = tmp_path / "access.log"
    good.write_text("".join(f'1.2.3.4 - - [07/Nov/2026:10:{i:02d}:00 +0000] "GET / HTTP/1.1" 200 5\n' for i in range(30)))
    empty = tmp_path / "empty.log"
    empty.write_text("")
    loose = tmp_path / "loose.log"
    loose.write_text("x\n")
    loose.chmod(0o666)
    link = tmp_path / "link.log"
    link.symlink_to(good)
    paths = [str(good), str(empty), str(loose), str(tmp_path / "absent.log"), str(link)]
    report = collect_log_health(paths, archives=archive_facts(tmp_path, []), logrotate_patterns=[])
    assert _codes(report, str(good)) == set()
    assert "empty" in _codes(report, str(empty))
    assert "world_writable" in _codes(report, str(loose))
    assert _codes(report, str(tmp_path / "absent.log")) == {"missing_library"}
    assert "duplicate" in _codes(report, str(link))
    assert report.archives is not None and report.archives.findings[0].code == "no_archives"
    data = report_to_dict(report)
    assert data["counts"]["problem"] == 1
    assert "OMEGA-LOG" in render_text(data)
    assert "OMEGA-LOG" in export_log_health_html(**html_arguments(data))


def test_naive_timestamps_compare_with_now(tmp_path: Path) -> None:
    """Regression : l'analyseur d'omega-log rend des heures sans fuseau (TypeError a la comparaison)."""
    log = tmp_path / "future.log"
    future = (datetime.now() + timedelta(days=5)).strftime("%d/%b/%Y:%H:%M:%S")
    log.write_text(f'1.2.3.4 - - [{future} +0000] "GET / HTTP/1.1" 200 5\n')
    report = collect_log_health([str(log)], archives=None, logrotate_patterns=[])
    assert "future_dates" in _codes(report, str(log))


@pytest.mark.skipif(os.geteuid() == 0, reason="root lit tout")
def test_unreadable_and_fix_world_writable(tmp_path: Path) -> None:
    secret = tmp_path / "secret.log"
    secret.write_text("x\n")
    secret.chmod(0o000)
    try:
        report = collect_log_health([str(secret)], archives=None, logrotate_patterns=[])
        assert "unreadable" in _codes(report, str(secret))
    finally:
        secret.chmod(0o666)
    fix_world_writable(str(secret))
    assert secret.stat().st_mode & 0o002 == 0


def test_automations_overdue_failing_and_missing_schedule() -> None:
    old = (_NOW - timedelta(days=10)).isoformat()
    automations = [
        {"path": "/a.log", "days_interval": 1, "created_at": old},
        {"path": "/b.log", "days_interval": 1, "created_at": old, "last_success": False, "last_result": "refus"},
    ]
    health = evaluate_automations(automations, False, _NOW)
    codes = [finding.code for finding in health.findings]
    assert codes == ["schedule_missing", "automation_overdue", "automation_failing"]
    assert health.level is HealthLevel.WARNING
    assert "/b.log" in finding_text({"code": "automation_failing", "params": dict(health.findings[2].params)})
