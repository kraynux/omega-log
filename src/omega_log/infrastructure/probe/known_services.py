# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
"""Known services reference list.

Liste fixe des services/serveurs qu'OMEGA-LOG recherche via detection de
process (pgrep) ou d'unite systemd, pour peupler le registre de
capacites (etape 1 de scan_logs, voir plan_omega_log.md §4). Construite
a partir de l'annuaire (omega_log_annuaire_chemins_logs.md §1-§11) —
categories alignees sur ses sections plutot que sur celles d'omega-fire
(oriente pare-feu) : omega-log s'interesse a CE QUI A UN LOG
CORRELABLE, pas a ce qui interesse un pare-feu.

Pour les entrees reprises d'omega-fire/infrastructure/probe/
known_services.py (ou verifiees identiques), le nom de process est
repris tel quel (deja eprouve en production). Les categories absentes de
FIRE (databases/mail/dns/file_sharing/vpn/monitoring/containers) sont
neuves, construites directement depuis l'annuaire.

Delibrement EXCLU (annuaire §8) : bureau distant (VNC/RDP/...) —
priorite basse pour la lecture de logs serveur, pas dans le scan par
defaut."""

KNOWN_SERVICES: dict[str, list[str]] = {
    "web": [
        "nginx", "apache2", "httpd", "lighttpd", "caddy", "haproxy",
        "traefik", "openresty", "php-fpm",
    ],
    "databases": [
        "mysqld", "mariadbd", "postgres", "redis-server", "mongod",
    ],
    "mail": [
        "postfix", "exim", "dovecot", "sendmail",
    ],
    "dns": [
        "bind9", "named", "unbound", "dnsmasq", "pdns_server",
    ],
    "file_sharing": [
        "smbd", "nmbd", "nfsd", "vsftpd", "proftpd", "pure-ftpd", "sftpgo",
    ],
    "vpn": [
        "openvpn", "charon",  # charon : daemon reel de strongSwan (pas "strongswan")
    ],
    "security": [
        "fail2ban-server", "crowdsec", "lfd", "opensnitchd",
    ],
    "monitoring": [
        "grafana-server", "prometheus", "netdata",
    ],
    "containers": [
        "docker", "dockerd", "containerd",
    ],
}

SYSTEMD_UNIT_SERVICES: dict[str, str] = {
    "omega-serv": "omega-serv.service",
}
"""Services detectes par unite systemd plutot que par pgrep (voir
infrastructure/probe/systemd_unit_probe.py) — necessaire quand le nom de
process visible est generique (ex. omega-serv se lance via
`python -m omega_serv ... serve`, voir annuaire §2/§15). Cle = capability
ID, valeur = nom d'unite systemd."""
