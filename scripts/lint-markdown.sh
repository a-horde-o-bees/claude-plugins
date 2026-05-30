#!/usr/bin/env bash
# lint-markdown.sh — lint git-tracked markdown against the project criteria
# (plugins/writing/skills/markdown-linter/criteria.md).
#
# File selection: every markdown file git tracks, minus the paths listed in
# lint/markdown-ignore.txt — the files we own and author, nothing scratch,
# borrowed, or journaled.
#
# Two passes: gating (fails CI on violation) then warn (reported only).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

IGNORE_FILE="lint/markdown-ignore.txt"

# Build git pathspecs: '*.md' plus a :(glob,exclude) entry per ignore pattern.
pathspecs=( '*.md' )
if [[ -f "$IGNORE_FILE" ]]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"                          # strip trailing comment
    line="${line#"${line%%[![:space:]]*}"}"     # ltrim
    line="${line%"${line##*[![:space:]]}"}"     # rtrim
    [[ -z "$line" ]] && continue
    pathspecs+=( ":(glob,exclude)$line" )
  done < "$IGNORE_FILE"
fi

# NUL-delimited so paths with spaces or special characters pass through intact.
mapfile -d '' -t FILES < <(git ls-files -z -- "${pathspecs[@]}")
if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "lint-markdown: no tracked markdown files to lint"
  exit 0
fi
echo "lint-markdown: ${#FILES[@]} files"

status=0
echo "== gating pass =="
npx --yes markdownlint-cli2 --config lint/gating.markdownlint-cli2.jsonc -- "${FILES[@]}" || status=$?

echo "== warn pass (non-gating) =="
npx --yes markdownlint-cli2 --config lint/warn.markdownlint-cli2.jsonc -- "${FILES[@]}" || true

exit "$status"
