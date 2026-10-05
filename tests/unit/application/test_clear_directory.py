# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de application/use_cases/clear_directory.py."""
from __future__ import annotations

from pathlib import Path

from omega_log.application.use_cases.clear_directory import clear_directory


def test_clear_directory_removes_all_files(tmp_path: Path) -> None:
    (tmp_path / "a.json").write_text("x")
    (tmp_path / "b.html").write_text("x")

    result = clear_directory(tmp_path)

    assert result.success
    assert result.deleted_count == 2
    assert list(tmp_path.iterdir()) == []


def test_clear_directory_keeps_subdirectories(tmp_path: Path) -> None:
    (tmp_path / "file.json").write_text("x")
    subdir = tmp_path / "nested"
    subdir.mkdir()
    (subdir / "inner.json").write_text("x")

    result = clear_directory(tmp_path)

    assert result.success
    assert result.deleted_count == 1
    assert subdir.exists()
    assert (subdir / "inner.json").exists()


def test_clear_directory_missing_directory_is_not_an_error(tmp_path: Path) -> None:
    result = clear_directory(tmp_path / "missing")
    assert result.success
    assert result.deleted_count == 0


def test_clear_directory_empty_directory(tmp_path: Path) -> None:
    result = clear_directory(tmp_path)
    assert result.success
    assert result.deleted_count == 0
