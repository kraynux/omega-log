# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Use cases Bibliotheque (plan_omega_log.md §3/§10) — hub central
referencant tous les logs a traiter. Alimentee par le Registre (import
au detail/en totalite) ou manuellement, jamais l'inverse (la Bibliotheque
elle-meme ne scanne rien)."""
from __future__ import annotations

from omega_log.application.use_cases.scan_logs import refresh_log_file
from omega_log.domain.entities.favorite import LibraryRecord
from omega_log.domain.entities.log_file import LogFile
from omega_log.ports.log_repository import LogRepository


def list_library(repository: LogRepository) -> list[LogFile]:
    """Liste la Bibliotheque avec l'etat REEL de chaque chemin au moment
    de l'appel (jamais une donnee figee a l'ajout — voir LibraryRecord)."""
    return [
        refresh_log_file(record.path, access=record.access, service_id=record.service_id)
        for record in repository.list_all()
    ]


def add_to_library(repository: LogRepository, log_file: LogFile) -> None:
    repository.add(LibraryRecord(path=log_file.path, access=log_file.access, service_id=log_file.service_id))


def add_many_to_library(repository: LogRepository, log_files: list[LogFile]) -> int:
    for log_file in log_files:
        add_to_library(repository, log_file)
    return len(log_files)


def remove_from_library(repository: LogRepository, path: str) -> None:
    repository.remove(path)
