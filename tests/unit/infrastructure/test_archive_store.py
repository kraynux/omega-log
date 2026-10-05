# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de infrastructure/storage/files/archive_store.py (I/O reelle
sur `tmp_path`, pas de mock — c'est exactement le genre de module qui
merite un vrai tar.gz, pas une simulation)."""
from __future__ import annotations

from pathlib import Path

from omega_log.infrastructure.storage.files.archive_store import ArchiveStore


def test_create_and_extract_archive_roundtrip(tmp_path: Path) -> None:
    source = tmp_path / "access.log"
    source.write_text("ligne 1\nligne 2\n")

    store = ArchiveStore(tmp_path / "backups")
    archive_path = store.create_archive("backup_access", [source])
    assert archive_path.exists()
    assert archive_path.suffix == ".gz"

    dest = tmp_path / "restored"
    store.extract_archive(archive_path, dest)
    assert (dest / "access.log").read_text() == "ligne 1\nligne 2\n"


def test_list_archives(tmp_path: Path) -> None:
    source = tmp_path / "a.log"
    source.write_text("x")
    store = ArchiveStore(tmp_path / "backups")
    store.create_archive("one", [source])
    store.create_archive("two", [source])
    assert len(store.list_archives()) == 2


def test_delete_archive(tmp_path: Path) -> None:
    source = tmp_path / "a.log"
    source.write_text("x")
    store = ArchiveStore(tmp_path / "backups")
    archive_path = store.create_archive("one", [source])
    assert store.delete_archive(archive_path) is True
    assert not archive_path.exists()
    assert store.delete_archive(archive_path) is False


def test_get_archive_info(tmp_path: Path) -> None:
    source = tmp_path / "a.log"
    source.write_text("x")
    store = ArchiveStore(tmp_path / "backups")
    archive_path = store.create_archive("one", [source])
    info = store.get_archive_info(archive_path)
    assert info["name"] == archive_path.name
    assert info["size_bytes"] > 0
