# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Log path catalog.

NEUF (couche de correlation, plan_omega_log.md §4 etape 2) : traduit en
code le catalogue de l'annuaire (omega_log_annuaire_chemins_logs.md) —
pour chaque service connu (infrastructure/probe/known_services.py),
quel(s) chemin(s) de log candidats verifier.

Volontairement une LISTE A PLAT de chemins candidats par service, PAS un
branchement sur la distribution detectee : plan_omega_log.md §4.1
interdit explicitement de filtrer par distribution — chaque chemin est
verifie reellement present sur la machine cible, les variantes qui
n'existent pas sont simplement absentes du resultat. Couvre
delibrement MOINS de services que known_services.py : certains
(traefik, nfsd, prometheus, netdata, dnsmasq...) n'ont aucun fichier de
log fixe connu (stdout de conteneur, journald uniquement, ou chemin
versionne imprevisible comme postgresql-<version>-main.log) — absents
d'ici plutot que presents avec un chemin invente, voir annuaire §0/§3."""
from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LogPathCandidate:
    path: str
    access: str  # "file" | "journald" | "file_or_journald"
    note: str = ""


SERVICE_LOG_PATHS: dict[str, tuple[LogPathCandidate, ...]] = {
    "nginx": (
        LogPathCandidate("/var/log/nginx/access.log", "file"),
        LogPathCandidate("/var/log/nginx/error.log", "file"),
    ),
    "apache2": (
        LogPathCandidate("/var/log/apache2/access.log", "file"),
        LogPathCandidate("/var/log/apache2/error.log", "file"),
    ),
    "httpd": (
        LogPathCandidate("/var/log/httpd/access_log", "file", "Arch : nom sans extension .log"),
        LogPathCandidate("/var/log/httpd/error_log", "file", "Arch : nom sans extension .log"),
    ),
    "lighttpd": (
        LogPathCandidate("/var/log/lighttpd/access.log", "file"),
        LogPathCandidate("/var/log/lighttpd/error.log", "file"),
    ),
    "caddy": (
        LogPathCandidate("/var/log/caddy/access.log", "file_or_journald", "seulement si directive log explicite"),
        LogPathCandidate("/var/log/caddy/error.log", "file_or_journald", "seulement si directive log explicite"),
    ),
    "openresty": (
        LogPathCandidate("/var/log/openresty/access.log", "file", "chemin variable selon build"),
        LogPathCandidate("/var/log/openresty/error.log", "file", "chemin variable selon build"),
    ),
    "php-fpm": (
        LogPathCandidate("/var/log/php-fpm.log", "file"),
    ),
    "mysqld": (
        LogPathCandidate("/var/log/mysql/error.log", "file_or_journald", "souvent desactive par defaut"),
    ),
    "mariadbd": (
        LogPathCandidate("/var/log/mysql/error.log", "file_or_journald", "souvent desactive par defaut"),
    ),
    "redis-server": (
        LogPathCandidate("/var/log/redis/redis-server.log", "file_or_journald"),
    ),
    "mongod": (
        LogPathCandidate("/var/log/mongodb/mongod.log", "file"),
    ),
    "postfix": (
        LogPathCandidate("/var/log/mail.log", "file_or_journald"),
    ),
    "exim": (
        LogPathCandidate("/var/log/exim4/mainlog", "file"),
    ),
    "dovecot": (
        LogPathCandidate("/var/log/mail.log", "file_or_journald"),
    ),
    "sendmail": (
        LogPathCandidate("/var/log/mail.log", "file_or_journald"),
    ),
    "pdns_server": (
        LogPathCandidate("/var/log/pdns.log", "file_or_journald"),
    ),
    "smbd": (
        LogPathCandidate("/var/log/samba/log.smbd", "file"),
    ),
    "nmbd": (
        LogPathCandidate("/var/log/samba/log.nmbd", "file"),
    ),
    "vsftpd": (
        LogPathCandidate("/var/log/vsftpd.log", "file"),
    ),
    "proftpd": (
        LogPathCandidate("/var/log/proftpd/proftpd.log", "file"),
    ),
    "openvpn": (
        LogPathCandidate("/var/log/openvpn.log", "file_or_journald"),
    ),
    "charon": (
        LogPathCandidate("/var/log/charon.log", "file_or_journald"),
    ),
    "fail2ban-server": (
        LogPathCandidate("/var/log/fail2ban.log", "file"),
    ),
    "crowdsec": (
        LogPathCandidate("/var/log/crowdsec.log", "file"),
    ),
    "lfd": (
        LogPathCandidate("/var/log/lfd.log", "file"),
        LogPathCandidate("/var/log/csf.log", "file"),
    ),
    "grafana-server": (
        LogPathCandidate("/var/log/grafana/grafana.log", "file"),
    ),
}

SYSTEM_LOG_PATHS: tuple[LogPathCandidate, ...] = (
    LogPathCandidate("/var/log/syslog", "file_or_journald"),
    LogPathCandidate("/var/log/messages", "file_or_journald", "variante RHEL/Fedora de syslog"),
    LogPathCandidate("/var/log/auth.log", "file_or_journald"),
    LogPathCandidate("/var/log/secure", "file_or_journald", "variante RHEL/Fedora de auth.log"),
    LogPathCandidate("/var/log/kern.log", "file_or_journald"),
    LogPathCandidate("/var/log/pacman.log", "file", "gestionnaire de paquets Arch/Manjaro"),
    LogPathCandidate("/var/log/apt/history.log", "file", "gestionnaire de paquets Debian/Ubuntu"),
    LogPathCandidate("/var/log/dpkg.log", "file", "gestionnaire de paquets Debian/Ubuntu"),
    LogPathCandidate("/var/log/dnf.log", "file", "gestionnaire de paquets RHEL/Fedora"),
    LogPathCandidate("/var/log/audit/audit.log", "file", "root uniquement, format structure type=... — pas de parseur dedie, voir plan §4.2"),
)
"""Chemins verifies independamment de toute detection de service — voir
annuaire §1. Certains n'existent jamais ensemble sur une meme machine
(syslog vs messages, auth.log vs secure, selon distribution) ; les deux
variantes sont listees et seules celles reellement presentes
ressortiront du scan (plan §4.1 : ne jamais presumer la distribution)."""


def _resolve_omega_serv_paths() -> tuple[LogPathCandidate, ...]:
    """Les 3 logs d'omega-serv sont relatifs a SA PROPRE racine
    d'installation (PROJECT_ROOT), pas un chemin OS standard — voir
    annuaire §2/§15. Resolue dynamiquement via la propriete systemd
    `WorkingDirectory` de l'unite, jamais codee en dur (ne fonctionnerait
    que sur la machine de developpement)."""
    try:
        result = subprocess.run(
            ["systemctl", "show", "-p", "WorkingDirectory", "omega-serv.service"],
            capture_output=True, text=True, timeout=5, check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return ()

    if result.returncode != 0:
        return ()

    _, _, value = result.stdout.strip().partition("=")
    working_directory = value.strip()
    if not working_directory:
        return ()

    base = f"{working_directory}/var/log"
    return (
        LogPathCandidate(f"{base}/access.log", "file"),
        LogPathCandidate(f"{base}/error.log", "file"),
        LogPathCandidate(f"{base}/waf-alerts.log", "file"),
    )


DYNAMIC_SERVICE_LOG_PATHS: dict[str, Callable[[], tuple[LogPathCandidate, ...]]] = {
    "omega-serv": _resolve_omega_serv_paths,
}
"""Services dont le chemin de log ne peut pas etre une liste statique
(depend de la configuration/installation reelle de la machine cible)."""
