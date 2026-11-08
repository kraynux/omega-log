# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Recherche locale des installations omega-serv (alias, registre d'instances, unites systemd) - faux
HOME et faux dossier systemd, jamais la vraie machine (2026-11-06)."""
import json
from pathlib import Path

from omega_log.infrastructure.probe.omega_serv_locator import find_installs, scan_omega_serv


def _install(root: Path, config: dict | str) -> Path:
    (root / "config").mkdir(parents=True)
    text = config if isinstance(config, str) else json.dumps(config)
    (root / "config" / "omega-serve.json").write_text(text)
    return root


def _config() -> dict:
    return {"logs": {"access": "var/log/access.log", "error": "var/log/error.log",
                     "waf_alerts": "var/log/waf-alerts.log"},
            "options": {"waf": {"enabled": True}}}


def test_alias_registry_and_systemd_are_found_without_duplicates(tmp_path: Path) -> None:
    home, units = tmp_path / "home", tmp_path / "units"
    home.mkdir()
    units.mkdir()
    main = _install(tmp_path / "main", _config())
    inst = _install(tmp_path / "inst", _config())
    service = _install(tmp_path / "svc", _config())
    (home / ".zshrc").write_text(f'export X=1\nalias serv="{main}/omega-serv.sh"\n')
    (home / ".bashrc").write_text(f'alias serv="{main}/omega-serv.sh"\nalias serv="{tmp_path}/gone/omega-serv.sh"\n')
    (home / ".config" / "omega-serv").mkdir(parents=True)
    (home / ".config" / "omega-serv" / "instances.json").write_text(json.dumps([{"name": "blog", "path": str(inst)}]))
    (units / "omega-serv-svc.service").write_text(f"[Service]\nWorkingDirectory={service}\n")
    (units / "other.service").write_text(f"[Service]\nWorkingDirectory={tmp_path}\n")

    installs = find_installs(home=home, unit_dir=units)
    assert {(i.root, i.instance) for i in installs} == {(main, None), (inst, "blog"), (service, None)}


def test_scan_reads_logs_and_reports_unreadable_config(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    good = _install(tmp_path / "good", _config())
    bad = _install(tmp_path / "bad", "{ pas du json")
    (home / ".bashrc").write_text(f'alias serv="{good}/omega-serv.sh"\nalias serv="{bad}/omega-serv.sh"\n')

    scan = scan_omega_serv(home=home, unit_dir=tmp_path / "absent")
    assert [log.path for log in scan.logs] == [str(good / "var/log" / n) for n in ("access.log", "error.log", "waf-alerts.log")]
    assert scan.unreadable == [bad]


def test_nothing_found_is_empty(tmp_path: Path) -> None:
    scan = scan_omega_serv(home=tmp_path, unit_dir=tmp_path)
    assert scan.installs == [] and scan.logs == []
