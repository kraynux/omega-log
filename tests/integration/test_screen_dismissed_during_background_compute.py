# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Regression du bug reel (2026-10-04, trouve dans var/app.log d'une
session utilisateur reelle) : `textual.worker.WorkerFailed: Worker
raised exception: NoMatches("No nodes match '#top-ips-table' on
ProcessIpScreen()")` — correspondait exactement au retour utilisateur
"rien ne se passe quand on choisit un log et une duree" sur Voir et
Traiter IP (et au meme risque, pas encore declenche, sur Statistiques) :
un calcul en arriere-plan (process pool) peut legitimement finir APRES
que l'utilisateur ait deja quitte l'ecran — `self.query_one()` levait
alors `NoMatches`, plantant le worker.

IMPORTANT sur la methode de test : Textual ISOLE deja les exceptions des
workers (elles finissent dans le logger de l'app, jamais ne remontent
pour faire echouer le test ni planter l'App) — c'est precisement
pourquoi le bug original etait SILENCIEUX pour l'utilisateur. Un test
base sur une course (declencher le calcul puis `dismiss()` aussitot, en
esperant 'gagner' la course avant la fin du calcul) ne peut donc PAS
detecter la regression de facon fiable : verifie empiriquement, un tel
test passe aussi bien AVEC que SANS le correctif. Les tests ci-dessous
appellent donc DIRECTEMENT les methodes `_apply_*`/`_show_compute_error`
APRES un dismiss() reel (`query_one` y leve alors vraiment `NoMatches`,
deterministe) et verifient qu'aucune exception n'en ressort — test
precis de la garde elle-meme, jamais tributaire d'un timing."""
from __future__ import annotations

from pathlib import Path

import pytest

from omega_log.app.bootstrap import bootstrap
from omega_log.interfaces.tui.app import OmegaLogApp
from omega_log.interfaces.tui.screens.access_log_stats_screen import AccessLogStatsScreen
from omega_log.interfaces.tui.screens.process_ip_screen import ProcessIpScreen


@pytest.fixture
def container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    built = bootstrap(console_logging=False)
    yield built
    built.close()


@pytest.mark.asyncio
async def test_process_ip_apply_top_ips_after_dismiss_does_not_raise(container) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 50)) as pilot:
        screen = ProcessIpScreen(container=container)
        app.push_screen(screen)
        await pilot.pause()
        screen.dismiss()
        await pilot.pause()

        # Sans la garde NoMatches, cet appel leverait directement —
        # `query_one` ne trouve plus aucun widget de cet ecran deja ferme.
        screen._apply_top_ips([])
        screen._show_compute_error("erreur de test")


@pytest.mark.asyncio
async def test_access_log_stats_apply_result_after_dismiss_does_not_raise(container) -> None:
    from omega_log.domain.logs.models import LogStats

    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 50)) as pilot:
        screen = AccessLogStatsScreen(container=container)
        app.push_screen(screen)
        await pilot.pause()
        screen.dismiss()
        await pilot.pause()

        from omega_log.application.use_cases.access_log_stats import AccessLogStatsResult

        fake_result = AccessLogStatsResult(sources=["/tmp/x.log"], period=None, stats=LogStats())
        screen._apply_result(["/tmp/x.log"], None, fake_result)
        screen._show_compute_error("erreur de test")
        screen._clear_summary()
