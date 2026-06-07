# PR methodology

> How this project opens and merges pull requests. Read by `/git pr-open`, `/git pr-status`, and `/git pr-merge`. Solo-vs-team gating is detected at runtime from branch protection — this file records preferences, not the live gate.

## Base branch

- Default base: `main`

## Merge strategy

- Default strategy: `squash`
- Allowed (from repo settings): `squash`
- Strategy is `default ∩ repo-allowed`; the default is overridable per merge via `--strategy`.

## Draft

- Open as draft by default: `no`

## Reviews

- Required reviewers: none configured (solo) — branch protection, if present, is authoritative at merge time
- On a protected base, `/git pr-merge` waits for required approvals + green CI (team path); on an unprotected base it merges immediately once CI is green (solo path)

## Conflict / behind-base recovery

- Default: exit to user with `git rebase {base}` guidance (opt in to an attempted rebase per merge)

## Branch cleanup after merge

- Delete the remote head branch on merge: `yes`
- Restore and prune local base after merge: `yes`
