#!/usr/bin/env bash
# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
# ==============================================================================
# Construit l'archive distribuable omega-log.tar.gz : copie le projet
# (sans artefacts dev/runtime ni donnees personnelles), vendore omega-lib
# (dependance obligatoire non publiee sur PyPI, voir install.sh), archive
# le tout dans ../dist/. Outil de maintenance, jamais lui-meme inclus
# dans l'archive generee. Meme patron que build-release.sh du reste de
# la suite omega- (TRACK/CHECK/FOLD/FUZZ/SCAN/SERV).
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${CYAN}ℹ️  $1${NC}"; }
ok()   { echo -e "${GREEN}✅ $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; }

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OMEGA_LIB_SRC="${OMEGA_LIB_SRC:-$HOME/DEV/LIB/omega-lib}"
DIST_DIR="${DIST_DIR:-$PROJECT_ROOT/../dist}"
ARCHIVE_NAME="omega-log.tar.gz"

if [ ! -d "$OMEGA_LIB_SRC" ]; then
    err "omega-lib introuvable : $OMEGA_LIB_SRC (definissez OMEGA_LIB_SRC si le chemin differe)."
    exit 1
fi

STAGING_DIR="$(mktemp -d)"
trap 'rm -rf "$STAGING_DIR"' EXIT
DEST="$STAGING_DIR/omega-log"
mkdir -p "$DEST"

info "Copie du projet omega-log..."
rsync -a \
    --exclude='.venv/' --exclude='venv/' \
    --exclude='__pycache__/' --exclude='*.pyc' \
    --exclude='.pytest_cache/' --exclude='.mypy_cache/' --exclude='.ruff_cache/' \
    --exclude='*.egg-info/' \
    --exclude='.git/' --exclude='.claude/' \
    --exclude='var/app.log' --exclude='var/*.jsonl' \
    --exclude='var/favorites.json' --exclude='var/library.json' --exclude='var/settings.json' \
    --include='var/backups/.gitkeep' --exclude='var/backups/*' \
    --include='var/exports/.gitkeep' --exclude='var/exports/*' \
    --exclude='*~' --exclude='*.bak' --exclude='*.swp' \
    --exclude='.coverage' --exclude='htmlcov/' \
    --exclude='vendor/' \
    --exclude='build-release.sh' --exclude='omega-log.tar.gz' \
    "$PROJECT_ROOT/" "$DEST/"

info "Vendoring d'omega-lib (dependance obligatoire, non publiee sur PyPI)..."
mkdir -p "$DEST/vendor/omega-lib"
rsync -a \
    --exclude='.venv/' --exclude='__pycache__/' --exclude='*.pyc' \
    --exclude='.pytest_cache/' --exclude='.mypy_cache/' --exclude='.ruff_cache/' \
    --exclude='*.egg-info/' --exclude='.git/' --exclude='tests/' \
    --exclude='*~' --exclude='*.bak' --exclude='*.swp' \
    "$OMEGA_LIB_SRC/" "$DEST/vendor/omega-lib/"

info "Archivage..."
mkdir -p "$DIST_DIR"
tar -C "$STAGING_DIR" -czf "$DIST_DIR/$ARCHIVE_NAME" omega-log

ok "Archive generee : $DIST_DIR/$ARCHIVE_NAME"
echo "sha256sum :"
sha256sum "$DIST_DIR/$ARCHIVE_NAME"
