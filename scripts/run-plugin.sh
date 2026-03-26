#!/usr/bin/env bash
#
# Run a plugin's CLI with correct environment variables.
#
# Usage:
#   ./scripts/run-plugin.sh <plugin> <command> [args...]
#   ./scripts/run-plugin.sh ocd status
#   ./scripts/run-plugin.sh ocd init --force
#   ./scripts/run-plugin.sh blueprint status
#
# For skill CLIs, use the skill's CLI script path directly:
#   ./scripts/run-plugin.sh blueprint skills/research/scripts/research_cli.py init --db /tmp/test.db

set -euo pipefail

if [ $# -lt 2 ]; then
    echo "Usage: $0 <plugin> <command> [args...]" >&2
    exit 1
fi

PLUGIN="$1"
shift

PLUGIN_DIR="plugins/${PLUGIN}"

if [ ! -d "$PLUGIN_DIR" ]; then
    echo "Error: plugin directory not found: ${PLUGIN_DIR}" >&2
    exit 1
fi

export CLAUDE_PLUGIN_ROOT="$PLUGIN_DIR"
export CLAUDE_PROJECT_DIR="$(pwd)"
export PYTHONPATH="${PLUGIN_DIR}/scripts"

# If first arg is a .py file path, run it directly (skill CLI)
if [[ "$1" == *.py ]]; then
    SCRIPT="$1"
    shift
    exec python3 "${PLUGIN_DIR}/${SCRIPT}" "$@"
fi

# Otherwise, run plugin_cli.py with the args
exec python3 "${PLUGIN_DIR}/scripts/plugin_cli.py" "$@"
