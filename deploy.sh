#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/venv/bin/activate"

python_path="$SCRIPT_DIR/venv/bin/python"

python "$python_path" "$SCRIPT_DIR/deploy.py" "$@"