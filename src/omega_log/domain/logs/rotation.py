# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Logs domain rotation logic.

Pure domain logic for log rotation rules. This module defines WHEN and
HOW to rotate logs, but does NOT perform the actual file operations.
Execution is delegated to infrastructure/. Porte verbatim depuis
omega-fire (domain/logs/rotation.py)."""
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class RotationStrategy(Enum):
    """Strategy for log rotation."""
    BY_SIZE = "by_size"
    BY_AGE = "by_age"
    BY_COUNT = "by_count"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class CompressionFormat(Enum):
    """Compression format for rotated logs."""
    NONE = "none"
    GZIP = "gzip"
    BZIP2 = "bzip2"
    XZ = "xz"


@dataclass
class RotationPolicy:
    """Policy defining when and how to rotate logs."""
    strategy: RotationStrategy
    max_size_bytes: int | None = None
    max_age_days: int | None = None
    max_lines: int | None = None
    max_rotations: int = 10
    compression: CompressionFormat = CompressionFormat.GZIP
    rotate_on_empty: bool = False

    def validate(self) -> list[str]:
        errors = []

        if self.strategy == RotationStrategy.BY_SIZE and (self.max_size_bytes is None or self.max_size_bytes <= 0):
            errors.append("max_size_bytes must be > 0 for BY_SIZE strategy")
        elif self.strategy == RotationStrategy.BY_AGE and (self.max_age_days is None or self.max_age_days <= 0):
            errors.append("max_age_days must be > 0 for BY_AGE strategy")
        elif self.strategy == RotationStrategy.BY_COUNT and (self.max_lines is None or self.max_lines <= 0):
            errors.append("max_lines must be > 0 for BY_COUNT strategy")

        if self.max_rotations < 1:
            errors.append("max_rotations must be >= 1")

        return errors

    def is_valid(self) -> bool:
        return len(self.validate()) == 0


@dataclass
class RotationPlan:
    """Plan of rotation operations."""
    log_path: str
    should_rotate: bool
    reason: str | None = None
    archive_name: str | None = None
    compress: bool = False
    compression_format: CompressionFormat = CompressionFormat.NONE
    rotations_to_delete: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def is_empty(self) -> bool:
        return not self.should_rotate


def should_rotate_by_size(file_size_bytes: int, max_size_bytes: int) -> tuple[bool, str | None]:
    if file_size_bytes >= max_size_bytes:
        return True, f"File size ({file_size_bytes} bytes) exceeds threshold ({max_size_bytes} bytes)"
    return False, None


def should_rotate_by_age(
    file_mtime: datetime, max_age_days: int, now: datetime | None = None
) -> tuple[bool, str | None]:
    if now is None:
        now = datetime.now()

    age = now - file_mtime
    max_age = timedelta(days=max_age_days)

    if age >= max_age:
        return True, f"File age ({age.days} days) exceeds threshold ({max_age_days} days)"
    return False, None


def should_rotate_by_count(line_count: int, max_lines: int) -> tuple[bool, str | None]:
    if line_count >= max_lines:
        return True, f"Line count ({line_count}) exceeds threshold ({max_lines})"
    return False, None


def should_rotate_by_schedule(
    last_rotation: datetime, strategy: RotationStrategy, now: datetime | None = None
) -> tuple[bool, str | None]:
    if now is None:
        now = datetime.now()

    if strategy == RotationStrategy.DAILY and now.date() > last_rotation.date():
        return True, "Daily rotation: new day started"
    if strategy == RotationStrategy.WEEKLY and now.isocalendar()[1] != last_rotation.isocalendar()[1]:
        return True, "Weekly rotation: new week started"
    if strategy == RotationStrategy.MONTHLY and (
        now.month != last_rotation.month or now.year != last_rotation.year
    ):
        return True, "Monthly rotation: new month started"

    return False, None


def generate_archive_name(
    log_path: str,
    rotation_number: int,
    timestamp: datetime,
    compression: CompressionFormat = CompressionFormat.NONE,
) -> str:
    base_name = os.path.basename(log_path)
    timestamp_str = timestamp.strftime("%Y%m%d-%H%M%S")
    archive_name = f"{base_name}.{timestamp_str}.{rotation_number}"

    if compression == CompressionFormat.GZIP:
        archive_name += ".gz"
    elif compression == CompressionFormat.BZIP2:
        archive_name += ".bz2"
    elif compression == CompressionFormat.XZ:
        archive_name += ".xz"

    return archive_name


def compute_rotations_to_delete(existing_rotations: list[str], max_rotations: int) -> list[str]:
    if len(existing_rotations) <= max_rotations:
        return []
    return existing_rotations[:len(existing_rotations) - max_rotations]


def plan_rotation(
    log_path: str,
    policy: RotationPolicy,
    file_size_bytes: int | None = None,
    file_mtime: datetime | None = None,
    line_count: int | None = None,
    last_rotation: datetime | None = None,
    existing_rotations: list[str] | None = None,
    rotation_number: int = 1,
    now: datetime | None = None,
) -> RotationPlan:
    """Plan a log rotation operation (determines need, does NOT execute)."""
    if now is None:
        now = datetime.now()

    if existing_rotations is None:
        existing_rotations = []

    should_rotate = False
    reason = None

    if policy.strategy == RotationStrategy.BY_SIZE and (
        file_size_bytes is not None and policy.max_size_bytes is not None
    ):
        should_rotate, reason = should_rotate_by_size(file_size_bytes, policy.max_size_bytes)
    elif policy.strategy == RotationStrategy.BY_AGE and (
        file_mtime is not None and policy.max_age_days is not None
    ):
        should_rotate, reason = should_rotate_by_age(file_mtime, policy.max_age_days, now)
    elif policy.strategy == RotationStrategy.BY_COUNT and (
        line_count is not None and policy.max_lines is not None
    ):
        should_rotate, reason = should_rotate_by_count(line_count, policy.max_lines)
    elif (
        policy.strategy in (RotationStrategy.DAILY, RotationStrategy.WEEKLY, RotationStrategy.MONTHLY)
        and last_rotation is not None
    ):
        should_rotate, reason = should_rotate_by_schedule(last_rotation, policy.strategy, now)

    if not should_rotate:
        return RotationPlan(log_path=log_path, should_rotate=False)

    archive_name = generate_archive_name(
        log_path=log_path, rotation_number=rotation_number, timestamp=now, compression=policy.compression,
    )
    rotations_to_delete = compute_rotations_to_delete(
        existing_rotations=existing_rotations, max_rotations=policy.max_rotations,
    )

    return RotationPlan(
        log_path=log_path,
        should_rotate=True,
        reason=reason,
        archive_name=archive_name,
        compress=(policy.compression != CompressionFormat.NONE),
        compression_format=policy.compression,
        rotations_to_delete=rotations_to_delete,
        created_at=now,
    )
