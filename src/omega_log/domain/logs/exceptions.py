# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Logs domain exceptions.

Pure domain exceptions for the logs subdomain. Porte verbatim depuis
omega-fire (domain/logs/exceptions.py)."""
from omega_log.shared.i18n import _


class LogsError(Exception):
    """Base exception for logs domain."""


class LogNotFoundError(LogsError):
    """Raised when attempting to analyze a log file that does not exist."""
    def __init__(self, log_path: str):
        self.log_path = log_path
        super().__init__(_("Fichier de log introuvable : {log_path}").format(log_path=log_path))


class LogParseError(LogsError):
    """Raised when a log line cannot be parsed according to expected format."""
    def __init__(self, log_path: str, line_number: int, reason: str):
        self.log_path = log_path
        self.line_number = line_number
        self.reason = reason
        super().__init__(_("Erreur d'analyse dans {log_path}, ligne {line_number} : {reason}").format(log_path=log_path, line_number=line_number, reason=reason))


class InvalidLogFormatError(LogsError):
    """Raised when the overall log format is invalid or unsupported."""
    def __init__(self, log_path: str, reason: str):
        self.log_path = log_path
        self.reason = reason
        super().__init__(_("Format de log invalide pour {log_path} : {reason}").format(log_path=log_path, reason=reason))


class LogAnalysisError(LogsError):
    """Raised when a log analysis operation fails."""
    def __init__(self, analysis_type: str, reason: str):
        self.analysis_type = analysis_type
        self.reason = reason
        super().__init__(_("Erreur d'analyse ({analysis_type}) : {reason}").format(analysis_type=analysis_type, reason=reason))


class LogRotationError(LogsError):
    """Raised when log rotation fails."""
    def __init__(self, log_path: str, reason: str):
        self.log_path = log_path
        self.reason = reason
        super().__init__(_("Erreur de rotation pour {log_path} : {reason}").format(log_path=log_path, reason=reason))


class LogCleanupError(LogsError):
    """Raised when log cleanup or purge fails."""
    def __init__(self, log_path: str, reason: str):
        self.log_path = log_path
        self.reason = reason
        super().__init__(_("Erreur de nettoyage pour {log_path} : {reason}").format(log_path=log_path, reason=reason))


class BackupNotFoundError(LogsError):
    """Raised when attempting to restore a backup that does not exist."""
    def __init__(self, backup_path: str):
        self.backup_path = backup_path
        super().__init__(_("Archive introuvable : {backup_path}").format(backup_path=backup_path))


class InvalidRetentionError(LogsError):
    """Raised when retention parameters are invalid."""
    def __init__(self, parameter: str, value: object, reason: str) -> None:
        self.parameter = parameter
        self.value = value
        self.reason = reason
        super().__init__(f"Invalid retention parameter '{parameter}' (value={value}): {reason}")
