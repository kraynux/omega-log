# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation JSON du port FavoriteRepository."""
from __future__ import annotations

import json
from pathlib import Path

from omega_log.domain.entities.favorite import Favorite
from omega_log.domain.value_objects.viewer_type import ViewerType


class JsonFavoriteRepository:
    """Implemente FavoriteRepository. Deduplique par `name` (un nom
    existant est remplace, pas duplique)."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def list_all(self) -> list[Favorite]:
        if not self._path.exists():
            return []
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        return [
            Favorite(name=entry["name"], paths=tuple(entry["paths"]), viewer=ViewerType(entry["viewer"]))
            for entry in raw
        ]

    def add(self, favorite: Favorite) -> None:
        favorites = {f.name: f for f in self.list_all()}
        favorites[favorite.name] = favorite
        self._write(list(favorites.values()))

    def remove(self, name: str) -> None:
        favorites = [f for f in self.list_all() if f.name != name]
        self._write(favorites)

    def _write(self, favorites: list[Favorite]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {"name": f.name, "paths": list(f.paths), "viewer": f.viewer.value}
            for f in favorites
        ]
        self._path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
