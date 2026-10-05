# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Use case scan_logs — coeur du Registre (plan_omega_log.md §4).

Etape 1 (portee depuis FIRE) : detecte les services actifs
(infrastructure/probe/scanner.py) — utilise pour les statistiques du
registre (capabilities_*) exposees par ScanLogsResult, PLUS pour
l'etape 3 (ecran Registre).
Etape 2 (NEUF, cette couche de correlation) : pour CHAQUE service connu
du catalogue (infrastructure/probe/log_path_catalog.py), verifie
l'existence/fraicheur reelle de ses chemins de log candidats sur CETTE
machine — jamais une simple presomption (plan §4.1).

CORRIGE le 2026-10-03 (retour utilisateur : "le scan n'est pas
operationnel, meme fail2ban il n'a pas trouvé") : la version precedente
ne verifiait les chemins de log d'un service QUE si le registre de
capacites le rapportait AVAILABLE/DEGRADED — correct pour FIRE (qui
s'interesse a des defenses ACTIVES), mais faux ici : le detecteur
process-based (known_services.py, categorie "backend") rapporte
MISSING des qu'un processus n'est PAS EN COURS D'EXECUTION, meme si le
binaire est installe (verifie reel sur la machine de reference :
`fail2ban-server`/`fail2ban-client` presents, `systemctl is-active
fail2ban` => inactive, capacite rapportee MISSING malgre
/var/log/fail2ban.log et ses rotations bel et bien presents sur disque).
Un VISUALISEUR de logs doit trouver un fichier qui EXISTE encore,
que le service qui l'a ecrit tourne encore ou non (service arrete,
desinstalle, log herite d'une install anterieure...) — le statut du
registre reste utile pour l'ecran Registre et les stats CLI, mais ne
doit plus JAMAIS conditionner la verification d'un chemin de log.

Etape 3 (restant a l'appelant, TUI pas encore construite) : proposer
l'import au detail ou en totalite des LogFile avec `exists=True` —
cette fonction se contente de les retourner, elle ne touche jamais a la
Bibliotheque (qui n'existe pas encore)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from omega_log.core.capability_registry import CapabilityRegistry
from omega_log.domain.entities.log_file import LogFile
from omega_log.infrastructure.probe.log_path_catalog import (
    DYNAMIC_SERVICE_LOG_PATHS,
    SERVICE_LOG_PATHS,
    SYSTEM_LOG_PATHS,
    LogPathCandidate,
)
from omega_log.infrastructure.probe.scanner import SystemScanner


@dataclass
class ScanLogsResult:
    capabilities_registered: int
    capabilities_available: int
    capabilities_degraded: int
    capabilities_missing: int
    capabilities_disqualified: int
    errors: list[str]
    discovered: list[LogFile] = field(default_factory=list)
    """Chemins existants (service detecte OU systeme), prets a proposer
    pour import au detail ou en totalite — seuls ceux-ci interessent
    l'etape 3 (ecran Registre)."""
    not_found: list[LogFile] = field(default_factory=list)
    """Chemins candidats verifies absents sur cette machine — pas une
    erreur, juste un service/chemin qui n'a pas ce candidat precis
    (annuaire multi-distribution, plan §4.1)."""

    @property
    def stale(self) -> list[LogFile]:
        """Sous-ensemble de `discovered` signale comme suspect (fichier
        vide, probablement mort — annuaire §0)."""
        return [f for f in self.discovered if f.is_stale]


def refresh_log_file(path: str, access: str = "file", service_id: str | None = None, note: str = "") -> LogFile:
    """Recalcule l'etat reel (existe/taille/mtime) d'un chemin — jamais
    une donnee figee au moment d'un scan ou d'un ajout anterieur (voir
    LibraryRecord, annuaire §0). Utilisee par scan_logs() ci-dessous ET
    par application/use_cases/library.py pour rafraichir l'affichage de
    la Bibliotheque a chaque ouverture."""
    try:
        stat = Path(path).stat()
    except OSError:
        return LogFile(path=path, access=access, service_id=service_id, exists=False, note=note)

    return LogFile(
        path=path,
        access=access,
        service_id=service_id,
        exists=True,
        size_bytes=stat.st_size,
        modified_at=datetime.fromtimestamp(stat.st_mtime),
        note=note,
    )


def _resolve_candidate(candidate: LogPathCandidate, service_id: str | None) -> LogFile:
    return refresh_log_file(candidate.path, access=candidate.access, service_id=service_id, note=candidate.note)


_KNOWN_EXTENSIONLESS_LOG_NAMES = frozenset({
    "messages", "secure", "syslog", "auth", "wtmp", "btmp", "lastlog",
    "faillog", "dmesg", "cron", "maillog", "kern", "daemon", "boot", "debug",
})
"""Noms traditionnels SANS ".log" du catalogue §1 de l'annuaire
(messages/secure RHEL, wtmp/btmp/lastlog...) — accepter uniquement un
nom EXACT (apres retrait d'une eventuelle rotation/compression), jamais
une simple sous-chaine (trop permissif, laisserait passer n'importe
quel nom contenant "cron" ou "boot")."""

_ROTATION_COMPRESSION_SUFFIXES = (".gz", ".bz2", ".xz", ".zst", ".old")


def _looks_like_log_file(name: str) -> bool:
    """Filtre du scan manuel (annuaire §13 + retour utilisateur
    2026-10-03 : "seul les fichiers log doivent etre propose, pas les
    fichiers .conf etc... puisque les viewvers sont calibres et parses
    pour des formats de logs serveurs, systeme etc...") — domain/logs/
    parser.py attend un format texte ligne-a-ligne reconnu, jamais un
    fichier de configuration/binaire/socket/etc. Accepte :
    - tout nom contenant ".log" (access.log, fail2ban.log.1,
      fail2ban.log.gz, Xorg.0.log... la quasi-totalite du catalogue
      §2-§12) ;
    - tout nom COMMENCANT par "log." (convention Samba reelle, verifiee
      sur la machine de reference : log.smbd, log.nmbd, log.samba...
      coexiste avec la convention inverse nmbd.log/smbd.log, deja
      couverte par la regle precedente) ;
    - les noms traditionnels sans extension du catalogue §1 (match
      EXACT apres retrait d'une rotation/compression finale, ex:
      "syslog.1" -> "syslog", "messages.gz" -> "messages")."""
    lower = name.lower()
    stem = lower
    for suffix in _ROTATION_COMPRESSION_SUFFIXES:
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    head, dot, tail = stem.rpartition(".")
    if dot and tail.isdigit():
        stem = head

    if ".log" in stem or stem.startswith("log."):
        return True
    return stem in _KNOWN_EXTENSIONLESS_LOG_NAMES


def scan_directory(directory: Path) -> list[LogFile]:
    """Registre, second mode (plan §7) : scan manuel d'un dossier,
    non recursif en profondeur 1 (annuaire §13 — evite de remonter les
    logs rotes `.gz`/`.1`/`.2` d'un sous-dossier comme des entrees
    separees). Exclut les sous-dossiers (le journal binaire systemd
    notamment, jamais un format ligne-a-ligne — annuaire §0/§13) ET tout
    fichier qui ne RESSEMBLE PAS a un log (_looks_like_log_file,
    2026-10-03) : les viewers (domain/logs/parser.py) sont calibres et
    parses pour des formats de logs serveurs/systeme, jamais pour des
    fichiers de configuration ou autres — leur proposer un `.conf` les
    ferait s'afficher vides ou illisibles sans jamais l'expliquer."""
    if not directory.is_dir():
        return []

    results: list[LogFile] = []
    for entry in sorted(directory.iterdir()):
        if entry.is_dir() or entry.is_symlink() and not entry.exists():
            continue
        if not _looks_like_log_file(entry.name):
            continue
        try:
            stat = entry.stat()
        except OSError:
            continue
        results.append(LogFile(
            path=str(entry),
            access="file",
            service_id=None,
            exists=True,
            size_bytes=stat.st_size,
            modified_at=datetime.fromtimestamp(stat.st_mtime),
        ))
    return results


def scan_logs(*, registry: CapabilityRegistry | None = None) -> ScanLogsResult:
    """Lance le scan complet : detection de services + correlation vers
    les chemins de log. `registry` est optionnel (nouveau registre creer
    si omis) — expose pour les tests et pour un futur "re-scanner"."""
    registry = registry if registry is not None else CapabilityRegistry()
    scanner = SystemScanner(registry)
    scan_result = scanner.scan()

    discovered: list[LogFile] = []
    not_found: list[LogFile] = []

    def _record(log_file: LogFile) -> None:
        if log_file.exists:
            discovered.append(log_file)
        else:
            not_found.append(log_file)

    for service_id, candidates in SERVICE_LOG_PATHS.items():
        for candidate in candidates:
            _record(_resolve_candidate(candidate, service_id))

    for service_id, resolver in DYNAMIC_SERVICE_LOG_PATHS.items():
        for candidate in resolver():
            _record(_resolve_candidate(candidate, service_id))

    for candidate in SYSTEM_LOG_PATHS:
        _record(_resolve_candidate(candidate, service_id=None))

    return ScanLogsResult(
        capabilities_registered=scan_result["capabilities_registered"],
        capabilities_available=scan_result["capabilities_available"],
        capabilities_degraded=scan_result["capabilities_degraded"],
        capabilities_missing=scan_result["capabilities_missing"],
        capabilities_disqualified=scan_result["capabilities_disqualified"],
        errors=scan_result["errors"],
        discovered=discovered,
        not_found=not_found,
    )
