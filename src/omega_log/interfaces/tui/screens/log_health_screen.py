# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Ecran Sante des logs (menu MAINTENANCE, apres Exporter) - porte d'omega-serv 2.6.0 le 2026-11-07
(interfaces/tui/screens/log_health_screen.py), OMEGA-LOG_PLAN_PORTAGE_SERV.md portage n°2 lot 5.

Controle en lecture seule des logs de la Bibliotheque, du disque qui les porte, des sauvegardes d'omega-log et
des sauvegardes planifiees (regles : domain/logs/health.py ; collecte : application/use_cases/log_health.py).
Une ligne par log (OK, Info, Attention, Probleme) ; la ligne surlignee montre tous ses constats et ce qu'on peut
faire.

Seule correction (toujours apres confirmation) : un log inscriptible par tout le monde - « Corriger les droits »
(`chmod o-w`, sans sudo, si le fichier vous appartient) ou « Corriger avec sudo » (meme commande, montree
avant). « Analyser avec sudo » complete les dates et le format des logs illisibles par votre compte. Export JSON
(donnees), HTML (5 themes) et TXT, dans la langue des exports.

La collecte tourne dans un thread : elle ne lit que le debut et la fin de chaque log."""
from __future__ import annotations

import getpass
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from omega_lib.theme.policies import DEFAULT_EXPORT_THEME, EXPORT_PALETTES
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.css.query import NoMatches
from textual.widgets import Button, DataTable, Footer, Header, Select, Static

from omega_log.application.use_cases.health_presentation import (
    archives_line,
    automations_line,
    disk_line,
    finding_hint,
    finding_text,
    format_age,
    format_bytes,
    html_arguments,
    level_label,
    log_facts_line,
    log_summary,
    origin_label,
    render_text,
    report_to_dict,
)
from omega_log.application.use_cases.library import list_library
from omega_log.application.use_cases.log_health import (
    archive_facts,
    collect_log_health,
    fix_world_writable,
    health_paths,
    owns,
    run_sudo_fix,
    shown_command,
    sudo_fix_command,
)
from omega_log.application.use_cases.rotation_automation import rotation_schedule_status
from omega_log.domain.logs.health import evaluate_automations
from omega_log.infrastructure.exporters.html_exporter import export_log_health_html
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens._elevation import request_elevation
from omega_log.interfaces.tui.screens.confirm import ConfirmScreen
from omega_log.shared.i18n import LANGUAGE, _, translating_as

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer
    from omega_log.ports.process_runner_port import ProcessRunnerPort


def _export_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def _world_writable(log: dict) -> bool:
    return any(finding["code"] == "world_writable" for finding in log["findings"])


class LogHealthScreen(OmegaScreen):
    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._data: dict | None = None
        self._analysing = False
        self._runner: ProcessRunnerPort | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static(_("SANTÉ DES LOGS"), classes="omega-title")
            yield Static(_("Contrôle en lecture seule des logs de la Bibliothèque, du disque qui les porte, des "
                           "sauvegardes et des sauvegardes planifiées. Surlignez un log pour voir le détail."),
                         classes="omega-hint")
            yield Static("", id="health-status", classes="omega-hint")
            yield Static("", id="health-summary")
            yield DataTable(id="health-table")
            yield Static("", id="health-detail")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Relancer l'analyse"), id="refresh", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Analyser avec sudo"), id="analyse-sudo", disabled=True)
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Corriger les droits"), id="fix", disabled=True)
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Corriger avec sudo"), id="fix-sudo", disabled=True)
            yield Static(_("DISQUES"), classes="omega-subtitle")
            yield Static("", id="health-disks")
            yield Static(_("SAUVEGARDES"), classes="omega-subtitle")
            yield Static("", id="health-archives")
            yield Static(_("SAUVEGARDES PLANIFIÉES"), classes="omega-subtitle")
            yield Static("", id="health-automations")

            yield Static(_("Thème d'export HTML"), classes="omega-subtitle")
            yield Select([(name, name) for name in EXPORT_PALETTES], value=DEFAULT_EXPORT_THEME, allow_blank=False,
                         id="theme-select")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Exporter JSON"), id="export-json")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Exporter HTML"), id="export-html")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Exporter TXT"), id="export-txt")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#health-table", DataTable)
        table.cursor_type = "row"
        table.add_columns(_("État"), _("Log"), _("Taille"), _("Modifié"), _("Constat"))
        self._analyse()

    # ---- analyse -----------------------------------------------------------

    def _analyse(self) -> None:
        if self._analysing:
            return
        self._analysing = True
        self.query_one("#refresh", Button).disabled = True
        self.query_one("#health-status", Static).update(_("Analyse en cours…"))
        runner = self._runner
        self.run_worker(lambda: self._collect(runner), thread=True, group="log-health")

    def _analyse_with_sudo(self) -> None:
        if request_elevation(self, self._container.process_runner):
            self._runner = self._container.process_runner
            self._analyse()

    def _collect(self, runner: ProcessRunnerPort | None) -> None:
        container = self._container
        try:
            library = list_library(container.log_repository)
            backups = container.persistence_port.list_backups(container.backup_dir)
            automations = container.rotation_automation_store.list_all()
            report = collect_log_health(
                health_paths(library),
                archives=archive_facts(container.backup_dir, [(b.size_bytes, b.created_at) for b in backups]),
                automations=evaluate_automations(
                    automations, self._schedule_installed(bool(automations)), datetime.now(timezone.utc)),
                privileged_runner=runner,
            )
            data = report_to_dict(report)
        except Exception as exc:  # noqa: BLE001 - jamais planter l'interface pour un controle
            self.app.call_from_thread(self._show_error, str(exc))
            return
        self.app.call_from_thread(self._apply, data)

    def _schedule_installed(self, has_automations: bool) -> bool | None:
        """Tache planifiee des sauvegardes presente ? None si rien a verifier ou pas de planificateur."""
        if not has_automations:
            return None
        status = rotation_schedule_status(getpass.getuser(), self._container.process_runner)
        return None if status.mechanism == "manual" else status.success

    def _finish(self) -> None:
        self._analysing = False
        try:
            self.query_one("#refresh", Button).disabled = False
        except NoMatches:
            pass  # ecran deja ferme

    def _show_error(self, message: str) -> None:
        self._finish()
        try:
            self.query_one("#health-status", Static).update(_("Erreur : {message}").format(message=message))
        except NoMatches:
            pass  # ecran deja ferme

    def _styles(self) -> dict[str, str]:
        variables = self.app.get_css_variables()
        return {
            "ok": variables.get("success", "green") or "green",
            "info": variables.get("secondary", "cyan") or "cyan",
            "warning": variables.get("warning", "yellow") or "yellow",
            "problem": f"bold {variables.get('error', 'red') or 'red'}",
        }

    def _apply(self, data: dict) -> None:
        self._finish()
        self._data = data
        try:
            table = self.query_one("#health-table", DataTable)
        except NoMatches:
            return  # ecran deja ferme
        styles = self._styles()
        now = datetime.fromisoformat(data["generated_at"])
        self.query_one("#health-status", Static).update(_("Analysé {age}.").format(
            age=format_age(data["generated_at"], datetime.now(timezone.utc))))
        summary = Text()
        summary.append(_("Résumé : "), style="bold")
        for index, code in enumerate(("ok", "info", "warning", "problem")):
            count = data["counts"][code]
            summary.append(" · " if index else "")
            summary.append(f"{count} {level_label(code)}", style=styles[code] if count else "dim")
        self.query_one("#health-summary", Static).update(summary)

        cursor = table.cursor_row
        table.clear()
        for log in data["logs"]:
            size = "-" if log["size_bytes"] is None else format_bytes(float(log["size_bytes"]))
            table.add_row(
                Text(level_label(log["level"]), style=styles[log["level"]]),
                log["path"], size, format_age(log["modified_at"], now), log_summary(log),
            )
        if data["logs"]:
            table.move_cursor(row=min(cursor, len(data["logs"]) - 1))
        unreadable = any(f["code"] == "unreadable" for log in data["logs"] for f in log["findings"])
        self.query_one("#analyse-sudo", Button).disabled = not unreadable or self._runner is not None
        self._show_detail(table.cursor_row)

        disks = Text()
        for disk in data["disks"]:
            disks.append(f"[{level_label(disk['level'])}] ", style=styles[disk["level"]])
            disks.append(disk_line(disk) + "\n")
            for finding in disk["findings"]:
                self._append_finding(disks, finding, disk["mount_point"], styles)
        self.query_one("#health-disks", Static).update(disks if data["disks"] else "-")
        archives = data["archives"]
        self.query_one("#health-archives", Static).update("-" if archives is None else archives_line(archives))
        automations_text = Text()
        if data.get("automations") is not None:
            automations_text.append(f"[{level_label(data['automations']['level'])}] ",
                                    style=styles[data["automations"]["level"]])
            automations_text.append(automations_line(data["automations"]) + "\n")
            for finding in data["automations"]["findings"]:
                self._append_finding(automations_text, finding, "", styles)
        self.query_one("#health-automations", Static).update(automations_text)

    def _append_finding(self, content: Text, finding: dict, path: str, styles: dict[str, str]) -> None:
        content.append("  ● ", style=styles[finding["level"]])
        content.append(finding_text(finding) + "\n")
        hint = finding_hint(finding, path)
        if hint:
            content.append(f"    → {hint}\n", style="dim")

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == "health-table":
            self._show_detail(event.cursor_row)

    def _selected_log(self, row: int | None = None) -> dict | None:
        if self._data is None or not self._data["logs"]:
            return None
        index = self.query_one("#health-table", DataTable).cursor_row if row is None else row
        return self._data["logs"][index] if 0 <= index < len(self._data["logs"]) else None

    def _show_detail(self, row: int) -> None:
        log = self._selected_log(row)
        fix_button = self.query_one("#fix", Button)
        sudo_button = self.query_one("#fix-sudo", Button)
        if log is None or self._data is None:
            self.query_one("#health-detail", Static).update("")
            fix_button.disabled = sudo_button.disabled = True
            return
        styles = self._styles()
        content = Text()
        content.append(f"\n{log['path']}\n", style="bold")
        content.append(origin_label(log) + "\n", style="dim")
        facts = log_facts_line(log, datetime.fromisoformat(self._data["generated_at"]))
        if facts:
            content.append(facts + "\n", style="dim")
        if not log["findings"]:
            content.append("  ● ", style=styles["ok"])
            content.append(_("Aucun problème.") + "\n")
        for finding in log["findings"]:
            self._append_finding(content, finding, log["path"], styles)
        self.query_one("#health-detail", Static).update(content)
        writable = _world_writable(log)
        fix_button.disabled = not (writable and owns(log["path"]))
        sudo_button.disabled = not (writable and not owns(log["path"]))

    # ---- correction des droits ---------------------------------------------

    def _fix_selected(self) -> None:
        log = self._selected_log()
        if log is None or not _world_writable(log):
            return
        path = log["path"]
        self.app.push_screen(
            ConfirmScreen(
                title=_("CORRIGER LES DROITS ?"),
                message=_("{path} : retirer l'écriture pour tout le monde (droits {mode}).").format(
                    path=path, mode=log["mode"]),
            ),
            lambda confirmed: self._fix_if_confirmed(confirmed, path),
        )

    def _fix_if_confirmed(self, confirmed: bool | None, path: str) -> None:
        if not confirmed:
            return
        try:
            fix_world_writable(path)
        except OSError as exc:
            self.app.notify(_("Correction impossible : {error}").format(error=exc), severity="error")
            return
        self.app.notify(_("Droits corrigés : {path}.").format(path=path))
        self._analyse()

    def _fix_with_sudo(self) -> None:
        log = self._selected_log()
        if log is None or not _world_writable(log):
            return
        path = log["path"]
        command = sudo_fix_command(path)
        self.app.push_screen(
            ConfirmScreen(
                title=_("CORRIGER AVEC SUDO ?"),
                message=_("Commande lancée après votre mot de passe :\n{command}").format(command=shown_command(command)),
            ),
            lambda confirmed: self._fix_with_sudo_if_confirmed(confirmed, path, command),
        )

    def _fix_with_sudo_if_confirmed(self, confirmed: bool | None, path: str, command: list[str]) -> None:
        if not confirmed:
            return
        runner = self._container.process_runner
        if not request_elevation(self, runner):  # sans mot de passe si sudo est encore valide
            return
        self._runner = runner
        error = run_sudo_fix(runner, command)
        if error is not None:
            self.app.notify(_("Correction impossible : {error}").format(error=error), severity="error")
            return
        self.app.notify(_("Droits corrigés avec sudo : {path}.").format(path=path))
        self._analyse()

    # ---- boutons et exports ------------------------------------------------

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id == "back":
            self.dismiss()
        elif button_id == "refresh":
            self._analyse()
        elif button_id == "fix":
            self._fix_selected()
        elif button_id == "fix-sudo":
            self._fix_with_sudo()
        elif button_id == "analyse-sudo":
            self._analyse_with_sudo()
        elif button_id == "export-json":
            self._export("json")
        elif button_id == "export-html":
            self._export("html")
        elif button_id == "export-txt":
            self._export("txt")

    def _export(self, extension: str) -> None:
        data = self._data
        if data is None:
            self.app.notify(_("Attendez la fin de l'analyse."), severity="warning")
            return
        if extension == "json":
            content = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            theme_name = str(self.query_one("#theme-select", Select).value)
            with translating_as(LANGUAGE.export_state(self._container.settings_store)):
                content = (export_log_health_html(theme_name=theme_name, **html_arguments(data))
                           if extension == "html" else render_text(data))
        export_dir: Path = self._container.default_exports_dir
        export_dir.mkdir(parents=True, exist_ok=True)
        out_path = export_dir / f"log-health-{_export_timestamp()}.{extension}"
        out_path.write_text(content, encoding="utf-8")
        self.app.notify(_("Export écrit : {export_path}").format(export_path=out_path))
