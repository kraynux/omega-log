# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Import des logs connus d'omega-serv dans la Bibliotheque (2026-11-06), sur clic seulement. Un chemin
deja reference est remplace, jamais duplique (JsonLogRepository deduplique par chemin). La recherche des
installations est faite par infrastructure/probe/omega_serv_locator.py."""
from __future__ import annotations

from omega_log.application.use_cases.library import add_to_library
from omega_log.domain.entities.log_file import LogFile
from omega_log.domain.logs.omega_serv_known_logs import KnownLog
from omega_log.ports.log_repository import LogRepository


def import_omega_serv_logs(repository: LogRepository, logs: list[KnownLog]) -> int:
    for log in logs:
        add_to_library(repository, LogFile(path=log.path, access="file", service_id=log.service_id))
    return len(logs)
