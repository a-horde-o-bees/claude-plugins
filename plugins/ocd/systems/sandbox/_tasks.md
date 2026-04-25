# Tasks

Read `SANDBOX-TASKS.md` from a sandbox sibling and present its content. Surfaces what the sandbox is meant to resolve, the pointers to source material, the running task checklist, and any open questions — all from the file's project root. Reading is a side effect: the file content lands in agent context so subsequent steps can act on it without a second Read.

### Variables

- {verb-arg} — positional value: optional feature id. If empty, infer from cwd's branch (must be `sandbox/<id>`).

### Process

1. Parse {verb-arg}:
    1. If {verb-arg} non-empty: {feature-id} = {verb-arg}
    2. Else:
        1. {current-branch} = bash: `git rev-parse --abbrev-ref HEAD`
        2. If {current-branch} does not start with `sandbox/`: Exit to user: tasks requires a feature id (or run from inside a `sandbox/<id>` worktree)
        3. {feature-id} = {current-branch} with `sandbox/` prefix removed
2. {sibling-name} = {feature-id} with every `/` replaced by `-`
3. {sibling-path} = bash: `ocd-run sandbox sibling-path {sibling-name}`
4. {tasks-file} = `{sibling-path}/SANDBOX-TASKS.md`

> Read the named sibling's tasks file. The file is sandbox-scoped and lives at the sibling's project root; absent siblings or absent files surface explicitly so the user knows which precondition needs fixing.

5. If {sibling-path} does not exist on disk: Exit to user: sandbox sibling not present at {sibling-path} — run `/sandbox open {feature-id}` first
6. If {tasks-file} does not exist: Exit to user: SANDBOX-TASKS.md not present at {tasks-file} — the sandbox predates the SANDBOX-TASKS.md migration or the file was deleted
7. Read: {tasks-file}

8. Return to caller:
    - feature: {feature-id}
    - tasks-file: {tasks-file}
    - content: as displayed (file body)
