# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Sauvegardes planifiees (ouvert depuis Rotate) - porte d'omega-serv 2.6.0 le 2026-11-07
(log_rotation_screen.py, modes « Configurer » et « Gerer les automatisations »), decision utilisateur :
« oui, comme omega-serv ».

Un log de la Bibliotheque, une frequence (tous les 1, 7 ou 30 jours) et un nombre de sauvegardes conservees.
La premiere automatisation installe la tache quotidienne (timer systemd : mot de passe sudo demande ; sinon
ligne de votre crontab), la derniere supprimee la retire. « Desinstaller l'execution » la retire a la demande
(2026-11-07) sans effacer les automatisations ; « Reinstaller l'execution » la remet. Chaque nuit, `omega-log rotate run-automations`
sauvegarde, sous votre compte, chaque log arrive a echeance."""
from __future__ import annotations

import getpass
import sys
from datetime import datetime
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Select, Static

from omega_log.application.use_cases.library import list_library
from omega_log.application.use_cases.rotation_automation import (
    ScheduleResult,
    install_rotation_schedule,
    remove_rotation_schedule,
    rotation_schedule_status,
    uses_systemd,
)
from omega_log.domain.logs.rotation_schedule import FREQUENCY_DAYS, next_run
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens._elevation import request_elevation
from omega_log.interfaces.tui.screens.confirm import ConfirmScreen
from omega_log.interfaces.tui.widgets.library_selection import (
    SINGLE_SELECTION_HINT,
    LibrarySelectionMixin,
)
from omega_log.interfaces.tui.widgets.log_library_table import LogLibraryTable
from omega_log.shared.i18n import _

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer
    from omega_log.domain.entities.log_file import LogFile


def _frequency_label(days: int) -> str:
    return {1: _("Tous les jours"), 7: _("Toutes les semaines"), 30: _("Tous les mois")}.get(
        days, _("Tous les {days} jours").format(days=days))


def _date(value: object) -> str:
    try:
        return datetime.fromisoformat(str(value)).strftime("%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        return "-"


class RotationAutomationsScreen(LibrarySelectionMixin, OmegaScreen):
    SINGLE_LIBRARY_SELECTION = True

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._entries: list[LogFile] = []
        self._selected_automation: int | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static(_("SAUVEGARDES PLANIFIÉES"), classes="omega-title")
            yield Static(_("Chaque nuit, omega-log sauvegarde, sous votre compte, chaque log arrivé à échéance "
                           "(comme « Sauvegarder maintenant »). Un log protégé (/var/log/...) ne peut pas être "
                           "sauvegardé la nuit sans mot de passe : faites-le depuis Rotate."), classes="omega-hint")
            yield LogLibraryTable(id="library-table")
            yield Input(placeholder=_("Numéro du log à planifier (ex: 1)"), id="selection-input")
            yield Static(SINGLE_SELECTION_HINT, classes="omega-hint")
            with Horizontal(classes="omega-actions"):
                yield Select([(_frequency_label(days), days) for days in FREQUENCY_DAYS], value=7,
                             allow_blank=False, id="frequency-select")
                yield Input(placeholder=_("Rotations à conserver"), value="7", id="keep-input")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Planifier ce log"), id="add-automation", variant="primary")

            yield Static(_("Automatisations planifiées"), classes="omega-subtitle")
            yield Static("", id="schedule-status", classes="omega-hint")
            yield DataTable(id="automations-table")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Supprimer la sélection"), id="delete-automation", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Réinstaller l'exécution"), id="install-schedule")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Désinstaller l'exécution"), id="uninstall-schedule", variant="error")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        self._entries = list_library(self._container.log_repository)
        self.query_one("#library-table", LogLibraryTable).load(self._entries)
        table = self.query_one("#automations-table", DataTable)
        table.cursor_type = "row"
        table.add_columns(_("Log"), _("Fréquence"), _("Conservées"), _("Dernière exécution"), _("Prochaine"))
        self._refresh()

    def _refresh(self) -> None:
        automations = self._container.rotation_automation_store.list_all()
        table = self.query_one("#automations-table", DataTable)
        table.clear()
        for index, item in enumerate(automations):
            due = next_run(item)
            last = _date(item.get("last_run_at"))
            if item.get("last_success") is False:
                last = _("échec : {error}").format(error=item.get("last_result", ""))
            table.add_row(str(item.get("path", "")), _frequency_label(int(str(item.get("days_interval", 0)))),
                          str(item.get("keep", 7)), last, "-" if due is None else due.strftime("%Y-%m-%d"),
                          key=str(index))
        self._selected_automation = None
        status = rotation_schedule_status(getpass.getuser(), self._container.process_runner)
        hint = "" if status.success or not automations else " " + _("Utilisez « Réinstaller l'exécution ».")
        self.query_one("#schedule-status", Static).update(status.message + hint)

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == "automations-table" and event.row_key is not None:
            self._selected_automation = int(str(event.row_key.value))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back":
            self.dismiss()
        elif button_id == "add-automation":
            self._add()
        elif button_id == "delete-automation":
            self._delete()
        elif button_id == "install-schedule":
            self._apply_schedule(install=True)
            self._refresh()
        elif button_id == "uninstall-schedule":
            self._uninstall()

    def _apply_schedule(self, install: bool) -> ScheduleResult | None:
        """systemd : authentification sudo d'abord (ecran suspendu), puis commandes `sudo -n`."""
        runner = self._container.process_runner
        if uses_systemd() and not request_elevation(self, runner):
            return None
        user = getpass.getuser()
        if install:
            result = install_rotation_schedule(user, self._container.var_dir, sys.executable, runner)
        else:
            result = remove_rotation_schedule(user, runner)
        if result.message:
            self.app.notify(result.message, severity="information" if result.success else "warning", timeout=12)
        return result

    def _uninstall(self) -> None:
        """Retire la tache planifiee (timer systemd ou ligne crontab) sans toucher aux automatisations
        (demande utilisateur 2026-11-07) : elles restent listees et « Reinstaller l'execution » les relance."""
        self.app.push_screen(
            ConfirmScreen(title=_("DÉSINSTALLER L'EXÉCUTION ?"),
                          message=_("La tâche planifiée (timer systemd ou ligne crontab) est retirée. Vos sauvegardes "
                                    "planifiées restent enregistrées mais ne s'exécutent plus, jusqu'à « Réinstaller "
                                    "l'exécution ».")),
            self._uninstall_if_confirmed,
        )

    def _uninstall_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed:
            return
        result = self._apply_schedule(install=False)
        if result is not None and result.success and not result.message:
            self.app.notify(_("Aucune tâche planifiée à retirer."))
        self._refresh()

    def _add(self) -> None:
        raw = self._library_selection()
        if not raw.isdigit() or not (1 <= int(raw) <= len(self._entries)):
            self.app.notify(_("Numéro de log invalide."), severity="warning")
            return
        path = self._entries[int(raw) - 1].path
        keep_raw = self.query_one("#keep-input", Input).value.strip()
        keep = int(keep_raw) if keep_raw.isdigit() and int(keep_raw) >= 1 else 7
        days = int(str(self.query_one("#frequency-select", Select).value))
        store = self._container.rotation_automation_store
        if any(str(item.get("path")) == path for item in store.list_all()):
            self.app.notify(_("Ce log a déjà une sauvegarde planifiée : supprimez-la d'abord."), severity="warning")
            return
        first = not store.list_all()
        store.add({"path": path, "days_interval": days, "keep": keep,
                   "created_at": datetime.now().astimezone().isoformat()})
        self.app.notify(_("Sauvegarde planifiée : {path} ({frequency}).").format(
            path=path, frequency=_frequency_label(days)))
        if first:
            self._apply_schedule(install=True)
        self._refresh()

    def _delete(self) -> None:
        if self._selected_automation is None:
            self.app.notify(_("Sélectionnez une automatisation."), severity="warning")
            return
        index = self._selected_automation
        self.app.push_screen(
            ConfirmScreen(title=_("SUPPRIMER CETTE AUTOMATISATION ?"),
                          message=_("Le log ne sera plus sauvegardé automatiquement. Les sauvegardes déjà "
                                    "faites sont conservées.")),
            lambda confirmed: self._delete_if_confirmed(confirmed, index),
        )

    def _delete_if_confirmed(self, confirmed: bool | None, index: int) -> None:
        if not confirmed:
            return
        store = self._container.rotation_automation_store
        if store.delete(index) and not store.list_all():
            self._apply_schedule(install=False)
        self._refresh()
