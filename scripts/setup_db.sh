#!/usr/bin/env bash
set -euo pipefail
# Usage: copy .env.example to .env and edit DATABASE_URL, then run:
#   bash scripts/setup_db.sh

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd -P)
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  echo ".env not found. Copying .env.example to .env"
  cp .env.example .env
  echo "Edit .env and set the proper DATABASE_URL if needed, then re-run this script."
  exit 1
fi

export $(grep -v '^#' .env | xargs)
export FLASK_APP=run.py

echo "Running database upgrade (Flask-Migrate)..."
flask --app run.py db upgrade

echo "Database migrations applied."
