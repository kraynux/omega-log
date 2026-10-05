# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Viewer 1 (SIMPLE) — tail -f + etat/stats, plan_omega_log.md §2.

ADAPTE depuis omega-fire/interfaces/tui/screens/live_tail_screen.py, PAS
porte verbatim : la version source y encapsule un `_LogProvider` qui
presume un format HTTP (method/path/status_code/bytes_sent/latence),
y compris dans sa branche "heuristique" — correct pour un access log,
trompeur pour tout le reste (auth.log, syslog, fail2ban, samba...) que
LOG doit aussi savoir afficher. Remplace par domain/logs/parser.py +
analytics.py (deja generiques, construits en Phase 2, DESTINATION
documentee depuis l'origine dans leurs propres commentaires "comment il
sera utilise" chez omega-fire — jamais branches par omega-fire lui-meme
sous cette forme). Le mecanisme de lecture incrementale (offset tracking
via LiveTailPort) reste, lui, directement reutilisable.

Elevation sudo ponctuelle (plan §5.1, 2026-10-03) AJOUTEE dans `_poll`
sur `PermissionError` specifiquement, meme principe que Viewer 2
(log_viewer_screen.py) : authentification une seule fois, puis bascule
definitive sur `read_new_lines_privileged` pour le reste du suivi.

`_load_initial` AJOUTE (2026-10-04, retour utilisateur : "le lecteur
simple ne fonctionne pas, il importe rien et le tableau a cote n'affiche
aucune donnees juste quelque titre") : bug reel, pas un ressenti —
`LiveTailReader.__init__` positionne son offset sur la FIN du fichier
(`path.stat().st_size`), donc `read_new_lines()` ne renvoie jamais que
les lignes ecrites APRES l'ouverture de l'ecran. Sans lecture initiale
separee, un fichier qui n'est pas activement en train de recevoir de
nouvelles lignes au moment ou l'ecran s'ouvre reste indefiniment vide a
l'affichage — exactement le symptome rapporte. Viewer 2
(log_viewer_screen.py) faisait deja cette lecture initiale depuis
Phase 4 ; Viewer 1 ne l'a jamais eue, oubli de portage, pas un choix
delibere.

Colonnes "Code"/"Timeout" + section stats "STATUTS HTTP" RETABLIES
(2026-10-04, retour utilisateur : "tu as modifie et enleve des elements,
il faut reprendre la meme chose que omega-fire") : la genericite
multi-format reste intacte (domain/logs/parser.py::extract_http_fields
retourne None pour tout ce qui n'est pas une ligne Combined/Common —
auth.log/syslog/fail2ban restent affiches exactement comme avant, "Code"/
"Timeout" valent alors "-"), mais le code HTTP et une latence
simplifiee (quand le format source la fournit) redeviennent visibles
pour un access log, colores comme chez omega-fire (2xx/3xx disponible,
4xx avertissement, 5xx danger) — jamais le tableau de bord HTTP complet
de la source (debit, bande passante, detection bot/CLI, tout ca restant
hors-sujet pour un outil multi-format)."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.timer import Timer
from textual.widgets import Button, DataTable, Footer, Header, Static

from omega_log.domain.logs.analytics import compute_stats
from omega_log.domain.logs.models import LogEntry
from omega_log.domain.logs.parser import parse_log_line
from omega_log.infrastructure.privileged.privileged_file_ops import read_file_privileged
from omega_log.infrastructure.tail.live_tail_reader import LiveTailReader
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens._elevation import request_elevation

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer

_REFRESH_SECONDS = 2.0
_VISIBLE_ROWS = 30
_BUFFER_SIZE = 500
_INITIAL_LINES = 200


class LiveTailScreen(OmegaScreen):
    """Viewer 1 : suit un fichier en direct, affiche les dernieres lignes
    parsees + un petit tableau de stats generique (compute_stats)."""

    def __init__(self, *, container: DependencyContainer, path: str) -> None:
        super().__init__()
        self._container = container
        self._path = path
        self._reader = LiveTailReader(Path(path))
        self._buffer: list[LogEntry] = []
        self._line_number = 0
        self._timer: Timer | None = None
        self._elevated = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static(f"VOIR LES LOGS — SIMPLE — {self._path}", classes="omega-title")
            with Horizontal():
                yield Static(id="stats-box", classes="omega-dash-box")
                yield DataTable(id="entries-table")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#entries-table", DataTable).add_columns(
            "Heure", "Niveau", "Source", "IP", "Service", "Code", "Timeout", "Message"
        )
        self._load_initial()
        self._poll()
        self._timer = self.set_interval(_REFRESH_SECONDS, self._poll)

    def _load_initial(self) -> None:
        """Lecture ponctuelle des dernieres lignes DEJA presentes dans le
        fichier au moment de l'ouverture — l'offset de `self._reader`,
        lui, reste positionne sur la fin du fichier (construit dans
        __init__ AVANT cette lecture) : aucun doublon avec le premier
        `_poll()` qui suit."""
        path = Path(self._path)
        if not path.is_file():
            return

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except PermissionError:
            text = self._load_initial_privileged()
            if text is None:
                return
        except OSError:
            return

        for line in text.splitlines()[-_INITIAL_LINES:]:
            self._line_number += 1
            entry = parse_log_line(line, line_number=self._line_number, log_path=self._path)
            if entry is not None:
                self._buffer.append(entry)

    def _load_initial_privileged(self) -> str | None:
        if not request_elevation(self, self._container.process_runner):
            self.app.notify(f"Permission refusee sur {self._path}.", severity="error")
            return None
        result = read_file_privileged(self._container.process_runner, self._path)
        if not result.success:
            self.app.notify(f"Lecture privilegiee impossible : {result.message}", severity="error")
            return None
        self._elevated = True
        return result.content

    def action_back(self) -> None:
        self._stop()
        self.dismiss()

    def _stop(self) -> None:
        if self._timer is not None:
            self._timer.stop()
            self._timer = None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.action_back()

    def _poll(self) -> None:
        try:
            if self._elevated:
                new_lines = self._reader.read_new_lines_privileged(self._container.process_runner)
            else:
                new_lines = self._reader.read_new_lines()
        except PermissionError:
            if not request_elevation(self, self._container.process_runner):
                self.app.notify(f"Permission refusee sur {self._path}.", severity="error")
                self._stop()
                return
            self._elevated = True
            try:
                new_lines = self._reader.read_new_lines_privileged(self._container.process_runner)
            except OSError as exc:
                self.app.notify(f"Lecture privilegiee impossible : {exc}", severity="error")
                self._stop()
                return
        except OSError as exc:
            self.app.notify(f"Lecture impossible : {exc}", severity="error")
            self._stop()
            return

        for line in new_lines:
            self._line_number += 1
            entry = parse_log_line(line, line_number=self._line_number, log_path=self._path)
            if entry is not None:
                self._buffer.append(entry)
        if len(self._buffer) > _BUFFER_SIZE:
            self._buffer = self._buffer[-_BUFFER_SIZE:]

        self._render_stats()
        self._render_table()

    def _render_stats(self) -> None:
        stats = compute_stats(self._buffer, top_n=5)
        content = Text()
        content.append("── APERCU ──────────────\n", style="bold")
        content.append(f" Lignes tampon : {len(self._buffer)}\n")
        content.append(f" IPs uniques   : {stats.unique_ips}\n")
        content.append(f" Taux d'erreur : {stats.error_rate():.1f}%\n\n")

        statuses = [e.http_status for e in self._buffer if e.http_status is not None]
        if statuses:
            # Section n'apparait que si au moins une ligne du tampon est
            # reconnue comme un access log Combined/Common — jamais
            # affichee (vide/inutile) pour un tampon auth.log/syslog/....
            content.append("── STATUTS HTTP ─────────\n", style="bold")
            s2xx = sum(1 for s in statuses if 200 <= s < 300)
            s3xx = sum(1 for s in statuses if 300 <= s < 400)
            s4xx = sum(1 for s in statuses if 400 <= s < 500)
            s5xx = sum(1 for s in statuses if 500 <= s < 600)
            content.append(f" 2xx succes    : {s2xx}\n", style="green")
            content.append(f" 3xx redirect  : {s3xx}\n", style="cyan")
            content.append(f" 4xx client    : {s4xx}\n", style="yellow")
            content.append(f" 5xx serveur   : {s5xx}\n\n", style="red")

        content.append("── TOP IP ───────────────\n", style="bold")
        for top_ip in stats.top_ips[:5]:
            content.append(f" {top_ip.ip:<15} {top_ip.count}\n")
        self.query_one("#stats-box", Static).update(content)

    def _render_table(self) -> None:
        table = self.query_one("#entries-table", DataTable)
        table.clear()
        for entry in self._buffer[-_VISIBLE_ROWS:]:
            level_style = {
                "error": "red", "critical": "bold red", "warning": "yellow",
            }.get(entry.level.value, "")

            if entry.http_status is None:
                code_cell: Text | str = "-"
            else:
                status = entry.http_status
                if 200 <= status < 300:
                    status_style = "green"
                elif 300 <= status < 400:
                    status_style = "cyan"
                elif 400 <= status < 500:
                    status_style = "yellow"
                else:
                    status_style = "red"
                code_cell = Text(str(status), style=status_style)

            if entry.latency_ms is None:
                timeout_cell: Text | str = "-"
            else:
                latency = entry.latency_ms
                latency_style = "green" if latency < 200 else ("yellow" if latency < 500 else "red")
                timeout_cell = Text(f"{latency}ms", style=latency_style)

            table.add_row(
                entry.timestamp.strftime("%H:%M:%S"),
                Text(entry.level.value.upper(), style=level_style) if level_style else entry.level.value.upper(),
                entry.source.value,
                entry.ip or "-",
                entry.service or "-",
                code_cell,
                timeout_cell,
                entry.message[:80],
            )
