# git ci

Report GitHub Actions run state for the latest pushed commit, parent and submodules alike. The driver recurses declared submodules deepest-first and classifies each repo deterministically; this verb emits the matching template per repo verbatim — no inventing, paraphrasing, or merging.

## Variables

- `{cwd}` — `--cwd <path>`; defaults to `.`
- `{branch}` — `--branch <name>`: confirmation at the top level; a mismatch with the current branch blocks. Omitted: each repo's current branch.

## Rules

- `{ci-status}` is a closed enum: `passed`, `failed`, `dispatched`, `incomplete`, `no-runs`, `no-ci`, `unavailable`. Classification lives in the driver; emit the matching template verbatim.
- `no-runs` (CI not triggered or not yet scheduled), `no-ci` (no `.github/workflows/`), and `unavailable` (gh could not answer — no remote or no auth) are reported states, not errors. Never substitute a guessed status for one the driver didn't return.
- Failed runs report synchronously with workflow name + URL; no watcher.
- In-flight runs spawn the async watcher per `watches[]` entry; foreground returns immediately. Task-completion text reports the outcome inline.

## Process

1. `{result}`: Bash: `uv run ${CLAUDE_SKILL_DIR}/scripts/gitflow.py ci --cwd {cwd}` (append ` --branch {branch}` when given). BLOCKED (branch mismatch): Exit process: the driver's surface.
2. For each `{repo}` in `{result}`.repos (already deepest-first, parent last): emit the template matching `{repo}`.ci_status — see ## Report.
3. For each `{watch}` in `{result}`.watches: Spawn async agent to: read and follow `${CLAUDE_SKILL_DIR}/partials/ci-watch.md` (`{cwd}`: `{watch}`.cwd, `{sha}`: `{watch}`.sha, `{run-ids}`: `{watch}`.watch_ids)

## Report

One block per repo, in the driver's order. Emit the literal template for the repo's `{ci-status}` verbatim; templates close with `Next:` corrective guidance where action is implied.

**`passed`:**

```
Repo: {cwd}   Branch: {branch}   SHA: {sha_short}
CI: passed
Workflows: {workflow_list}
```

**`failed`:**

```
Repo: {cwd}   Branch: {branch}   SHA: {sha_short}
CI: FAILED
Failing workflow: {failing_workflow}
Run URL: {failing_url}
Next: open the run URL to inspect logs; fix the failure and re-push.
```

**`dispatched`:**

```
Repo: {cwd}   Branch: {branch}   SHA: {sha_short}
CI: dispatched (async watch in flight)
Watching run IDs: {watch_ids}
Next: result lands as task-completion text in this session; no action required now.
```

**`incomplete`:**

```
Repo: {cwd}   Branch: {branch}   SHA: {sha_short}
CI: incomplete (cancelled / timed-out / non-success conclusion)
Runs:
{trouble_list}
Next: rerun via `gh run rerun <id>` or inspect each run for cause.
```

**`no-runs`:**

```
Repo: {cwd}   Branch: {branch}   SHA: {sha_short}
CI: no runs scheduled
Next: check manually via `gh run list --branch {branch}` — GitHub may not have triggered yet, or no workflows match this branch.
```

**`no-ci`:**

```
Repo: {cwd}   Branch: {branch}   SHA: {sha_short}
CI: no-ci (no .github/workflows/ in this repo)
```

**`unavailable`:**

```
Repo: {cwd}   Branch: {branch}   SHA: {sha_short}
CI: unavailable — gh could not read runs (no remote, or gh unauthenticated)
Next: check the repo's origin remote and `gh auth status`, then re-run.
```
