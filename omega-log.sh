#!/usr/bin/env bash
# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
# ==============================================================================
# Script de lancement - OMEGA-LOG
# Aucun privilege particulier requis pour lancer ce script - l'application
# elle-meme refuse de demarrer en tant que root par defaut (voir
# plan_omega_log.md §5/§5.1 : prefere la delegation par groupe systeme a
# l'elevation complete), meme choix que omega-serv.
# Dispatch TUI (aucun argument) / CLI (au moins un argument) gere par
# __main__.py - meme patron que le reste de la suite omega-.
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
WHITE='\033[1;37m'
NC='\033[0m'

echo -e "${WHITE}${NC}"
echo -e "${WHITE}DÉMARRAGE DE L'APPLICATION${NC}"
echo -e "${WHITE}${NC}"
echo -e "${WHITE}    ░▒▓█████████████████████▓▒░${NC}"
echo -e "${WHITE}    ░▒▓█ Ω M E G A - L O G █▓▒░${NC}"
echo -e "${WHITE}    ░▒▓█████████████████████▓▒░${NC}"
echo -e "${WHITE}${NC}"
echo -e "${WHITE}Chargement en cours...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}❌ Environnement virtuel introuvable : $VENV_DIR${NC}"
    echo ""
    echo "Lancez d'abord : $SCRIPT_DIR/install.sh"
    exit 1
fi

if ! "$VENV_DIR/bin/python" -c "import omega_log" 2>/dev/null; then
    echo "⚠️  Le venv semble incomplet, reinstallation..."
    if [ -d "$SCRIPT_DIR/vendor/omega-lib" ]; then
        "$VENV_DIR/bin/pip" install -q -e "$SCRIPT_DIR/vendor/omega-lib"
    fi
    "$VENV_DIR/bin/pip" install -q -e "$SCRIPT_DIR"
fi

# Ancrer var/ (Bibliotheque, favoris, reglages, app.log, exports) sur l'emplacement du script, jamais sur le
# repertoire courant du shell (meme ligne qu'omega-check et omega-track). Sans elle, `log` lance depuis / voulait
# ecrire /var/app.log (PermissionError, constate sur hpc-109 le 2026-11-26), et lance depuis un autre dossier il
# ouvrait une Bibliotheque vide. $OMEGA_LOG_VAR_DIR, s'il est deja defini, reste prioritaire.
export OMEGA_LOG_VAR_DIR="${OMEGA_LOG_VAR_DIR:-$SCRIPT_DIR/var}"

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
exec omega-log "$@"
