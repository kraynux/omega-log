# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran "Voir et Traiter IP" (plan_omega_log.md §3/§7) : top 10 ADAPTE
depuis omega-serv/top_ips_screen.py (source retenue, generalise a
N'IMPORTE QUEL log de la Bibliotheque), retrait d'IP ADAPTE depuis
omega-fire/remove_ip_from_log_screen.py (complement). Selection des logs
par numeros, meme convention que screens/view_logs.py.

`_compute` EXECUTE DANS UN PROCESSUS SEPARE depuis le 2026-10-04 — meme
bug reel MESURE (pas un ressenti) et meme correctif que screens/
access_log_stats_screen.py (voir sa note en tete de fichier pour la
mesure precise) : `compute_top_ips_for_paths()` fait EXACTEMENT la meme
I/O bloquante CPU-bound — un thread (`run_worker(thread=True)`, premier
correctif insuffisant) se dispute encore le GIL avec la boucle Textual,
d'ou le "gele/degele/regele" rapporte malgre ce premier correctif. Seul
un vrai PROCESSUS separe (infrastructure/concurrency/process_pool.py)
y echappe entierement — `_compute` est une methode ASYNCHRONE qui
`await` `loop.run_in_executor(STATS_PROCESS_POOL, ...)`.
`_remove_if_confirmed` (ecriture) reste volontairement synchrone pour
l'instant — risque moindre (filtrage simple, pas de parsing structure
ligne par ligne) et deja plus complexe a deporter proprement (elevation
possible EN COURS de boucle multi-fichiers).

NoMatches RATTRAPEE AJOUTE (2026-10-04, bug reel trouve dans var/app.log
d'une session utilisateur reelle — "Worker raised exception: NoMatches
(\"No nodes match '#top-ips-table' on ProcessIpScreen()\")", correspond
exactement au retour "rien ne se passe quand on choisit un log et une
duree" pour cet ecran precisement) : un calcul en arriere-plan de
plusieurs secondes peut legitimement finir APRES que l'utilisateur ait
deja quitte cet ecran — `self.query_one()` leve alors `NoMatches`, ce
qui faisait planter le worker SILENCIEUSEMENT (visible uniquement dans
le fichier de log applicatif, jamais pour l'utilisateur). Voir la meme
note, plus detaillee, dans access_log_stats_screen.py (meme bug, meme
correctif, trouve ici en premier via le log reel).

GARDE "_computing" AJOUTEE (2026-10-04, retour utilisateur : "je change
les delais les resultats ne bougent plus") — bug reel, pas un ressenti :
`exclusive=True` sur `run_worker()` annule le TASK ASYNCIO de l'ancien
calcul des qu'un nouveau demarre, mais PAS le travail deja soumis au
ProcessPoolExecutor — un `concurrent.futures.Future` dont le travail a
DEJA DEMARRE dans un processus du pool ne peut plus etre annule
(`Future.cancel()` retourne alors silencieusement False, le processus
continue a tourner jusqu'au bout pour un resultat que plus personne
n'attend). En cliquant plusieurs periodes de suite avant que chaque
calcul precedent soit termine, chaque clic laissait un calcul "fantome"
occuper une des 2 places du pool (`max_workers=2`) — apres 2 clics
rapprochés, le pool etait sature de calculs fantomes et le CLIC SUIVANT
restait en file d'attente indefiniment, d'ou "les resultats ne bougent
plus". Corrige en empechant tout nouveau calcul de demarrer tant qu'un
autre est en cours (boutons de periode desactives + indicateur "Calcul
en cours..." — qui corrige du meme coup l'autre retour "y'a pas
d'indications" : il n'y en avait effectivement aucune sur cet ecran,
contrairement a Statistiques qui l'avait deja)."""
from __future__ import annotations

import asyncio
import functools
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from omega_log.application.use_cases.library import list_library
from omega_log.application.use_cases.process_ip import (
    compute_top_ips_for_paths,
    remove_ip_from_file,
)
from omega_log.domain.logs.models import TopIP
from omega_log.infrastructure.concurrency.process_pool import STATS_PROCESS_POOL
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens._elevation import request_elevation
from omega_log.interfaces.tui.screens.confirm import ConfirmScreen

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer
    from omega_log.ports.process_runner_port import ProcessRunnerPort

_PERIODS: tuple[tuple[str, str | None], ...] = (
    ("24h", "24h"), ("7j", "7d"), ("30j", "30d"), ("Tout", None),
)


class ProcessIpScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._entries: list = []
        self._current_paths: list[str] = []
        self._selected_ip: str | None = None
        self._elevated = False
        self._computing = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static("VOIR ET TRAITER IP", classes="omega-title")
            yield DataTable(id="library-table")
            yield Static("Logs a analyser (numeros ci-dessus, separes par des virgules)", classes="omega-subtitle")
            yield Input(placeholder="ex: 1,2", id="selection-input")
            with Horizontal(classes="omega-actions"):
                for label, period in _PERIODS:
                    with Container(classes="omega-btn-frame"):
                        yield Button(label, id=f"period-{label}")
            yield Static("", id="ip-status", classes="omega-hint")
            yield DataTable(id="top-ips-table")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retirer cette IP des logs analyses", id="remove-ip", variant="error", disabled=True)
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#library-table", DataTable).cursor_type = "row"
        self.query_one("#library-table", DataTable).add_columns("#", "Chemin")
        self.query_one("#top-ips-table", DataTable).cursor_type = "row"
        self.query_one("#top-ips-table", DataTable).add_columns("IP", "Occurrences")
        self._entries = list_library(self._container.log_repository)
        table = self.query_one("#library-table", DataTable)
        for idx, entry in enumerate(self._entries, start=1):
            table.add_row(str(idx), entry.path)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id != "top-ips-table":
            return
        row = event.data_table.get_row_at(event.cursor_row)
        self._selected_ip = str(row[0]) if row else None
        self.query_one("#remove-ip", Button).disabled = self._selected_ip is None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id == "back":
            self.dismiss()
        elif button_id.startswith("period-"):
            label = button_id.removeprefix("period-")
            period = dict(_PERIODS)[label]
            self._compute(period)
        elif button_id == "remove-ip":
            self._remove_selected_ip()

    def _selected_paths(self) -> list[str] | None:
        raw = self.query_one("#selection-input", Input).value.strip()
        if not raw:
            self.app.notify("Saisissez au moins un numero de ligne.", severity="warning")
            return None
        paths: list[str] = []
        for token in raw.split(","):
            token = token.strip()
            if not token.isdigit() or not (1 <= int(token) <= len(self._entries)):
                self.app.notify(f"Numero invalide : '{token}'.", severity="warning")
                return None
            paths.append(self._entries[int(token) - 1].path)
        return paths

    def _compute(self, period: str | None) -> None:
        if self._computing:
            self.app.notify("Un calcul est deja en cours, patientez.", severity="warning")
            return
        paths = self._selected_paths()
        if paths is None:
            return
        self._current_paths = paths
        runner = self._container.process_runner if self._elevated else None
        self._computing = True
        self._set_period_buttons_disabled(True)
        self._set_status("Calcul en cours...")
        self.run_worker(self._compute_async(paths, period, runner))

    def _set_period_buttons_disabled(self, disabled: bool) -> None:
        try:
            for label, _period in _PERIODS:
                self.query_one(f"#period-{label}", Button).disabled = disabled
        except NoMatches:
            pass  # ecran deja ferme (utilisateur reparti avant la fin du calcul) — rien a mettre a jour

    def _set_status(self, message: str) -> None:
        try:
            self.query_one("#ip-status", Static).update(message)
        except NoMatches:
            pass  # ecran deja ferme (utilisateur reparti avant la fin du calcul) — rien a mettre a jour

    async def _compute_async(
        self, paths: list[str], period: str | None, runner: ProcessRunnerPort | None,
    ) -> None:
        loop = asyncio.get_running_loop()
        func = functools.partial(compute_top_ips_for_paths, paths, period=period, n=10, runner=runner)
        try:
            top_ips = await loop.run_in_executor(STATS_PROCESS_POOL, func)
        except PermissionRequiredError:
            if not request_elevation(self, self._container.process_runner):
                self.app.notify("Permission refusee sur au moins un log selectionne.", severity="error")
                self._finish_computing()
                return
            self._elevated = True
            func = functools.partial(
                compute_top_ips_for_paths, paths, period=period, n=10, runner=self._container.process_runner,
            )
            try:
                top_ips = await loop.run_in_executor(STATS_PROCESS_POOL, func)
            except Exception as exc:  # noqa: BLE001 - jamais planter l'appli pour un calcul de top IP
                self._show_compute_error(str(exc))
                return
        except Exception as exc:  # noqa: BLE001 - jamais planter l'appli pour un calcul de top IP
            self._show_compute_error(str(exc))
            return

        self._apply_top_ips(top_ips)

    def _finish_computing(self) -> None:
        """A appeler sur TOUTE sortie de `_compute_async` (succes, erreur,
        permission refusee) — jamais seulement le chemin heureux, sinon
        un calcul en erreur laisserait les boutons de periode desactives
        pour toujours."""
        self._computing = False
        self._set_period_buttons_disabled(False)

    def _show_compute_error(self, message: str) -> None:
        self.app.notify(f"Erreur de calcul : {message}", severity="error")
        self._set_status(f"Erreur : {message}")
        self._finish_computing()

    def _apply_top_ips(self, top_ips: list[TopIP]) -> None:
        self._finish_computing()
        try:
            table = self.query_one("#top-ips-table", DataTable)
            remove_button = self.query_one("#remove-ip", Button)
        except NoMatches:
            return  # ecran deja ferme (utilisateur reparti avant la fin du calcul) — rien a mettre a jour

        self._set_status("")
        table.clear()
        self._selected_ip = None
        remove_button.disabled = True
        for top_ip in top_ips:
            table.add_row(top_ip.ip, str(top_ip.count), key=top_ip.ip)
        if not top_ips:
            self.app.notify("Aucune IP trouvee dans les log(s) selectionne(s) pour cette periode.")

    def _remove_selected_ip(self) -> None:
        if self._selected_ip is None or not self._current_paths:
            return
        ip = self._selected_ip
        self.app.push_screen(
            ConfirmScreen(
                title="RETIRER CETTE IP ?",
                message=f"Retirer toutes les lignes contenant {ip} de {len(self._current_paths)} fichier(s).",
            ),
            lambda confirmed: self._remove_if_confirmed(confirmed, ip),
        )

    def _remove_if_confirmed(self, confirmed: bool | None, ip: str) -> None:
        if not confirmed:
            return
        total = 0
        errors: list[str] = []
        for path in self._current_paths:
            runner = self._container.process_runner if self._elevated else None
            try:
                result = remove_ip_from_file(path, ip, runner=runner)
            except PermissionRequiredError:
                if not request_elevation(self, self._container.process_runner):
                    errors.append(f"{path} : permission refusee.")
                    continue
                self._elevated = True
                result = remove_ip_from_file(path, ip, runner=self._container.process_runner)
            if result.success:
                total += result.occurrences
            else:
                errors.append(f"{path} : {result.message}")
        if errors:
            self.app.notify("; ".join(errors), severity="error")
        self.app.notify(f"{total} occurrence(s) de {ip} retiree(s) au total.")
        self._compute(None)
