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

### 6. Unbox and reintegration walkthrough

- Invoke `/ocd:git unbox boxprobe:target` from main
- Expect:
    - `--no-ff` merge of dev into main, producing merge commit `unbox boxprobe:target`
    - Push main to origin
    - Delete `dev/boxprobe/target` local + remote
    - Reintegration checklist emitted — `git show <box-commit> --stat` over files that had references removed on box
- **User-perspective evaluation**: reading the reintegration output alone, can the user tell what (if anything) they need to re-wire? If "nothing to re-wire," is that stated explicitly?

### 7. Tendril-bearing box (extension scenario)

*Not yet run — placeholder for the meaningful reintegration walkthrough test.*

- Before boxing, add external references to the system: a README row, an architecture doc mention, a rule file reference
- Exercise box — verify auto-delete + auto-migrate + interactive classification handle each
- Exercise unbox — verify reintegration checklist surfaces the deleted external content so the user can decide which to restore
- **User-perspective evaluation**: does the checklist give the user enough to decide per-file what to restore, without running `git show` themselves?

## Precondition Guards (additional scenarios to run)

- Box with dirty working tree → rejected with guidance
- Box when `dev/<plugin>/<system>` already exists locally → rejected
- Box when `dev/<plugin>/<system>` already exists on origin → rejected
- Close from main (not a `dev/*` branch) → rejected with guidance
- Unbox with non-ff main → rejected with reconciliation guidance
- Open with rebase conflict → presents `--continue` / `--abort` instructions

## Known Observations

Findings accumulated across runs. Each observation is either a proposed scenario refinement or a skill-behavior gap to address.

- **O1. Reintegration checklist lists system's own files as deletions.** ✅ Resolved — unbox now filters `{system-path}` from the checklist and emits the full `git show --patch` over external files only. If no external references were cut, unbox says so explicitly instead of showing an empty stat.
- **O2. Close does not push rebased dev branch.** ✅ Resolved — close now pushes the dev branch with `--force-with-lease` before switching to main, so `open` can rely on origin matching local next cycle. Contract shifted: the user can rely on "close = work is persisted to origin" rather than remembering to push manually.
- **O3. Output formatting varies across invocations.** Open — subject to A/B testing in scenario 7 runs to determine which phrasing best matches the User Perspective. Pin the winning format in the skill after comparison.
- **O4. Reintegration checklist uses `--stat`, not full diff.** ✅ Resolved alongside O1 — `--patch` output now included so the user can see actual deleted content without running `git show` themselves.
- **O5. All tendril variants need exercise.** Scenario 7 must cover every tendril type and every disposition:
    - Path references, module references, and slash-command references
    - Auto-delete (README skills-table row, architecture subsystem-table row, pure-reference code line)
    - Auto-migrate (state.md section, log file with matching filename or H1)
    - Interactive dispositions: `migrate`, `remove`, `edit`, `leave`

## Cleanup

After a run, remove `{sandbox}` and `{bare}` entirely. No state persists across test runs — each run starts fresh so prior runs' state can't leak.
