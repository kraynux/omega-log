#!/usr/bin/env bash
# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
# ==============================================================================
# Script d'installation - OMEGA-LOG
# À lancer depuis le dossier extrait de l'archive : cd omega-log && ./install.sh
# Résilient : peut être relancé sans erreur si une étape a déjà été faite.
# Aucune étape ici ne nécessite les privilèges root : omega-log refuse
# lui-même de démarrer en tant que root par défaut (voir plan_omega_log.md
# §5/§5.1, délégation par groupe systeme plutôt qu'élévation complète).
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; }
tip()  { echo -e "${WHITE}💡 $1${NC}"; }

echo -e "${WHITE}    ░▒▓█████████████████████████████████████████████▓▒░${NC}"
echo -e "${WHITE}    ░▒▓█ Ω M E G A - LOG — I N S T A L L A T I O N █▓▒░${NC}"
echo -e "${WHITE}    ░▒▓█████████████████████████████████████████████▓▒░${NC}"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# -------------------------------------------------------------------------
# 1. Environnement virtuel Python
# -------------------------------------------------------------------------
if [ -d ".venv" ]; then
    info ".venv existe déjà, création ignorée."
else
    if ! python3 -m venv .venv 2>/tmp/omega-log-venv-err.log; then
        err "Échec de la création de l'environnement virtuel."
        warn "Sur Debian/Ubuntu (et dérivées), le module venv n'est pas toujours inclus avec python3 de base."
        tip "Installez-le puis relancez ce script : sudo apt install python3-venv"
        cat /tmp/omega-log-venv-err.log >&2
        rm -f /tmp/omega-log-venv-err.log
        exit 1
    fi
    rm -f /tmp/omega-log-venv-err.log
    ok "Environnement virtuel créé (.venv)."
fi

# -------------------------------------------------------------------------
# 2. Dépendances — pyproject.toml reste l'unique source de verite.
#    omega-lib n'est pas publiee sur PyPI : l'archive distribuable la
#    vendore dans vendor/omega-lib/ (meme convention que CHECK/DEEP/FOLD/
#    FUZZ/TRACK/SCAN/SERV) - installee ICI, avant omega-log lui-meme, pour
#    que pip la trouve deja satisfaite dans le venv. Absente en clone de
#    developpement (omega-lib vient alors du monorepo local
#    ~/DEV/LIB/omega-lib, deja installee a part) : etape silencieusement
#    ignoree si vendor/omega-lib/ n'existe pas.
# -------------------------------------------------------------------------
source .venv/bin/activate
pip install -q --upgrade pip
if [ -d "$SCRIPT_DIR/vendor/omega-lib" ]; then
    pip install -q -e "$SCRIPT_DIR/vendor/omega-lib"
    ok "Dépendance vendorée omega-lib installée."
fi
pip install -q -e .
ok "Dépendances installées."

# -------------------------------------------------------------------------
# 3. Scripts exécutables
# -------------------------------------------------------------------------
chmod +x omega-log.sh
chmod +x "$SCRIPT_DIR/install.sh"
ok "Scripts rendus exécutables."

# -------------------------------------------------------------------------
# 4. Verification de la presence de lnav (necessaire uniquement pour le
#    Viewer 3 - fusion multi-fichiers ; les Viewers 1 et 2 fonctionnent
#    normalement sans). Jamais installe ici : binaire systeme de la
#    distribution, pas une dependance Python du projet (voir
#    infrastructure/probe/lnav_capability.py, qui fait la meme detection
#    au runtime pour degrader proprement le menu si absent).
# -------------------------------------------------------------------------
if command -v lnav >/dev/null 2>&1; then
    ok "lnav détecté ($(lnav -V 2>&1 | head -n1))."
else
    warn "lnav introuvable : le Viewer 3 (fusion multi-fichiers) ne fonctionnera pas."
    tip "Arch/Manjaro : sudo pacman -S lnav  —  Debian/Ubuntu : sudo apt install lnav"
fi

# -------------------------------------------------------------------------
# 5. Alias (optionnel) — bash et zsh, quel que soit celui réellement utilisé.
#    Pas de sudo ici : omega-log refuse lui-meme de demarrer en tant que
#    root par defaut (voir plan_omega_log.md §5.1).
# -------------------------------------------------------------------------
ALIAS_LINE="alias log=\"${SCRIPT_DIR}/omega-log.sh\""

for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    rc_name="$(basename "$rc")"
    if grep -qxF "$ALIAS_LINE" "$rc" 2>/dev/null; then
        info "Alias déjà présent dans $rc_name."
    elif echo "$ALIAS_LINE" >> "$rc" 2>/dev/null; then
        ok "Alias ajouté à $rc_name."
    else
        warn "Impossible d'ajouter l'alias à $rc_name."
    fi
done

echo ""
ok "Installation terminée."
tip "Lancez Omega-Log avec : ${SCRIPT_DIR}/omega-log.sh (ou 'log' dans un nouveau terminal si l'alias vient d'être ajouté)."
