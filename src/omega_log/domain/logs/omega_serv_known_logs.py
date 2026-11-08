# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Logs connus d'une installation omega-serv (2026-11-06) - meme liste que le bouton « Ajouter les logs
connus d'Omega-Serv » d'omega-serv (interfaces/tui/screens/log_library_screen.py) : access, error, puis
alertes WAF si le WAF est actif, puis les 2 logs magnet si le magnet l'est aussi.

Pur domaine : recoit la configuration deja lue (dict JSON), ne lit jamais le disque. Les chemins
relatifs de la configuration sont resolus depuis la racine de l'installation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

SERVICE_ID = "omega-serv"
MAGNET_SERVICE_ID = "omega-serv-magnet"
_BASE_LOG_KEYS = ("access", "error")
_MAGNET_DEFAULT_LOGS = {
    "alerts_log": "var/log/waf-magnet-alerts.log",
    "blocklist_log": "var/log/waf-magnet-blocklist.log",
}
"""Defauts d'omega-serv (domain/security/waf/config.py::MagnetPathsConfig) quand la configuration ne
les surcharge pas."""


@dataclass(frozen=True, slots=True)
class KnownLog:
    path: str
    service_id: str


def _resolve(root: Path, relative: str) -> str:
    candidate = Path(relative)
    return str(candidate if candidate.is_absolute() else root / candidate)


def _tagged(service_id: str, instance: str | None) -> str:
    return f"{service_id}:{instance}" if instance else service_id


def known_logs(config: dict[str, Any], root: Path, *, instance: str | None = None) -> list[KnownLog]:
    """`instance` : nom d'une instance supplementaire (registre d'omega-serv), None pour l'installation
    principale - il etiquette la colonne Service (`omega-serv:<nom>`)."""
    logs = config.get("logs") or {}
    found: list[KnownLog] = []
    for key in _BASE_LOG_KEYS:
        if isinstance(logs.get(key), str):
            found.append(KnownLog(_resolve(root, logs[key]), _tagged(SERVICE_ID, instance)))

    waf = (config.get("options") or {}).get("waf") or {}
    if not waf.get("enabled"):
        return found
    if isinstance(logs.get("waf_alerts"), str):
        found.append(KnownLog(_resolve(root, logs["waf_alerts"]), _tagged(SERVICE_ID, instance)))

    magnet = waf.get("magnet") or {}
    if magnet.get("enabled"):
        paths = magnet.get("paths") or {}
        for key, default in _MAGNET_DEFAULT_LOGS.items():
            relative = paths.get(key, default)
            if isinstance(relative, str):
                found.append(KnownLog(_resolve(root, relative), _tagged(MAGNET_SERVICE_ID, instance)))
    return found
