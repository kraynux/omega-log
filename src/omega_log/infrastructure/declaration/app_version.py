# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Version d'omega-log envoyee dans une declaration : pyproject.toml (seule source de la version,
livre dans l'archive), repli sur les metadonnees du paquet installe - comme omega-serv."""
from __future__ import annotations

import importlib.metadata
import re
from pathlib import Path

_VERSION_LINE = re.compile(r'^version = "([^"]+)"$', re.MULTILINE)
PROJECT_ROOT = Path(__file__).resolve().parents[4]


def application_version(project_root: Path = PROJECT_ROOT) -> str:
    try:
        match = _VERSION_LINE.search((project_root / "pyproject.toml").read_text(encoding="utf-8"))
    except OSError:
        match = None
    if match:
        return match.group(1)
    try:
        return importlib.metadata.version("omega-log")
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0"
