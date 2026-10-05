# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Regression du bug reel (2026-10-04, retour utilisateur : "je change
les delais les resultats ne bougent plus") : `exclusive=True` sur
`run_worker()` annulait le TASK ASYNCIO d'un calcul precedent des qu'un
nouveau demarrait, mais jamais le travail DEJA SOUMIS au
ProcessPoolExecutor — un calcul deja lance dans un processus du pool
continue jusqu'au bout meme "annule" de notre point de vue. Changer de
periode plusieurs fois de suite, avant la fin de chaque calcul,
saturait donc `STATS_PROCESS_POOL` (max_workers=2) de calculs
"fantomes" — le clic suivant restait en file d'attente indefiniment.

Corrige en empechant tout nouveau calcul de demarrer tant qu'un autre
est en cours (boutons de periode desactives + notification si on
essaie quand meme) — verifie ici qu'un enchainement de PLUSIEURS
periodes DIFFERENTES, chacune attendue jusqu'au bout avant la
suivante (usage normal), continue de produire un resultat a chaque
fois — pas seulement les deux premieres comme rapporte."""
from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path

import pytest

from omega_log.app.bootstrap import bootstrap
from omega_log.application.use_cases.library import add_to_library
from omega_log.application.use_cases.scan_logs import refresh_log_file
from omega_log.interfaces.tui.app import OmegaLogApp
from omega_log.interfaces.tui.screens.process_ip_screen import ProcessIpScreen

_MONTH_ABBR = (
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
)


def _apache_timestamp(when: datetime, second: int) -> str:
    """Horodatage Apache base sur l'instant REEL d'execution du test (jour/mois/
    annee/heure de `when`, seule la seconde varie par ligne) — JAMAIS une date
    calendaire figee en dur : un "04/Oct/2026" fixe passait silencieusement
    hors de la fenetre "24h" (voire "7j"/"30j") des que le jour change
    reellement sur la machine qui execute les tests, faisant echouer ces
    tests sans aucun rapport avec le code qu'ils verifient. `%b` evite via
    une table explicite toute dependance a la locale systeme (C/en requis
    pour produire "Oct" et non une abreviation localisee)."""
    return f"{when.day:02d}/{_MONTH_ABBR[when.month - 1]}/{when.year}:{when.hour:02d}:{when.minute:02d}:{second:02d} +0200"


_NOW = datetime.now()

_ACCESS_LOG_CONTENT = "\n".join(
    f'10.0.0.{i % 7} - - [{_apache_timestamp(_NOW, i % 60)}] "GET /x HTTP/1.1" 200 100'
    for i in range(2000)
)

# Volume dedie plus important pour le test de desactivation-pendant-calcul
# ci-dessous : avec 2000 lignes, le calcul peut finir AVANT meme que
# `pilot.click()` ne rende la main (course perdue a tort, constate en
# pratique) — jamais assez de marge pour observer fiablement l'etat
# "boutons desactives" entre le clic et la fin du calcul. 20 000 lignes
# mesure ~1,5-2s en pratique (toutes les lignes tombent dans la fenetre
# "24h" vu l'horodatage synthetique fixe — aucun gain possible de
# l'arret anticipe par periode ici, calcul complet a chaque fois) :
# marge confortable sans alourdir excessivement la suite de tests.
_LARGE_ACCESS_LOG_CONTENT = "\n".join(
    f'10.0.0.{i % 7} - - [{_apache_timestamp(_NOW, i % 60)}] "GET /x HTTP/1.1" 200 100'
    for i in range(20_000)
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


@pytest.fixture
def large_container(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OMEGA_LOG_VAR_DIR", str(tmp_path / "var"))
    log_path = tmp_path / "access.log"
    log_path.write_text(_LARGE_ACCESS_LOG_CONTENT)
    built = bootstrap(console_logging=False)
    add_to_library(built.log_repository, refresh_log_file(str(log_path), access="file"))
    yield built
    built.close()


async def _wait_until_computation_done(pilot, screen, iterations: int = 100) -> int:
    """Attend `screen._computing is False` — PAS `row_count > 0`, qui
    resterait vrai a tort entre deux periodes (anciennes lignes encore
    affichees le temps que le NOUVEAU calcul les remplace, voir
    `_apply_top_ips` : `_finish_computing()` puis seulement `table.
    clear()`/`add_row()`)."""
    for _ in range(iterations):
        if not screen._computing:
            return screen.query_one("#top-ips-table").row_count
        await asyncio.sleep(0.05)
        await pilot.pause()
    pytest.fail("timeout: calcul jamais termine apres plusieurs secondes")


@pytest.mark.asyncio
async def test_changing_period_several_times_in_a_row_keeps_working(container) -> None:
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 50)) as pilot:
        screen = ProcessIpScreen(container=container)
        app.push_screen(screen)
        await pilot.pause()
        screen.query_one("#selection-input").value = "1"
        await pilot.pause()

        for period_label in ("24h", "7j", "30j", "Tout", "7j"):
            await pilot.click(f"#period-{period_label}")
            rows = await _wait_until_computation_done(pilot, screen)
            assert rows > 0, f"periode {period_label} : aucune ligne produite"
            # boutons reactives une fois le calcul termine — sinon le
            # CLIC SUIVANT de la boucle ne ferait rien (meme symptome
            # que le bug rapporte, cette fois par un oubli de reactivation)
            assert screen.query_one(f"#period-{period_label}").disabled is False


@pytest.mark.asyncio
async def test_clicking_another_period_while_computing_is_ignored_not_queued(large_container) -> None:
    # Fichier dedie plus volumineux : avec un calcul trop rapide,
    # `pilot.click()` peut laisser le temps au cycle desactive -> termine
    # -> reactive de se jouer ENTIEREMENT avant meme de rendre la main,
    # rendant l'etat "desactive" impossible a observer de facon fiable.
    container = large_container
    app = OmegaLogApp(container)
    async with app.run_test(size=(120, 50)) as pilot:
        screen = ProcessIpScreen(container=container)
        app.push_screen(screen)
        await pilot.pause()
        screen.query_one("#selection-input").value = "1"
        await pilot.pause()

        await pilot.click("#period-24h")
        # boutons desactives PENDANT le calcul — jamais la peine
        # d'attendre pour le verifier, c'est synchrone avec le clic
        assert screen.query_one("#period-7j").disabled is True
        assert screen._computing is True

        await _wait_until_computation_done(pilot, screen, iterations=300)
        assert screen._computing is False
        assert screen.query_one("#period-7j").disabled is False
