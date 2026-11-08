# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Widget LogLibraryTable - table unique des logs de la Bibliotheque, porte depuis omega-serv
(interfaces/tui/widgets/log_library_table.py, 2026-11-06) : meme representation dans la Bibliotheque
et dans chaque ecran qui choisit des logs (Voir les logs, Favoris, Voir et traiter IP, Statistiques,
Rotation, Purge), jamais une table reinventee par ecran. La colonne « # » donne le numero a cliquer
ou a saisir (voir widgets/library_selection.py)."""
from __future__ import annotations

from typing import Any

from textual.widgets import DataTable

from omega_log.domain.entities.log_file import LogFile
from omega_log.shared.i18n import _


class LogLibraryTable(DataTable):
    """Table #/Chemin/Service/Acces/Taille/Modifie/Etat. `Modifie` : pour une copie recuperee par SSH
    (access="ssh"), c'est la date de la derniere recuperation (scp sans -p), jamais celle du fichier
    distant ; pour un log local, la derniere ecriture (voir d'un coup d'oeil un service qui n'ecrit plus)."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.cursor_type = "row"

    def on_mount(self) -> None:
        self.add_columns("#", _("Chemin"), _("Service"), _("Accès"), _("Taille"), _("Modifié"), _("État"))

    def load(self, log_files: list[LogFile]) -> None:
        """Remplace le contenu. Pas de `key=` : un meme chemin peut apparaitre deux fois, un `key`
        duplique leverait `DuplicateKey` et couperait le chargement."""
        self.clear()
        for index, log_file in enumerate(log_files, start=1):
            size = f"{log_file.size_bytes} o" if log_file.size_bytes is not None else "?"
            modified = log_file.modified_at.strftime("%Y-%m-%d %H:%M") if log_file.modified_at else "-"
            state = _("SUSPECT (vide)") if log_file.is_stale else (_("ABSENT") if not log_file.exists else "OK")
            self.add_row(str(index), log_file.path, log_file.service_id or "-", log_file.access, size, modified, state)
