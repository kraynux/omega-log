# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Logs domain exceptions.

Pure domain exceptions for the logs subdomain. Porte verbatim depuis
omega-fire (domain/logs/exceptions.py)."""


class LogsError(Exception):
    """Base exception for logs domain."""


class LogNotFoundError(LogsError):
    """Raised when attempting to analyze a log file that does not exist."""
    def __init__(self, log_path: str):
        self.log_path = log_path
        super().__init__(f"Log file not found: {log_path}")


class LogParseError(LogsError):
    """Raised when a log line cannot be parsed according to expected format."""
    def __init__(self, log_path: str, line_number: int, reason: str):
        self.log_path = log_path
        self.line_number = line_number
        self.reason = reason
        super().__init__(f"Parse error in {log_path} at line {line_number}: {reason}")


class InvalidLogFormatError(LogsError):
    """Raised when the overall log format is invalid or unsupported."""
    def __init__(self, log_path: str, reason: str):
        self.log_path = log_path
        self.reason = reason
        super().__init__(f"Invalid log format for {log_path}: {reason}")


class LogAnalysisError(LogsError):
    """Raised when a log analysis operation fails."""
    def __init__(self, analysis_type: str, reason: str):
        self.analysis_type = analysis_type
        self.reason = reason
        super().__init__(f"Log analysis error ({analysis_type}): {reason}")


class LogRotationError(LogsError):
    """Raised when log rotation fails."""
    def __init__(self, log_path: str, reason: str):
        self.log_path = log_path
        self.reason = reason
        super().__init__(f"Log rotation error for {log_path}: {reason}")


class LogCleanupError(LogsError):
    """Raised when log cleanup or purge fails."""
    def __init__(self, log_path: str, reason: str):
        self.log_path = log_path
        self.reason = reason
        super().__init__(f"Log cleanup error for {log_path}: {reason}")


class BackupNotFoundError(LogsError):
    """Raised when attempting to restore a backup that does not exist."""
    def __init__(self, backup_path: str):
        self.backup_path = backup_path
        super().__init__(f"Backup not found: {backup_path}")


class InvalidRetentionError(LogsError):
    """Raised when retention parameters are invalid."""
    def __init__(self, parameter: str, value, reason: str):
        self.parameter = parameter
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid retention parameter '{parameter}' (value={value}): {reason}")
