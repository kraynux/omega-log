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
contrairement a Statistiques qui l'avait deja).

Recherche manuelle d'une IP (portee d'omega-serv 2.6.0, 2026-11-07) : saisir une IP, compter ses lignes dans les
logs selectionnes (fichier entier, sudo si besoin) et pouvoir la retirer, sans attendre qu'elle apparaisse dans le
top. Meme regle que le retrait (domain/logs/ip_match.py) : le compte affiche est exactement ce qui sera retire."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from omega_log.application.use_cases.library import list_library
from omega_log.application.use_cases.process_ip import (
    count_ip_occurrences,
    remove_ip_from_file,
)
from omega_log.domain.logs.ip_match import normalize_ip
from omega_log.domain.logs.models import TopIP
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens._elevation import request_elevation
from omega_log.interfaces.tui.screens._parallel_compute import accumulate_in_pool
from omega_log.interfaces.tui.screens.confirm import ConfirmScreen
from omega_log.interfaces.tui.widgets.busy_indicator import (
    PERIOD_BUTTON_LABELS,
    PERIOD_HINT,
    BusyIndicator,
    describe_selection,
)
from omega_log.interfaces.tui.widgets.library_selection import SELECTION_HINT, LibrarySelectionMixin
from omega_log.interfaces.tui.widgets.log_library_table import LogLibraryTable
from omega_log.shared.i18n import _

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer
    from omega_log.ports.process_runner_port import ProcessRunnerPort

_PERIODS: tuple[tuple[str, str | None], ...] = (
    ("24h", "24h"), ("7j", "7d"), ("30j", "30d"), ("Tout", None),
)


class ProcessIpScreen(LibrarySelectionMixin, OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._entries: list = []
        self._current_paths: list[str] = []
        self._selected_ip: str | None = None
        self._elevated = False
        self._computing = False
        self._searched_ip: str | None = None
        """IP de la derniere recherche manuelle : apres un retrait, c'est elle qu'on recompte."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static(_("VOIR ET TRAITER IP"), classes="omega-title")
            yield LogLibraryTable(id="library-table")
            yield Static(_("Logs à analyser (numéros ci-dessus, séparés par des virgules)"), classes="omega-subtitle")
            yield Input(placeholder=_("ex: 1,2"), id="selection-input")
            yield Static(SELECTION_HINT, classes="omega-hint")
            with Horizontal(classes="omega-actions"):
                for label, period in _PERIODS:
                    with Container(classes="omega-btn-frame"):
                        yield Button(_(PERIOD_BUTTON_LABELS[label]), id=f"period-{label}")
            yield Static(PERIOD_HINT, classes="omega-hint")
            yield Static("", id="selection-size", classes="omega-hint")
            yield Static(_("Ou cherchez une IP précise dans ces logs (fichier entier) :"), classes="omega-subtitle")
            with Horizontal(classes="omega-actions"):
                yield Input(placeholder=_("ex: 203.0.113.42"), id="ip-input")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Rechercher cette IP"), id="search-ip")
            yield BusyIndicator(id="busy")
            yield Static("", id="ip-status", classes="omega-hint")
            yield Static("", id="ip-search-result", classes="omega-hint")
            yield DataTable(id="top-ips-table")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Retirer cette IP des logs analysés"), id="remove-ip", variant="error", disabled=True)
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#top-ips-table", DataTable).cursor_type = "row"
        self.query_one("#top-ips-table", DataTable).add_columns(_("IP"), _("Occurrences"))
        self._entries = list_library(self._container.log_repository)
        self.query_one("#library-table", LogLibraryTable).load(self._entries)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "ip-input":
            self._search_ip()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "selection-input":
            self._refresh_selection_size()

    def _refresh_selection_size(self) -> None:
        """Taille et nombre de lignes estime de la selection, affiches AVANT le calcul (2026-11-06)."""
        raw = self._library_selection()
        tokens = [token.strip() for token in raw.split(",") if token.strip()]
        paths = [self._entries[int(t) - 1].path for t in tokens if t.isdigit() and 1 <= int(t) <= len(self._entries)]
        description = describe_selection(paths)
        self.query_one("#selection-size", Static).update(_("Sélection : {description}").format(description=description) if description else "")

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == "library-table":
            self._refresh_selection_size()
            return
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
        elif button_id == "search-ip":
            self._search_ip()
        elif button_id == "remove-ip":
            self._remove_selected_ip()

    def _selected_paths(self) -> list[str] | None:
        raw = self._library_selection()
        if not raw:
            self.app.notify(_("Saisissez au moins un numéro de ligne."), severity="warning")
            return None
        paths: list[str] = []
        for token in raw.split(","):
            token = token.strip()
            if not token.isdigit() or not (1 <= int(token) <= len(self._entries)):
                self.app.notify(_("Numéro invalide : '{token}'.").format(token=token), severity="warning")
                return None
            paths.append(self._entries[int(token) - 1].path)
        return paths

    def _compute(self, period: str | None) -> None:
        if self._computing:
            self.app.notify(_("Un calcul est déjà en cours, patientez."), severity="warning")
            return
        paths = self._selected_paths()
        if paths is None:
            return
        self._current_paths = paths
        self._searched_ip = None
        self.query_one("#ip-search-result", Static).update("")
        runner = self._container.process_runner if self._elevated else None
        self._computing = True
        self._set_period_buttons_disabled(True)
        self._set_status("")
        self.query_one("#busy", BusyIndicator).start(paths, period)
        self.run_worker(self._compute_async(paths, period, runner))

    def _search_ip(self) -> None:
        if self._computing:
            self.app.notify(_("Un calcul est déjà en cours, patientez."), severity="warning")
            return
        paths = self._selected_paths()
        if paths is None:
            return
        typed = self.query_one("#ip-input", Input).value
        ip = normalize_ip(typed)
        if ip is None:
            self._set_status(_("Adresse IP invalide : {value!r}.").format(value=typed.strip()))
            return
        self._run_search(ip, paths)

    def _run_search(self, ip: str, paths: list[str]) -> None:
        self._current_paths = paths
        self._searched_ip = ip
        self._computing = True
        self._set_period_buttons_disabled(True)
        self._set_status("")
        self.query_one("#busy", BusyIndicator).start(paths, None)
        self.run_worker(self._search_async(ip, paths))

    def _count_all(self, ip: str, paths: list[str], runner: ProcessRunnerPort | None) -> list[tuple[str, int]]:
        return [(path, count_ip_occurrences(path, ip, runner=runner)) for path in paths]

    async def _search_async(self, ip: str, paths: list[str]) -> None:
        """Comptage dans un thread (lecture en flux) ; un log illisible : authentification sudo dans le
        processus de l'interface (jamais dans le thread), puis nouvel essai avec sudo."""
        runner = self._container.process_runner if self._elevated else None
        try:
            try:
                results = await asyncio.to_thread(self._count_all, ip, paths, runner)
            except PermissionRequiredError:
                if not request_elevation(self, self._container.process_runner):
                    self.app.notify(_("Permission refusée sur au moins un log sélectionné."), severity="error")
                    self._finish_computing()
                    return
                self._elevated = True
                results = await asyncio.to_thread(self._count_all, ip, paths, self._container.process_runner)
        except Exception as exc:  # noqa: BLE001 - jamais planter l'appli pour une recherche
            self._show_compute_error(str(exc))
            return
        self._apply_ip_search(ip, results)

    def _apply_ip_search(self, ip: str, results: list[tuple[str, int]]) -> None:
        self._finish_computing()
        try:
            table = self.query_one("#top-ips-table", DataTable)
            remove_button = self.query_one("#remove-ip", Button)
            result_line = self.query_one("#ip-search-result", Static)
        except NoMatches:
            return  # ecran deja ferme
        total = sum(count for _path, count in results)
        names = [Path(path).name for path, _count in results]
        # Nom seul, sauf si deux logs portent le meme (deux access.log) : chemin complet
        labels = [path if names.count(name) > 1 else name for (path, _count), name in zip(results, names, strict=True)]
        detail = " · ".join(f"{label} : {count}" for label, (_path, count) in zip(labels, results, strict=True))
        result_line.update(_("{ip} : {total} ligne(s) - {detail}").format(ip=ip, total=total, detail=detail))
        table.clear()
        self._selected_ip = None
        remove_button.disabled = True
        if not total:
            self.app.notify(_("{ip} est absente des log(s) sélectionné(s).").format(ip=ip))
            return
        table.add_row(ip, str(total), key=ip)
        self._selected_ip = ip
        remove_button.disabled = False

    def _set_period_buttons_disabled(self, disabled: bool) -> None:
        try:
            for label, _period in _PERIODS:
                self.query_one(f"#period-{label}", Button).disabled = disabled
            self.query_one("#search-ip", Button).disabled = disabled
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
        try:
            accumulator = await accumulate_in_pool(paths, period, runner, self._show_progress)
        except PermissionRequiredError:
            if not request_elevation(self, self._container.process_runner):
                self.app.notify(_("Permission refusée sur au moins un log sélectionné."), severity="error")
                self._finish_computing()
                return
            self._elevated = True
            try:
                accumulator = await accumulate_in_pool(
                    paths, period, self._container.process_runner, self._show_progress,
                )
            except Exception as exc:  # noqa: BLE001 - jamais planter l'appli pour un calcul de top IP
                self._show_compute_error(str(exc))
                return
        except Exception as exc:  # noqa: BLE001 - jamais planter l'appli pour un calcul de top IP
            self._show_compute_error(str(exc))
            return

        top_ips = accumulator.top_ips(10)
        self._apply_top_ips(top_ips)

    def _show_progress(self, done_bytes: int, total_bytes: int, done_parts: int, total_parts: int) -> None:
        try:
            self.query_one("#busy", BusyIndicator).set_progress(done_bytes, total_bytes, done_parts, total_parts)
        except NoMatches:
            pass  # ecran deja ferme

    def _finish_computing(self) -> None:
        """A appeler sur TOUTE sortie de `_compute_async` (succes, erreur,
        permission refusee) — jamais seulement le chemin heureux, sinon
        un calcul en erreur laisserait les boutons de periode desactives
        pour toujours."""
        self._computing = False
        self._set_period_buttons_disabled(False)
        try:
            self.query_one("#busy", BusyIndicator).stop()
        except NoMatches:
            pass  # ecran deja ferme

    def _show_compute_error(self, message: str) -> None:
        self.app.notify(_("Erreur de calcul : {message}").format(message=message), severity="error")
        self._set_status(_("Erreur : {message}").format(message=message))
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
            self.app.notify(_("Aucune IP trouvée dans les log(s) sélectionné(s) pour cette "
                              "période."))

    def _remove_selected_ip(self) -> None:
        if self._selected_ip is None or not self._current_paths:
            return
        ip = self._selected_ip
        self.app.push_screen(
            ConfirmScreen(
                title=_("RETIRER CETTE IP ?"),
                message=_("Retirer toutes les lignes contenant {ip} de {count} fichier(s).").format(ip=ip, count=len(self._current_paths)),
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
                    errors.append(_("{path} : permission refusée.").format(path=path))
                    continue
                self._elevated = True
                result = remove_ip_from_file(path, ip, runner=self._container.process_runner)
            if result.success:
                total += result.occurrences
            else:
                errors.append(f"{path} : {result.message}")
        if errors:
            self.app.notify("; ".join(errors), severity="error")
        self.app.notify(_("{total} occurrence(s) de {ip} retirée(s) au total.").format(total=total, ip=ip))
        if self._searched_ip == ip:
            self._run_search(ip, list(self._current_paths))  # recherche manuelle : on recompte cette IP
        else:
            self._compute(None)
