# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Implementation reelle de LiveTailPort — portee verbatim depuis
omega-serv (infrastructure/logging/live_tail_reader.py) : `seek()` +
lecture incrementale, aucune adaptation necessaire (deja generique,
pas specifique aux logs d'omega-serv).

`read_new_lines_privileged` AJOUTE le 2026-10-03 (plan §5.1, logs
proteges de /var/log) : variante privilegiee de `read_new_lines`,
MEME suivi d'offset (toujours recale sur `stat().st_size`, jamais sur
la longueur du texte decode — un caractere de remplacement
errors="replace" ne correspond pas a un octet)."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from omega_log.infrastructure.privileged.privileged_file_ops import read_new_bytes_privileged

if TYPE_CHECKING:
    from omega_log.ports.process_runner_port import ProcessRunnerPort


class LiveTailReader:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._offset = path.stat().st_size if path.exists() else 0

    def read_new_lines(self) -> list[str]:
        if not self._path.exists():
            return []
        size = self._path.stat().st_size
        if size < self._offset:
            self._offset = 0
        if size == self._offset:
            return []
        with self._path.open(encoding="utf-8", errors="replace") as f:
            f.seek(self._offset)
            data = f.read()
            self._offset = f.tell()
        return data.splitlines()

    def read_new_lines_privileged(self, runner: ProcessRunnerPort) -> list[str]:
        if not self._path.exists():
            return []
        size = self._path.stat().st_size
        if size < self._offset:
            self._offset = 0
        if size == self._offset:
            return []
        result = read_new_bytes_privileged(runner, str(self._path), self._offset)
        self._offset = size
        if not result.success:
            raise OSError(result.message)
        return result.content.splitlines()
