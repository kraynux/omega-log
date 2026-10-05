# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Entite LogFile — candidat de log decouvert par le Registre (scan_logs,
plan_omega_log.md §4) ou importe manuellement dans la Bibliotheque (pas
encore construite). Pure donnee de domaine, aucune I/O ici : la lecture
disque reelle est faite par application/use_cases/scan_logs.py, pas par
cette entite."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class LogFile:
    """Un chemin de log candidat, avec son etat au moment du scan.

    `service_id` est None pour les chemins systeme generiques (syslog,
    auth.log, pacman.log...) non rattaches a un service detecte — voir
    annuaire §1 vs §2-§11."""

    path: str
    access: str  # "file" | "journald" | "file_or_journald"
    service_id: str | None = None
    exists: bool = False
    size_bytes: int | None = None
    modified_at: datetime | None = None
    note: str = ""

    @property
    def is_stale(self) -> bool:
        """Fichier present mais vide — candidat "mort", probablement
        route vers journald plutot qu'alimente (voir annuaire §0,
        verifie reel avec /var/log/auth.log sur la machine de reference).
        Ne doit jamais etre propose au meme rang qu'un fichier alimente."""
        return self.exists and self.size_bytes == 0
