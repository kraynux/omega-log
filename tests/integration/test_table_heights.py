# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Balayage des tableaux (2026-11-06, meme piege qu'omega-fire 2026-10-28) : chaque tableau d'un ecran,
rempli de 6 lignes, doit les montrer toutes - jamais ecrase a son seul en-tete parce que le panneau
defile. Feuilles de style reelles de l'application."""
from __future__ import annotations

from pathlib import Path

import pytest
from textual.widgets import DataTable, Static

from omega_log.app.bootstrap import bootstrap
from omega_log.interfaces.tui.app import OmegaLogApp
from omega_log.interfaces.tui.screens.access_log_stats_screen import AccessLogStatsScreen
from omega_log.interfaces.tui.screens.export_screen import ExportScreen
from omega_log.interfaces.tui.screens.favorites import FavoritesScreen
from omega_log.interfaces.tui.screens.home import HomeScreen
from omega_log.interfaces.tui.screens.library import LibraryScreen
from omega_log.interfaces.tui.screens.process_ip_screen import ProcessIpScreen
from omega_log.interfaces.tui.screens.purge_screen import PurgeScreen
from omega_log.interfaces.tui.screens.remote_log_sources_screen import RemoteLogSourcesScreen
from omega_log.interfaces.tui.screens.rotate_screen import RotateScreen
from omega_log.interfaces.tui.screens.view_logs import ViewLogsScreen

SCREENS = (AccessLogStatsScreen, ExportScreen, FavoritesScreen, LibraryScreen, ProcessIpScreen, PurgeScreen,
           RemoteLogSourcesScreen, RotateScreen, ViewLogsScreen)
ROWS = 6


@pytest.fixture
def container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    built = bootstrap(console_logging=False)
    yield built
    built.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("screen_class", SCREENS, ids=lambda cls: cls.__name__)
async def test_every_table_shows_its_rows(container, screen_class) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        app.push_screen(HomeScreen(container=container))
        await pilot.pause()
        screen = screen_class(container=container)
        app.push_screen(screen)
        await pilot.pause()
        # Pire cas : un resultat long affiche sous les tableaux (Statistiques, Voir et traiter IP).
        for static in screen.query(Static):
            if static.id in {"stats-hourly", "stats-summary"}:
                static.update("\n".join(f"ligne {i}" for i in range(40)))
        for table in screen.query(DataTable):
            table.display = True
            columns = len(table.columns)
            for index in range(ROWS):
                table.add_row(*[f"v{index}"] * columns)
        await pilot.pause()
        await pilot.pause()
        for table in screen.query(DataTable):
            assert table.region.height >= ROWS + 1, f"{screen_class.__name__} #{table.id} : {table.region.height}"
