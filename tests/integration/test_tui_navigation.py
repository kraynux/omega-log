# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Test d'integration TUI : reprend la verification manuelle faite a
chaque phase du plan (splash -> menu -> chaque ecran -> retour), formalisee
en pytest. N'exerce PAS le PTY+lnav reel (Viewer 3) : exige un vrai
terminal interactif, impossible sous le pilote Textual (voir
infrastructure/lnav/render.py) — seule la navigation vers LnavScreen
elle-meme (pas le lancement de lnav) est verifiee ici."""
from __future__ import annotations

from pathlib import Path

import pytest

from omega_log.app.bootstrap import bootstrap
from omega_log.interfaces.tui.app import OmegaLogApp
from omega_log.interfaces.tui.screens.home import _COLUMN_1, _COLUMN_2, HomeScreen


@pytest.fixture
def container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    built = bootstrap(console_logging=False)
    yield built
    built.close()


@pytest.mark.asyncio
async def test_splash_then_menu(container) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 50)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, HomeScreen)


@pytest.mark.asyncio
async def test_every_menu_item_opens_a_real_screen_and_returns(container) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.press("enter")
        await pilot.pause()

        for item_id, _label in (*_COLUMN_1, *_COLUMN_2):
            if item_id == "quit":
                continue
            await pilot.click(f"#{item_id}")
            await pilot.pause()
            assert not isinstance(app.screen, HomeScreen), f"{item_id} did not open a screen"
            await pilot.press("escape")
            await pilot.pause()
            assert isinstance(app.screen, HomeScreen), f"{item_id} did not return to the menu"


@pytest.mark.asyncio
async def test_theme_cycling_does_not_crash(container) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 50)) as pilot:
        await pilot.press("enter")
        await pilot.pause()
        before = app.theme
        await pilot.press("t")
        await pilot.pause()
        assert app.theme != before
