# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Statistiques (plan_omega_log.md §3/§7) : ADAPTE depuis
omega-serv/log_stats_screen.py (source retenue) — periode 24h/7j/30j,
top IPs, repartition horaire, generalise a la Bibliotheque LOG. Ajoute
l'export 5 themes jinja2 (plan §2/§6, deja present chez SERV mais
jamais relie a cet ecran — corrélation neuve, pas du code neuf dans le
moteur d'export lui-meme).

`_compute` EXECUTE DANS UN PROCESSUS SEPARE depuis le 2026-10-04 (retour
utilisateur : "bug severe, l'interface gele" PUIS, apres un premier
correctif `run_worker(thread=True)` insuffisant : "rien ne change...
l'ecran n'est pas gele mais... se degele et regele") — bug reel MESURE,
pas un ressenti : `compute_access_log_stats()` lit et parse
l'INTEGRALITE du/des fichier(s) choisi(s) ligne par ligne, un calcul
100% CPU-bound en Python pur. Deporte dans un THREAD, il se dispute
encore le GIL avec la boucle d'evenements Textual — mesure directe sur
un access.log de 300 000 lignes : jusqu'a 1.2s de latence d'un simple
`pilot.pause()` pendant les ~49s du calcul, exactement le "gele/degele/
regele" rapporte. Seul un vrai PROCESSUS separe echappe entierement au
GIL (infrastructure/concurrency/process_pool.py) : `_compute` est donc
maintenant une METHODE ASYNCHRONE lancee via `run_worker()` (jamais
`thread=True`), qui `await` `loop.run_in_executor(STATS_PROCESS_POOL,
...)` — la boucle d'evenements reste entierement libre pendant l'attente,
`self.query_one()`/`request_elevation()` restent appeles directement
(plus besoin de `call_from_thread()`, on est deja sur le thread
principal).

NoMatches RATTRAPEE AJOUTE (2026-10-04, bug reel trouve dans var/app.log
d'une session utilisateur reelle — "Worker raised exception: NoMatches
('No nodes match ...')") : un calcul en arriere-plan peut legitimement
finir APRES que l'utilisateur ait deja quitte cet ecran (Retour, ou tout
simplement ferme l'app) — `self.query_one()` leve alors `NoMatches` (plus
aucun widget de CET ecran dans l'arbre), ce qui faisait planter le
worker SILENCIEUSEMENT (l'exception n'atteint jamais l'utilisateur,
seulement le fichier de log applicatif) — exactement le "rien ne se
passe" rapporte quand le calcul met plusieurs secondes et que
l'utilisateur, impatient, navigue ailleurs avant la fin. Toute mise a
jour de widget qui suit un `await` doit donc rattraper `NoMatches` et ne
rien faire (l'ecran n'existe plus, personne a qui montrer le resultat).

GARDE "_computing" AJOUTEE (2026-10-04, meme correctif que screens/
process_ip_screen.py, voir sa note detaillee — meme retour utilisateur,
meme cause : `exclusive=True` annule le TASK ASYNCIO d'un calcul
precedent des qu'un nouveau demarre, mais jamais le travail DEJA
soumis au ProcessPoolExecutor — un calcul deja lance dans un processus
du pool continue jusqu'au bout meme "annule" de notre point de vue,
saturant `max_workers=2` apres quelques changements de periode
rapproches. Empeche desormais tout nouveau calcul tant qu'un autre est
en cours (boutons de periode desactives pendant le calcul)."""
from __future__ import annotations

import asyncio
import functools
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from omega_lib.theme.policies import DEFAULT_EXPORT_THEME, EXPORT_PALETTES
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.widgets import Button, DataTable, Footer, Header, Input, Select, Static

from omega_log.application.use_cases.access_log_stats import (
    AccessLogStatsResult,
    compute_access_log_stats,
    hourly_stats_for_export,
)
from omega_log.application.use_cases.library import list_library
from omega_log.infrastructure.concurrency.process_pool import STATS_PROCESS_POOL
from omega_log.infrastructure.exporters.html_exporter import export_access_log_stats_html
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens._elevation import request_elevation

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer
    from omega_log.ports.process_runner_port import ProcessRunnerPort

_PERIODS: tuple[tuple[str, str | None], ...] = (
    ("24h", "24h"), ("7j", "7d"), ("30j", "30d"), ("Tout", None),
)
_BAR_WIDTH = 40


def _export_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


class AccessLogStatsScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._entries: list = []
        self._result = None
        self._elevated = False
        self._computing = False

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static("STATISTIQUES", classes="omega-title")
            yield DataTable(id="library-table")
            yield Input(placeholder="Numeros separes par des virgules (ex: 1,2)", id="selection-input")
            with Horizontal(classes="omega-actions"):
                for label, period in _PERIODS:
                    with Container(classes="omega-btn-frame"):
                        yield Button(label, id=f"period-{label}")

            yield Static("", id="stats-summary")
            yield Static("", id="stats-hourly")

            yield Static("Theme d'export HTML", classes="omega-subtitle")
            with Horizontal(classes="omega-actions"):
                yield Select([(name, name) for name in EXPORT_PALETTES], value=DEFAULT_EXPORT_THEME, id="theme-select")
                with Container(classes="omega-btn-frame"):
                    yield Button("Exporter JSON", id="export-json")
                with Container(classes="omega-btn-frame"):
                    yield Button("Exporter HTML", id="export-html")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#library-table", DataTable).cursor_type = "row"
        self.query_one("#library-table", DataTable).add_columns("#", "Chemin")
        self._entries = list_library(self._container.log_repository)
        table = self.query_one("#library-table", DataTable)
        for idx, entry in enumerate(self._entries, start=1):
            table.add_row(str(idx), entry.path)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id == "back":
            self.dismiss()
        elif button_id.startswith("period-"):
            label = button_id.removeprefix("period-")
            period = dict(_PERIODS)[label]
            self._compute(period)
        elif button_id == "export-json":
            self._export_json()
        elif button_id == "export-html":
            self._export_html()

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
        runner = self._container.process_runner if self._elevated else None
        self._computing = True
        self._set_period_buttons_disabled(True)
        self.run_worker(self._compute_async(paths, period, runner))

    def _set_period_buttons_disabled(self, disabled: bool) -> None:
        try:
            for label, _period in _PERIODS:
                self.query_one(f"#period-{label}", Button).disabled = disabled
        except NoMatches:
            pass  # ecran deja ferme (utilisateur reparti avant la fin du calcul) — rien a mettre a jour

    def _finish_computing(self) -> None:
        """A appeler sur TOUTE sortie de `_compute_async` (succes, erreur,
        permission refusee) — jamais seulement le chemin heureux, sinon
        un calcul en erreur laisserait les boutons de periode desactives
        pour toujours."""
        self._computing = False
        self._set_period_buttons_disabled(False)

    async def _compute_async(
        self, paths: list[str], period: str | None, runner: ProcessRunnerPort | None,
    ) -> None:
        try:
            self.query_one("#stats-summary", Static).update("Calcul en cours...")
            self.query_one("#stats-hourly", Static).update("")
        except NoMatches:
            self._finish_computing()
            return  # ecran deja ferme avant meme le lancement du calcul (improbable mais gratuit a couvrir)

        loop = asyncio.get_running_loop()
        func = functools.partial(compute_access_log_stats, paths, period=period, runner=runner)
        try:
            result = await loop.run_in_executor(STATS_PROCESS_POOL, func)
        except PermissionRequiredError:
            if not request_elevation(self, self._container.process_runner):
                self.app.notify("Permission refusee sur au moins un log selectionne.", severity="error")
                self._clear_summary()
                self._finish_computing()
                return
            self._elevated = True
            func = functools.partial(
                compute_access_log_stats, paths, period=period, runner=self._container.process_runner,
            )
            try:
                result = await loop.run_in_executor(STATS_PROCESS_POOL, func)
            except Exception as exc:  # noqa: BLE001 - jamais planter l'appli pour un calcul de stats
                self._show_compute_error(str(exc))
                return
        except Exception as exc:  # noqa: BLE001 - jamais planter l'appli pour un calcul de stats
            self._show_compute_error(str(exc))
            return

        self._apply_result(paths, period, result)

    def _clear_summary(self) -> None:
        try:
            self.query_one("#stats-summary", Static).update("")
        except NoMatches:
            pass  # ecran deja ferme (utilisateur reparti avant la fin du calcul) — rien a mettre a jour

    def _show_compute_error(self, message: str) -> None:
        self.app.notify(f"Erreur de calcul : {message}", severity="error")
        self._finish_computing()
        try:
            self.query_one("#stats-summary", Static).update(f"Erreur de calcul : {message}")
        except NoMatches:
            pass  # ecran deja ferme (utilisateur reparti avant la fin du calcul) — rien a mettre a jour

    def _apply_result(self, paths: list[str], period: str | None, result: AccessLogStatsResult) -> None:
        self._finish_computing()
        self._result = result
        stats = result.stats

        try:
            summary_widget = self.query_one("#stats-summary", Static)
            hourly_widget = self.query_one("#stats-hourly", Static)
        except NoMatches:
            return  # ecran deja ferme (utilisateur reparti avant la fin du calcul) — rien a mettre a jour

        top_lines = "\n".join(f"  {ip.ip:<18} {ip.count:>8}" for ip in stats.top_ips) or "  (aucune IP)"
        summary_widget.update(
            f"Periode : {period or 'tout'} — {len(paths)} log(s)\n"
            f"Lignes analysees : {stats.parsed_lines}\n"
            f"IPs uniques : {stats.unique_ips}\n"
            f"Taux d'erreur : {stats.error_rate():.1f}%\n\n"
            f"Top IPs :\n{top_lines}"
        )

        hourly = hourly_stats_for_export(stats)
        hourly_lines = "\n".join(
            f"  {h['hour']:>2}h  {'#' * int(h['percent'] / 100 * _BAR_WIDTH):<{_BAR_WIDTH}}  {h['count']}"
            for h in hourly
        )
        hourly_widget.update(f"Repartition horaire :\n{hourly_lines}")

    def _export_json(self) -> None:
        if self._result is None:
            self.app.notify("Calculez d'abord les statistiques (choisissez une periode).", severity="warning")
            return
        import json

        stats = self._result.stats
        payload = {
            "sources": self._result.sources,
            "period": self._result.period,
            "total_entries": stats.parsed_lines,
            "unique_ips": stats.unique_ips,
            "error_rate": stats.error_rate(),
            "top_ips": [{"ip": t.ip, "count": t.count} for t in stats.top_ips],
            "hourly_stats": hourly_stats_for_export(stats),
        }
        export_dir = self._container.default_exports_dir
        export_dir.mkdir(parents=True, exist_ok=True)
        out_path = export_dir / f"stats-{_export_timestamp()}.json"
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self.app.notify(f"Export JSON : {out_path}")

    def _export_html(self) -> None:
        if self._result is None:
            self.app.notify("Calculez d'abord les statistiques (choisissez une periode).", severity="warning")
            return
        stats = self._result.stats
        theme_name = self.query_one("#theme-select", Select).value
        html = export_access_log_stats_html(
            sources=self._result.sources,
            period=self._result.period,
            total_entries=stats.parsed_lines,
            unique_ips=stats.unique_ips,
            error_rate=stats.error_rate(),
            top_ips=[{"ip": t.ip, "count": t.count} for t in stats.top_ips],
            hourly_stats=hourly_stats_for_export(stats),
            theme_name=str(theme_name),
        )
        export_dir = self._container.default_exports_dir
        export_dir.mkdir(parents=True, exist_ok=True)
        out_path = export_dir / f"stats-{_export_timestamp()}.html"
        out_path.write_text(html, encoding="utf-8")
        self.app.notify(f"Export HTML : {out_path}")
