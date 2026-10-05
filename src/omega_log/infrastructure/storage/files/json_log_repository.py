# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation JSON du port LogRepository — meme convention que le
reste de la suite (JSON pour la configuration legere, pas SQLite ; voir
plan_omega_log.md §5)."""
from __future__ import annotations

import json
from pathlib import Path

from omega_log.domain.entities.favorite import LibraryRecord


class JsonLogRepository:
    """Implemente LogRepository. Deduplique par `path` (un meme chemin
    ne peut etre reference qu'une fois)."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def list_all(self) -> list[LibraryRecord]:
        if not self._path.exists():
            return []
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        return [LibraryRecord(**entry) for entry in raw]

    def add(self, record: LibraryRecord) -> None:
        records = {r.path: r for r in self.list_all()}
        records[record.path] = record
        self._write(list(records.values()))

    def remove(self, path: str) -> None:
        records = [r for r in self.list_all() if r.path != path]
        self._write(records)

    def contains(self, path: str) -> bool:
        return any(r.path == path for r in self.list_all())

    def _write(self, records: list[LibraryRecord]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {"path": r.path, "access": r.access, "service_id": r.service_id}
            for r in records
        ]
        self._path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
