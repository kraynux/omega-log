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

from rich.cells import cell_len, set_cell_size
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Center, Container, Horizontal, Vertical, VerticalScroll
from textual.timer import Timer
from textual.widgets import Button, DataTable, Footer, Header, Static

from omega_log.domain.logs.analytics import compute_traffic_stats
from omega_log.domain.logs.models import LogEntry, TrafficStats
from omega_log.domain.logs.parser import parse_log_line
from omega_log.infrastructure.privileged.privileged_file_ops import read_file_privileged
from omega_log.infrastructure.tail.live_tail_reader import LiveTailReader
from omega_log.interfaces.tui.screens._base import OmegaScreen
from omega_log.interfaces.tui.screens._elevation import request_elevation
from omega_log.shared.i18n import _

if TYPE_CHECKING:
    from omega_log.app.dependency_container import DependencyContainer

_REFRESH_SECONDS = 2.0
_BUFFER_SIZE = 500
_INITIAL_LINES = 200
_TOP_WIDTH = 29
"""Largeur utile du cadre de gauche avant son premier affichage (34 colonnes, cadre et barre deduits)."""


def _format_bytes(size: float) -> str:
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.1f} KB"
    return f"{int(size)} B"


class LiveTailScreen(OmegaScreen):
    """Viewer 1 : IDENTIQUE au viewer Simple d'omega-serv (reference validee 2026-11-02) - tout le
    tampon dans un tableau qui defile (suivi automatique quand on est en bas) + barre d'etat a 5 blocs
    (rendement, bande passante, statuts HTTP, clients et reseau, sante et tampon). Retour utilisateur
    2026-11-02 : 30 lignes sans ascenseur et une barre limitee a « Apercu » / « Top IP »."""

    def __init__(self, *, container: DependencyContainer, path: str) -> None:
        super().__init__()
        self._container = container
        self._path = path
        self._reader = LiveTailReader(Path(path))
        self._buffer: list[LogEntry] = []
        self._line_number = 0
        self._timer: Timer | None = None
        self._elevated = False
        self._first_render = True

    def compose(self) -> ComposeResult:
        yield Header()
        # Panneau remonte (porte d'omega-serv, 2026-11-07) : 3 lignes de plus pour le cadre de stats.
        with Vertical(id="simple-viewer-panel", classes="omega-panel"):
            with Center():  # titre et bouton centres, comme omega-serv (2026-11-06)
                yield Static(_("VOIR LES LOGS — SIMPLE — {path}").format(path=self._path), classes="omega-title")
            with Horizontal(id="simple-viewer-body"):
                # Cadre qui defile (omega-serv 2026-11-05) : avec les tops, un Static seul a hauteur fixe
                # coupait la fin de son contenu.
                with VerticalScroll(id="stats-frame", classes="omega-dash-box"):
                    yield Static(id="stats-box")
                yield DataTable(id="entries-table")
            with Center(), Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#entries-table", DataTable).add_columns(
            _("Heure"), _("Niveau"), _("Source"), _("IP"), _("Service"), _("Code"), _("Timeout"), _("Message")
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
            self.app.notify(_("Permission refusée sur {path}.").format(path=self._path), severity="error")
            return None
        result = read_file_privileged(self._container.process_runner, self._path)
        if not result.success:
            self.app.notify(_("Lecture privilégiée impossible : {message}").format(message=result.message), severity="error")
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
                self.app.notify(_("Permission refusée sur {path}.").format(path=self._path), severity="error")
                self._stop()
                return
            self._elevated = True
            try:
                new_lines = self._reader.read_new_lines_privileged(self._container.process_runner)
            except OSError as exc:
                self.app.notify(_("Lecture privilégiée impossible : {exc}").format(exc=exc), severity="error")
                self._stop()
                return
        except OSError as exc:
            self.app.notify(_("Lecture impossible : {exc}").format(exc=exc), severity="error")
            self._stop()
            return

        added = False
        for line in new_lines:
            self._line_number += 1
            entry = parse_log_line(line, line_number=self._line_number, log_path=self._path)
            if entry is not None:
                self._buffer.append(entry)
                added = True
        if len(self._buffer) > _BUFFER_SIZE:
            self._buffer = self._buffer[-_BUFFER_SIZE:]

        self._render_stats()
        if added or self._first_render:
            self._first_render = False
            self._render_table()

    def _render_stats(self) -> None:
        self.query_one("#stats-box", Static).update(self._stats_text(compute_traffic_stats(self._buffer)))

    def _stats_text(self, stats: TrafficStats) -> Text:
        variables = self.app.get_css_variables()
        heading = f"bold {variables.get('secondary', '')}".strip()
        good = variables.get("success", "green") or "green"
        warn = variables.get("warning", "yellow") or "yellow"
        bad = variables.get("error", "red") or "red"
        info = variables.get("secondary", "cyan") or "cyan"
        none = "-"

        content = Text()
        content.append(_("── RENDEMENT ──────────────\n"), style=heading)
        rps = none if stats.requests_per_second is None else _("{requests_per_second:.1f} req/s").format(requests_per_second=stats.requests_per_second)
        content.append(_(" ⚡ Débit        : {rps}\n").format(rps=rps), style=info)
        if stats.avg_latency_ms is None:
            content.append(_(" ⏱ Latence moy. : {none}\n\n").format(none=none))
        else:
            latency = stats.avg_latency_ms
            style = good if latency < 200 else (warn if latency < 500 else bad)
            content.append(_(" ⏱ Latence moy. : {latency:.0f} ms\n\n").format(latency=latency), style=style)

        content.append(_("── BANDE PASSANTE ─────────\n"), style=heading)
        bps = none if stats.bytes_per_second is None else f"{_format_bytes(stats.bytes_per_second)}/s"
        total = none if stats.bytes_total is None else _format_bytes(stats.bytes_total)
        average = none if stats.avg_size is None else _format_bytes(stats.avg_size)
        content.append(_(" 🌐 Débit réseau : {bps}\n").format(bps=bps))
        content.append(_(" 📦 Volume total : {total}\n").format(total=total))
        content.append(_(" 🗜 Taille moy.  : {average}\n\n").format(average=average))

        content.append(_("── STATUTS HTTP ───────────\n"), style=heading)
        content.append(_(" 📊 Requêtes     : {http_total}\n").format(http_total=stats.http_total))
        content.append(_(" √  Succès 2xx   : {status_2xx}\n").format(status_2xx=stats.status_2xx), style=good)
        content.append(_(" ↔  Redir. 3xx   : {status_3xx}\n").format(status_3xx=stats.status_3xx), style=info)
        content.append(_(" ⚠  Erreurs 4xx  : {status_4xx}\n").format(status_4xx=stats.status_4xx), style=warn)
        content.append(_(" ❌ Erreurs 5xx  : {status_5xx}\n").format(status_5xx=stats.status_5xx), style=bad)
        content.append(_(" ⛔ Refus 403    : {status_403}\n").format(status_403=stats.status_403), style=warn)
        content.append(_(" ⏳ Refus 429    : {status_429}\n\n").format(status_429=stats.status_429), style=warn)

        content.append(_("── CLIENTS & RÉSEAU ───────\n"), style=heading)
        content.append(_(" 💻 IPs uniques  : {unique_ips}\n").format(unique_ips=stats.unique_ips))
        # Adresse sur sa propre ligne : une IPv4 longue ou une IPv6 deborderait du cadre (34 colonnes).
        content.append(_(" 🖧 Top 5 IP     :\n"), style=info)
        self._append_top(content, stats.top_ips, info)
        if stats.top_paths:
            content.append(_("── CHEMINS DEMANDÉS ───────\n"), style=heading)
            self._append_top(content, stats.top_paths, "")
            content.append(_("── CHEMINS EN 404 ─────────\n"), style=heading)
            self._append_top(content, stats.top_not_found, warn)

        content.append(_("── SANTÉ & TAMPON ─────────\n"), style=heading)
        rate = stats.error_rate
        health_style = good if rate < 5 else (warn if rate < 15 else bad)
        health = "EXCELLENT" if rate < 2 else ("CORRECT" if rate < 10 else _("DÉGRADÉ"))
        content.append(_(" 🌡 Santé        : {health}\n").format(health=health), style=health_style)
        content.append(_(" ⚠  Taux d'erreur: {rate:.1f}%\n").format(rate=rate), style=health_style)
        content.append(_(" 📥 Tampon       : {count}/{BUFFER_SIZE}").format(count=len(self._buffer), BUFFER_SIZE=_BUFFER_SIZE))
        return content

    def _append_top(self, content: Text, items: list[tuple[str, int]], style: str) -> None:
        """Valeur (IP, chemin) depuis le bord gauche, compte aligne a droite une colonne avant le bord (omega-serv
        2026-11-05, marge 2026-11-07) : le chemin dispose de toute la largeur restante au lieu de commencer au
        milieu du cadre."""
        if not items:
            content.append("    " + _("(aucun)") + "\n\n", style="dim")
            return
        width = self.query_one("#stats-box", Static).size.width or _TOP_WIDTH
        count_width = max(len(str(count)) for _value, count in items)
        # 1 espace de marge a gauche, 1 avant le compte et 1 apres (omega-serv 2026-11-07 : colle a l'ascenseur,
        # on ne savait pas si un chiffre etait cache derriere)
        room = max(8, width - 3 - count_width)
        for value, count in items:
            shown = value if cell_len(value) <= room else set_cell_size(value, room - 1) + "…"
            content.append(" " + shown + " " * (room - cell_len(shown)) + " ", style=style)
            content.append(f"{count:>{count_width}}\n", style="bold")
        content.append("\n")

    def _render_table(self) -> None:
        table = self.query_one("#entries-table", DataTable)
        # Suivi automatique seulement si on etait deja en bas : jamais arrache d'une lecture plus haut.
        follow = table.scroll_y >= table.max_scroll_y - 1
        table.clear()
        for entry in self._buffer:
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
        if follow:
            table.call_after_refresh(table.scroll_end, animate=False)
