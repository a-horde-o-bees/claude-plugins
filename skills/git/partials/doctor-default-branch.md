# git doctor — default-branch domain

> Advisory component for `/git doctor`. `origin/HEAD` is unset, so `git symbolic-ref --short refs/remotes/origin/HEAD` returns empty and branch-resolving verbs fall through to their fallback. Non-blocking — this is a convenience fix, not a safety gate. Called only when `detect.sh` flags `default-branch ADVISORY`.

## Process

1. {default}: bash: `gh api repos/{owner}/{repo} --jq .default_branch 2>/dev/null || echo main` — the repo's true default branch
2. AskUserQuestion — set `refs/remotes/origin/HEAD` → `{default}` now? It is a local, reversible pointer that makes `git symbolic-ref` resolve without a network call, so every verb's default-branch lookup is correct (not just falling back to `main`).
3. If approved: bash: `git remote set-head origin {default}`

## Report

Return to caller:

- Default branch: {default}
- `origin/HEAD`: set → {default} | left unset (verbs resolve via `gh api` / `main` fallback)
