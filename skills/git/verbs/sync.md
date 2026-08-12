# git sync

Bring another line of work into the current branch: fetch a remote, then integrate a ref by merge, rebase, or cherry-pick, resolving conflicts with judgment. The driver owns the state machinery — clean-tree and in-progress guards, the conflict file list, the marker-guarded continue; this verb owns the mode choice and the resolution content.

## Variables

- `{cwd}` — `--cwd <path>`; defaults to `.`
- `{remote}` — remote to fetch first (e.g. `upstream`); omitted when the source ref is already local
- `{source}` — the ref to integrate (e.g. `upstream/main`, a branch, or an `A..B` range for cherry-pick)
- `{mode}` — `merge`, `rebase`, or `cherry-pick`; chosen, not defaulted

## Rules

- **Mode is a history decision, not a preference.** `merge` for a published/shared branch absorbing another line (a fork tracking upstream keeps its overlay commits' identity); `rebase` only for an unpublished topic branch replaying onto a moved base; `cherry-pick` for adopting selected commits. Never rebase a branch others may hold — push's no-force rule is the backstop, not the excuse.
- **Conflicts are the adaptation point, never noise.** A conflicted file means both lines touched it for reasons; read both sides and the owning scope's design docs before writing the resolution, and keep both intents unless one is genuinely superseded. Wholesale `ours`/`theirs` without reading is forbidden.
- **Resolution edits carry no leftovers.** The driver refuses `--continue` while conflict markers remain; that guard is a backstop, not the review — reread each resolved file whole before continuing.
- **After integration, prove the tree.** Run the repo's own gates (build, tests) before reporting the sync done; an integration that compiles both sides but breaks the suite is not integrated.

## Process

1. If `{remote}` given: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py fetch --remote {remote} --cwd {cwd}` — note the ref updates.
2. If the work belongs on another existing branch: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py switch --branch <b> --cwd {cwd}` (new branches via `branch-create`).
3. `{result}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py integrate --source {source} --mode {mode} --cwd {cwd}`
4. While `{result}` reports conflicts:
    1. For each listed file: read it whole, plus enough of both sides' history (`read -- log/show`) to know what each intended; write the resolution per ## Rules.
    2. Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py integrate --continue --cwd {cwd}` — rebase/cherry-pick may surface the next step's conflicts; loop.
    3. If the integration was the wrong call: `integrate --abort` restores the pre-integration head; report why.
5. Run the repo's gates; fix what the integration broke before reporting.
6. Report.

## Report

- Integrated: `{source}` → branch, `{mode}`, new head
- Conflicts resolved: files + one line each on the resolution's intent (or "none")
- Gates run: results
