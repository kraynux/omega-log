# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Sauvegardes planifiees des logs (porte d'omega-serv 2.6.0, 2026-11-07) : une entree par log de la
Bibliotheque (`path`, `days_interval`, `created_at`), plus le resultat de la derniere execution
(`last_run_at`, `last_result`, `last_success`) note par `omega-log rotate run-automations`."""
from __future__ import annotations

import json
from pathlib import Path


class RotationAutomationStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    def list_all(self) -> list[dict[str, object]]:
        if not self._path.exists():
            return []
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return data if isinstance(data, list) else []

    def add(self, automation: dict[str, object]) -> None:
        automations = self.list_all()
        automations.append(automation)
        self._save(automations)

    def delete(self, index: int) -> bool:
        automations = self.list_all()
        if not (0 <= index < len(automations)):
            return False
        automations.pop(index)
        self._save(automations)
        return True

    def save_all(self, automations: list[dict[str, object]]) -> None:
        self._save(automations)

    def _save(self, automations: list[dict[str, object]]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(automations, indent=2, ensure_ascii=False), encoding="utf-8")
