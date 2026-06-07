#!/usr/bin/env sh
# detect.sh — mechanical repo-health detector for /git doctor.
#
# Cheap, local, no network. Scans the problem domains that gate everyday
# commit/push/checkpoint work and emits a parseable report the skill dispatches
# on. Per-commit domains only: submodule conformance (BLOCKING — committing
# through drift escalates Tier 1 into Tier 2 history pollution) and default-branch
# resolvability (ADVISORY). The CI domain is on-demand / on-workflow-change and is
# NOT run here.
#
# Output (stdout): one `STATUS:` line, then one line per detected problem:
#   STATUS: healthy | problems | not-a-repo
#   submodule BLOCKING <detail>
#   default-branch ADVISORY <detail>
# Submodule drift detail (the git-roots state table) follows on stderr.
#
# Exit: 0 healthy, 1 a BLOCKING problem present, 3 ADVISORY-only, 2 not a git repo.

set -eu

DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "STATUS: not-a-repo"
  exit 2
fi

blocking=0
advisory=0
lines=""

# --- submodule conformance (BLOCKING) — delegate to git-roots.sh ---
# git-roots.sh roots: exit 0 conforming, exit 1 drift (state table on stderr), exit 2 not-a-repo.
roots_rc=0
sh "$DIR/git-roots.sh" roots >/dev/null 2>/tmp/.gd-roots-err || roots_rc=$?
if [ "$roots_rc" -eq 1 ]; then
  blocking=$((blocking + 1))
  lines="${lines}submodule BLOCKING submodule drift — see table below
"
  # surface the state table on stderr for the skill to bind
  cat /tmp/.gd-roots-err >&2 2>/dev/null || true
fi
rm -f /tmp/.gd-roots-err 2>/dev/null || true

# --- default-branch resolvability (ADVISORY) ---
if [ -z "$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)" ]; then
  advisory=$((advisory + 1))
  lines="${lines}default-branch ADVISORY origin/HEAD unset — branch resolution falls back; fix with: git remote set-head origin -a
"
fi

# --- submodule routing native-key gaps (ADVISORY) — local, no network ---
# A declared submodule with no `branch =` makes recursive push fall back to the
# checked-out branch (or exit if detached). Flag it so the native key can be
# written into the parent's .gitmodules. The gh-based routing audit (ownership,
# fork-contribution, protection) is computed live by /git checkpoint, not here.
if [ -f .gitmodules ]; then
  routing_gaps=$(git config -f .gitmodules --get-regexp '^submodule\..+\.path$' 2>/dev/null \
    | while read -r key path; do
        name=$(printf '%s' "$key" | sed -E 's/^submodule\.(.+)\.path$/\1/')
        if [ -z "$(git config -f .gitmodules --get "submodule.${name}.branch" 2>/dev/null)" ]; then
          printf 'submodule-routing ADVISORY submodule %s has no `branch =` in .gitmodules — recursive push falls back to the checked-out branch; /git doctor can write the native key\n' "$path"
        fi
      done)
  if [ -n "$routing_gaps" ]; then
    advisory=$((advisory + 1))
    lines="${lines}${routing_gaps}
"
  fi
fi

# --- CI config (ADVISORY, on-workflow-change only) ---
# The CI domain is on-demand; the detector flags it only when the change being
# committed touches workflows, so a CI-config edit gets a hardening pass.
if git diff --cached --name-only 2>/dev/null | grep -q '^\.github/workflows/'; then
  advisory=$((advisory + 1))
  lines="${lines}ci ADVISORY workflow files in this change — run the CI domain (\`/git doctor ci\`) to audit/harden
"
fi

if [ "$blocking" -gt 0 ]; then
  echo "STATUS: problems"
  printf '%s' "$lines"
  exit 1
elif [ "$advisory" -gt 0 ]; then
  echo "STATUS: problems"
  printf '%s' "$lines"
  exit 3
else
  echo "STATUS: healthy"
  exit 0
fi
