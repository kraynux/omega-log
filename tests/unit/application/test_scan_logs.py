# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Tests de application/use_cases/scan_logs.py — limites a
refresh_log_file()/scan_directory() (purs, deterministes). `scan_logs()`
dans son ensemble (etape 1 : detection reelle de services via pgrep/
systemctl) depend de l'etat reel de la machine qui execute les tests —
deja verifie par un scan reel en Phase 2/3 (voir le plan), pas re-teste
ici sous une forme mockee qui testerait surtout le mock lui-meme."""
from __future__ import annotations

from pathlib import Path

import pytest

from omega_log.application.use_cases.scan_logs import refresh_log_file, scan_directory


def test_refresh_log_file_existing(tmp_path: Path) -> None:
    log_path = tmp_path / "access.log"
    log_path.write_text("some content")

    log_file = refresh_log_file(str(log_path), access="file", service_id="nginx")

    assert log_file.exists
    assert log_file.size_bytes == len("some content")
    assert log_file.service_id == "nginx"
    assert not log_file.is_stale


def test_refresh_log_file_missing(tmp_path: Path) -> None:
    log_file = refresh_log_file(str(tmp_path / "missing.log"))
    assert not log_file.exists
    assert log_file.size_bytes is None


def test_refresh_log_file_empty_is_stale(tmp_path: Path) -> None:
    log_path = tmp_path / "empty.log"
    log_path.write_text("")
    log_file = refresh_log_file(str(log_path))
    assert log_file.exists
    assert log_file.is_stale


def test_scan_directory_lists_files_non_recursively(tmp_path: Path) -> None:
    (tmp_path / "a.log").write_text("x")
    (tmp_path / "b.log").write_text("yy")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "nested.log").write_text("z")

    results = scan_directory(tmp_path)

    paths = {r.path for r in results}
    assert str(tmp_path / "a.log") in paths
    assert str(tmp_path / "b.log") in paths
    assert str(subdir / "nested.log") not in paths  # non recursif


def test_scan_directory_on_non_directory_returns_empty(tmp_path: Path) -> None:
    file_path = tmp_path / "not_a_dir.log"
    file_path.write_text("x")
    assert scan_directory(file_path) == []


def test_scan_directory_excludes_non_log_files(tmp_path: Path) -> None:
    """Regression du bug reel (2026-10-03, retour utilisateur) : le scan
    manuel d'un dossier proposait TOUT son contenu (`.conf`, `.service`,
    README...) alors que les viewers sont calibres pour des formats de
    logs — seuls les fichiers reconnaissables comme des logs doivent
    etre proposes."""
    (tmp_path / "access.log").write_text("x")
    (tmp_path / "nginx.conf").write_text("x")
    (tmp_path / "service.socket").write_text("x")
    (tmp_path / "README").write_text("x")

    results = scan_directory(tmp_path)

    names = {Path(r.path).name for r in results}
    assert names == {"access.log"}


def test_scan_directory_accepts_rotated_and_extensionless_system_logs(tmp_path: Path) -> None:
    """Rotations/compressions (annuaire §0/§13) et noms traditionnels
    sans extension ".log" (wtmp/btmp/lastlog/messages/secure, catalogue
    §1) doivent rester proposes, pas seulement les "*.log" simples."""
    for name in ("fail2ban.log.1", "fail2ban.log.gz", "syslog.old", "wtmp", "btmp", "lastlog", "messages"):
        (tmp_path / name).write_text("x")
    (tmp_path / "config.yaml").write_text("x")

    results = scan_directory(tmp_path)

    names = {Path(r.path).name for r in results}
    assert names == {"fail2ban.log.1", "fail2ban.log.gz", "syslog.old", "wtmp", "btmp", "lastlog", "messages"}


def test_scan_directory_accepts_samba_log_dot_prefix_convention(tmp_path: Path) -> None:
    """Convention Samba reelle (verifiee sur la machine de reference) :
    certains fichiers sont nommes "log.<service>" (prefixe) plutot que
    "<service>.log" (suffixe) — les deux conventions coexistent dans le
    meme dossier et doivent toutes deux etre proposees."""
    (tmp_path / "log.smbd").write_text("x")
    (tmp_path / "log.smbd.1").write_text("x")
    (tmp_path / "smbd.log").write_text("x")

    results = scan_directory(tmp_path)

    names = {Path(r.path).name for r in results}
    assert names == {"log.smbd", "log.smbd.1", "smbd.log"}


def test_scan_logs_checks_service_log_paths_regardless_of_capability_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression du bug reel (2026-10-03, retour utilisateur : "le scan
    n'est pas operationnel, meme fail2ban il n'a pas trouvé") :
    fail2ban-server est installe mais pas EN COURS D'EXECUTION sur la
    machine de reference, ce que le detecteur process-based rapporte
    MISSING — scan_logs() ne doit plus jamais sauter la verification
    d'un chemin de log a cause de ce statut (le fichier, lui, existe
    toujours sur disque, que le service tourne ou non)."""
    import omega_log.application.use_cases.scan_logs as scan_logs_module
    from omega_log.infrastructure.probe.log_path_catalog import LogPathCandidate

    fake_log = tmp_path / "fake-service.log"
    fake_log.write_text("contenu")

    monkeypatch.setattr(
        scan_logs_module, "SERVICE_LOG_PATHS",
        {"fake-service-definitely-not-running": (LogPathCandidate(str(fake_log), "file"),)},
    )
    monkeypatch.setattr(scan_logs_module, "DYNAMIC_SERVICE_LOG_PATHS", {})

    result = scan_logs_module.scan_logs()

    paths = {lf.path for lf in result.discovered}
    assert str(fake_log) in paths
