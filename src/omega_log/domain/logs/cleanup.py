# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Logs domain cleanup logic.

Pure domain logic for log and archive cleanup rules. This module defines
WHAT to purge based on retention policies, but does NOT perform the
actual file deletions. Execution is delegated to infrastructure/. Porte
verbatim depuis omega-fire (domain/logs/cleanup.py)."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class RetentionUnit(Enum):
    """Unit for retention period."""
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"


@dataclass
class RetentionPolicy:
    """Policy defining how long to keep logs and archives."""
    max_age_days: int = 30
    max_archive_age_days: int = 90
    max_total_size_bytes: int | None = None
    min_free_space_bytes: int | None = None

    def validate(self) -> list[str]:
        errors = []

        if self.max_age_days < 1:
            errors.append("max_age_days must be >= 1")
        if self.max_archive_age_days < 1:
            errors.append("max_archive_age_days must be >= 1")
        if self.max_total_size_bytes is not None and self.max_total_size_bytes <= 0:
            errors.append("max_total_size_bytes must be > 0 if set")
        if self.min_free_space_bytes is not None and self.min_free_space_bytes <= 0:
            errors.append("min_free_space_bytes must be > 0 if set")

        return errors

    def is_valid(self) -> bool:
        return len(self.validate()) == 0

    def to_days(self, value: int, unit: RetentionUnit) -> int:
        if unit == RetentionUnit.DAYS:
            return value
        if unit == RetentionUnit.WEEKS:
            return value * 7
        if unit == RetentionUnit.MONTHS:
            return value * 30
        return value


@dataclass
class FileInfo:
    """Metadata about a log or archive file."""
    path: str
    size_bytes: int
    mtime: datetime
    is_archive: bool = False

    def age_days(self, now: datetime | None = None) -> float:
        if now is None:
            now = datetime.now()
        delta = now - self.mtime
        return delta.total_seconds() / 86400.0

    def is_expired(self, max_age_days: int, now: datetime | None = None) -> bool:
        return self.age_days(now) >= max_age_days


@dataclass
class CleanupPlan:
    """Plan of cleanup operations."""
    files_to_delete: list[str] = field(default_factory=list)
    total_size_to_free_bytes: int = 0
    files_to_keep: list[str] = field(default_factory=list)
    reasons: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def count(self) -> int:
        return len(self.files_to_delete)

    def is_empty(self) -> bool:
        return len(self.files_to_delete) == 0

    def size_to_free_mb(self) -> float:
        return self.total_size_to_free_bytes / (1024 * 1024)


def identify_expired_files(
    files: list[FileInfo], max_age_days: int, now: datetime | None = None
) -> list[FileInfo]:
    return [f for f in files if f.is_expired(max_age_days, now)]


def identify_expired_archives(
    files: list[FileInfo], max_archive_age_days: int, now: datetime | None = None
) -> list[FileInfo]:
    archives = [f for f in files if f.is_archive]
    return [f for f in archives if f.is_expired(max_archive_age_days, now)]


def identify_oversized_files(
    files: list[FileInfo], max_total_size_bytes: int, now: datetime | None = None
) -> list[FileInfo]:
    """Identify files to delete (oldest first) to stay under the total size limit."""
    total_size = sum(f.size_bytes for f in files)

    if total_size <= max_total_size_bytes:
        return []

    sorted_files = sorted(files, key=lambda f: f.mtime)

    to_delete = []
    current_size = total_size

    for file in sorted_files:
        if current_size <= max_total_size_bytes:
            break
        to_delete.append(file)
        current_size -= file.size_bytes

    return to_delete


def compute_total_size(files: list[FileInfo]) -> int:
    return sum(f.size_bytes for f in files)


def plan_cleanup(
    files: list[FileInfo], policy: RetentionPolicy, now: datetime | None = None
) -> CleanupPlan:
    """Plan a cleanup operation (determines what to delete, does NOT delete)."""
    if now is None:
        now = datetime.now()

    files_to_delete: list[FileInfo] = []
    reasons: dict[str, str] = {}

    expired_logs = identify_expired_files([f for f in files if not f.is_archive], policy.max_age_days, now)
    for f in expired_logs:
        if f.path not in reasons:
            files_to_delete.append(f)
            reasons[f.path] = f"Expired (age: {f.age_days(now):.1f} days, max: {policy.max_age_days} days)"

    expired_archives = identify_expired_archives(files, policy.max_archive_age_days, now)
    for f in expired_archives:
        if f.path not in reasons:
            files_to_delete.append(f)
            reasons[f.path] = (
                f"Archive expired (age: {f.age_days(now):.1f} days, "
                f"max: {policy.max_archive_age_days} days)"
            )

    if policy.max_total_size_bytes is not None:
        remaining_files = [f for f in files if f not in files_to_delete]
        oversized = identify_oversized_files(remaining_files, policy.max_total_size_bytes, now)
        for f in oversized:
            if f.path not in reasons:
                files_to_delete.append(f)
                reasons[f.path] = "Total size limit exceeded (oldest files removed first)"

    total_size_to_free = sum(f.size_bytes for f in files_to_delete)
    files_to_keep = [f.path for f in files if f not in files_to_delete]

    return CleanupPlan(
        files_to_delete=[f.path for f in files_to_delete],
        total_size_to_free_bytes=total_size_to_free,
        files_to_keep=files_to_keep,
        reasons=reasons,
        created_at=now,
    )


def validate_retention_parameters(
    max_age_days: int | None = None,
    max_archive_age_days: int | None = None,
    max_total_size_bytes: int | None = None,
) -> list[str]:
    errors = []

    if max_age_days is not None and max_age_days < 1:
        errors.append(f"max_age_days must be >= 1 (got {max_age_days})")
    if max_archive_age_days is not None and max_archive_age_days < 1:
        errors.append(f"max_archive_age_days must be >= 1 (got {max_archive_age_days})")
    if max_total_size_bytes is not None and max_total_size_bytes <= 0:
        errors.append(f"max_total_size_bytes must be > 0 (got {max_total_size_bytes})")
    if (
        max_age_days is not None
        and max_archive_age_days is not None
        and max_archive_age_days < max_age_days
    ):
        errors.append(
            f"max_archive_age_days ({max_archive_age_days}) should be >= max_age_days ({max_age_days})"
        )

    return errors
