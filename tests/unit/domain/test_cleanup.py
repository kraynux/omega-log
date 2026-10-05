# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de domain/logs/cleanup.py."""
from __future__ import annotations

from datetime import datetime

from omega_log.domain.logs.cleanup import FileInfo, RetentionPolicy, plan_cleanup


def test_plan_cleanup_identifies_expired_file() -> None:
    policy = RetentionPolicy(max_age_days=30)
    files = [FileInfo(path="/var/log/old.log", size_bytes=10, mtime=datetime(2020, 1, 1))]
    plan = plan_cleanup(files, policy, now=datetime(2026, 1, 1))
    assert plan.files_to_delete == ["/var/log/old.log"]
    assert not plan.is_empty()


def test_plan_cleanup_keeps_recent_file() -> None:
    policy = RetentionPolicy(max_age_days=30)
    files = [FileInfo(path="/var/log/recent.log", size_bytes=10, mtime=datetime(2026, 1, 1))]
    plan = plan_cleanup(files, policy, now=datetime(2026, 1, 2))
    assert plan.is_empty()
    assert plan.files_to_keep == ["/var/log/recent.log"]


def test_plan_cleanup_enforces_total_size_limit() -> None:
    policy = RetentionPolicy(max_age_days=3650, max_total_size_bytes=100)
    files = [
        FileInfo(path="/a.log", size_bytes=80, mtime=datetime(2026, 1, 1)),
        FileInfo(path="/b.log", size_bytes=80, mtime=datetime(2026, 1, 2)),
    ]
    plan = plan_cleanup(files, policy, now=datetime(2026, 1, 3))
    assert plan.files_to_delete == ["/a.log"]
