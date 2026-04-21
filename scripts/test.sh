#!/bin/bash
# Delegate to `bin/plugins-run tests` — the project-level test runner
# discovers the project and per-plugin suites, resolves each suite's own
# venv, runs pytest per suite, and compiles a unified report. Arguments
# are forwarded (e.g. --plugin, --project).
set -e

exec "$(dirname "$(readlink -f "$0")")/../bin/plugins-run" tests "$@"
