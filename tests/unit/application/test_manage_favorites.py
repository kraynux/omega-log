# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de application/use_cases/manage_favorites.py — regle de
compatibilite viewer/nombre de logs du plan_omega_log.md §5."""
from __future__ import annotations

from pathlib import Path

from omega_log.application.use_cases.manage_favorites import (
    create_favorite,
    list_favorites,
    remove_favorite,
)
from omega_log.domain.value_objects.viewer_type import ViewerType
from omega_log.infrastructure.storage.files.json_favorite_repository import JsonFavoriteRepository


def test_create_favorite_single_log_with_simple_viewer(tmp_path: Path) -> None:
    repo = JsonFavoriteRepository(tmp_path / "favorites.json")
    result = create_favorite(repo, name="test", paths=["/var/log/a.log"], viewer=ViewerType.SIMPLE)
    assert result.success
    assert len(list_favorites(repo)) == 1


def test_create_favorite_multiple_logs_rejects_simple_viewer(tmp_path: Path) -> None:
    repo = JsonFavoriteRepository(tmp_path / "favorites.json")
    result = create_favorite(repo, name="bad", paths=["/a.log", "/b.log"], viewer=ViewerType.SIMPLE)
    assert not result.success
    assert list_favorites(repo) == []


def test_create_favorite_multiple_logs_accepts_lnav(tmp_path: Path) -> None:
    repo = JsonFavoriteRepository(tmp_path / "favorites.json")
    result = create_favorite(repo, name="multi", paths=["/a.log", "/b.log"], viewer=ViewerType.LNAV)
    assert result.success


def test_create_favorite_requires_name(tmp_path: Path) -> None:
    repo = JsonFavoriteRepository(tmp_path / "favorites.json")
    result = create_favorite(repo, name="  ", paths=["/a.log"], viewer=ViewerType.SIMPLE)
    assert not result.success


def test_create_favorite_requires_at_least_one_path(tmp_path: Path) -> None:
    repo = JsonFavoriteRepository(tmp_path / "favorites.json")
    result = create_favorite(repo, name="empty", paths=[], viewer=ViewerType.SIMPLE)
    assert not result.success


def test_remove_favorite(tmp_path: Path) -> None:
    repo = JsonFavoriteRepository(tmp_path / "favorites.json")
    create_favorite(repo, name="test", paths=["/a.log"], viewer=ViewerType.SIMPLE)
    remove_favorite(repo, "test")
    assert list_favorites(repo) == []


def test_create_favorite_overwrites_existing_name(tmp_path: Path) -> None:
    repo = JsonFavoriteRepository(tmp_path / "favorites.json")
    create_favorite(repo, name="test", paths=["/a.log"], viewer=ViewerType.SIMPLE)
    create_favorite(repo, name="test", paths=["/b.log"], viewer=ViewerType.CLASSIC)
    favorites = list_favorites(repo)
    assert len(favorites) == 1
    assert favorites[0].paths == ("/b.log",)
