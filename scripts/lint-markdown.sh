#!/usr/bin/env bash
# lint-markdown.sh — lint the repo's markdown with the suite's own linter
# (skills/markdown-authoring/scripts/lint.mjs, mirrored from the live skill).
# The spec it enforces is skills/markdown-authoring/lint-spec.md; the default
# run skips dot-directories, so the linter's own .fixtures/ never reports.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

node skills/markdown-authoring/scripts/lint.mjs README.md CHANGELOG.md CLAUDE.md skills
