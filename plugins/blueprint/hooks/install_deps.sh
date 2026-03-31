#!/bin/bash
# Install Python dependencies into plugin venv.
# Runs on SessionStart; skips when requirements.txt unchanged.

set -euo pipefail

requirements="$CLAUDE_PLUGIN_ROOT/requirements.txt"
cached="$CLAUDE_PLUGIN_DATA/requirements.txt"
venv_dir="$CLAUDE_PLUGIN_DATA/venv"

# Skip if requirements unchanged since last install
if diff -q "$requirements" "$cached" >/dev/null 2>&1; then
    exit 0
fi

# Check for uv
if ! command -v uv >/dev/null 2>&1; then
    echo "blueprint plugin: uv is required to install Python dependencies." >&2
    echo "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    echo "MCP server will not be available until uv is installed." >&2
    exit 1
fi

# Create venv and install
if uv venv --seed "$venv_dir" --quiet \
    && "$venv_dir/bin/pip" install -q -r "$requirements"; then
    cp "$requirements" "$cached"
else
    rm -f "$cached"
    exit 1
fi
