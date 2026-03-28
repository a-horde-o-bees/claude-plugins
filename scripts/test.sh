#!/bin/bash
# Run all test layers — mirrors production isolation per plugin.
set -e

echo "=== Project tests ==="
.venv/bin/python3 -m pytest tests/ -v

echo ""
echo "=== OCD plugin tests ==="
.venv/bin/python3 -m pytest plugins/ocd/ -c plugins/ocd/pytest.ini -v

echo ""
echo "=== Blueprint plugin tests ==="
.venv/bin/python3 -m pytest plugins/blueprint/ -c plugins/blueprint/pytest.ini -v

echo ""
echo "All tests passed."
