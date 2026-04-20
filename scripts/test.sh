#!/bin/bash
# Delegate to `ocd-run tests` — the framework's test runner discovers the
# project and per-plugin suites, resolves each suite's own venv, runs
# pytest per suite, and compiles a unified report. Arguments are forwarded
# (e.g. --plugin, --project).
set -e

exec ocd-run tests "$@"
