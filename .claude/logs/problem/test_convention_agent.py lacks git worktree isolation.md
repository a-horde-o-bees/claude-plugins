# test_convention_agent.py lacks git worktree isolation

## Purpose

`plugins/ocd/servers/tests/integration/test_convention_agent.py` creates a scratch directory `_test_scratch/` directly inside the project repo (line 29, `SCRATCH_DIR = PROJECT_ROOT / "_test_scratch"`) and runs spawned claude agents with `cwd=PROJECT_ROOT` against it. The teardown uses `shutil.rmtree(SCRATCH_DIR)` instead of git worktree removal. Per `.claude/conventions/ocd/testing.md` Git Worktree Isolation, integration tests that create/modify/stage files in the project repo must run in a disposable worktree — the rule is absolute to prevent agents or git operations from escaping the scratch area and affecting the main working tree.

## Failure mode

The current test's exposure is theoretical rather than observed: the spawned agents are invoked with explicit Edit/Write tool targets inside `_test_scratch/`, so escape would require agent error. But the rule exists because theoretical exposure becomes real exposure the moment an agent or a git command reaches outside the scratch path.

## Fix direction

Add a session-scoped worktree fixture in `plugins/ocd/servers/tests/integration/conftest.py`:

- `git worktree add <path> HEAD --detach` at session start
- Yield worktree path
- `git worktree remove --force <path>` at session end

Refactor the existing module-level `SCRATCH_DIR` / `scratch_files` fixture to run inside the worktree rather than `PROJECT_ROOT`. Spawned agents' `cwd` becomes the worktree path.

Estimated scope: ~30 lines of fixture setup + 5-10 lines of call-site updates. Moderate — the fixture layering is load-bearing (session-scoped worktree, module-scoped scratch files within it).

## When this surfaced

Found during Phase 2 consumer audit of python-related conventions (2026-04-14). Not a v1 blocker but the rule is lockdown-final as of that audit — test should be brought into conformance before Phase 6 runs `evaluate-governance` on the full chain, or the governance run will flag it.

## Also surfaced

Audit noted an undefined `claude_cli` fixture referenced in `test_convention_agent.py` (lines 162, 170, 179, 187, 201) that is not declared in the test module or in an accompanying `conftest.py`. Needs tracing or a new conftest.py at `servers/tests/integration/` providing the fixture.
