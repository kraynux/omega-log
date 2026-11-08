# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Regression du bug reel (2026-10-04, retour utilisateur : "bug severe
dans statistique, choix de fichier (access.log) l'interface gele,
impossible d'exporter ou de faire marche arriere") : AccessLogStatsScreen
calculait ses stats SYNCHRONE sur le thread UI, bloquant tout clic/frappe
pendant la duree du calcul — corrige via `run_worker(thread=True)`.
Verifie ici avec un VRAI Pilot (pas juste la fonction pure deja testee
dans tests/unit/application/test_access_log_stats.py) : le calcul
s'execute bien en arriere-plan et finit par peupler le resultat."""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from omega_log.app.bootstrap import bootstrap
from omega_log.application.use_cases.library import add_to_library
from omega_log.application.use_cases.scan_logs import refresh_log_file
from omega_log.interfaces.tui.app import OmegaLogApp
from omega_log.interfaces.tui.screens.access_log_stats_screen import AccessLogStatsScreen
from omega_log.interfaces.tui.screens.home import HomeScreen

_ACCESS_LOG_CONTENT = "\n".join(
    f'10.0.0.{i % 5} - - [04/Oct/2026:10:00:{i % 60:02d} +0200] "GET /x HTTP/1.1" 200 100'
    for i in range(500)
)


@pytest.fixture
def container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    log_path = tmp_path / "access.log"
    log_path.write_text(_ACCESS_LOG_CONTENT)
    built = bootstrap(console_logging=False)
    add_to_library(built.log_repository, refresh_log_file(str(log_path), access="file"))
    yield built
    built.close()


@pytest.mark.asyncio
async def test_compute_runs_in_background_and_populates_result(container) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 50)) as pilot:
        app.push_screen(HomeScreen(container=container))
        await pilot.pause()
        screen = AccessLogStatsScreen(container=container)
        app.push_screen(screen)
        await pilot.pause()

        screen.query_one("#selection-input").value = "1"
        await pilot.pause()
        await pilot.click("#period-Tout")

        # Le resultat n'est pas garanti pret au premier `pause()` (calcul en
        # arriere-plan, `run_worker(thread=True)` + `call_from_thread`) : on
        # attend sa mise a jour au lieu de l'exiger immediatement — c'est
        # precisement le changement qui corrige le gel rapporte (l'ancien
        # code bloquait le gestionnaire de clic jusqu'a la fin du calcul).
        for _ in range(50):
            if screen._result is not None:
                break
            await asyncio.sleep(0.05)
            await pilot.pause()

        assert screen._result is not None
        assert screen._result.report.total == 500

        # L'app reste reactive PENDANT et APRES le calcul (Retour fonctionne) —
        # exactement ce que le bug rapporte cassait ("impossible de faire
        # marche arriere"). `escape` (OmegaScreen::action_back) plutot que
        # cliquer "#back" : independant de la position de defilement du
        # bouton dans le VerticalScroll (source de flakiness constatee ici,
        # le bouton pouvant rester hors-vue malgre scroll_visible() selon
        # le moment exact ou le rendu du resultat a fini de s'etablir).
        await pilot.press("escape")
        for _ in range(60):
            if app.screen_stack[-1].__class__.__name__ != "AccessLogStatsScreen":
                break
            await asyncio.sleep(0.05)
            await pilot.pause()
        assert app.screen_stack[-1].__class__.__name__ != "AccessLogStatsScreen"


@pytest.mark.asyncio
async def test_library_table_keeps_its_rows_after_result(container) -> None:
    """Retour utilisateur 2026-11-06 : apres le calcul, la liste des logs disparaissait (seul l'en-tete
    restait) - tableau `height: 1fr` dans un panneau qui defile, ecrase quand le resultat le remplit."""
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        app.push_screen(HomeScreen(container=container))
        await pilot.pause()
        screen = AccessLogStatsScreen(container=container)
        app.push_screen(screen)
        await pilot.pause()
        screen.query_one("#selection-input").value = "1"
        await pilot.click("#period-Tout")
        for _ in range(50):
            if screen._result is not None:
                break
            await asyncio.sleep(0.05)
            await pilot.pause()
        await pilot.pause()
        table = screen.query_one("#library-table")
        assert table.row_count == 1
        assert table.region.height >= table.row_count + 1   # en-tete + chaque ligne visibles


@pytest.mark.asyncio
async def test_rich_report_on_screen_and_in_exports(container) -> None:
    """Rapport a la omega-fire (2026-11-06) : synthese, statuts, tops, horaire, tendance par jour, a l'ecran
    et dans les exports HTML et JSON."""
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        app.push_screen(HomeScreen(container=container))
        await pilot.pause()
        screen = AccessLogStatsScreen(container=container)
        app.push_screen(screen)
        await pilot.pause()
        screen.query_one("#selection-input").value = "1"
        await pilot.click("#period-Tout")
        for _ in range(50):
            if screen._result is not None:
                break
            await asyncio.sleep(0.05)
            await pilot.pause()
        summary = str(screen.query_one("#stats-summary").render())
        timeline = str(screen.query_one("#stats-hourly").render())
        for text in ("SYNTHÈSE", "STATUTS HTTP", "TOP IP", "CHEMINS DEMANDÉS", "Heure de pointe"):
            assert text in summary
        assert "RÉPARTITION HORAIRE" in timeline and "TENDANCE PAR JOUR" in timeline and "█" in timeline
        screen._export_html()
        screen._export_json()
    html = next(container.default_exports_dir.glob("stats-*.html")).read_text(encoding="utf-8")
    for text in ("Synthèse", "Répartition horaire", "Tendance par jour", "Statuts HTTP", "Chemins les plus demandés"):
        assert text in html
    data = __import__("json").loads(next(container.default_exports_dir.glob("stats-*.json")).read_text())
    assert data["total"] == 500 and len(data["hourly"]) == 24 and data["statuses"]["2xx"] == 500
