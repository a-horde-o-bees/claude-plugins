# Sandbox Test: /ocd:git

End-to-end exercise of the box-family verbs (`box`, `open`, `close`, `unbox`, `boxes`) against a disposable sibling project. Verifies the full lifecycle — branch off, edit cycles, rebase on main advancement, and merge back — without touching the parent repo.

## User Perspective

When executing this test, impersonate a user with this profile. The perspective locks evaluation into a specific mental model so findings are reproducible across runs rather than drifting toward mechanical "did the command exit 0" checks.

- **Context held**: "I boxed this system weeks ago to get it off main for holistic testing. I've been doing intermittent work on it in its dev branch. Today I'm either resuming a work session or finalizing it."
- **Context lost**: the exact list of external references that were cut on box; which README / architecture / rule / convention files knew about this system.
- **Goal**: bring the system back to a clean merged state without quietly leaving half-advertised dependencies.
- **Success feel**: at each step the user can point at a concrete next-action list or a clear "nothing to do" statement — no need to run `git log`, `git show`, or grep manually to understand what just happened.

## Setup

Runs in a sibling project with a local bare-repo origin so git operations stay isolated from the parent repo's branch list.

1. `{sandbox} = {parent-dir}/{parent-project}-test-box-cycle`
2. `{bare} = {sandbox}.git`
3. bash: `mkdir -p {sandbox} {bare}`
4. bash: `git -C {sandbox} init -q -b main`
5. bash: `git -C {bare} init --bare -q -b main`
6. bash: `git -C {sandbox} remote add origin {bare}`
7. Create `{sandbox}/plugins/boxprobe/.claude-plugin/plugin.json` with `name: boxprobe, version: 0.1.0`
8. Create `{sandbox}/plugins/boxprobe/systems/target/SKILL.md` with a minimal skill (no external references)
9. Commit + push main

## Scenarios

### 1. Box a zero-tendril system

- Invoke `/ocd:git box boxprobe:target` from `{sandbox}`
- Expect:
    - Main advances 1 commit (`box boxprobe:target`); system directory removed
    - `dev/boxprobe/target` branch created with `restore boxprobe:target` commit; system directory preserved
    - Both branches pushed to origin
    - No `_status.md` written (no migrated content)

### 2. Open with no main divergence

- Invoke `/ocd:git open boxprobe:target`
- Expect:
    - Checked out `dev/boxprobe/target`
    - Rebase onto `origin/main` is a no-op (main hasn't moved)
    - No conflicts

### 3. Edit cycle

- Edit `plugins/boxprobe/systems/target/SKILL.md` on dev
- Commit manually on dev
- Invoke `/ocd:git close`
- Expect:
    - Back on main
    - `dev/boxprobe/target` persists with the edit commit
    - Output names next action to resume: `/ocd:git open boxprobe:target`

### 4. Main advances during close + re-open with rebase

- Create an unrelated file on main (simulating other work)
- Commit + push main
- Invoke `/ocd:git open boxprobe:target`
- Expect:
    - Dev checked out
    - Rebase onto `origin/main` succeeds cleanly (dev commits replay on top of new main)
    - Commit hashes on dev are rewritten (new parent)
- Repeat: edit, commit, close, advance main, open — verify multi-cycle coherence

### 5. Boxes inventory

- Invoke `/ocd:git boxes` while on dev — expect state `open`
- Close, invoke `/ocd:git boxes` — expect state `closed`
- Output includes Plugin, System, State, Location (`local+remote`), Last Commit

### 6. Unbox after on-dev reintegration

- On the dev branch (open state): do intelligent reintegration — update docs against current conventions, rewire references, adjust structure to match the ecosystem as it exists now. Close to push.
- Verify the dev branch works (sandbox-test against dev, or whatever verification is appropriate)
- Invoke `/ocd:git unbox boxprobe:target` from main
- Expect:
    - `--no-ff` merge of dev into main, producing merge commit `unbox boxprobe:target`
    - Push main to origin
    - Delete `dev/boxprobe/target` local + remote
    - No checklist output, no diff, no narrative — purely mechanical confirmation
- **User-perspective evaluation**: does the user ever feel like unbox withheld information? If yes, the integration on dev wasn't complete.

### 7. Tendril-bearing box

Setup requires 9 fixture tendrils so every scanner pattern and every disposition gets exercised:

| Fixture | Location | Scanner pattern | Classification |
|---------|----------|-----------------|----------------|
| F1 | `plugins/<plugin>/README.md` skills-table row | slash | auto-delete |
| F2 | `plugins/<plugin>/architecture.md` subsystem-table row | module (if row embeds a path ref) | auto-delete if caught; see O7 |
| F3 | `plugins/<plugin>/runner.py` bare import line | module | interactive → `edit` (import + call both removed) |
| F4 | `state.md` section about the system | path + module | auto-migrate |
| F5 | `.claude/logs/<type>/<system>*.md` whose filename names the system | slash | auto-migrate |
| F6 | `docs/guide.md` illustrative prose | slash | interactive → `migrate` |
| F7 | `plugins/<plugin>/helper.py` docstring example | slash | interactive → `edit` |
| F8 | `.claude/logs/idea/unrelated.md` body-only mention | slash | interactive → `leave` |
| F9 | `plugins/<plugin>/config.yml` inline comment | slash | interactive → `remove` |

- Exercise box — verify auto-delete + auto-migrate + all 4 interactive dispositions route correctly
- On the dev branch (open state): do intelligent reintegration — update docs against current conventions, rewire references, adjust structure to match the ecosystem as it exists now. Close to push.
- Verify the dev branch works (sandbox-test against dev, or whatever verification is appropriate for the feature)
- Exercise unbox — verify it's mechanically dumb: merge, push, delete. No checklist output.
- **User-perspective evaluation**: does the user ever feel like unbox withheld information? If yes, the integration on dev wasn't complete — re-evaluate where the judgment should live.

## Precondition Guards (additional scenarios to run)

- Box with dirty working tree → rejected with guidance
- Box when `dev/<plugin>/<system>` already exists locally → rejected
- Box when `dev/<plugin>/<system>` already exists on origin → rejected
- Close from main (not a `dev/*` branch) → rejected with guidance
- Unbox with non-ff main → rejected with reconciliation guidance
- Open with rebase conflict → presents `--continue` / `--abort` instructions

## Known Observations

Findings accumulated across runs. Each observation is either a proposed scenario refinement or a skill-behavior gap to address.

- **O1. Reintegration checklist lists system's own files as deletions.** ✅ Resolved by removing the checklist entirely — see O10. Unbox no longer emits a reintegration output; the concept was misplaced.
- **O2. Close does not push rebased dev branch.** ✅ Resolved — close now pushes the dev branch with `--force-with-lease` before switching to main, so `open` can rely on origin matching local next cycle. Contract shifted: the user can rely on "close = work is persisted to origin" rather than remembering to push manually.
- **O3. Output formatting varies across invocations.** Open — subject to A/B testing in scenario 7 runs to determine which phrasing best matches the User Perspective. Pin the winning format in the skill after comparison.
- **O11. Close integration state is ephemeral.** Close now asks the user to classify the branch state (`Ready for unbox` / `Still in progress`) and emits the answer in its report. The state doesn't persist across sessions — a week later, if the user forgets, they'd have to re-open and re-close to re-confirm. Possible fix: persist the last-close state as a trailer on the close's push, or in a `_ready` marker committed to the dev branch, so `boxes` can surface it and `unbox` can optionally gate on it.
- **O4. Reintegration checklist uses `--stat`, not full diff.** ✅ Resolved by removing the checklist entirely — see O10.
- **O5. All tendril variants need exercise.** ✅ First run complete on the box side. Scenario 7 exercised 9 fixture tendrils covering path, module, and slash patterns across all four interactive dispositions (`migrate`, `remove`, `edit`, `leave`) plus both auto-handled paths (auto-delete README row, auto-migrate state.md section + matching-filename log). Unbox output evaluation from that run is moot — the checklist it emitted is no longer what unbox does (see O10). Next scenario 7 run should exercise on-dev reintegration work before unbox to validate the revised lifecycle.
- **O6. This test should be driven by `/ocd:sandbox exercise`, not hand-routed.** The sandbox skill's `exercise` verb (renamed from `test`) already classifies concerns per the Interactivity criterion and routes them to the right substrate — that is exactly the job I did manually on the first run. Scenarios with interactive tendril dispositions classify as `worktree` (AskUserQuestion available, branches live in parent `.git` but scoped to the sandbox topic and cleaned up after); deterministic fresh-install concerns classify as `project`. Future runs of this spec invoke `/ocd:sandbox exercise` with the scenario as input and let the verb's classifier handle routing. Deferred follow-up: teach `/ocd:sandbox exercise` to load a sandbox-test.md directly (`/ocd:sandbox run <system>`), eliminating the hand-authored prompt.
- **O7. Scanner misses architecture.md subsystem rows with bare system names.** ✅ Resolved via scope-based scanning. Box now resolves a scope object containing paths and symbols (slash, module, bare), iterates them to build the scan, and the `bare` symbol pattern specifically catches backticked names and table-row first columns in markdown files under `plugins/`. System shorthand `<plugin>:<system>` auto-populates the scope with the system name as a bare symbol. Cross-cutting features provide their own scope via the scope-confirmation conversation. O7's root cause — hardcoded patterns keyed to a single system name — no longer applies.
- **O8. Agent narrative output diverged from spec-prescribed raw patch.** ✅ Resolved by removing the checklist entirely — see O10.
- **O9. Raw diff not emitted in checklist.** ✅ Resolved by removing the checklist entirely — see O10.
- **O10. Reintegration is intelligent evaluation, not a scripted diff.** When a feature is boxed, the ecosystem evolves — conventions shift, docs restructure, new patterns emerge. By unbox time, what "correctly integrated" looks like has likely changed from what was cut on box. A checklist of deleted references is misleading: it implies restoration when the right question is "how does this feature integrate with the ecosystem as it is now?" That's judgment work, and the right place for it is on the dev branch while open — user does the reintegration (update docs against current conventions, rewire references, adjust structure), closes to push, verifies the dev branch works, then unboxes. Unbox is mechanically dumb: merge, push, delete. No checklist, no diff, no narrative. The intelligent work happens before unbox, not after. This restructures the lifecycle — `open` is the integration moment, not just "resume editing".

## Cleanup

After a run, remove `{sandbox}` and `{bare}` entirely. No state persists across test runs — each run starts fresh so prior runs' state can't leak.
