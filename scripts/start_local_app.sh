#!/bin/zsh
set -e

APP_DIR="/Users/djblubloods/Downloads/Blu Royal Temp"
PYTHON_BIN="$APP_DIR/venv/bin/python"
LOG_FILE="$APP_DIR/app.log"

PIDS=$(lsof -ti:8000 2>/dev/null || true)
if [ -n "$PIDS" ]; then
  kill $PIDS 2>/dev/null || true
  sleep 1
fi

cd "$APP_DIR"
exec "$PYTHON_BIN" -m uvicorn src.main:app --host 127.0.0.1 --port 8000 >> "$LOG_FILE" 2>&1
