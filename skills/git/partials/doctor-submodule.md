# git doctor — submodule domain

Repair component for `/git doctor`. Diagnoses and repairs submodule conformance so canonical git (`submodule status --recursive`, `foreach`, `--show-superproject-working-tree`) works. Called only when the detector flags submodule drift (BLOCKING) or a routing gap. The driver runs every repair; this component classifies, gets approval, and dispatches — the deliberate cases (tier 2, unknown intent) are refused by the driver even if asked.

## Rules

- **Conform, don't circumvent** — repairs restore proper submodule structure (gitlinks) so standard git commands operate; never substitute a filesystem-scan workaround for git's own machinery.
- **Every repair is scoped to one broken path** — the driver's subcommands take explicit paths; never project-wide.
- **Tier the risk, never auto-refactor:**
    - *Tier 1 — index-only* (gitlink missing, interior files staged as blobs, **0 commits in history**): reversible. Propose with the state row + what `sub-repair` will do; apply on approval. The driver refuses any path with history — the tier boundary is enforced mechanically.
    - *Tier 2 — history-polluted* (interior files committed to superproject history): destructive to fix (history rewrite → SHA churn, force-push, broken clones). **Never automatic.** Surface with a heavy warning as a separate, deliberate decision; there is no driver subcommand for it.
- **Postpone → stop.** If the caller declines a repair, halt — do not proceed to commit. Committing while a submodule is staged-as-blobs is exactly what escalates Tier 1 into Tier 2.
- Submodule **name ≠ path** is legal — the driver resolves by `.gitmodules` `.path`; this component always passes paths.
- **Routing native keys live in the parent's `.gitmodules`, never in the submodule.** Detection decides routing by default; the four-key vocabulary (`branch`, `update`, `x-integration`, `x-contribute`) is the only override surface, written via `write-native-key` on approval (the driver validates key and value). Never write `.claude/git/*` into a submodule.

## Process

1. `{detect}`: the caller's doctor-detect JSON (re-run `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py doctor-detect` if stale). Bind `{superproject}` and the `{submodules}` state rows (`{state, path, staged, history}`).
2. Assign a disposition per row from `{state}` + `{history}` (conformance needs BOTH a gitlink AND a `.gitmodules` declaration — `gitsubmodules(7)`):
    - `broken-link`, history 0 → **Tier 1** — reversible index repair (`sub-repair`)
    - `broken-link`, history `> 0` → **Tier 2** — destructive fix; surface only
    - `orphan-gitlink` → **declare-or-drop** — gitlink with no declaration (invisible to `git submodule`); `sub-declare` to conform, or `gitlink-drop` to remove
    - `not-checked-out` / `declared-only` → **init** (`sub-init`)
    - `undeclared` → **ambiguous** — an on-disk repo not in `.gitmodules` and not parent-gitignored; intent unknown (forgotten submodule vs. deliberately vendored code)
    - `nested-independent` → **benign, skip** — parent-gitignored on-disk repo (umbrella pattern); intentionally not a submodule
    - `anomaly` → **surface** — doesn't fit a known pattern; report, don't act
3. Emit ### diagnosis (per-path state + disposition + scope counts)
4. Tier 1 — AskUserQuestion per path: approve the scoped repair? Then one batch: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py sub-repair` with one `--path {p}` per approved path — re-borders each as a gitlink and commits the batch (the "adding embedded git repository" warning is the expected outcome)
5. Init — for each `not-checked-out` / `declared-only` path: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py sub-init --path {p}`
6. Undeclared / orphan-gitlink — AskUserQuestion per path: declare + link it as a submodule (`sub-declare --path {p}`, url from its origin), leave as vendored content (no action), drop the orphan gitlink (`gitlink-drop --path {p}`, orphan only), or stop for manual handling. Act only on the chosen option; never guess intent.
7. Tier 2 — present the history-rewrite warning per path; do NOT act — require a separate explicit instruction
8. Routing native-key gaps (when the detector flagged `submodule-routing`) — for each declared submodule with no `branch =`:
    1. `{current}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py read --cwd {superproject}/{path} -- rev-parse --abbrev-ref HEAD`
    2. If `{current}` is `HEAD` (detached): surface — `{path}` is detached with no declared branch; normalize it onto a branch first (there is no branch to record yet)
    3. Else: AskUserQuestion — record `branch = {current}`? On approval: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py write-native-key --path {path} --key branch --value {current}`
9. Integration override (when a checkpoint routing gap points here — e.g. `edits-to-readonly` — or the user wants a path detection wouldn't pick) — only ever a deliberate override, never to restate what detection already reads:
    1. AskUserQuestion — write `x-integration = <read-only|direct|pr>`? Use it to force a PR on an unprotected branch, pin a writable repo as read-only, or admit a deliberate direct-land; leave unset to let detection decide. On approval: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py write-native-key --path {path} --key x-integration --value {v}`
    2. If the submodule's origin is a fork and the contribution target is ambiguous: AskUserQuestion — `x-contribute = <upstream|origin>`? On approval: the same `write-native-key` with `--key x-contribute`
10. `{verify}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py doctor-detect` — bind the fresh `{status}`
11. Return to caller: ### result

## Report

### diagnosis

```
Repo: {superproject}
Submodule conformance (every detected boundary, declared or on-disk):
{per-path: <path> — <state> (staged: {staged}, history: {history})}
Tier 1 (reversible index repair): {tier1-list}
Tier 2 (history rewrite — needs deliberate decision): {tier2-list}
Undeclared (intent decision): {undeclared-list}
Uninitialized: {uninit-list}
```

### result

```
Submodule domain:
Repaired (Tier 1): {repaired-list + commit}
Initialized: {init-list}
Declared / dropped: {declare-drop-list}
Deferred (Tier 2 / postponed): {deferred-list}
Native keys written: {key-list}
Verify: {status healthy = conforming | still drifting — see diagnosis}
Blocking unresolved: {yes — do not commit until resolved | none}
```
