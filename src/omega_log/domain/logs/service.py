# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Logs domain service.

Orchestrates business operations on logs. This service coordinates the
domain modules (parser, analytics, rotation, cleanup) and enforces
business rules by raising domain exceptions. Porte verbatim depuis
omega-fire (domain/logs/service.py)."""
from datetime import datetime

from omega_log.domain.logs.analytics import (
    compute_stats,
    compute_top_ips,
    filter_entries_by_ip,
    filter_entries_by_level,
    filter_entries_by_source,
    filter_entries_by_time_range,
    filter_error_entries,
)
from omega_log.domain.logs.cleanup import (
    CleanupPlan,
    FileInfo,
    RetentionPolicy,
    plan_cleanup,
    validate_retention_parameters,
)
from omega_log.domain.logs.exceptions import (
    InvalidRetentionError,
    LogAnalysisError,
    LogCleanupError,
    LogParseError,
    LogRotationError,
)
from omega_log.domain.logs.models import LogAnalysis, LogEntry, LogLevel, LogSource, LogStats, TopIP
from omega_log.domain.logs.parser import parse_log_lines
from omega_log.domain.logs.rotation import RotationPlan, RotationPolicy, plan_rotation


class LogsService:
    """Domain service for log operations."""

    def parse_lines(
        self,
        lines: list[str],
        log_path: str | None = None,
        source: LogSource | None = None,
    ) -> list[LogEntry]:
        """Parse raw log lines into structured LogEntry objects."""
        try:
            return parse_log_lines(lines, log_path=log_path, source=source)
        except Exception as e:
            raise LogParseError(log_path or "unknown", 0, f"Parsing failed: {e}") from e

    def analyze_entries(
        self,
        entries: list[LogEntry],
        total_lines: int = 0,
        log_path: str | None = None,
        top_n: int = 10,
    ) -> LogStats:
        """Analyze log entries and compute statistics."""
        try:
            return compute_stats(entries=entries, total_lines=total_lines, log_path=log_path, top_n=top_n)
        except Exception as e:
            raise LogAnalysisError("stats_computation", f"Analysis failed: {e}") from e

    def get_top_ips(self, entries: list[LogEntry], n: int = 10, min_count: int = 1) -> list[TopIP]:
        """Get the Top N IP addresses by occurrence count."""
        return compute_top_ips(entries, n=n, min_count=min_count)

    def filter_entries(
        self,
        entries: list[LogEntry],
        ip: str | None = None,
        level: LogLevel | None = None,
        source: LogSource | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        errors_only: bool = False,
    ) -> list[LogEntry]:
        """Filter log entries by various criteria."""
        filtered = entries

        if ip:
            filtered = filter_entries_by_ip(filtered, ip)
        if level:
            filtered = filter_entries_by_level(filtered, level)
        if source:
            filtered = filter_entries_by_source(filtered, source)
        if start_time or end_time:
            filtered = filter_entries_by_time_range(filtered, start_time, end_time)
        if errors_only:
            filtered = filter_error_entries(filtered)

        return filtered

    def plan_rotation(
        self,
        log_path: str,
        policy: RotationPolicy,
        file_size_bytes: int | None = None,
        file_mtime: datetime | None = None,
        line_count: int | None = None,
        last_rotation: datetime | None = None,
        existing_rotations: list[str] | None = None,
        rotation_number: int = 1,
    ) -> RotationPlan:
        """Plan a log rotation operation."""
        errors = policy.validate()
        if errors:
            raise LogRotationError(log_path, f"Invalid rotation policy: {'; '.join(errors)}")

        try:
            return plan_rotation(
                log_path=log_path,
                policy=policy,
                file_size_bytes=file_size_bytes,
                file_mtime=file_mtime,
                line_count=line_count,
                last_rotation=last_rotation,
                existing_rotations=existing_rotations,
                rotation_number=rotation_number,
            )
        except Exception as e:
            raise LogRotationError(log_path, f"Rotation planning failed: {e}") from e

    def plan_cleanup(
        self, files: list[FileInfo], policy: RetentionPolicy, now: datetime | None = None
    ) -> CleanupPlan:
        """Plan a cleanup operation based on retention policy."""
        errors = policy.validate()
        if errors:
            raise InvalidRetentionError(
                "retention_policy", policy, f"Invalid retention policy: {'; '.join(errors)}"
            )

        try:
            return plan_cleanup(files=files, policy=policy, now=now)
        except Exception as e:
            raise LogCleanupError("multiple files", f"Cleanup planning failed: {e}") from e

    def validate_retention_parameters(
        self,
        max_age_days: int | None = None,
        max_archive_age_days: int | None = None,
        max_total_size_bytes: int | None = None,
    ) -> list[str]:
        """Validate retention parameters."""
        return validate_retention_parameters(
            max_age_days=max_age_days,
            max_archive_age_days=max_archive_age_days,
            max_total_size_bytes=max_total_size_bytes,
        )

    def create_full_analysis(
        self,
        entries: list[LogEntry],
        total_lines: int = 0,
        log_path: str | None = None,
        top_n: int = 10,
    ) -> LogAnalysis:
        """Create a complete log analysis with entries and statistics."""
        stats = self.analyze_entries(entries=entries, total_lines=total_lines, log_path=log_path, top_n=top_n)

        return LogAnalysis(entries=entries, stats=stats, top_ips=stats.top_ips)
