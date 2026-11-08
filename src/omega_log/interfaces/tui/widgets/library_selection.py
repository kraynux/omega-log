# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Selection dans les tables de la Bibliotheque (#library-table + champ #selection-input) - porte depuis
omega-serv (interfaces/tui/widgets/log_library_table.py, retour utilisateur 2026-10-31), retour
utilisateur 2026-11-02 : « le double clic aussi pas op dans omega-log ».

- double-clic ou Entree sur une ligne : ajoute ou retire son numero dans le champ (plusieurs logs) ;
  ecran a un seul log (Rotation) : remplace le numero ;
- simple clic, champ vide : la ligne surlignee suffit (comme omega-fire et omega-serv) ;
- champ rempli : toujours prioritaire."""
from __future__ import annotations

from textual.widgets import DataTable, Input

from omega_log.shared.i18n import _

SELECTION_HINT = (
    _("Clic : choisir un log. Double-clic ou Entrée : ajouter ou retirer son numéro dans le "
      "champ (plusieurs logs). Le champ, s'il est rempli, a priorité.")
)
SINGLE_SELECTION_HINT = (
    _("Clic : choisir un log. Double-clic ou Entrée : mettre son numéro dans le champ. Le "
      "champ, s'il est rempli, a priorité.")
)


def toggle_selection_number(raw: str, number: int) -> str:
    """Ajoute `number` a la liste « 1,3 » du champ, ou l'en retire s'il y est deja. Ordre conserve."""
    tokens = [token.strip() for token in raw.split(",") if token.strip()]
    if str(number) in tokens:
        tokens.remove(str(number))
    else:
        tokens.append(str(number))
    return ",".join(tokens)


def selection_or_cursor(raw: str, cursor_row: int | None, count: int) -> str:
    """Champ vide : la ligne surlignee. Sinon le champ, prioritaire. Table vide : chaine vide (l'ecran
    affiche son message habituel)."""
    if raw.strip() or count == 0 or cursor_row is None or not 0 <= cursor_row < count:
        return raw.strip()
    return str(cursor_row + 1)


class LibrarySelectionMixin:
    """A placer AVANT OmegaScreen dans les bases de l'ecran."""

    SINGLE_LIBRARY_SELECTION = False

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id != "library-table":
            return
        field = self.query_one("#selection-input", Input)  # type: ignore[attr-defined]
        number = event.cursor_row + 1
        if self.SINGLE_LIBRARY_SELECTION:
            field.value = str(number)
        else:
            field.value = toggle_selection_number(field.value, number)

    def _library_selection(self) -> str:
        field = self.query_one("#selection-input", Input)  # type: ignore[attr-defined]
        table = self.query_one("#library-table", DataTable)  # type: ignore[attr-defined]
        return selection_or_cursor(field.value, table.cursor_row, table.row_count)
