#!/usr/bin/env bash
set -e
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi
echo
echo "Virtual environment ready. To activate later:"
echo "  source .venv/bin/activate"
