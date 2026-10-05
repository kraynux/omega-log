# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Logs domain parser.

Pure domain logic for extracting structured data from raw log lines.
This module contains regex patterns and extraction functions that
operate on strings only — it does NOT read files from disk.

Porte verbatim depuis omega-fire (domain/logs/parser.py) — couverture
reelle verifiee dans plan_omega_log.md §4.2 : generique (AUTH/FAIL2BAN/
ACCESS/KERN/SYSLOG par heuristique de mots-cles), mais aucun parseur
dedie pour auditd/pacman/samba/json-file — a etendre au fil des besoins,
pas un enum/parseur figes.

PERFORMANCE CORRIGEE (2026-10-04, retour utilisateur : "bug severe dans
statistique... l'ecran n'est pas gele mais aucun resultat ne sort",
reproduit aussi sur "Voir et Traiter IP") — bug reel mesure, pas un
ressenti : `compute_access_log_stats()` mettait 23 SECONDES pour
seulement 34811 lignes d'un access.log reel (profilage cProfile a
l'appui), rendant le calcul perceptiblement "bloque" pour tout fichier
de taille normale de production (potentiellement des minutes). Deux
causes identifiees et corrigees ici :
1. `extract_log_level()` compilait et executait JUSQU'A 15 regex
   DIFFERENTS par ligne (une boucle sur chaque niveau connu) — remplace
   par UN SEUL motif precompile (alternance) + recherche unique, en
   conservant EXACTEMENT le meme ordre de priorite qu'avant (le niveau
   le plus specifique dans LOG_LEVELS l'emporte, pas le premier trouve
   dans le texte).
2. Tous les autres motifs (IP, timestamps, service, utilisateur, port)
   etaient passes comme chaines brutes a `re.search()`/`re.findall()`
   au lieu d'objets `re.Pattern` precompiles — chaque appel repassait
   par le cache interne du module `re` (dictionnaire, cle = chaine),
   mesure a lui seul a ~4.7s cumules sur ce fichier de test. Precompiles
   en constantes `_XXX_RE` au niveau module, comme COMBINED_LOG_PATTERN
   l'etait deja.
`extract_timestamp()` ne passe en outre plus par `datetime.strptime()`
(machinerie generique de parsing de format, mesuree ~4.25s cumules) mais
construit `datetime(...)` directement a partir des groupes numeriques
captures par les memes regex precompiles — strictement equivalent pour
les 3 formats geres ici (tous a largeur fixe), nettement plus rapide."""
import re
from datetime import datetime

from omega_log.domain.logs.models import LogEntry, LogLevel, LogSource

IPV4_PATTERN = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
IPV6_PATTERN = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
IP_PATTERN = rf'(?:{IPV4_PATTERN}|{IPV6_PATTERN})'
_IP_RE = re.compile(IP_PATTERN)

SYSLOG_TIMESTAMP = r'(\w{3})\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})'
ISO_TIMESTAMP = r'(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})'
APACHE_TIMESTAMP = r'\[(\d{2})/(\w{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2})'
"""Format Combined/Common Apache/Nginx (ex. [10/Oct/2026:10:00:00 +0200]) —
AJOUTE ici (absent de la version source omega-fire, verifie par un test
reel en Phase 7 : une ligne access log classique tombait silencieusement
sur `datetime.now()`, faussant toute statistique par periode/heure —
exactement le format que `detect_log_source()` reconnait pourtant comme
ACCESS quelques lignes plus bas, incoherence non remarquee cote source).
Groupes individuels (jour/mois/annee/heure/min/sec) depuis le 2026-10-04
(optimisation performance, voir note de tete de fichier) — auparavant un
seul groupe texte repasse a `datetime.strptime()`."""

_SYSLOG_TIMESTAMP_RE = re.compile(SYSLOG_TIMESTAMP)
_ISO_TIMESTAMP_RE = re.compile(ISO_TIMESTAMP)
_APACHE_TIMESTAMP_RE = re.compile(APACHE_TIMESTAMP)

_MONTH_ABBR = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

COMBINED_LOG_PATTERN = re.compile(
    r'(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<time>[^\]]+)\]\s+'
    r'"(?P<method>\S+)\s+(?P<path>\S+)[^"]*"\s+(?P<status>\d+)\s+(?P<size>\d+|-)'
)
"""Format Combined/Common (IP - - [date] "METHODE CHEMIN HTTP/x.x" STATUT
TAILLE) — AJOUTE 2026-10-04 (retour utilisateur : Viewer 1 doit remontrer
code HTTP/latence comme omega-fire pour les access logs) : `LogEntry.
http_method/http_path/http_status/latency_ms` restaient tous `None`
jusqu'ici, aucune fonction ne les renseignait, malgre leur presence dans
le modele (porte verbatim depuis omega-fire, jamais branche cote parser
contrairement a la source). Reprise du MEME regex que
omega-fire/interfaces/cli/renderers/live_tail_screen.py::_LogProvider
(deja valide empiriquement), jamais re-derive."""

LOG_LEVELS = {
    'debug': LogLevel.DEBUG,
    'info': LogLevel.INFO,
    'information': LogLevel.INFO,
    'notice': LogLevel.INFO,
    'warning': LogLevel.WARNING,
    'warn': LogLevel.WARNING,
    'error': LogLevel.ERROR,
    'err': LogLevel.ERROR,
    'critical': LogLevel.CRITICAL,
    'crit': LogLevel.CRITICAL,
    'fatal': LogLevel.CRITICAL,
    'alert': LogLevel.CRITICAL,
    'emergency': LogLevel.CRITICAL,
    'emerg': LogLevel.CRITICAL,
}

_LOG_LEVEL_RE = re.compile(r'\b(' + '|'.join(LOG_LEVELS) + r')\b')
"""UN SEUL motif (alternance) pour reperer TOUS les mots de niveau
presents dans la ligne en une seule passe — voir note de performance en
tete de fichier. `extract_log_level()` retrouve ensuite le niveau a
retenir en reparcourant `LOG_LEVELS` dans son ordre d'origine (premiere
cle presente dans l'ensemble trouve), EXACTEMENT le meme ordre de
priorite que la version precedente (boucle + regex separee par cle) —
jamais le premier mot rencontre dans le texte, qui aurait un sens
different (position dans la ligne plutot que priorite du niveau)."""

_SERVICE_RE = re.compile(r'\w+\s+([a-zA-Z0-9_-]+)(?:\[\d+\])?:')

_USER_PATTERNS = [
    re.compile(r'user\s+([a-zA-Z0-9_-]+)', re.IGNORECASE),
    re.compile(r'for\s+([a-zA-Z0-9_-]+)', re.IGNORECASE),
    re.compile(r'Accepted\s+\w+\s+for\s+([a-zA-Z0-9_-]+)', re.IGNORECASE),
    re.compile(r'Failed\s+\w+\s+for\s+([a-zA-Z0-9_-]+)', re.IGNORECASE),
]

_PORT_PATTERNS = [
    re.compile(r'port\s+(\d+)'),
    re.compile(r':(\d+)\b'),
]


def extract_ip(line: str) -> str | None:
    """Extract the first IP address from a log line."""
    match = _IP_RE.search(line)
    return match.group(0) if match else None


def extract_all_ips(line: str) -> list[str]:
    """Extract all IP addresses from a log line."""
    return _IP_RE.findall(line)


def extract_timestamp(line: str) -> datetime | None:
    """Extract timestamp from a log line.

    Supports syslog format (Jan 1 12:00:00), ISO format
    (2024-01-01T12:00:00), and the Apache/Nginx Combined format
    ([10/Oct/2026:10:00:00 +0200]).
    """
    iso_match = _ISO_TIMESTAMP_RE.search(line)
    if iso_match:
        try:
            year, month, day, hour, minute, second = (int(g) for g in iso_match.groups())
            return datetime(year, month, day, hour, minute, second)
        except ValueError:
            pass

    apache_match = _APACHE_TIMESTAMP_RE.search(line)
    if apache_match:
        day_s, month_s, year_s, hour_s, minute_s, second_s = apache_match.groups()
        month = _MONTH_ABBR.get(month_s.lower())
        if month is not None:
            try:
                return datetime(int(year_s), month, int(day_s), int(hour_s), int(minute_s), int(second_s))
            except ValueError:
                pass

    syslog_match = _SYSLOG_TIMESTAMP_RE.search(line)
    if syslog_match:
        month_s, day_s, hour_s, minute_s, second_s = syslog_match.groups()
        month = _MONTH_ABBR.get(month_s.lower())
        if month is not None:
            try:
                return datetime(datetime.now().year, month, int(day_s), int(hour_s), int(minute_s), int(second_s))
            except ValueError:
                pass

    return None


def extract_log_level(line: str) -> LogLevel:
    """Extract log level from a log line (default: INFO if not found)."""
    line_lower = line.lower()

    found = set(_LOG_LEVEL_RE.findall(line_lower))
    if not found:
        return LogLevel.INFO

    for level_str, level_enum in LOG_LEVELS.items():
        if level_str in found:
            return level_enum

    return LogLevel.INFO


def extract_service(line: str) -> str | None:
    """Extract service name from a syslog-style log line."""
    match = _SERVICE_RE.search(line)
    return match.group(1) if match else None


def extract_user(line: str) -> str | None:
    """Extract username from an auth log line."""
    for pattern in _USER_PATTERNS:
        match = pattern.search(line)
        if match:
            return match.group(1)

    return None


def extract_port(line: str) -> int | None:
    """Extract port number from a log line."""
    for pattern in _PORT_PATTERNS:
        match = pattern.search(line)
        if match:
            try:
                port = int(match.group(1))
                if 1 <= port <= 65535:
                    return port
            except ValueError:
                pass

    return None


def extract_http_fields(line: str) -> tuple[str | None, str | None, int | None, int | None]:
    """Extrait (methode, chemin, code HTTP, latence_ms) d'une ligne
    access log Combined/Common — None partout si le format ne matche
    pas (jamais un log auth/syslog/fail2ban/etc., ces champs n'ont pas
    de sens pour eux). Latence : heuristique reprise d'omega-fire
    (_LogProvider._parse_generic_line, branche Combined) — dernier
    jeton numerique court (<=6 chiffres) APRES la partie matchee,
    convention qu'omega-fire a deja validee empiriquement pour les
    formats de log personnalises qui ajoutent la duree en fin de ligne
    (ex. directive Apache "%D"/"%T") ; simplement absente du Common Log
    Format standard, d'ou `None` le plus souvent — colonne "Timeout"
    cote Viewer 1, affichee "-" dans ce cas, jamais une valeur inventee."""
    match = COMBINED_LOG_PATTERN.search(line)
    if not match:
        return None, None, None, None

    status = int(match.group("status"))
    tail = line[match.end():].strip().split()
    latency_ms: int | None = None
    for token in reversed(tail):
        clean_token = token.strip('"').replace(".", "")
        if clean_token.isdigit() and len(clean_token) <= 6:
            latency_ms = int(clean_token)
            break

    return match.group("method"), match.group("path"), status, latency_ms


def detect_log_source(line: str) -> LogSource:
    """Detect the log source from a log line."""
    line_lower = line.lower()

    if any(indicator in line_lower for indicator in [
        'sshd', 'sudo', 'authentication', 'login', 'accepted password',
        'failed password', 'invalid user'
    ]):
        return LogSource.AUTH

    if 'fail2ban' in line_lower:
        return LogSource.FAIL2BAN

    if any(indicator in line_lower for indicator in [
        'get /', 'post /', 'http/', '404', '500', 'apache', 'nginx'
    ]):
        return LogSource.ACCESS

    if any(indicator in line_lower for indicator in [
        'kernel:', 'iptables', 'nftables', 'netfilter'
    ]):
        return LogSource.KERN

    return LogSource.SYSLOG


def parse_log_line(
    line: str,
    line_number: int = 0,
    log_path: str | None = None,
    source: LogSource | None = None,
) -> LogEntry | None:
    """Parse a raw log line into a structured LogEntry."""
    if not line.strip():
        return None

    timestamp = extract_timestamp(line)
    ip = extract_ip(line)
    level = extract_log_level(line)
    service = extract_service(line)
    user = extract_user(line)
    port = extract_port(line)
    http_method, http_path, http_status, latency_ms = extract_http_fields(line)

    if source is None:
        source = detect_log_source(line)

    if http_status is not None and http_status >= 400 and level == LogLevel.INFO:
        # Un code HTTP 4xx/5xx est un echec meme si la ligne ne contient
        # aucun mot-cle de niveau reconnu par extract_log_level() (le cas
        # courant : un access log Combined standard n'ecrit jamais
        # "error"/"warning" en toutes lettres, seulement le code) —
        # jamais ecrase si un niveau plus specifique a deja ete detecte.
        level = LogLevel.ERROR if http_status >= 500 else LogLevel.WARNING

    return LogEntry(
        timestamp=timestamp or datetime.now(),
        source=source,
        level=level,
        ip=ip,
        message=line.strip(),
        raw_line=line,
        line_number=line_number,
        log_path=log_path,
        user=user,
        port=port,
        http_method=http_method,
        http_path=http_path,
        http_status=http_status,
        latency_ms=latency_ms,
        service=service,
    )


def parse_log_lines(
    lines: list[str],
    log_path: str | None = None,
    source: LogSource | None = None,
) -> list[LogEntry]:
    """Parse multiple log lines into structured LogEntry objects."""
    entries = []

    for i, line in enumerate(lines, start=1):
        entry = parse_log_line(line, line_number=i, log_path=log_path, source=source)
        if entry is not None:
            entries.append(entry)

    return entries
