# git ci

> Report GitHub Actions run state for the latest commit on a branch. Recurses depth-first into declared submodules; submodules without `.github/workflows/` are soft-skipped as `no-ci`. Async background watcher when runs are in flight; foreground returns immediately.

## Variables

- `{cwd}` — `--cwd <path>` argument; defaults to `.` (top-level invocation). All git operations use `git -C {cwd}`. Recursive calls pass `{cwd}/{sub}` so depth flows through one variable.

## Rules

- Branch defaults to current when `--branch` is omitted
- No-runs-scheduled is reported, not an error — CI may not have triggered for this commit or GitHub may not have scheduled runs yet
- Submodules without `.github/workflows/` emit the `no-ci` template and recursion still descends into their sub-submodules
- Failed runs report synchronously with workflow name + URL; no background watcher
- In-flight runs spawn the async watcher; foreground returns immediately. Task-completion text reports the outcome inline
- `{ci-status}` is a 6-value enum (`passed`, `failed`, `dispatched`, `incomplete`, `no-runs`, `no-ci`). Classification is deterministic and lives in `scripts/ci.py`; the process consumes its JSON output and emits the matching template verbatim — no inventing, paraphrasing, or merging

## Process

1. Recurse into submodules first (depth-first):
    1. {submodules}: bash: `git config -f {cwd}/.gitmodules --get-regexp '^submodule\..+\.path$' 2>/dev/null | awk '{print $2}'`
    2. For each {sub} in {submodules}: Call: verbs/ci.md --cwd {cwd}/{sub} — recursive call handles its own sub-submodules and CI check at this submodule

2. If not {branch}: {branch}: bash: `git -C {cwd} branch --show-current`
3. {has-workflows}: bash: `test -d {cwd}/.github/workflows && echo yes || echo no`
4. If {has-workflows} is `no`: bind {sha}, {sha-short} from bash: `git -C {cwd} rev-parse HEAD` and `git -C {cwd} rev-parse --short HEAD`; set {ci-status} = `no-ci`; skip to step 7
5. {classification}: bash: `uv run --directory {cwd} ${CLAUDE_SKILL_DIR}/scripts/ci.py classify --branch {branch}` — `${CLAUDE_SKILL_DIR}` resolves to this skill's directory; `uv run --directory {cwd}` sets the project root so `gh` auto-detects the right repo
6. Bind from {classification} JSON:
    - {sha}, {sha-short}, {ci-status} — always present
    - {workflow-list} — when {ci-status} is `passed`
    - {failing-workflow}, {failing-url} — when `failed`
    - {watch-ids} — when `dispatched`
    - {trouble-list} — when `incomplete`

7. If {ci-status} is `dispatched`: async Spawn: Call: partials/ci-watch.md ({sha}: {sha}, {run-ids}: {watch-ids})
8. Emit the template matching {ci-status} — see ### Report

## Report

Emit the literal template for the current {ci-status} verbatim. Templates close with `Next:` corrective guidance where action is implied.

**`passed`:**

```
Branch: {branch}
SHA: {sha-short}
CI: passed
Workflows: {workflow-list}
```

**`failed`:**

```
Branch: {branch}
SHA: {sha-short}
CI: FAILED
Failing workflow: {failing-workflow}
Run URL: {failing-url}
Next: open the run URL to inspect logs; fix the failure and re-push.
```

**`dispatched`:**

```
Branch: {branch}
SHA: {sha-short}
CI: dispatched (async watch in flight)
Watching run IDs: {watch-ids}
Next: result lands as task-completion text in this session; no action required now.
```

**`incomplete`:**

```
Branch: {branch}
SHA: {sha-short}
CI: incomplete (cancelled / timed-out / non-success conclusion)
Runs:
{trouble-list}
Next: rerun via `gh run rerun <id>` or inspect each run for cause.
```

**`no-runs`:**

```
Branch: {branch}
SHA: {sha-short}
CI: no runs scheduled
Next: check manually via `gh run list --branch {branch}` — GitHub may not have triggered yet, or no workflows match this branch.
```

**`no-ci`:**

```
Branch: {branch}
SHA: {sha-short}
CI: no-ci (no .github/workflows/ in this repo)
```

Recursed submodule results are returned alongside this level's template — one block per submodule, in depth-first order, followed by the parent block.
