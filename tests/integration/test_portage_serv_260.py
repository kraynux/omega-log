# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Portage n°2 depuis omega-serv 2.6.0 (2026-11-07) : menu (Sante des logs, sans Quitter), Sante des logs,
sauvegardes planifiees, recherche manuelle d'une IP, version et verification des mises a jour.
Jamais de vraie crontab, de vrai systemd ni de vrai reseau : faux remplacants."""
from __future__ import annotations

from pathlib import Path

import pytest
from textual.widgets import Button, DataTable, Input, Static

from omega_log.app.bootstrap import bootstrap
from omega_log.application.use_cases.library import add_to_library, refresh_log_file
from omega_log.application.use_cases.rotation_automation import ScheduleResult
from omega_log.interfaces.tui.app import OmegaLogApp
from omega_log.interfaces.tui.screens import rotation_automations_screen
from omega_log.interfaces.tui.screens.contact_support_screen import ContactSupportScreen
from omega_log.interfaces.tui.screens.home import _COLUMN_2, HomeScreen
from omega_log.interfaces.tui.screens.log_health_screen import LogHealthScreen
from omega_log.interfaces.tui.screens.process_ip_screen import ProcessIpScreen
from omega_log.interfaces.tui.screens.rotation_automations_screen import RotationAutomationsScreen

_LINES = ('1.1.1.1 - - [07/Nov/2026:10:00:00 +0000] "GET / HTTP/1.1" 200 5\n'
          '2a03:2880:f800:15:: - - [07/Nov/2026:10:00:01 +0000] "GET / HTTP/1.1" 403 5\n'
          '1.1.1.11 - - [07/Nov/2026:10:00:02 +0000] "GET / HTTP/1.1" 200 5\n')


class _Source:
    def __init__(self, content: str | None) -> None:
        self.content = content

    def fetch_sha_list(self) -> str | None:
        return self.content


@pytest.fixture
def container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    log_path = tmp_path / "access.log"
    log_path.write_text(_LINES)
    built = bootstrap(console_logging=False)
    add_to_library(built.log_repository, refresh_log_file(str(log_path), access="file"))
    built.open_url = lambda url: True
    built.release_source = _Source("aa  omega-log-9.9.0.tar.gz\n")
    yield built
    built.close()


async def _wait(pilot, condition, iterations: int = 100) -> None:
    for _attempt in range(iterations):
        await pilot.pause(0.05)
        if condition():
            return
    pytest.fail("condition jamais atteinte")


def test_menu_has_log_health_after_export_and_no_quit() -> None:
    ids = [item_id for item_id, _label in _COLUMN_2]
    assert "quit" not in ids
    assert ids.index("log_health") == ids.index("export") + 1


@pytest.mark.asyncio
async def test_title_shows_version_and_health_screen_analyses(container) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(140, 50)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        assert app.title.endswith(container.app_version)
        assert isinstance(app.screen, HomeScreen)
        await pilot.click("#log_health")
        await pilot.pause()
        screen = app.screen
        assert isinstance(screen, LogHealthScreen)
        await _wait(pilot, lambda: screen._data is not None)
        assert screen.query_one("#health-table", DataTable).row_count == 1
        screen.query_one("#export-txt", Button).press()
        await pilot.pause()
        assert list((container.default_exports_dir).glob("log-health-*.txt"))


@pytest.mark.asyncio
async def test_process_ip_manual_search_counts_and_removes(container, tmp_path: Path) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(140, 60)) as pilot:
        app.push_screen(ProcessIpScreen(container=container))
        await pilot.pause()
        screen = app.screen
        screen.query_one("#selection-input", Input).value = "1"
        screen.query_one("#ip-input", Input).value = "2a03:2880:f800:15::"
        screen.query_one("#search-ip", Button).press()
        await _wait(pilot, lambda: not screen._computing and str(screen.query_one("#ip-search-result", Static).render()))
        assert "1 ligne(s)" in str(screen.query_one("#ip-search-result", Static).render())
        assert not screen.query_one("#remove-ip", Button).disabled
        screen.query_one("#remove-ip", Button).press()
        await pilot.pause()
        await pilot.click("#confirm")
        await _wait(pilot, lambda: not screen._computing and "0 ligne(s)" in str(
            screen.query_one("#ip-search-result", Static).render()))
    content = (tmp_path / "access.log").read_text()
    assert "2a03:2880:f800:15::" not in content and "1.1.1.11" in content


@pytest.mark.asyncio
async def test_scheduled_backup_added_installs_then_removes_schedule(container, monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(rotation_automations_screen, "uses_systemd", lambda: False)
    monkeypatch.setattr(rotation_automations_screen, "install_rotation_schedule",
                        lambda *a, **k: calls.append("install") or ScheduleResult("cron", True, "installé"))
    monkeypatch.setattr(rotation_automations_screen, "remove_rotation_schedule",
                        lambda *a, **k: calls.append("remove") or ScheduleResult("cron", True, "retiré"))
    monkeypatch.setattr(rotation_automations_screen, "rotation_schedule_status",
                        lambda *a, **k: ScheduleResult("cron", bool(calls) and calls[-1] == "install", "état"))
    app = OmegaLogApp(container)
    async with app.run_test(size=(140, 60)) as pilot:
        app.push_screen(RotationAutomationsScreen(container=container))
        await pilot.pause()
        screen = app.screen
        screen.query_one("#selection-input", Input).value = "1"
        screen.query_one("#add-automation", Button).press()
        await pilot.pause()
        assert calls == ["install"]
        table = screen.query_one("#automations-table", DataTable)
        assert table.row_count == 1
        table.move_cursor(row=0)
        await pilot.pause()
        screen.query_one("#delete-automation", Button).press()
        await pilot.pause()
        await pilot.click("#confirm")
        await pilot.pause()
        assert calls == ["install", "remove"]
    assert container.rotation_automation_store.list_all() == []


@pytest.mark.asyncio
async def test_check_update_shows_new_version(container) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(140, 60)) as pilot:
        app.push_screen(ContactSupportScreen(container=container))
        await pilot.pause()
        screen = app.screen
        screen.query_one("#check-update", Button).press()
        await _wait(pilot, lambda: not screen.query_one("#release-notes", Button).disabled)
        assert "9.9.0" in str(screen.query_one("#update-state", Static).render())


@pytest.mark.asyncio
async def test_library_starts_on_the_list_so_the_status_bar_is_complete(container) -> None:
    """Retour utilisateur 2026-11-07 : focus sur le champ de saisie = raccourcis d'une lettre absents de la barre."""
    from omega_log.interfaces.tui.screens.library import LibraryScreen

    app = OmegaLogApp(container)
    async with app.run_test(size=(140, 50)) as pilot:
        app.push_screen(LibraryScreen(container=container))
        await pilot.pause()
        keys = {active.binding.key for active in app.active_bindings.values() if active.binding.show}
        assert {"q", "t", "r", "a"} <= keys


@pytest.mark.asyncio
async def test_opening_options_does_not_notify(container) -> None:
    """Retour utilisateur 2026-11-07 : la valeur initiale de « Langue des exports » declenchait une notification."""
    from omega_log.interfaces.tui.screens.settings_screen import SettingsScreen

    app = OmegaLogApp(container)
    async with app.run_test(size=(140, 50)) as pilot:
        before = len(app._notifications)
        app.push_screen(SettingsScreen(container=container))
        await pilot.pause(0.5)
        assert len(app._notifications) == before


@pytest.mark.asyncio
async def test_uninstall_schedule_keeps_the_automations(container, monkeypatch) -> None:
    """Demande utilisateur 2026-11-07 : « Desinstaller l'execution » retire la tache, jamais les automatisations."""
    calls: list[str] = []
    monkeypatch.setattr(rotation_automations_screen, "uses_systemd", lambda: False)
    monkeypatch.setattr(rotation_automations_screen, "remove_rotation_schedule",
                        lambda *a, **k: calls.append("remove") or ScheduleResult("cron", True, "retiré"))
    monkeypatch.setattr(rotation_automations_screen, "rotation_schedule_status",
                        lambda *a, **k: ScheduleResult("cron", False, "état"))
    container.rotation_automation_store.add({"path": "/x.log", "days_interval": 7, "created_at": "2026-11-01T00:00:00"})
    app = OmegaLogApp(container)
    async with app.run_test(size=(140, 60)) as pilot:
        app.push_screen(RotationAutomationsScreen(container=container))
        await pilot.pause()
        app.screen.query_one("#uninstall-schedule", Button).press()
        await pilot.pause()
        await pilot.click("#confirm")
        await pilot.pause()
        assert calls == ["remove"]
    assert len(container.rotation_automation_store.list_all()) == 1


@pytest.mark.asyncio
async def test_lnav_launches_directly_and_returns(container, monkeypatch, tmp_path: Path) -> None:
    """Retour utilisateur 2026-11-07 : plus d'ecran intermediaire qui redemande « Lancer lnav »."""
    from omega_log.interfaces.tui.screens import lnav_screen
    from omega_log.interfaces.tui.screens.lnav_screen import LnavScreen

    class _Usable:
        def is_usable(self) -> bool:
            return True

    launched: list[list[str]] = []
    monkeypatch.setattr(lnav_screen, "probe_lnav", lambda: _Usable())
    monkeypatch.setattr(LnavScreen, "_run_lnav", lambda self: launched.append(self._paths))
    app = OmegaLogApp(container)
    async with app.run_test(size=(140, 50)) as pilot:
        app.push_screen(HomeScreen(container=container))
        await pilot.pause()
        app.push_screen(LnavScreen(container=container, paths=[str(tmp_path / "access.log")]))
        await _wait(pilot, lambda: launched and isinstance(app.screen, HomeScreen))
    assert launched == [[str(tmp_path / "access.log")]]


@pytest.mark.asyncio
async def test_lnav_failure_keeps_the_screen_with_the_error(container, monkeypatch, tmp_path: Path) -> None:
    from omega_log.interfaces.tui.screens import lnav_screen
    from omega_log.interfaces.tui.screens.lnav_screen import LnavScreen

    class _Usable:
        def is_usable(self) -> bool:
            return True

    def _boom(self) -> None:
        raise IndexError("string index out of range")

    monkeypatch.setattr(lnav_screen, "probe_lnav", lambda: _Usable())
    monkeypatch.setattr(LnavScreen, "_run_lnav", _boom)
    app = OmegaLogApp(container)
    async with app.run_test(size=(140, 50)) as pilot:
        app.push_screen(LnavScreen(container=container, paths=[str(tmp_path / "access.log")]))
        await _wait(pilot, lambda: "string index" in str(app.screen.query_one("#lnav-error", Static).render()))
        assert isinstance(app.screen, LnavScreen)
