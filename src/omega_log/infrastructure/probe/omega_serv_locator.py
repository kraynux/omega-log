# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Trouve les installations omega-serv de la machine (2026-11-06) - LECTURE SEULE de fichiers locaux,
lancee uniquement sur clic (« Ajouter les logs connus d'Omega-Serv »), jamais en arriere-plan.

Trois indices, une racine n'etant retenue que si `config/omega-serve.json` y existe :
- l'alias `serv="…/omega-serv.sh"` qu'install.sh d'omega-serv ajoute a ~/.bashrc et ~/.zshrc ;
- le registre des instances supplementaires `~/.config/omega-serv/instances.json` (champ `path`) ;
- `WorkingDirectory=` des unites systemd omega-serv (installation en service, lisibles sans privilege).

Tout fichier illisible ou mal forme est ignore : un indice manquant ne doit jamais empecher les autres."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from omega_log.domain.logs.omega_serv_known_logs import KnownLog, known_logs

CONFIG_RELATIVE = Path("config") / "omega-serve.json"
_ALIAS_RE = re.compile(r"""^\s*alias\s+serv=["']?([^"'\s]+)/omega-serv\.sh["']?\s*$""")
_SHELL_RC_FILES = (".bashrc", ".zshrc")


@dataclass(frozen=True, slots=True)
class OmegaServInstall:
    root: Path
    instance: str | None = None
    """Nom d'instance du registre d'omega-serv, None pour une installation principale."""


@dataclass(frozen=True, slots=True)
class OmegaServScan:
    installs: list[OmegaServInstall]
    logs: list[KnownLog]
    unreadable: list[Path]
    """Racines trouvees dont la configuration n'a pas pu etre lue (droits du service, JSON invalide)."""


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _alias_roots(home: Path) -> list[Path]:
    roots: list[Path] = []
    for name in _SHELL_RC_FILES:
        text = _read_text(home / name)
        for line in (text or "").splitlines():
            match = _ALIAS_RE.match(line)
            if match:
                roots.append(Path(match.group(1)))
    return roots


def _registry_installs(registry: Path) -> list[OmegaServInstall]:
    text = _read_text(registry)
    if not text:
        return []
    try:
        raw = json.loads(text)
    except ValueError:
        return []
    if not isinstance(raw, list):
        return []
    return [
        OmegaServInstall(root=Path(item["path"]), instance=str(item.get("name") or "") or None)
        for item in raw
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    ]


def _systemd_roots(unit_dir: Path) -> list[Path]:
    try:
        units = sorted(unit_dir.glob("*omega-serv*.service"))
    except OSError:
        return []
    roots: list[Path] = []
    for unit in units:
        for line in (_read_text(unit) or "").splitlines():
            stripped = line.strip()
            if stripped.startswith("WorkingDirectory="):
                roots.append(Path(stripped.removeprefix("WorkingDirectory=")))
    return roots


def find_installs(
    *, home: Path | None = None, unit_dir: Path = Path("/etc/systemd/system"),
) -> list[OmegaServInstall]:
    home = home if home is not None else Path.home()
    candidates = (
        [OmegaServInstall(root) for root in _alias_roots(home)]
        + _registry_installs(home / ".config" / "omega-serv" / "instances.json")
        + [OmegaServInstall(root) for root in _systemd_roots(unit_dir)]
    )
    installs: dict[Path, OmegaServInstall] = {}
    for candidate in candidates:
        try:
            root = candidate.root.resolve()
        except OSError:
            continue
        if not (root / CONFIG_RELATIVE).is_file():
            continue
        # Une instance nommee l'emporte sur la meme racine vue par l'alias ou systemd.
        if root not in installs or candidate.instance:
            installs[root] = OmegaServInstall(root, candidate.instance)
    return list(installs.values())


def scan_omega_serv(
    *, home: Path | None = None, unit_dir: Path = Path("/etc/systemd/system"),
) -> OmegaServScan:
    installs = find_installs(home=home, unit_dir=unit_dir)
    logs: list[KnownLog] = []
    unreadable: list[Path] = []
    for install in installs:
        config: Any = None
        text = _read_text(install.root / CONFIG_RELATIVE)
        if text is not None:
            try:
                config = json.loads(text)
            except ValueError:
                config = None
        if not isinstance(config, dict):
            unreadable.append(install.root)
            continue
        logs.extend(known_logs(config, install.root, instance=install.instance))
    return OmegaServScan(installs=installs, logs=logs, unreadable=unreadable)
