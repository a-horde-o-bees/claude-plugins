#!/bin/bash
# Install Python dependencies into plugin venv.
# Runs on SessionStart. Docs-prescribed pattern: diff -q change detection
# against a cached manifest, with rm-on-failure so the next session retries.
#
# Canonical copy lives under plugins/ocd/hooks/ and is propagated to
# every plugin's hooks/install_deps.sh via the pre-commit hook.

set -euo pipefail

plugin_name=$(python3 -c "import json; print(json.load(open('$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json'))['name'])")
manifest="$CLAUDE_PLUGIN_ROOT/pyproject.toml"
cached_manifest="$CLAUDE_PLUGIN_DATA/pyproject.toml"
venv_dir="$CLAUDE_PLUGIN_DATA/venv"

if ! command -v uv >/dev/null 2>&1; then
    echo "$plugin_name plugin: uv is required to install Python dependencies." >&2
    echo "Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
    echo "MCP server will not be available until uv is installed." >&2
    exit 1
fi

# Reinstall when the venv is missing, the cached manifest is missing, or the
# bundled manifest differs from the cached copy. Existence checks catch
# first-run and upgrade-removed-venv cases; diff -q catches upstream changes.
needs_install=0
if [ ! -x "$venv_dir/bin/python3" ]; then
    needs_install=1
elif [ ! -f "$cached_manifest" ]; then
    needs_install=1
elif ! diff -q "$manifest" "$cached_manifest" >/dev/null 2>&1; then
    needs_install=1
fi

if [ "$needs_install" = "1" ]; then
    # Retry-next-session invariant: if install fails mid-way, remove the
    # cached manifest so the next session's diff -q sees a mismatch and
    # retries. Without this, a partial failure leaves a stale cached
    # manifest in place and the plugin stays broken silently.
    mkdir -p "$CLAUDE_PLUGIN_DATA"
    trap 'rm -f "$cached_manifest"' ERR

    uv venv --seed "$venv_dir" --quiet --allow-existing
    uv pip install --quiet --requirement "$manifest" --python "$venv_dir/bin/python3"

    # Record the installed manifest only after success — poisoned cache
    # would otherwise skip install on the next session.
    cp "$manifest" "$cached_manifest"
    trap - ERR
fi

# If the plugin ships bash wrappers in bin/, persist the venv python path
# so they can find it without relying on CLAUDE_PLUGIN_DATA (which isn't
# exposed in agent shells).
if [ -d "$CLAUDE_PLUGIN_ROOT/bin" ]; then
    echo "$venv_dir/bin/python3" > "$CLAUDE_PLUGIN_ROOT/.venv-python"
fi
