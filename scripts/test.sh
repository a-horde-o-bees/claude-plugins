#!/bin/bash
# Run all test layers — mirrors production isolation per plugin.
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

echo ""
echo "=== OCD plugin tests ==="
.venv/bin/python3 -m pytest plugins/ocd/ -c plugins/ocd/pytest.ini -v "${ocd_args[@]}" "${common_args[@]}"

echo ""
echo "=== Blueprint plugin tests ==="
.venv/bin/python3 -m pytest plugins/blueprint/ -c plugins/blueprint/pytest.ini -v "${common_args[@]}"

echo ""
echo "All tests passed."
