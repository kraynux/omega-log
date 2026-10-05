#!/usr/bin/env bash
# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
# ==============================================================================
# Script de lancement - OMEGA-LOG
# Aucun privilege particulier requis pour lancer ce script - l'application
# elle-meme refuse de demarrer en tant que root par defaut (voir
# plan_omega_log.md §5/§5.1 : prefere la delegation par groupe systeme a
# l'elevation complete), meme choix que omega-serv.
# Dispatch TUI (aucun argument) / CLI (au moins un argument) gere par
# __main__.py - meme patron que le reste de la suite omega-. Pas de
# OMEGA_LOG_VAR_DIR a exporter ici : la racine var/ par defaut est relative
# au repertoire courant d'execution (infrastructure/config/paths.py::
# resolve_var_dir()), pas a l'emplacement du script - comportement voulu,
# cf. plan_omega_log.md §5 (meme convention que CHECK/FIRE/TRACK, a la
# difference de SERV).
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

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
exec omega-log "$@"
