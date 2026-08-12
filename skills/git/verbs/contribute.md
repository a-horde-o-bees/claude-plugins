# git contribute

File a change against an upstream repo we don't own: prior-art search → conventions recon → fork → minimal change → PR, driver-backed end to end. The clone lives under a workspace dir (scratchpad), origin is the fork, so the standard commit/push commands work there unchanged — no raw `git`/`gh` anywhere in the flow, and the verb works under a user-level box.

## Variables

- `{upstream}` — `owner/repo` being contributed to.
- `{workdir}` — parent directory for the clone (a scratchpad or workspace path).

## Rules

- **Prior art before code.** The search gate runs before anything is written; a live duplicate stops the flow for the user's call (reference / extend / abandon). A duplicate found after filing costs a walk-back comment; found first, it costs nothing. (Incident: 2026-07-28, OpenSpec #1474 filed as an unknowing duplicate of #1207.)
- **Match the house conventions, read not assumed** — CONTRIBUTING.md, `.github/` templates, commit style from the log. On a single-commit branch GitHub pre-fills the PR description from the commit body — author it accordingly.
- **Minimal diff wins merges.** Mirror an existing pattern in their code; carry a test mirroring their nearest existing test; run their own gates (typecheck, touched test files) and record results for the PR body.
- **Commit messages via a message file, never inline `-m` with backticks** — backticks in a double-quoted `-m` execute as command substitution and silently mangle the message. (Incident: the same 2026-07-28 filing.) The plan-file commit flow satisfies this by construction.
- **The 403 fallback is mechanical.** Fine-grained PATs are resource-owner-bound and cannot create PRs upstream; `pr-create --repo` catches the failure and returns `fallback_compare_url` + the body file path — hand both to the user to file by hand. A classic PAT with `public_repo` (as a second `gh auth`) is the durable fix for regular filing.
- **Post-file duplicate discovery** → comment on our own PR naming the prior art, the concrete differences, and deference to the maintainers; the mention cross-links automatically.

## Process

1. `{art}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py search-prior-art --repo {upstream} <keywords>` — JSON of PRs + issues, all states.
2. If `{art}` holds a live match: Exit process: the matches — referencing, extending, or abandoning is the user's call before any code.
3. `{prep}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py contribute-prep --upstream {upstream} --workdir {workdir}` (add `--shallow` for large repos) — forks, clones the fork as origin, wires the `upstream` remote; bind `{clone}`, `{default-branch}` from its JSON.
4. Conventions recon in `{clone}`: CONTRIBUTING, `.github/` templates, recent subjects via `gitflow.py read -- log --oneline -10`.
5. Branch in `{clone}`; make the minimal change + mirrored test + docs touch; run their gates on the touched surface and capture results.
6. Commit + push via the standard flow with `--cwd {clone}`: `inspect` → plan file (house commit style, co-author trailer) → `apply`, then `push`.
7. `{pr}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py pr-create --cwd {clone} --repo {upstream} --title "..." --body-file <file>` — body authored under description-authoring and concise-prose: why → what → testing → attribution trailer.
8. If `{pr}` carries `fallback_compare_url`: Exit process: it plus the body file path, for manual filing.

## Report

- PR: url, or the compare-URL fallback + body file path
- Prior art: matches found (or "none" with the terms used)
- Gates run: results
