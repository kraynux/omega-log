# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Logs dans un dossier ferme a votre compte (demande 2026-11-26 : /var/log/lighttpd/access.log, droits 750).

`stat()` y leve PermissionError : avant, chaque module le prenait pour un fichier absent (Bibliotheque « ABSENT »,
Registre qui l'ecartait, viewers « introuvable » sans proposer sudo, Statistiques qui le sautait, Sante « Fichier
absent »). Ici, un vrai dossier `chmod 000` et un faux sudo qui repond comme le vrai."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from textual.widgets import DataTable

from omega_log.app.bootstrap import bootstrap
from omega_log.application.commands.rotate_logs import RotateLogsRequest
from omega_log.application.use_cases import log_tasks
from omega_log.application.use_cases.library import add_to_library, list_library
from omega_log.application.use_cases.log_health import collect_log_facts
from omega_log.application.use_cases.process_ip import remove_ip_from_file
from omega_log.domain.entities.log_file import LogFile
from omega_log.domain.logs.health import evaluate_log
from omega_log.infrastructure.privileged import elevation, file_access
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.infrastructure.privileged.file_access import Access, probe_file
from omega_log.infrastructure.tail.live_tail_reader import LiveTailReader
from omega_log.interfaces.tui.app import OmegaLogApp
from omega_log.interfaces.tui.screens import library as library_screen
from omega_log.interfaces.tui.screens import live_tail_screen
from omega_log.interfaces.tui.screens.confirm import ConfirmScreen
from omega_log.interfaces.tui.screens.library import LibraryScreen
from omega_log.interfaces.tui.screens.live_tail_screen import LiveTailScreen
from omega_log.interfaces.tui.widgets.log_library_table import log_state_label
from omega_log.ports.process_runner_port import ProcessResult

pytestmark = pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root traverse tout dossier")

LINES = [
    '203.0.113.7 - - [26/Nov/2026:10:00:00 +0000] "GET / HTTP/1.1" 200 512 "-" "curl/8"',
    '203.0.113.8 - - [26/Nov/2026:10:00:01 +0000] "GET /x HTTP/1.1" 404 12 "-" "curl/8"',
]
CONTENT = "\n".join(LINES) + "\n"


class FakeSudo:
    """Repond a `sudo -n env LC_ALL=C stat …`, `sudo cat` et `sudo tail -c +N` avec le vrai contenu (lu en
    rouvrant le dossier le temps de la commande), comme le ferait sudo."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.calls: list[list[str]] = []

    def _open(self):
        os.chmod(self.folder, 0o755)
        return self

    def _close(self):
        os.chmod(self.folder, 0o000)

    def run(self, args: list[str], input_text: str | None = None, timeout: float | None = None) -> ProcessResult:
        self.calls.append(args)
        path = Path(args[-1])
        self._open()
        try:
            if not path.exists():
                return ProcessResult(1, "", f"stat: cannot statx '{path}': No such file or directory")
            if "setfacl" in args:
                return ProcessResult(0, "", "")
            if "stat" in args:
                info = path.stat()
                mode = "700" if path == self.folder else "644"   # le dossier tel qu'il est ferme
                kind = "directory" if path.is_dir() else "regular file"
                return ProcessResult(0, f"{info.st_size} {int(info.st_mtime)} {mode} {info.st_dev} {kind}\n", "")
            data = path.read_bytes()
            if "cat" in args:
                return ProcessResult(0, data.decode(), "")
            if "head" in args:
                return ProcessResult(0, data[:int(args[args.index("-c") + 1])].decode(), "")
            if "tail" in args:
                count = args[args.index("-c") + 1]
                chunk = data[int(count[1:]) - 1:] if count.startswith("+") else data[-int(count):]
                return ProcessResult(0, chunk.decode(), "")
            return ProcessResult(1, "", "commande non simulee")
        finally:
            self._close()

    def run_interactive(self, args: list[str]) -> int:
        return 0


@pytest.fixture
def closed(tmp_path: Path):
    folder = tmp_path / "lighttpd"
    folder.mkdir()
    (folder / "access.log").write_text(CONTENT)
    os.chmod(folder, 0o000)
    yield folder / "access.log"
    os.chmod(folder, 0o755)


@pytest.fixture
def sudo_granted(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setitem(elevation._SESSION, "granted", True)


@pytest.fixture
def no_sudo(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setitem(elevation._SESSION, "granted", False)


def test_dossier_ferme_protege_jamais_absent_et_sans_sudo_tente(closed: Path, no_sudo) -> None:
    sudo = FakeSudo(closed.parent)
    probe = probe_file(str(closed), sudo)
    assert probe.access is Access.PROTECTED and not probe.exists
    assert sudo.calls == []                       # jamais de sudo avant une authentification
    log_file = LogFile(path=str(closed), access="file", protected=True)
    assert log_state_label(log_file) == "PROTÉGÉ (sudo)"
    assert probe_file(str(closed.parent / "absent.log")).access is Access.PROTECTED  # sudo seul peut trancher
    assert probe_file(str(closed.parent.parent / "rien" / "x.log")).access is Access.MISSING


def test_avec_sudo_accorde_taille_et_absence_vues(closed: Path, sudo_granted) -> None:
    sudo = FakeSudo(closed.parent)
    probe = probe_file(str(closed), sudo)
    assert probe.exists and probe.protected and probe.size == len(CONTENT.encode())
    assert sudo.calls[0][:5] == ["sudo", "-n", "env", "LC_ALL=C", "stat"]   # -n : jamais d'invite
    assert probe_file(str(closed.parent / "absent.log"), sudo).access is Access.MISSING


def test_bibliotheque_et_lectures_des_modules(closed: Path, tmp_path: Path, no_sudo,
                                              monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    container = bootstrap(console_logging=False)
    try:
        add_to_library(container.log_repository, LogFile(path=str(closed), access="file"))
        [entry] = list_library(container.log_repository)
        assert entry.protected and not entry.exists     # avant : ABSENT
    finally:
        container.close()
    # Rotate : plus « Fichier source introuvable »
    assert RotateLogsRequest(source_path=str(closed)).validate() == []
    # Statistiques / Voir et Traiter IP : demande sudo au lieu de sauter le log
    with pytest.raises(PermissionRequiredError):
        log_tasks.plan_read_tasks([str(closed)], workers=1)
    [task] = log_tasks.plan_read_tasks([str(closed)], workers=1, runner=FakeSudo(closed.parent))
    assert task.privileged
    with pytest.raises(PermissionRequiredError):
        remove_ip_from_file(str(closed), "203.0.113.7")


def test_suivi_en_direct_demande_sudo_puis_lit_la_suite(closed: Path, sudo_granted) -> None:
    sudo = FakeSudo(closed.parent)
    reader = LiveTailReader(closed)
    with pytest.raises(PermissionError):           # avant : [] en silence, a chaque rafraichissement
        reader.read_new_lines()
    reader.sync_privileged(sudo)
    assert reader.read_new_lines_privileged(sudo) == []
    os.chmod(closed.parent, 0o755)
    with closed.open("a") as handle:
        handle.write('203.0.113.9 - - [26/Nov/2026:10:00:02 +0000] "GET /y HTTP/1.1" 200 1 "-" "curl/8"\n')
    os.chmod(closed.parent, 0o000)
    assert [line.split()[0] for line in reader.read_new_lines_privileged(sudo)] == ["203.0.113.9"]


def test_sante_des_logs_dossier_ferme(closed: Path, no_sudo, monkeypatch: pytest.MonkeyPatch) -> None:
    facts = collect_log_facts(str(closed), logrotate_patterns=[])
    assert facts.closed_folder and not facts.exists
    assert [f.code for f in evaluate_log(facts, facts.modified_at or _now()).findings] == ["closed_folder"]
    monkeypatch.setitem(elevation._SESSION, "granted", True)   # « Analyser avec sudo »
    seen = collect_log_facts(str(closed), logrotate_patterns=[], privileged_runner=FakeSudo(closed.parent))
    assert seen.exists and not seen.readable and seen.size == len(CONTENT.encode())
    assert seen.sampled_lines == 2
    codes = {f.code: f.params for f in evaluate_log(seen, _now()).findings}
    assert codes["unreadable_folder"] == {"mode": "700", "folder": str(closed.parent)}   # le dossier, pas le 644
    assert "unreadable" not in codes


def _now():
    from datetime import datetime, timezone
    return datetime(2026, 11, 26, 12, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_ajout_manuel_confirme_puis_sudo(closed: Path, tmp_path: Path, no_sudo,
                                              monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    container = bootstrap(console_logging=False)
    container.process_runner = FakeSudo(closed.parent)

    def fake_elevation(_screen, _runner) -> bool:
        elevation._SESSION["granted"] = True
        return True

    monkeypatch.setattr(library_screen, "request_elevation", fake_elevation)
    monkeypatch.setattr(file_access, "_DEFAULT_RUNNER", container.process_runner)  # liste de la Bibliotheque
    try:
        app = OmegaLogApp(container)
        async with app.run_test(size=(140, 45)) as pilot:
            screen = LibraryScreen(container=container)
            app.push_screen(screen)
            await pilot.pause()
            screen.query_one("#path-input").value = str(closed)
            screen._add_manual()
            await pilot.pause()
            assert isinstance(app.screen, ConfirmScreen)
            app.screen.dismiss(True)
            await pilot.pause()
            table = screen.query_one("#log-list", DataTable)
            assert table.row_count == 1
            assert str(table.get_row_at(0)[-1]) == "PROTÉGÉ (sudo)"
            assert str(table.get_row_at(0)[4]) == f"{len(CONTENT.encode())} o"   # taille vue avec sudo
    finally:
        container.close()


@pytest.mark.asyncio
async def test_viewer_simple_lit_un_dossier_ferme_avec_sudo(closed: Path, tmp_path: Path, no_sudo,
                                                            monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    container = bootstrap(console_logging=False)
    container.process_runner = FakeSudo(closed.parent)
    asked: list[bool] = []

    def fake_elevation(_screen, _runner) -> bool:
        asked.append(True)
        elevation._SESSION["granted"] = True
        return True

    monkeypatch.setattr(live_tail_screen, "request_elevation", fake_elevation)
    try:
        app = OmegaLogApp(container)
        async with app.run_test(size=(140, 45)) as pilot:
            screen = LiveTailScreen(container=container, path=str(closed))
            app.push_screen(screen)
            await pilot.pause()
            await pilot.pause()
            assert asked == [True]                  # une seule demande de mot de passe
            assert screen.query_one("#entries-table", DataTable).row_count == 2
            screen._poll()                          # rafraichissement : rien en double
            assert screen.query_one("#entries-table", DataTable).row_count == 2
    finally:
        container.close()


def test_registre_propose_le_log_d_un_dossier_ferme(closed: Path, no_sudo, monkeypatch: pytest.MonkeyPatch) -> None:
    from omega_log.application.use_cases import scan_logs as scan
    from omega_log.infrastructure.probe.log_path_catalog import LogPathCandidate

    class NoScanner:
        def __init__(self, _registry) -> None:
            pass

        def scan(self) -> dict:
            return {key: 0 for key in ("capabilities_registered", "capabilities_available", "capabilities_degraded",
                                       "capabilities_missing", "capabilities_disqualified")} | {"errors": []}

    monkeypatch.setattr(scan, "SystemScanner", NoScanner)
    monkeypatch.setattr(scan, "SERVICE_LOG_PATHS", {"lighttpd": (LogPathCandidate(str(closed), "file"),)})
    monkeypatch.setattr(scan, "DYNAMIC_SERVICE_LOG_PATHS", {})
    monkeypatch.setattr(scan, "SYSTEM_LOG_PATHS", ())
    result = scan.scan_logs()
    assert [f.path for f in result.discovered] == [str(closed)]     # avant : rangé dans « introuvables »
    assert result.discovered[0].protected
    assert scan.scan_directory(closed.parent) == []                  # dossier ferme : jamais un plantage


def test_commandes_acl_lecture_seule_pour_votre_compte(closed: Path) -> None:
    from omega_log.application.use_cases.log_health import grant_read_commands
    folder = str(closed.parent)
    assert grant_read_commands(str(closed), "kraynux", closed_folder=True) == [
        ["setfacl", "-m", "u:kraynux:rx", "--", folder],
        ["setfacl", "-d", "-m", "u:kraynux:r", "--", folder],
        ["setfacl", "-m", "u:kraynux:r", "--", str(closed)],
    ]
    assert grant_read_commands("/var/log/auth.log", "kraynux", closed_folder=False) == [
        ["setfacl", "-m", "u:kraynux:r", "--", "/var/log/auth.log"]]


@pytest.mark.asyncio
async def test_sante_corriger_avec_sudo_rend_lisible(closed: Path, tmp_path: Path, no_sudo,
                                                     monkeypatch: pytest.MonkeyPatch) -> None:
    """Retour d'utilisation 2026-11-26 : « le log reste illisible et Corriger avec sudo reste grisé »."""
    import shutil

    from textual.widgets import Button

    from omega_log.interfaces.tui.screens import log_health_screen
    from omega_log.interfaces.tui.screens.log_health_screen import LogHealthScreen

    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    monkeypatch.setattr(shutil, "which", lambda name: f"/usr/bin/{name}")
    container = bootstrap(console_logging=False)
    sudo = FakeSudo(closed.parent)
    container.process_runner = sudo

    def fake_elevation(_screen, _runner) -> bool:
        elevation._SESSION["granted"] = True
        return True

    monkeypatch.setattr(log_health_screen, "request_elevation", fake_elevation)
    monkeypatch.setattr(file_access, "_DEFAULT_RUNNER", sudo)
    add_to_library(container.log_repository, LogFile(path=str(closed), access="file"))
    try:
        app = OmegaLogApp(container)
        async with app.run_test(size=(160, 50)) as pilot:
            screen = LogHealthScreen(container=container)
            app.push_screen(screen)
            await app.workers.wait_for_complete()
            await pilot.pause()
            screen._analyse_with_sudo()
            await app.workers.wait_for_complete()
            await pilot.pause()
            codes = [f["code"] for log in screen._data["logs"] for f in log["findings"]]
            assert "unreadable_folder" in codes
            assert not screen.query_one("#fix-sudo", Button).disabled       # avant : grise
            screen._fix_with_sudo()
            await pilot.pause()
            assert isinstance(app.screen, ConfirmScreen)
            app.screen.dismiss(True)
            await app.workers.wait_for_complete()
            await pilot.pause()
            setfacl = [call[call.index("setfacl"):] for call in sudo.calls if "setfacl" in call]
            assert setfacl[0][:3] == ["setfacl", "-m", f"u:{os.environ.get('USER') or __import__('getpass').getuser()}:rx"]
            assert len(setfacl) == 3
    finally:
        container.close()
