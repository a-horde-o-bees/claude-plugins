# git doctor — default-branch domain

> Advisory component for `/git doctor`. Two related findings on the repo's default branch: `origin/HEAD` unset (branch-resolving verbs fall through to their fallback) and a default that isn't `main` (the modern standard the repo silently contradicts). Non-blocking — convenience and conformance, not a safety gate. Each fix is gated on approval and declinable; the repo keeps whatever it has if you decline. Called when `detect.sh` flags `default-branch ADVISORY`.

## Process

1. {origin-head}: bash: `git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@'` — empty when unset
2. {default}: if {origin-head} is non-empty, {origin-head}; else bash: `gh api repos/{owner}/{repo} --jq .default_branch 2>/dev/null || echo main` — the repo's true default (network call, only when the local pointer is unset)

3. Set `origin/HEAD` — only when {origin-head} is empty:
    1. AskUserQuestion — set `refs/remotes/origin/HEAD` → {default} now? A local, reversible pointer that makes `git symbolic-ref` resolve without a network call, so every verb's default-branch lookup is correct (not just falling back to `main`).
    2. If approved: bash: `git remote set-head origin {default}`

4. Rename to the `main` standard — only when {default} ≠ `main`:
    1. AskUserQuestion — the default branch is `{default}`, not `main`; rename it to `main` across every remote now? This is the modern standard, not a hard requirement — decline to keep `{default}`. The rename is outward-facing: it changes what new clones check out and touches every remote's forge default.
    2. If declined: surface the finding in the report unchanged — the repo keeps `{default}`, no gloss over the contradiction.
    3. If approved, run the canonical rename (order matters — a forge refuses to delete its current default branch):
        1. {remotes}: bash: `git remote` — every remote, not just origin
        2. bash: `git branch -m {default} main` — local rename
        3. For each {r} in {remotes}: bash: `git push {r} main` — publish the renamed branch before any default flips
        4. Flip each remote's forge default to `main` (per the remote's host, from `git remote get-url {r}`):
            - `github.com`: bash: `gh repo edit {owner}/{repo} --default-branch main`
            - `gitlab.com`: bash: `glab api -X PUT projects/{enc} -f default_branch=main` ({enc}: the URL-encoded `owner/repo`, e.g. `owner%2Frepo`)
        5. For each {r} in {remotes}: bash: `git push {r} --delete {default}`. If a remote rejects the delete because `{default}` is protected, unprotect it there first, delete, then re-apply equivalent protection to `main` — so the rename never silently drops the default branch's protection:
            - `github.com`: bash: `gh api -X DELETE repos/{owner}/{repo}/branches/{default}/protection`
            - `gitlab.com`: bash: `glab api -X DELETE projects/{enc}/protected_branches/{default}`, then after the delete `glab api -X POST projects/{enc}/protected_branches -f name=main`
        6. For each {r} in {remotes}: bash: `git remote set-head {r} main` then `git fetch --prune {r}` — point the local pointer at the renamed default and drop the stale `{default}` ref

## Report

Return to caller:

- Default branch: {default}{ → renamed to `main` | kept (rename declined)}
- `origin/HEAD`: set → {main/default} | already set | left unset (verbs resolve via `gh api` / `main` fallback)
- Remotes updated: {list of remotes flipped to `main` | — none}
- Protection: {carried to `main` on {remotes} | none to carry}
