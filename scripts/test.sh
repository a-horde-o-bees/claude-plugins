#!/bin/bash
# Run all test layers — each plugin's tests run under that plugin's own venv,
# mirroring the runtime isolation Claude Code provides at session time.
# --run-agent: include agent tests in ocd suite (spawns claude CLI, real API calls).
# Other args forwarded to all pytest invocations.
set -e

ocd_args=()
common_args=()
for arg in "$@"; do
    case "$arg" in
        --run-agent) ocd_args+=("$arg") ;;
        *) common_args+=("$arg") ;;
    esac
done

echo "=== Project tests ==="
.venv/bin/python3 -m pytest tests/ -v "${common_args[@]}"

OCD_PLUGIN_DATA="${HOME}/.claude/plugins/data/ocd-a-horde-o-bees"
OCD_VENV_PY="${OCD_PLUGIN_DATA}/venv/bin/python3"
if [ ! -x "${OCD_VENV_PY}" ]; then
    echo ""
    echo "ERROR: ocd plugin venv not found at ${OCD_VENV_PY}."
    echo "Install the plugin first via Claude Code:"
    echo "    /plugin install ocd@a-horde-o-bees"
    echo "or ensure ${OCD_PLUGIN_DATA} exists with a populated venv."
    exit 1
fi

echo ""
echo "=== OCD plugin tests ==="
CLAUDE_PLUGIN_DATA="${OCD_PLUGIN_DATA}" "${OCD_VENV_PY}" -m pytest plugins/ocd/ \
    -c plugins/ocd/pytest.ini -v "${ocd_args[@]}" "${common_args[@]}"

echo ""
echo "All tests passed."
