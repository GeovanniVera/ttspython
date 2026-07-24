#!/usr/bin/env bash
# PDF To Speech Studio — Desktop Launcher
# Installed by ~/.local/share/applications/ttspython.desktop
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$APP_DIR/.venv"
PYTHON="$VENV_DIR/bin/python"
LAUNCH_LOG_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/ttspython"
LAUNCH_LOG="$LAUNCH_LOG_DIR/launcher.log"
ENTRY_POINT="$APP_DIR/main_hexagonal.py"
NOTIFY="notify-send --app-name='PDF To Speech Studio' --icon=$APP_DIR/app.png"

mkdir -p "$LAUNCH_LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LAUNCH_LOG"
}

notify() {
    local urgency="${2:-normal}"
    $NOTIFY --urgency="$urgency" "PDF To Speech Studio" "$1" 2>/dev/null || true
}

# ── Step 1: Ensure venv exists with critical modules ──
if [ ! -f "$PYTHON" ]; then
    log "Venv no encontrado. Creando..."
    notify "Creando entorno virtual..." normal
    python3 -m venv "$VENV_DIR" >> "$LAUNCH_LOG" 2>&1
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Quick check: can we import PySide6?
if ! "$PYTHON" -c "import PySide6" 2>/dev/null; then
    log "PySide6 no importable. Instalando dependencias..."
    notify "Instalando dependencias…" normal
    "$PYTHON" -m pip install -r "$APP_DIR/requirements.txt" >> "$LAUNCH_LOG" 2>&1 || {
        log "FALLO: pip install falló."
        notify "Error al instalar dependencias. Revisá $LAUNCH_LOG" critical
        exit 1
    }
fi

# ── Step 2: Launch the app ──
log "Lanzando $ENTRY_POINT"
cd "$APP_DIR"

if ! "$PYTHON" "$ENTRY_POINT" >> "$LAUNCH_LOG" 2>&1; then
    EXIT_CODE=$?
    log "FALLO: Exit code $EXIT_CODE"
    notify "La aplicación cerró inesperadamente (código $EXIT_CODE). Revisá $LAUNCH_LOG" critical
    exit $EXIT_CODE
fi
