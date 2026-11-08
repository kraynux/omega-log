#!/usr/bin/env bash
# Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE)
# ==============================================================================
# Construit l'archive distribuable omega-log-<version>.tar.gz : copie le projet
# (sans artefacts dev/runtime ni donnees personnelles), vendore omega-lib
# (dependance obligatoire non publiee sur PyPI, voir install.sh), archive
# le tout dans ../html/download/ (dossier publie du site, /omega-log/download/)
# et ajoute son empreinte a sha.txt (format sha256sum, une ligne par version) :
# meme modele de publication qu'omega-serv depuis la 1.6.0 (2026-11-07), lu par
# « Verifier les mises a jour ». Version = pyproject.toml, seule source.
# Outil de maintenance, jamais lui-meme inclus dans l'archive generee.
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
DIST_DIR="${DIST_DIR:-$PROJECT_ROOT/../html/download}"
VERSION="$(sed -n 's/^version = "\(.*\)"$/\1/p' "$PROJECT_ROOT/pyproject.toml" | head -n1)"
if [ -z "$VERSION" ]; then
    err "Version introuvable dans pyproject.toml."
    exit 1
fi
ARCHIVE_NAME="omega-log-$VERSION.tar.gz"
SHA_FILE="$DIST_DIR/sha.txt"

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
    --exclude='var/rotation_automations.json' --exclude='var/rotation-automations.log' \
    --exclude='var/declaration*' --exclude='var/remote-log-sources.json' --exclude='var/remote/' \
    --include='var/backups/.gitkeep' --exclude='var/backups/*' \
    --include='var/exports/.gitkeep' --exclude='var/exports/*' \
    --exclude='*~' --exclude='*.bak' --exclude='*.swp' \
    --exclude='.coverage' --exclude='htmlcov/' \
    --exclude='vendor/' \
    --exclude='build-release.sh' --exclude='omega-log.tar.gz' --exclude='omega-log-*.tar.gz' \
    "$PROJECT_ROOT/" "$DEST/"

info "Vendoring d'omega-lib (dependance obligatoire, non publiee sur PyPI)..."
mkdir -p "$DEST/vendor/omega-lib"
rsync -a \
    --exclude='.venv/' --exclude='__pycache__/' --exclude='*.pyc' \
    --exclude='.pytest_cache/' --exclude='.mypy_cache/' --exclude='.ruff_cache/' \
    --exclude='*.egg-info/' --exclude='.git/' --exclude='tests/' \
    --exclude='*~' --exclude='*.bak' --exclude='*.swp' \
    "$OMEGA_LIB_SRC/" "$DEST/vendor/omega-lib/"

# Langues de l'interface et des exports (meme mecanisme que la suite omega) : chaque .po de
# l'archive (omega-log, omega-lib vendoree et son catalogue partage) est recompile en .mo depuis
# sa source - jamais un .mo plus ancien que son .po ; .po et .pot ne sont pas livres.
if find "$DEST" -name '*.po' -path '*/LC_MESSAGES/*' | grep -q .; then
    if ! command -v msgfmt > /dev/null; then
        err "msgfmt introuvable (paquet gettext) : impossible de compiler les langues."
        exit 1
    fi
    info "Compilation des langues..."
    while IFS= read -r po; do
        msgfmt --check -o "${po%.po}.mo" "$po" || { err "Catalogue invalide : $po"; exit 1; }
        rm -f "$po"
    done < <(find "$DEST" -name '*.po' -path '*/LC_MESSAGES/*')
    find "$DEST" -name '*.pot' -path '*/locale/*' -delete
fi

info "Archivage..."
mkdir -p "$DIST_DIR"
tar -C "$STAGING_DIR" -czf "$DIST_DIR/$ARCHIVE_NAME" omega-log

# sha.txt (repris d'omega-serv build-release.sh) : en-tete, puis une section par version, la plus recente
# en tete. Version reconstruite : sa ligne est remplacee sur place (jamais deux empreintes pour le meme
# nom). Reste lisible par `sha256sum -c --ignore-missing`.
SHA_LINE="$(cd "$DIST_DIR" && sha256sum "$ARCHIVE_NAME")"
SHA_LINE="$SHA_LINE" ARCHIVE_NAME="$ARCHIVE_NAME" VERSION="$VERSION" python3 - "$SHA_FILE" <<'PY'
import os, sys
path = sys.argv[1]
line, name, version = os.environ["SHA_LINE"], os.environ["ARCHIVE_NAME"], os.environ["VERSION"]
sep = "=" * 89
lines = open(path, encoding="utf-8").read().splitlines() if os.path.exists(path) else []
if not any(l.strip() for l in lines):
    lines = ["", sep, "Controle d integrite des archives OMEGA-LOG", "", sep, ""]
if any(l.endswith("  " + name) for l in lines):
    lines = [line if l.endswith("  " + name) else l for l in lines]
elif f"version {version} :" in lines:
    i = lines.index(f"version {version} :")
    lines[i + 1:i + 1] = ["", line]
else:
    first = next((i for i, l in enumerate(lines) if l.startswith("version ")), len(lines))
    lines[first:first] = [f"version {version} :", "", line, "", sep, ""]
open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
PY

ok "Archive generee : $DIST_DIR/$ARCHIVE_NAME"
echo "sha256sum (ajoute a $SHA_FILE) :"
echo "$SHA_LINE"
