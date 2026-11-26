# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""« Voir les exports » (demande 2026-11-26, meme principe que les autres outils) : le dossier des exports dans le
navigateur ; sans navigateur, la liste et la lecture dans l'interface, sans jamais interpreter le contenu."""
from __future__ import annotations

from pathlib import Path

import pytest
from textual.widgets import Button, DataTable, Static

from omega_log.app.bootstrap import bootstrap
from omega_log.interfaces.tui.app import OmegaLogApp
from omega_log.interfaces.tui.screens.access_log_stats_screen import AccessLogStatsScreen
from omega_log.interfaces.tui.screens.export_screen import ExportScreen
from omega_log.interfaces.tui.screens.exports import ExportsScreen, list_exports, read_export
from omega_log.interfaces.tui.screens.help_screen import HelpScreen
from omega_log.interfaces.tui.screens.log_health_screen import LogHealthScreen


@pytest.fixture
def container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    built = bootstrap(console_logging=False)
    folder = built.default_exports_dir
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "log-health-20261126-190000.txt").write_text("SANTÉ\n[bold red]pas du balisage[/]\n")
    (folder / "stats-20261126-190100.html").write_text(
        "<html><style>p{color:red}</style><script>alert(1)</script><h1>Statistiques</h1><p>Requêtes : 42</p></html>")
    (folder / "sous-dossier").mkdir()
    (folder / "lien.txt").symlink_to(tmp_path / "ailleurs.txt")
    yield built
    built.close()


def test_liste_et_lecture_sans_interpretation(container) -> None:
    folder = container.default_exports_dir
    # ni le lien ni le sous-dossier (ordre : du plus recent au plus ancien, ici crees a la meme seconde)
    assert {p.name for p in list_exports(folder)} == {"stats-20261126-190100.html", "log-health-20261126-190000.txt"}
    text = read_export(folder / "stats-20261126-190100.html")
    assert "Statistiques" in text and "Requêtes : 42" in text
    assert "alert" not in text and "color" not in text
    assert "[bold red]pas du balisage[/]" in read_export(folder / "log-health-20261126-190000.txt")


@pytest.mark.asyncio
@pytest.mark.parametrize("screen_class", [ExportScreen, AccessLogStatsScreen, LogHealthScreen, HelpScreen])
async def test_bouton_ouvre_le_dossier_dans_le_navigateur(container, screen_class) -> None:
    opened: list[Path] = []
    container.open_folder = lambda path: opened.append(path) or True
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        screen = screen_class(container=container)
        app.push_screen(screen)
        await pilot.pause()
        screen.on_button_pressed(Button.Pressed(screen.query_one("#view-exports", Button)))
        await app.workers.wait_for_complete()
        await pilot.pause()
        assert opened == [container.default_exports_dir]
        assert app.screen is screen                       # rien d'autre a l'ecran


@pytest.mark.asyncio
async def test_sans_navigateur_liste_et_lecture_dans_l_interface(container) -> None:
    container.open_folder = lambda _path: False
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        screen = ExportScreen(container=container)
        app.push_screen(screen)
        await pilot.pause()
        screen.on_button_pressed(Button.Pressed(screen.query_one("#view-exports", Button)))
        await app.workers.wait_for_complete()
        await pilot.pause()
        exports = app.screen
        assert isinstance(exports, ExportsScreen)
        assert exports.query_one("#exports-table", DataTable).row_count == 2    # ni lien ni sous-dossier
        exports._read()
        await pilot.pause()
        shown = str(exports.query_one("#export-content", Static).render())
        assert "Statistiques" in shown or "SANTÉ" in shown
