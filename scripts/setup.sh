#!/usr/bin/env bash

# Environment setup for Codex agents
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv package manager..."
  pip install uv
fi

if [ ! -d ".venv" ]; then
  uv venv
fi

source .venv/bin/activate

uv sync --all-extras

if [ ! -f .env ]; then
  cp config/.env.example .env
  echo "Created .env from template"
fi

uv run pre-commit install

echo "Environment setup complete."
