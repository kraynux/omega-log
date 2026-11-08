# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Bibliotheque reprise d'omega-serv (2026-11-06) : table commune, « Ajouter les logs connus
d'Omega-Serv » et « Sources distantes (SSH) ». Jamais de vrai `scp` ni de vraie machine : faux runner,
faux HOME (meme discipline que les tests d'omega-serv)."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from textual.widgets import Button, DataTable, Input

from omega_log.app.bootstrap import bootstrap
from omega_log.application.use_cases.library import list_library
from omega_log.infrastructure.probe.omega_serv_locator import scan_omega_serv
from omega_log.interfaces.tui.app import OmegaLogApp
from omega_log.interfaces.tui.screens.home import HomeScreen
from omega_log.interfaces.tui.screens.library import LibraryScreen
from omega_log.interfaces.tui.screens.remote_log_sources_screen import RemoteLogSourcesScreen
from omega_log.interfaces.tui.widgets.log_library_table import LogLibraryTable
from omega_log.ports.process_runner_port import ProcessResult


class _FakeScpRunner:
    """Succes : ecrit un vrai fichier a la destination (dernier argument), comme scp."""

    def __init__(self, *, succeeds: bool = True, stderr: str = "Connection refused") -> None:
        self._succeeds = succeeds
        self._stderr = stderr
        self.calls: list[list[str]] = []

    def run(self, args, input_text=None, timeout=None):
        self.calls.append(args)
        if self._succeeds:
            local_dest = Path(args[-1])
            local_dest.parent.mkdir(parents=True, exist_ok=True)
            local_dest.write_text("ligne distante 1\n")
            return ProcessResult(returncode=0, stdout="", stderr="")
        return ProcessResult(returncode=1, stdout="", stderr=self._stderr)

    def run_interactive(self, args):
        raise NotImplementedError


@pytest.fixture
def container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    built = bootstrap(console_logging=False)
    built.tmp_path = tmp_path  # type: ignore[attr-defined]
    yield built
    built.close()


async def _open_library(app: OmegaLogApp, pilot, container) -> LibraryScreen:
    app.push_screen(HomeScreen(container=container))
    await pilot.pause()
    screen = LibraryScreen(container=container)
    app.push_screen(screen)
    await pilot.pause()
    return screen


@pytest.mark.asyncio
async def test_add_known_omega_serv_logs(container) -> None:
    tmp = container.tmp_path
    root = tmp / "omega-serv"
    (root / "config").mkdir(parents=True)
    (root / "config" / "omega-serve.json").write_text(json.dumps({
        "logs": {"access": "var/log/access.log", "error": "var/log/error.log", "waf_alerts": "var/log/waf-alerts.log"},
        "options": {"waf": {"enabled": True, "magnet": {"enabled": True}}},
    }))
    home = tmp / "home"
    home.mkdir()
    (home / ".zshrc").write_text(f'alias serv="{root}/omega-serv.sh"\n')
    container.find_omega_serv_logs = lambda: scan_omega_serv(home=home, unit_dir=tmp / "units")

    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_library(app, pilot, container)
        screen.query_one("#add-known", Button).press()
        await pilot.pause()
        table = screen.query_one("#log-list", LogLibraryTable)
        assert table.row_count == 5            # access, error, WAF, 2 magnet
        assert str(table.get_row_at(0)[0]) == "1"
        assert str(table.get_row_at(0)[6]) == "ABSENT"
        # Deuxieme clic : remplace, jamais duplique.
        screen.query_one("#add-known", Button).press()
        await pilot.pause()
        assert table.row_count == 5
    services = {entry.service_id for entry in list_library(container.log_repository)}
    assert services == {"omega-serv", "omega-serv-magnet"}


@pytest.mark.asyncio
async def test_add_known_without_install_adds_nothing(container) -> None:
    container.find_omega_serv_logs = lambda: scan_omega_serv(home=container.tmp_path, unit_dir=container.tmp_path)
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open_library(app, pilot, container)
        screen.query_one("#add-known", Button).press()
        await pilot.pause()
    assert list_library(container.log_repository) == []


async def _save_and_fetch(app: OmegaLogApp, pilot, container) -> RemoteLogSourcesScreen:
    library = await _open_library(app, pilot, container)
    library.query_one("#remote-sources", Button).press()
    await pilot.pause()
    screen = app.screen
    assert isinstance(screen, RemoteLogSourcesScreen)
    screen.query_one("#label-input", Input).value = "backend1"
    screen.query_one("#host-input", Input).value = "192.168.1.10"
    screen.query_one("#remote-path-input", Input).value = "/var/log/access.log"
    screen.query_one("#save", Button).press()
    await pilot.pause()
    table = screen.query_one("#sources-table", DataTable)
    assert table.row_count == 1
    table.move_cursor(row=0)
    await pilot.pause()
    screen.query_one("#fetch", Button).press()
    await pilot.pause()
    await asyncio.sleep(0.3)
    await pilot.pause()
    return screen


@pytest.mark.asyncio
async def test_ssh_fetch_success_adds_copy_to_library(container) -> None:
    runner = _FakeScpRunner(succeeds=True)
    container.process_runner = runner
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 45)) as pilot:
        await _save_and_fetch(app, pilot, container)
        assert len(runner.calls) == 1
        assert runner.calls[0][0] == "scp"
    entries = list_library(container.log_repository)
    assert [(e.access, e.service_id, e.exists) for e in entries] == [("ssh", "backend1", True)]
    assert Path(entries[0].path).parent == container.remote_cache_dir


@pytest.mark.asyncio
async def test_ssh_fetch_failure_shows_error_and_adds_nothing(container) -> None:
    container.process_runner = _FakeScpRunner(succeeds=False)
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _save_and_fetch(app, pilot, container)
        assert "Connection refused" in str(screen.query_one("#sources-error").content)
    assert list_library(container.log_repository) == []
