# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Retours utilisateur 2026-11-02 :
- viewer Simple identique a omega-serv (reference) : barre d'etat a 5 blocs et tout le tampon dans un
  tableau qui defile (avant : 30 lignes sans ascenseur, barre « Apercu » / « Top IP ») ;
- « le double clic aussi pas op dans omega-log » : double-clic / Entree ajoute ou retire le numero
  de la ligne dans le champ, simple clic suffisant quand le champ est vide (comme omega-serv)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from textual.widgets import DataTable, Input, Static

from omega_log.app.bootstrap import bootstrap
from omega_log.application.use_cases.library import add_to_library
from omega_log.application.use_cases.scan_logs import refresh_log_file
from omega_log.interfaces.tui.app import OmegaLogApp
from omega_log.interfaces.tui.screens.home import HomeScreen
from omega_log.interfaces.tui.screens.live_tail_screen import LiveTailScreen
from omega_log.interfaces.tui.screens.view_logs import ViewLogsScreen
from omega_log.interfaces.tui.widgets.library_selection import (
    selection_or_cursor,
    toggle_selection_number,
)


def _access_lines() -> str:
    start = datetime(2026, 11, 2, 7, 0, 0, tzinfo=timezone.utc)
    rows = []
    for i in range(200):
        moment = (start + timedelta(seconds=i)).strftime("%d/%b/%Y:%H:%M:%S")
        status = 404 if i % 10 == 0 else 200
        size = "-" if i % 2 else "1024"
        rows.append(f'2001:db8::{i % 7} - - [{moment} +0000] "GET /p{i} HTTP/1.1" {status} {size} "-" "curl"')
    return "\n".join(rows) + "\n"


@pytest.fixture
def container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    built = bootstrap(console_logging=False)
    for name in ("access.log", "other.log"):
        path = tmp_path / name
        path.write_text(_access_lines())
        add_to_library(built.log_repository, refresh_log_file(str(path), access="file"))
    built.tmp_path = tmp_path  # type: ignore[attr-defined]
    yield built
    built.close()


@pytest.mark.asyncio
async def test_simple_viewer_matches_omega_serv(container) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 45)) as pilot:
        app.push_screen(HomeScreen(container=container))
        await pilot.pause()
        screen = LiveTailScreen(container=container, path=str(container.tmp_path / "access.log"))
        app.push_screen(screen)
        await pilot.pause()
        await pilot.pause()
        stats = str(screen.query_one("#stats-box", Static).render())
        for heading in ("RENDEMENT", "BANDE PASSANTE", "STATUTS HTTP", "CLIENTS & RÉSEAU", "SANTÉ & TAMPON"):
            assert heading in stats
        assert "1.0 req/s" in stats            # 200 lignes sur 199 s
        assert "100.0 KB" in stats             # tailles « - » jamais estimees
        assert "IPs uniques  : 7" in stats     # IPv6 compressee reconnue
        assert "200/500" in stats
        # Barre complete d'omega-serv (2026-11-06) : refus, top 5 IP, chemins demandes et en 404.
        for line in ("Refus 403", "Refus 429", "Top 5 IP", "CHEMINS DEMANDÉS", "CHEMINS EN 404"):
            assert line in stats
        assert screen.query_one("#stats-frame").styles.width.value == 34
        table = screen.query_one("#entries-table", DataTable)
        assert table.row_count == 200          # tout le tampon
        assert table.max_scroll_y > 0          # donc un ascenseur
        assert table.scroll_y >= table.max_scroll_y - 1


@pytest.mark.asyncio
async def test_double_click_toggles_number_and_single_click_suffices(container) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 45)) as pilot:
        app.push_screen(HomeScreen(container=container))
        await pilot.pause()
        screen = ViewLogsScreen(container=container)
        app.push_screen(screen)
        await pilot.pause()
        table = screen.query_one("#library-table", DataTable)
        field = screen.query_one("#selection-input", Input)
        # simple clic (ligne surlignee), champ vide : la ligne suffit
        table.move_cursor(row=1)
        await pilot.pause()
        assert screen._library_selection() == "2"
        # Entree (= double-clic) : ajoute, puis retire
        table.focus()
        await pilot.press("enter")
        await pilot.pause()
        assert field.value == "2"
        table.move_cursor(row=0)
        await pilot.press("enter")
        await pilot.pause()
        assert field.value == "2,1"
        await pilot.press("enter")
        await pilot.pause()
        assert field.value == "2"
        assert screen._library_selection() == "2"   # champ rempli : prioritaire


def test_selection_helpers() -> None:
    assert toggle_selection_number("", 3) == "3"
    assert toggle_selection_number("1,3", 3) == "1"
    assert selection_or_cursor("", 0, 2) == "1"
    assert selection_or_cursor(" 2 ", 0, 2) == "2"
    assert selection_or_cursor("", 0, 0) == ""
