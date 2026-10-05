# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de application/use_cases/library.py."""
from __future__ import annotations

from pathlib import Path

from omega_log.application.use_cases.library import (
    add_many_to_library,
    add_to_library,
    list_library,
    remove_from_library,
)
from omega_log.domain.entities.log_file import LogFile
from omega_log.infrastructure.storage.files.json_log_repository import JsonLogRepository


def test_add_and_list_library(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text("content")
    repo = JsonLogRepository(tmp_path / "library.json")

    add_to_library(repo, LogFile(path=str(log_path), access="file", service_id="nginx"))
    entries = list_library(repo)

    assert len(entries) == 1
    assert entries[0].path == str(log_path)
    assert entries[0].exists is True
    assert entries[0].service_id == "nginx"


def test_list_library_reflects_current_disk_state_not_stale_snapshot(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text("content")
    repo = JsonLogRepository(tmp_path / "library.json")
    add_to_library(repo, LogFile(path=str(log_path), access="file"))

    log_path.unlink()
    entries = list_library(repo)
    assert entries[0].exists is False


def test_add_many_to_library_deduplicates_by_path(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text("content")
    repo = JsonLogRepository(tmp_path / "library.json")

    log_file = LogFile(path=str(log_path), access="file")
    add_many_to_library(repo, [log_file, log_file])
    assert len(list_library(repo)) == 1


def test_remove_from_library(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text("content")
    repo = JsonLogRepository(tmp_path / "library.json")
    add_to_library(repo, LogFile(path=str(log_path), access="file"))

    remove_from_library(repo, str(log_path))
    assert list_library(repo) == []
