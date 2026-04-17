#!/bin/bash
# Install Python dependencies into plugin venv.
# Runs on SessionStart; idempotent — always verifies venv and deps.
#
# Canonical copy lives under plugins/ocd/hooks/ and is propagated to
# every plugin's hooks/install_deps.sh via the pre-commit hook.

set -euo pipefail

plugin_name=$(python3 -c "import json; print(json.load(open('$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json'))['name'])")
requirements="$CLAUDE_PLUGIN_ROOT/requirements.txt"
venv_dir="$CLAUDE_PLUGIN_DATA/venv"

# Check for uv
if ! command -v uv >/dev/null 2>&1; then
    echo "$plugin_name plugin: uv is required to install Python dependencies." >&2
    echo "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    echo "MCP server will not be available until uv is installed." >&2
    exit 1
fi

# Ensure venv exists and install/update dependencies — both are idempotent
uv venv --seed "$venv_dir" --quiet --allow-existing
"$venv_dir/bin/pip" install -q -r "$requirements"

# If the plugin ships bash wrappers in bin/, persist the venv python path
# so they can find it without relying on CLAUDE_PLUGIN_DATA (which isn't
# exposed in agent shells).
if [ -d "$CLAUDE_PLUGIN_ROOT/bin" ]; then
    echo "$venv_dir/bin/python3" > "$CLAUDE_PLUGIN_ROOT/.venv-python"
fi
