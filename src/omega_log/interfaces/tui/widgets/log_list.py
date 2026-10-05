# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Widget LogList — table reutilisable pour afficher une liste de
LogFile (plan_omega_log.md §3). Utilise par le Registre maintenant, par
la Bibliotheque/Favoris plus tard (meme representation partout, pas une
table reinventee par ecran)."""
from __future__ import annotations

from textual.widgets import DataTable

from omega_log.domain.entities.log_file import LogFile


class LogList(DataTable):
    """Table Chemin/Service/Acces/Taille/Etat pour une liste de LogFile."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cursor_type = "row"

    def on_mount(self) -> None:
        self.add_columns("Chemin", "Service", "Acces", "Taille", "Etat")

    def load(self, log_files: list[LogFile]) -> None:
        """Remplace le contenu de la table par `log_files`.

        Pas de `key=` explicite sur `add_row` : un meme chemin peut
        apparaitre a la fois dans la correlation service (discovered) et
        dans un scan manuel du dossier qui le contient (ex. /var/log/
        auth.log via le registre ET via un scan de /var/log) — un `key`
        duplique fait lever `DuplicateKey` et interrompt le chargement en
        plein milieu (bug reel rencontre ici). Laisser Textual generer
        des cles internes evite la collision ; aucun code n'a besoin de
        retrouver une ligne par chemin pour l'instant."""
        self.clear()
        for log_file in log_files:
            size = f"{log_file.size_bytes} o" if log_file.size_bytes is not None else "?"
            state = "SUSPECT (vide)" if log_file.is_stale else "OK"
            self.add_row(log_file.path, log_file.service_id or "-", log_file.access, size, state)
