<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->

<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-log.png" alt="Omega-Log" width="384">
</div>

# 📜 OMEGA-LOG

**Gestionnaire et visualisateur de logs serveur**

> Élaboré par **kraynux** pour **Omega-server**
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Page officielle : [OMEGA-LOG](https://kraynux.snake-mackarel.ts.net/omega-log/) &nbsp; Aperçu : [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-log/screenshots/)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-Textual%20TUI-cyan.svg)](https://github.com/Textualize/textual)

**Langues:**
🇫🇷 **[Français](README.md)** · 🇬🇧 [English](README.en.md) · 🇪🇸 [Español](README.es.md) · 🇷🇺 [Русский](README.ru.md) · 🇨🇳 [中文](README.zh.md)

---

**Omega-log** est l'outil de la suite `omega-` dédié à la gestion, la lecture et l'analyse de fichiers logs serveur en TUI — détection automatique des services actifs et de leurs logs, bibliothèque centrale, trois modes de lecture (suivi simple, lecture classique, fusion multi-fichiers via `lnav`), traitement des IP, statistiques, rotation/sauvegarde/restauration, purge sécurisée et export. Construit par **portage et adaptation** du code déjà mûr d'[omega-fire](https://github.com/kraynux/omega-fire) et [omega-serv](https://github.com/kraynuxomega-serv) plutôt que réécrit depuis zéro.

## 1. Vision et périmètre

Omega-log répond à une question simple : « qu'est-ce qui se passe dans mes logs, et comment je m'en occupe ? » — sans dépendre d'une liste figée de chemins connus, sans jamais tourner en root par défaut, et sans jamais perdre ou corrompre silencieusement un fichier de log réel.

### Ce que fait Omega-log

- Détecte automatiquement les services actifs sur la machine (serveurs web, bases de données, mail, DNS, sécurité, `omega-serv`...) et propose l'import de leurs logs connus, au détail ou en totalité — en complément d'un scan manuel de n'importe quel dossier.
- Centralise les logs à traiter dans une Bibliothèque unique, point d'entrée de tous les autres écrans.
- Lit un log suivant trois modes selon le besoin : suivi simple avec parsing et statistiques, lecture classique brute avec suivi en direct, ou fusion multi-fichiers encapsulant `lnav`.
- Mémorise des combinaisons logs + viewer sous forme de Favoris, pour un lancement direct.
- Calcule le top 10 des IP par période et permet leur suppression ciblée dans un ou plusieurs fichiers.
- Calcule des statistiques d'accès (volume, IPs uniques, taux d'erreur, répartition horaire) exportables en JSON ou HTML à thème.
- Sauvegarde (compression + rétention automatique), restaure (fusion ou écrasement, avec sauvegarde de sécurité) et purge (troncature en place ou suppression) les fichiers de log, toujours avec confirmation explicite.
- S'adapte automatiquement aux capacités du terminal (couleurs, taille) via `omega-lib`, comme le reste de la suite.

### Ce qu'Omega-log ne fait pas

| Fonction | Outil responsable |
|---|---|
| Pare-feu, règles réseau, détection d'intrusion | OMEGA-FIRE |
| Serveur web, reverse proxy, WAF, Active Defense | OMEGA-SERV |
| Scan de ports, identification de services réseau | OMEGA-CHECK |
| Observation réseau, identité numérique d'une cible | OMEGA-TRACK |

Pas (encore) de CLI à parité complète avec la TUI (le mode ligne de commande actuel ne couvre que le scan de services, voir §3.2), pas d'agrégation centralisée multi-machines, pas d'alerting temps réel sur seuil — Omega-log reste un outil d'inspection et de maintenance locale, pas un SIEM.

### Avertissement d'usage

Les actions de maintenance (**Purger**, **Rotate → Restaurer en mode Écrasement**) modifient ou effacent définitivement le contenu réel de vos fichiers de log — toujours précédées d'une confirmation explicite détaillant les fichiers concernés, jamais déclenchées automatiquement. En cas de doute, sauvegardez (**Rotate → Sauvegarder maintenant**) avant d'agir.

## 2. Installation

### Prérequis

- Python 3.10+
- Linux (testé Arch/Manjaro, Debian/Ubuntu, RHEL/Fedora)
- `lnav` installé sur le système, uniquement pour le viewer de fusion multi-fichiers (les deux autres viewers fonctionnent normalement sans) :

```bash
# Arch / Manjaro
sudo pacman -S lnav

# Debian / Ubuntu
sudo apt install lnav
```

### Installation

```bash
[ -d omega-log ] && echo "ℹ️ Déjà extrait ici, étape ignorée." || tar -xzf omega-log.tar.gz
cd omega-log/
chmod +x install.sh
./install.sh
```

`install.sh` :

1. Crée l'environnement virtuel `.venv` s'il n'existe pas déjà.
2. Installe les dépendances (vendored `omega-lib` d'abord si présente, puis `pip install -e .` — `pyproject.toml` reste l'unique source de vérité).
3. Rend `omega-log.sh` et `install.sh` exécutables.
4. Vérifie la présence de `lnav` (avertissement informatif si absent, jamais bloquant).
5. Ajoute l'alias `log` à `~/.bashrc` et `~/.zshrc` (sans doublon si déjà présent).

### Dépendances

Déclarées dans `pyproject.toml` (pas de `requirements.txt` séparé) :
- `omega-lib` : bibliothèque partagée de la suite (thèmes TUI + export, détection de terminal, stockage de réglages)
- `textual` : interface TUI
- `jinja2` : export HTML à thème (statistiques, archives)
- `pyte` : émulation de terminal pour le viewer `lnav` (rendu dans un pty encapsulé)
- Dépendances de développement (`pip install -e ".[dev]"`) : `pytest`, `pytest-asyncio`, `ruff`, `mypy`

## 3. Utilisation

### 3.1. Mode interactif (TUI)

Recommandé pour l'usage quotidien — lancé sans argument :

```bash
./omega-log.sh
```
si vous avez créé l'alias, tapez juste `log` dans un nouveau terminal :
```bash
log
```

Parcours général : écran de démarrage → menu principal (deux colonnes — Registre/Bibliothèque/Voir les logs/Favoris/Voir et Traiter IP/Statistiques d'un côté, Rotate/Purger/Exporter/Options/Aide/Quitter de l'autre) → écran de la fonction choisie → retour au menu (`Échap`). L'aide complète (`a`) détaille chaque écran, chaque viewer et les concepts transverses (élévation sudo ponctuelle, états des logs, sélection par numéros) — voir §4 pour l'essentiel.

#### Raccourcis clavier

| Touche | Action |
|---|---|
| `↑` / `↓` | Naviguer entre les éléments d'un écran |
| `Tab` / `Maj+Tab` | Naviguer entre les champs d'un formulaire |
| `Échap` | Retour à l'écran précédent (confirmation de sortie sur l'accueil) |
| `t` | Thème suivant (appliqué immédiatement, sans confirmation) |
| `r` | Rafraîchir la détection du terminal |
| `a` | Afficher l'aide (exhaustive, un chapitre par écran) |
| `q` | Quitter (avec confirmation) |

### 3.2. Mode ligne de commande (CLI)                                                              

Limité au scan de services pour l'instant (pas encore de parité complète avec la TUI — favoris, rotate, purge viendront avec leurs propres phases, voir `plan_omega_log.md` §12) :

```bash
# Detecte les services actifs et leurs logs connus
python -m omega_log scan

# + scan manuel d'un dossier supplementaire
python -m omega_log scan --path /var/log
```

### 3.3. Variables d'environnement

| Variable | Effet |
|---|---|
| `OMEGA_LOG_VAR_DIR` | Change l'emplacement du dossier d'état applicatif (`./var` par défaut, relatif au dossier de lancement) |

## 4. Fonctionnalités

| Écran | Description |
|---|---|
| **Registre des capacités** | Détecte les services actifs sur la machine et propose l'import de leurs logs connus, au détail ou en totalité. Scan manuel d'un dossier en complément. |
| **Bibliothèque** | Hub central référençant tous les logs à traiter — alimentée par le Registre ou par import manuel. |
| **Voir les logs** | Sélection d'un ou plusieurs logs de la Bibliothèque + choix du viewer (1 log → les 3 viewers ; 2+ logs → `lnav` uniquement). |
| **Favoris** | Combinaisons logs + viewer enregistrées sous un nom, pour un lancement direct. |
| **Voir et Traiter IP** | Top 10 des IP par période (24h/7j/30j/tout) et suppression ciblée d'une IP d'un ou plusieurs logs. |
| **Statistiques (accès)** | Volume, IPs uniques, taux d'erreur, top IP, répartition horaire — export JSON/HTML à 5 thèmes. |
| **Rotate** | Sauvegarde compressée d'un log + rétention automatique des archives excédentaires + restauration (fusion ou écrasement, avec sauvegarde de sécurité). |
| **Purger** | Vide le contenu d'un log (troncature en place, sûre pour un service qui l'a encore ouvert) ou supprime complètement un ou plusieurs fichiers — toujours avec confirmation. |
| **Exporter** | Export de la liste des archives (Rotate) en JSON ou HTML à thème. |
| **Options** | Thème, profil de rendu, purge des dossiers applicatifs (exports/screenshots). |

### Les 3 viewers

1. **Simple** — suivi en direct avec parsing générique (horodatage, IP, niveau, service) et mini-tableau de statistiques. Pour un access log HTTP reconnu, colonnes supplémentaires Code HTTP / latence, colorées par seuil.
2. **Classique** — lecture des dernières lignes brutes + bascule « Suivre en direct », sans parsing : le plus simple et le plus fiable quel que soit le format.
3. **lnav** — fusion de plusieurs fichiers dans un terminal encapsulé (pty), pour une analyse croisée. Cycle de thème (`t`), marquage + copie presse-papier (`Ctrl+C`, OSC 52), sortie (`Ctrl+Q`) — tous interceptés avant `lnav` lui-même.

## 5. Compatibilité terminaux

Le TUI (Textual) détecte automatiquement les capacités du terminal (émulateur, taille) et adapte sa feuille de style structurelle en conséquence (`complete`/`standard`/`reduced`/`mono`), sans flag manuel — même politique partagée par toute la suite `omega-` (`omega-lib`, `terminal/policies.py`). Rafraîchissable en direct par la touche `r`.

### Profil selon l'émulateur détecté

| Émulateur | Profil initial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderne | `reduced` |
| TTY Linux, SSH legacy | `mono` |
| Émulateur non reconnu | `reduced` (repli par défaut) |

### Profil selon la taille du terminal

| Taille minimale (colonnes × lignes) | Plafond de profil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| en dessous | `mono` |

Le profil final retenu est **le plus restrictif des deux** (émulateur et taille).

## 6. Architecture

Clean Architecture (domaine / application / infrastructure / interfaces), même convention que le reste de la suite OMEGA :

```text
src/omega_log/
├── core/            Registre de capacites (detection de services)
├── domain/          Logique metier pure (parsing, statistiques, rotation, purge)
├── ports/           Contrats (Protocol)
├── application/     Cas d'usage
├── infrastructure/  Implementations reelles (probes, stockage, archives, export, lnav, concurrence)
├── interfaces/      TUI (Textual) + CLI
└── app/             Composition root
```

Dépend d'[`omega-lib`](../LIB/omega-lib) pour le thème (10 thèmes TUI + 5 thèmes d'export), la détection de terminal et le stockage de réglages — même socle que le reste de la suite. Les calculs lourds (top IP, statistiques d'accès) s'exécutent dans un `ProcessPoolExecutor` dédié (`infrastructure/concurrency/`), jamais sur le thread d'interface, pour rester réactif même sur un fichier de plusieurs centaines de milliers de lignes.

## 7. Tests

```bash
source .venv/bin/activate
pytest tests/ -q      # 171 tests
ruff check .
mypy src
```

Structure : `tests/unit/` (domaine et application, sans I/O réelle), `tests/integration/` (fichiers réels, TUI headless via l'API `Pilot` de Textual).

## 8. État du développement

Les 10 phases du plan de développement sont terminées : socle, domaine, TUI de base, viewers, favoris/bibliothèque/IP, maintenance, statistiques/export, finalisation, élévation sudo ponctuelle, calculs CPU-bound déportés en processus séparé — voir `plan_omega_log.md` pour le détail de chaque décision de portage.

## 9. Licence

MIT — voir [LICENSE](LICENSE).

---

> Omega-log — Détecter, centraliser, lire, analyser, maintenir.
> Vos logs restent les vôtres : aucune élévation de privilège sans nécessité réelle, aucune action destructrice sans confirmation.
