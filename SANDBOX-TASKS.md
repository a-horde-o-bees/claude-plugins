# Sandbox: ocd/sandbox-derivatives

Eliminate the deterministic-conflict cycle that auto-init's derivative commits create on `/sandbox update`, and stop accumulating sandbox-internal "Deployed —" commits in main's history forever.

## Pointers

- `sandbox-derivative-friction.md` (this sandbox's root) — the analysis doc. Symptoms, root cause, three strategies considered, recommendation. Read first.
- `plugins/ocd/systems/sandbox/SKILL.md` — the umbrella skill; verb dispatch lives here.
- `plugins/ocd/systems/sandbox/_update.md` — current rebase flow (the file that exits to user on derivative conflicts today).
- `plugins/ocd/systems/sandbox/_close.md` — current "refuse on uncommitted work" gate.
- `plugins/ocd/systems/sandbox/_unpack.md` — current PR/merge flow; needs the new pre-PR auto-init step.
- `.claude/skills/checkpoint/SKILL.md` — project-local checkpoint skill; step 4 (derivative commit) needs branch-aware skip.
- `scripts/auto_init.py` — owns what gets written to `.claude/`; will own the derivative-path allowlist as a single source of truth.
- Recent commits demonstrating the friction in main's history:
    - `043be50 Deployed — reinstall navigator.db`
    - `1ff5461 Sandbox tasks — clear before unpack`
    - `7324613 Track — enabled-systems.json travels with the repo`
    These survived a prior `--merge` unpack; future readers must skip past them.

## Strategy

Recommendation from the analysis doc: **Strategy 1 (don't commit derivatives mid-sandbox) as the primary fix; Strategy 2 (auto-resolve in `/sandbox update`) as the safety net.** Strategy 3 (`--squash` at unpack) was rejected — its cost (loss of topic-grouped commit history) outweighs its benefit.

Strategy 1 attacks the structural cause: derivatives shouldn't be committed eagerly on a feature branch when main is also regenerating them. One canonical "Deployed —" commit lands per feature, just before the PR opens.

Strategy 2 catches edge cases: a derivative committed by an older flow, by a session that didn't know the rule, or by a non-allowlisted path that drifts in. The skill becomes self-sufficient on the rebase path — matches the user's expressed expectation that `/sandbox update` should "just work".

The allowlist is owned by `auto_init.py` itself — it already knows what paths it writes — so a new system added to auto-init automatically extends the allowlist with no separate registration step.

## Tasks

- [ ] **Expose the derivative path set from auto_init.** Add a public function (e.g., `auto_init.derivative_paths()`) that returns the relative paths auto-init writes — DBs under `.claude/<plugin>/<system>/*.db`, deployed governance under `.claude/{rules,conventions,patterns}/`, deployed paths.csv files. Single source of truth; consumed by both `/checkpoint` and `/sandbox update`.
- [ ] **`/checkpoint` skip on sandbox branches.** In `.claude/skills/checkpoint/SKILL.md`, gate step 4 (derivative-commit) on `git branch --show-current` not starting with `sandbox/`. Step 3 (auto-init) still runs every checkpoint so the working tree stays testable. On main, behavior unchanged.
- [ ] **`/sandbox update` allowlist-aware rebase.** Pre-rebase: detect uncommitted changes; partition into derivative vs non-derivative via `auto_init.derivative_paths()`. Stash derivatives via `git stash push --keep-index -- <paths>`; refuse if any non-derivative dirty paths remain. Post-rebase: re-run `auto_init.py` to regenerate against new HEAD, drop the stash (its content is regenerated, not restored). On rebase conflict on a derivative path, auto-resolve by `git checkout --theirs <path>` + re-run auto-init + `git rebase --continue`.
- [ ] **`/sandbox close` allowlist exception.** Extend the "uncommitted-changes refusal" so derivative dirt does not block parking. Same allowlist source as update.
- [ ] **`/sandbox unpack` adds the canonical derivative commit.** Just before `gh pr create`: run `auto_init.py` against the rebased branch, commit the result as a single `Deployed — rectify against current main` (or similar) with only the auto-init paths staged, push. The branch ends with exactly one derivative commit alongside the user-authored work.
- [ ] **Tests.** Per-skill: `_update.md` rebase happy-path with a derivative-only diff (no conflict, stash-and-restore). `_update.md` rebase conflict on a derivative (auto-resolve path). `_unpack.md` adds the pre-PR derivative commit. `/checkpoint` skip on sandbox branch via subprocess against a synthetic repo.
- [ ] **Documentation.** Update `plugins/ocd/systems/sandbox/SKILL.md` Process Model + Rules to describe the derivative-aware update path. The friction analysis (`sandbox-derivative-friction.md`) graduates into either a decision log entry under `logs/decision/sandbox.md` or stays as a worked methodology example — decide during cleanup.
- [ ] **Validation pass.** Exercise via `/ocd:sandbox exercise` against a synthetic sandbox + main pair where main also touches a derivative — confirm the rebase no-ops cleanly. Also exercise the divergent-derivative path (derivative actually conflicts) to confirm auto-resolve works.

## Open Questions

- **Allowlist granularity** — does `auto_init.derivative_paths()` return concrete paths (`.claude/ocd/navigator/navigator.db`) or globs (`.claude/ocd/**/*.db`)? Concrete is robust to "what auto-init actually writes"; globs are robust to systems being added without auto-init knowing. Probably concrete + a glob layer for files auto-init clears via the orphan sweep.
- **Where the friction doc lands at unpack time** — a logged decision under `logs/decision/sandbox.md`, an idea-log entry, or stays as a standalone methodology artifact at project root. The analysis is self-contained; a decision log is probably the right home but `logs/decision/` entries are typically shorter.
- **Interaction with the in-flight `sandbox/purpose-map` migration** — that branch ships substantial helper centralization (tools/db.py, init contract rework) that this sandbox depends on for the canonical "what does init do" semantics. Resolution: this sandbox lands AFTER `sandbox/purpose-map` does. Recorded so the dependency doesn't get lost.
