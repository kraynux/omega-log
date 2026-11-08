# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Logs connus d'omega-serv : meme liste que le bouton d'omega-serv, WAF et magnet seulement s'ils sont
actifs (2026-11-06)."""
from pathlib import Path

from omega_log.domain.logs.omega_serv_known_logs import KnownLog, known_logs

ROOT = Path("/srv/omega-serv")
LOGS = {"access": "var/log/access.log", "error": "var/log/error.log", "waf_alerts": "var/log/waf-alerts.log"}


def test_without_waf_only_access_and_error() -> None:
    assert [log.path for log in known_logs({"logs": LOGS}, ROOT)] == [
        "/srv/omega-serv/var/log/access.log", "/srv/omega-serv/var/log/error.log",
    ]


def test_waf_enabled_adds_alerts_log() -> None:
    config = {"logs": LOGS, "options": {"waf": {"enabled": True}}}
    assert known_logs(config, ROOT)[-1] == KnownLog("/srv/omega-serv/var/log/waf-alerts.log", "omega-serv")


def test_waf_disabled_ignores_magnet() -> None:
    config = {"logs": LOGS, "options": {"waf": {"enabled": False, "magnet": {"enabled": True}}}}
    assert len(known_logs(config, ROOT)) == 2


def test_magnet_defaults_and_overrides_and_absolute_paths() -> None:
    config = {"logs": LOGS, "options": {"waf": {"enabled": True, "magnet": {
        "enabled": True, "paths": {"blocklist_log": "/var/log/magnet-bl.log"},
    }}}}
    magnet = [log for log in known_logs(config, ROOT) if log.service_id == "omega-serv-magnet"]
    assert [log.path for log in magnet] == ["/srv/omega-serv/var/log/waf-magnet-alerts.log", "/var/log/magnet-bl.log"]


def test_instance_name_tags_service() -> None:
    assert {log.service_id for log in known_logs({"logs": LOGS}, ROOT, instance="blog")} == {"omega-serv:blog"}
