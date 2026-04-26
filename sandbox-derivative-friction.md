# Sandbox Derivative Friction

Analysis of a recurring failure mode in the durable-sandbox workflow: deterministic conflicts at `/sandbox update` time, caused by tracking auto-init's outputs in git on feature branches. The friction is observable; the root cause is structural; today's mitigation pushes manual resolution onto every update cycle and accumulates noise in main's history forever.

## Symptoms

The user observation that triggered this analysis: "almost every time I've run `/sandbox update`, it says we should move files away for best results and revert commits."

Concrete instance from the `sandbox/ocd/transcripts` rebase:

- 4 commits to replay onto `origin/main`
- 3 user-authored commits (skill code, tests, tracker docs) — applied cleanly via git's standard merge, including a `ROADMAP.md` → `TASKS.md` rename that git's rename detection carried through transparently
- 1 derivative commit (`Deployed — reinstall navigator.db`) — **deterministic conflict**, because origin/main also reinstalled the DB during the same window

Resolution required a manual `git rebase --skip` followed by re-running `auto_init.py` and a fresh derivative commit. The skill's documented advice was "cd into the sibling and resolve" — workable for source-code conflicts, useless for binary derivatives where there is no semantically meaningful merge.

## Root Cause

Two separable concerns are conflated in `/checkpoint`:

| Step | Operation | Functional purpose |
|------|-----------|-------------------|
| 3 | Run `auto_init.py` | Bring working-tree deployed state (rules, conventions, navigator DB) into agreement with current templates and source data — required so the branch can exercise its own deployed governance |
| 4 | Stage + commit derivatives | Record that on-disk state into git history — required eventually so main ships the right artifacts; otherwise has no functional purpose mid-sandbox |

Step 3 is what makes a sandbox testable. Step 4 is what makes step 3's output durable across session boundaries. They are independent — a sandbox can run step 3 every checkpoint without ever running step 4 and still be testable, as long as auto-init is idempotent (it is).

The conflict arises only from step 4. Specifically:

1. Branch's `<derivative>` commit captures a binary blob `B1` regenerated against branch state at time T1.
2. `origin/main` advances to a commit that regenerates the same derivative against main state at time T2, producing blob `B2`.
3. Rebase tries to apply branch's commit on top of main. `B1 ≠ B2`, no semantic merge possible, conflict.

This is **deterministic** — it happens every time main also touches the derivative between two updates. It is not a flaky failure that occasional cleanup fixes; it is the expected behavior of git's binary merge applied to two independently-regenerated artifacts.

## Why Today's Mitigation Compounds

`/sandbox unpack` uses `gh pr merge --merge --delete-branch`. Under `--merge`, every commit on the sandbox branch lands in main's full history. The remote branch is deleted, but the commits remain reachable through the merge commit's second parent — `git log --first-parent main` hides them, `git log main` shows them all.

The current main contains visible evidence of this:

```
1ff5461 Sandbox tasks — clear before unpack
043be50 Deployed — reinstall navigator.db
7324613 Track — enabled-systems.json travels with the repo
```

Those are sandbox-internal commits — including a "Deployed —" derivative — that survived an earlier unpack and now live on main forever.

Compounding: a sandbox with N checkpoints, M update cycles, and K rounds of conflict-resolution leaves N + K "Deployed —" commits on main's history forever. None of them are useful to read or bisect on. None of them are findable by anyone trying to understand the *feature* that was merged. They are pure churn that future readers must skip past.

## Options

Three structural strategies, each addressing a different layer:

### Strategy 1 — Don't commit derivatives mid-sandbox

**Mechanism.** Sandbox `/checkpoint` runs auto-init (preserving testability) but does not commit step 4's output. Working tree carries dirty derivatives during the sandbox's life, regenerated each checkpoint. One canonical "Deployed —" commit lands once, just before `/sandbox unpack` opens the PR, against the final rebased state. Main's `/checkpoint` keeps step 4 because there's no rebase pressure on main.

**Tradeoffs.**

- ✓ Eliminates rebase conflicts on derivatives entirely — they're never committed during the conflict-prone window
- ✓ Reduces main-history noise to one derivative commit per feature
- ✗ Working tree is persistently dirty during sandbox's life — every `git status` shows the derivative paths
- ✗ `/sandbox update` currently refuses on dirty trees; needs an exception or auto-stash for known-derivative paths
- ✗ `/sandbox close` rules ("refuses to park a sibling with uncommitted work") need a derivative carve-out
- ✗ Reopening a sandbox after a long gap requires re-running auto-init to repopulate the derivatives, since they were never committed

### Strategy 2 — `/sandbox update` auto-resolves derivative conflicts

**Mechanism.** When rebase fails on a known-derivative path, the skill resolves automatically: `git checkout --theirs <path>` (take origin/main's version), re-run `auto_init.py` to regenerate against the new HEAD, `git add` the result, `git rebase --continue`. The skill becomes self-sufficient as expected.

**Tradeoffs.**

- ✓ Smaller patch; preserves today's "everything is a commit" assumption
- ✓ Other skill flows (close, unpack) work unchanged
- ✓ Self-sufficient — matches the user's expressed expectation
- ✗ Doesn't address the main-history noise problem; "Deployed —" commits still accumulate
- ✗ Requires maintaining an allowlist of derivative paths that auto-init owns (drift risk if a new system is added but not added to the allowlist)
- ✗ Treats a structural problem (we shouldn't be committing these eagerly) as a procedural problem (let's smooth over the conflict)

### Strategy 3 — `--squash` at unpack

**Mechanism.** `/sandbox unpack` uses `gh pr merge --squash --delete-branch` instead of `--merge`. All sandbox-internal commits collapse into a single squashed commit on main. Derivative noise vanishes from main's history.

**Tradeoffs.**

- ✓ Solves the main-history noise problem completely
- ✓ Doesn't change `/checkpoint` or `/sandbox update` behavior at all
- ✗ Loses the topic-grouped commit history within a feature — the user-authored commits ("Transcripts — port chat extraction skill", "Tracker — document substrate") which carry real semantic value get collapsed alongside the derivative noise
- ✗ Loses bisect granularity within a feature
- ✗ Conflicts with the existing `/ocd:git commit` discipline, which exists specifically to produce focused topic-grouped commits

## Cross-Cutting Observations

- **Strategies 1 and 2 are not mutually exclusive.** Strategy 1 fixes the structural cause (derivatives shouldn't be committed eagerly); Strategy 2 fixes the symptom for any derivative that does get committed. Doing both is defensible — Strategy 1 prevents most cases, Strategy 2 catches edge cases where a derivative was committed deliberately or by an older flow.
- **Strategy 3 is independent of 1 and 2.** It addresses the main-history-noise consequence regardless of where on the branch the noise lives. But its tradeoff against topic-grouped commits is severe and crosses an existing discipline boundary.
- **The friction is not random.** Every claim of "almost every time" is a deterministic-conflict claim — the conditions that produce it are predictable from the workflow shape. Treating it as procedural noise (occasional cleanup) means accepting that friction permanently. Treating it as structural means one design pass eliminates it for good.

## Recommendation

**Strategy 1 as the primary fix; Strategy 2 as a hedge.** Strategy 3 is rejected because its cost (loss of semantic commit history) outweighs its benefit (cosmetic main-history cleanup) — `--merge` with one derivative commit per feature is good enough.

Concrete implementation outline for Strategy 1:

1. `/checkpoint` skill detects branch (`git branch --show-current`) and skips step 4 when on `sandbox/*`. Step 3 still runs. The "Deployed —" derivative commit becomes a main-only step.
2. `/sandbox update` allows uncommitted changes on a small allowlist of derivative paths (e.g. `.claude/ocd/navigator/navigator.db`, `.claude/ocd/**/*.db`, deployed governance under `.claude/`); auto-stashes them across the rebase, re-runs `auto_init.py` post-rebase, restores. Falls through to today's "refuse on dirty tree" for any path outside the allowlist.
3. `/sandbox close` extends the same allowlist exception — derivative dirt does not block parking.
4. `/sandbox unpack` adds a final pre-PR step: run `auto_init.py` against the rebased branch, commit the resulting derivative as a single "Deployed —" commit, push, then open the PR. The branch now ships exactly one derivative commit alongside the user-authored work.

The allowlist is owned by `auto_init.py` itself — it already knows what paths it writes — so a new system added to auto-init automatically extends the allowlist with no separate registration step.

## Why This Belongs in Methodology Context

The friction has been observed multiple times. The mitigation has been treated as procedural ("resolve manually each time") rather than structural ("the workflow shouldn't produce this"). That gap — the difference between treating a recurring problem as a series of incidents vs. treating it as a design defect — is exactly the analytical bias that purpose-map / needs-map methodology exists to surface.

Recording the analysis here, in the worktree currently doing methodology work, anchors it as a worked example: a recurring symptom that resolves cleanly when traced to the structural cause, with a concrete fix that closes the loop.
