SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

source "$SCRIPT_DIR/venv/bin/activate"

"$SCRIPT_DIR/venv/bin/python" "$SCRIPT_DIR/deploy.py" "$@"
