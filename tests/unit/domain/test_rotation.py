# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de domain/logs/rotation.py."""
from __future__ import annotations

from datetime import datetime

from omega_log.domain.logs.rotation import (
    CompressionFormat,
    RotationPolicy,
    RotationStrategy,
    compute_rotations_to_delete,
    generate_archive_name,
    plan_rotation,
    should_rotate_by_size,
)


def test_rotation_policy_validates_by_size_requires_max_size() -> None:
    policy = RotationPolicy(strategy=RotationStrategy.BY_SIZE)
    assert "max_size_bytes" in "; ".join(policy.validate())


def test_should_rotate_by_size() -> None:
    should, reason = should_rotate_by_size(file_size_bytes=200, max_size_bytes=100)
    assert should
    assert reason is not None


def test_generate_archive_name_includes_gzip_extension() -> None:
    name = generate_archive_name(
        "/var/log/access.log", rotation_number=1, timestamp=datetime(2026, 10, 3, 12, 0, 0),
        compression=CompressionFormat.GZIP,
    )
    assert name.endswith(".gz")
    assert name.startswith("access.log.")


def test_compute_rotations_to_delete_keeps_most_recent() -> None:
    existing = ["a.1", "a.2", "a.3", "a.4"]
    to_delete = compute_rotations_to_delete(existing, max_rotations=2)
    assert to_delete == ["a.1", "a.2"]


def test_compute_rotations_to_delete_noop_under_limit() -> None:
    assert compute_rotations_to_delete(["a.1"], max_rotations=5) == []


def test_plan_rotation_triggers_on_size_threshold() -> None:
    policy = RotationPolicy(strategy=RotationStrategy.BY_SIZE, max_size_bytes=100)
    plan = plan_rotation("/var/log/access.log", policy, file_size_bytes=200)
    assert plan.should_rotate
    assert plan.archive_name is not None


def test_plan_rotation_noop_below_threshold() -> None:
    policy = RotationPolicy(strategy=RotationStrategy.BY_SIZE, max_size_bytes=1000)
    plan = plan_rotation("/var/log/access.log", policy, file_size_bytes=10)
    assert not plan.should_rotate
    assert plan.is_empty()
