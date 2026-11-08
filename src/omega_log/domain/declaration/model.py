# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Declaration anonyme d'utilisateur - reprise d'omega-serv (domain/declaration/model.py,
OMEGA-SERV_ETUDE_TELEMETRIE.md §3b), SIMPLIFIEE pour omega-log (decision utilisateur 2026-11-06) :
pas de serveur ni d'instance, donc un seul mode, « une seule fois », envoye sur clic depuis l'ecran.

Ce qui est envoye, et rien d'autre : une cle tiree au hasard (sans lien avec la machine), le
logiciel (`omega-log`, pour que la reception distingue les logiciels), sa version, le mode et,
facultatifs, un continent et un pays pris dans des listes fermees. Pure, aucune I/O.

Retrait (« Ne plus me declarer ») : `{"cle": ..., "retrait": true}`, la reception supprime l'entree."""
from __future__ import annotations

import re
from dataclasses import dataclass

from omega_log.domain.declaration.countries import COUNTRY_CODES

RECEPTION_URL = "https://kraynux.snake-mackarel.ts.net/compteur/"
"""Adresse de reception (site kraynux, HTTPS), la meme qu'omega-serv. Affichee telle quelle."""

SOFTWARE = "omega-log"
"""Champ « logiciel » du message : la reception tient une liste fermee des logiciels omega."""

MODE_ONCE = "unique"
"""Seul mode d'omega-log (omega-serv propose aussi « quotidien », envoye par son serveur)."""

OTHER = "autre"
CONTINENTS = ("AF", "AN", "AS", "EU", "NA", "OC", "SA")

_KEY = re.compile(r"^[0-9a-f]{32}$")
_VERSION = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}$")


@dataclass(frozen=True)
class Declaration:
    key: str
    continent: str = ""
    country: str = ""


def declaration_errors(declaration: Declaration) -> list[str]:
    """Noms des champs invalides ; liste vide si la declaration est envoyable telle quelle."""
    errors = []
    if not _KEY.match(declaration.key):
        errors.append("cle")
    if declaration.continent and declaration.continent not in (*CONTINENTS, OTHER):
        errors.append("continent")
    if declaration.country and declaration.country not in (*COUNTRY_CODES, OTHER):
        errors.append("pays")
    return errors


def is_valid_version(version: str) -> bool:
    return bool(_VERSION.match(version))


def build_payload(declaration: Declaration, version: str) -> dict[str, str]:
    """Le message exact envoye (et affiche avant l'envoi). Continent et pays absents s'ils ne sont
    pas choisis."""
    payload = {"cle": declaration.key, "logiciel": SOFTWARE, "version": version, "envoi": MODE_ONCE}
    if declaration.continent:
        payload["continent"] = declaration.continent
    if declaration.country:
        payload["pays"] = declaration.country
    return payload


def build_withdrawal(key: str) -> dict[str, object]:
    return {"cle": key, "retrait": True}
