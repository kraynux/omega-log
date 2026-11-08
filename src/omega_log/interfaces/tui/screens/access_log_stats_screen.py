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

from dataclasses import asdict
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from omega_lib.theme.policies import DEFAULT_EXPORT_THEME, EXPORT_PALETTES
from rich.cells import cell_len
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.widgets import Button, DataTable, Footer, Header, Input, Select, Static

from omega_log.application.use_cases.access_log_stats import (
    AccessLogStatsResult,
)
from omega_log.application.use_cases.library import list_library
from omega_log.domain.logs.stats_report import RankedItem, StatsReport
from omega_log.infrastructure.exporters.html_exporter import export_access_log_stats_html
from omega_log.infrastructure.privileged.elevation import PermissionRequiredError
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens._elevation import request_elevation
from omega_log.interfaces.tui.screens._parallel_compute import accumulate_in_pool
from omega_log.interfaces.tui.widgets.busy_indicator import (
    PERIOD_BUTTON_LABELS,
    PERIOD_HINT,
    BusyIndicator,
    describe_selection,
)
from omega_log.interfaces.tui.widgets.gauges import append_gauge_line
from omega_log.interfaces.tui.widgets.library_selection import SELECTION_HINT, LibrarySelectionMixin
from omega_log.interfaces.tui.widgets.log_library_table import LogLibraryTable
from omega_log.shared.i18n import LANGUAGE, N_, _, translating_as

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer
    from omega_log.ports.process_runner_port import ProcessRunnerPort

_PERIODS: tuple[tuple[str, str | None], ...] = (
    ("24h", "24h"), ("7j", "7d"), ("30j", "30d"), ("Tout", None),
)
_BAR_WIDTH = 40
_LABEL_WIDTH = 39
"""Largeur maximale des libelles des classements (ajustee au plus long) : une IPv6 complete (39
caracteres) tient sans coupure."""
_PERIOD_LABELS: dict[str | None, str] = {
    "24h": N_("24 dernières heures"), "7d": N_("7 derniers jours"), "30d": N_("30 derniers jours"),
}
"""Traduits a l'affichage (l'export peut etre dans une autre langue que l'interface)."""


def _format_bytes(size: float) -> str:
    for unit, factor in ((_("Go"), 1024 ** 3), (_("Mo"), 1024 ** 2), (_("Ko"), 1024)):
        if size >= factor:
            return f"{size / factor:.1f} {unit}"
    return f"{int(size)} o"


def _export_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


class AccessLogStatsScreen(LibrarySelectionMixin, OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._entries: list = []
        self._result: AccessLogStatsResult | None = None
        self._elevated = False
        self._computing = False

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static(_("STATISTIQUES"), classes="omega-title")
            yield LogLibraryTable(id="library-table")
            yield Input(placeholder=_("Numéros séparés par des virgules (ex: 1,2)"), id="selection-input")
            yield Static(SELECTION_HINT, classes="omega-hint")
            with Horizontal(classes="omega-actions"):
                for label, period in _PERIODS:
                    with Container(classes="omega-btn-frame"):
                        yield Button(_(PERIOD_BUTTON_LABELS[label]), id=f"period-{label}")
            yield Static(PERIOD_HINT, classes="omega-hint")
            yield Static("", id="selection-size", classes="omega-hint")
            yield BusyIndicator(id="busy")

            yield Static("", id="stats-summary")
            yield Static("", id="stats-hourly")

            # Theme seul sur sa ligne, boutons en dessous a gauche (retour utilisateur 2026-11-06).
            yield Static(_("Thème d'export HTML"), classes="omega-subtitle")
            yield Select([(name, name) for name in EXPORT_PALETTES], value=DEFAULT_EXPORT_THEME, allow_blank=False,
                         id="theme-select")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Exporter JSON"), id="export-json")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Exporter HTML"), id="export-html")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        self._entries = list_library(self._container.log_repository)
        self.query_one("#library-table", LogLibraryTable).load(self._entries)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "selection-input":
            self._refresh_selection_size()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == "library-table":
            self._refresh_selection_size()

    def _refresh_selection_size(self) -> None:
        """Taille et nombre de lignes estime de la selection, affiches AVANT le calcul (2026-11-06)."""
        raw = self._library_selection()
        tokens = [token.strip() for token in raw.split(",") if token.strip()]
        paths = [self._entries[int(t) - 1].path for t in tokens if t.isdigit() and 1 <= int(t) <= len(self._entries)]
        description = describe_selection(paths)
        self.query_one("#selection-size", Static).update(_("Sélection : {description}").format(description=description) if description else "")

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
        runner = self._container.process_runner if self._elevated else None
        self._computing = True
        self._set_period_buttons_disabled(True)
        self.query_one("#busy", BusyIndicator).start(paths, period)
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
        try:
            self.query_one("#busy", BusyIndicator).stop()
        except NoMatches:
            pass  # ecran deja ferme

    async def _compute_async(
        self, paths: list[str], period: str | None, runner: ProcessRunnerPort | None,
    ) -> None:
        try:
            self.query_one("#stats-summary", Static).update("")
            self.query_one("#stats-hourly", Static).update("")
        except NoMatches:
            self._finish_computing()
            return  # ecran deja ferme avant meme le lancement du calcul (improbable mais gratuit a couvrir)

        try:
            accumulator = await accumulate_in_pool(paths, period, runner, self._show_progress)
        except PermissionRequiredError:
            if not request_elevation(self, self._container.process_runner):
                self.app.notify(_("Permission refusée sur au moins un log sélectionné."), severity="error")
                self._clear_summary()
                self._finish_computing()
                return
            self._elevated = True
            try:
                accumulator = await accumulate_in_pool(
                    paths, period, self._container.process_runner, self._show_progress,
                )
            except Exception as exc:  # noqa: BLE001 - jamais planter l'appli pour un calcul de stats
                self._show_compute_error(str(exc))
                return
        except Exception as exc:  # noqa: BLE001 - jamais planter l'appli pour un calcul de stats
            self._show_compute_error(str(exc))
            return

        result = AccessLogStatsResult(sources=paths, period=period, report=accumulator.to_report())
        self._apply_result(paths, period, result)

    def _show_progress(self, done_bytes: int, total_bytes: int, done_parts: int, total_parts: int) -> None:
        try:
            self.query_one("#busy", BusyIndicator).set_progress(done_bytes, total_bytes, done_parts, total_parts)
        except NoMatches:
            pass  # ecran deja ferme

    def _clear_summary(self) -> None:
        try:
            self.query_one("#stats-summary", Static).update("")
        except NoMatches:
            pass  # ecran deja ferme (utilisateur reparti avant la fin du calcul) — rien a mettre a jour

    def _show_compute_error(self, message: str) -> None:
        self.app.notify(_("Erreur de calcul : {message}").format(message=message), severity="error")
        self._finish_computing()
        try:
            self.query_one("#stats-summary", Static).update(_("Erreur de calcul : {message}").format(message=message))
        except NoMatches:
            pass  # ecran deja ferme (utilisateur reparti avant la fin du calcul) — rien a mettre a jour

    def _apply_result(self, paths: list[str], period: str | None, result: AccessLogStatsResult) -> None:
        self._finish_computing()
        self._result = result

        try:
            summary_widget = self.query_one("#stats-summary", Static)
            hourly_widget = self.query_one("#stats-hourly", Static)
        except NoMatches:
            return  # ecran deja ferme (utilisateur reparti avant la fin du calcul) — rien a mettre a jour

        colors = self._colors()
        summary_widget.update(self._summary_text(result, len(paths), colors))
        hourly_widget.update(self._time_text(result.report, colors))

    def _colors(self) -> dict[str, str]:
        variables = self.app.get_css_variables()
        return {
            "heading": f"bold {variables.get('secondary', '')}".strip(),
            "bar": variables.get("accent", "cyan") or "cyan",
            "peak": variables.get("error", "red") or "red",
            "good": variables.get("success", "green") or "green",
            "warn": variables.get("warning", "yellow") or "yellow",
            "bad": variables.get("error", "red") or "red",
            "info": variables.get("secondary", "cyan") or "cyan",
        }

    def _summary_text(self, result: AccessLogStatsResult, log_count: int, colors: dict[str, str]) -> Text:
        """Synthese, statuts HTTP et classements (2026-11-06, presentation du rapport d'omega-fire)."""
        report = result.report
        content = Text()
        period_label = _(_PERIOD_LABELS.get(result.period, N_("tout le fichier")))
        content.append(_("── SYNTHÈSE — {period_label}, {log_count} log(s) ──\n").format(period_label=period_label, log_count=log_count), style=colors["heading"])
        if report.total == 0:
            content.append(_(" Aucune ligne sur cette période.\n"))
            return content
        rate_style = colors["good"] if report.error_rate < 5 else (colors["warn"] if report.error_rate < 15 else colors["bad"])
        volume = "-" if report.bytes_total is None else _format_bytes(report.bytes_total)
        covered = "-" if report.first_day is None else f"{report.first_day} → {report.last_day}"
        content.append(_(" Lignes analysées   : {total}\n").format(total=report.total))
        content.append(_(" Requêtes HTTP      : {http_total}\n").format(http_total=report.http_total))
        content.append(_(" IPs uniques        : {unique_ips}\n").format(unique_ips=report.unique_ips))
        content.append(_(" Taux d'erreur      : {error_rate:.1f} %\n").format(error_rate=report.error_rate), style=rate_style)
        content.append(_(" Volume transféré   : {volume}\n").format(volume=volume))
        content.append(_(" Heure de pointe    : {peak_hour:02d}h ({peak_count} lignes)\n").format(peak_hour=report.peak_hour, peak_count=report.peak_count), style=colors["info"])
        content.append(_(" Période couverte   : {covered}\n\n").format(covered=covered))

        if report.statuses:
            content.append(_("── STATUTS HTTP ──\n"), style=colors["heading"])
            status_styles = {"2xx": colors["good"], "3xx": colors["info"], "4xx": colors["warn"], "5xx": colors["bad"],
                             "403": colors["warn"], "429": colors["warn"]}
            labels = {name: _("Refus {name}").format(name=name) if name in ("403", "429") else name
                      for name in report.statuses}
            # Largeur du plus long libelle (« Abgewiesen 403 » en allemand), jamais coupe a 10 colonnes.
            label_width = min(_LABEL_WIDTH, max(10, *(cell_len(label) for label in labels.values())))
            for name, count in report.statuses.items():
                share = count / report.http_total * 100 if report.http_total else 0
                append_gauge_line(content, labels[name], count, report.http_total, label_width=label_width,
                                  bar_width=_BAR_WIDTH, style=status_styles[name], suffix=f"  {share:5.1f} %")
            content.append("\n")

        self._append_ranking(content, _("TOP IP"), report.top_ips, colors["bar"], colors)
        if report.top_paths:
            self._append_ranking(content, _("CHEMINS DEMANDÉS"), report.top_paths, colors["bar"], colors)
            self._append_ranking(content, _("CHEMINS EN 404"), report.top_not_found, colors["warn"], colors)
        return content

    def _append_ranking(self, content: Text, title: str, items: list[RankedItem], style: str,
                        colors: dict[str, str]) -> None:
        content.append(f"── {title} ──\n", style=colors["heading"])
        if not items:
            content.append("  " + _("(aucun)") + "\n\n", style="dim")
            return
        maximum = items[0].count
        label_width = min(_LABEL_WIDTH, max(cell_len(item.value) for item in items))
        for item in items:
            suffix = "  " + _("dont {errors} en erreur").format(errors=item.errors) if item.errors else ""
            append_gauge_line(content, item.value, item.count, maximum, label_width=label_width,
                              bar_width=_BAR_WIDTH // 2, style=style, suffix=suffix)
        content.append("\n")

    def _time_text(self, report: StatsReport, colors: dict[str, str]) -> Text:
        """Repartition horaire (24 jauges, heure de pointe en couleur d'alerte) puis tendance par jour."""
        content = Text()
        if report.total == 0:
            return content
        content.append(_("── RÉPARTITION HORAIRE (24 h) ──\n"), style=colors["heading"])
        maximum = max(report.hourly)
        for hour, count in enumerate(report.hourly):
            style = colors["peak"] if count == maximum and count > 0 else colors["bar"]
            append_gauge_line(content, f"{hour:02d}h", count, maximum, label_width=4, bar_width=_BAR_WIDTH, style=style)
        content.append("\n")
        content.append(_("── TENDANCE PAR JOUR ({count} j) ──\n").format(count=len(report.daily)), style=colors["heading"])
        maximum_day = max((count for _day, count in report.daily), default=0)
        for day, count in report.daily:
            append_gauge_line(content, day, count, maximum_day, label_width=10, bar_width=_BAR_WIDTH, style=colors["bar"])
        return content

    def _export_json(self) -> None:
        if self._result is None:
            self.app.notify(_("Calculez d'abord les statistiques (choisissez une période)."), severity="warning")
            return
        import json

        payload = {
            "sources": self._result.sources,
            "period": self._result.period,
            **asdict(self._result.report),
        }
        export_dir = self._container.default_exports_dir
        export_dir.mkdir(parents=True, exist_ok=True)
        out_path = export_dir / f"stats-{_export_timestamp()}.json"
        out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        self.app.notify(_("Export JSON : {out_path}").format(out_path=out_path))

    def _export_html(self) -> None:
        if self._result is None:
            self.app.notify(_("Calculez d'abord les statistiques (choisissez une période)."), severity="warning")
            return
        report = self._result.report
        theme_name = self.query_one("#theme-select", Select).value
        with translating_as(LANGUAGE.export_state(self._container.settings_store)):
            html = export_access_log_stats_html(
                sources=self._result.sources,
                period_label=_(_PERIOD_LABELS.get(self._result.period, N_("tout le fichier"))),
                report=asdict(report),
                volume="-" if report.bytes_total is None else _format_bytes(report.bytes_total),
                theme_name=str(theme_name),
            )
        export_dir = self._container.default_exports_dir
        export_dir.mkdir(parents=True, exist_ok=True)
        out_path = export_dir / f"stats-{_export_timestamp()}.html"
        out_path.write_text(html, encoding="utf-8")
        self.app.notify(_("Export HTML : {out_path}").format(out_path=out_path))
