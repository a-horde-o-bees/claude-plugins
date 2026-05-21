# Sandbox skill — rebuild brief

Rebuild needed because `ocd-run` (the CLI shim every Python primitive currently calls through) is defunct. This brief captures the refinements to fold in during the rebuild — naming, file structure, command funneling, permission surface, and integration with built-in worktree tooling. The replacement Python-invocation mechanism comes from whichever skill-authoring path is used for the rebuild; this brief stays agnostic of that detail.

## Naming

`/sandbox` is semantically accurate (durable feature isolation + ephemeral validation substrates) but undiscoverable to someone searching for "worktree". Options:

- **Keep `sandbox`** — most accurate; surface "worktree" via the description rather than the name.
- **`worktree-plus`** — surfaces the worktree-adjacent role but oversells worktree mechanics; most of the skill's weight is feature-lifecycle, validation, and task scaffolding rather than worktree plumbing.
- **`feature-sandbox` / `sandbox-worktree`** — carries both signals.

Decision deferred to the rebuild. If discoverability matters, prefer surfacing "worktree" in the description rather than in the name.

## Verb file structure — extract every verb

Today: eight durable verbs each have a `_<verb>.md`; `exercise` and `cleanup` live inline in `SKILL.md`.

Target: every verb in its own file, including `_exercise.md` and `_cleanup.md`.

- Symmetric dispatch — easier to read and predict.
- Context economy — callers running a durable verb don't load the ~70-line `exercise` workflow.

Caveat: the Interactivity criterion prose at the top of `SKILL.md` is consumed by `exercise`. Move that prose into `_exercise.md` rather than referencing back into `SKILL.md`.

## Command funneling — narrow the allowed-tools surface

Today, `update` and `unpack` invoke `git -C` and `gh` directly from the markdown, so `allowed-tools` carries `Bash(git *)`, `Bash(gh *)`, `Bash(env -C *)`, plus the Python CLI invocation.

Target: every mechanical step goes through the Python module. Markdown drafts and decides (PR title/body, classification, task seeds); Python executes with those drafts as arguments.

- **Strong candidate — `unpack`.** The post-checks sequence (clear-`SANDBOX-TASKS.md` commit → push → `gh pr create` → wait for checks → `gh pr merge --delete-branch` → worktree-remove) is try/finally-shaped and needs structured cleanup on failure. Belongs in Python. The PR title/body come in as arguments from the drafting step in the markdown.
- **Borderline — `update`.** A thin wrapper around `git rebase` adds little value, because the markdown's actual job is to exit to the user when conflicts arise. Worth doing for surface uniformity, but no functional gain. The wrapper should report conflict state structurally so the markdown can route to the human-resolve exit.

After funneling, `allowed-tools` shrinks to roughly:

- The skill-authoring-provided invocation primitive (replacement for `ocd-run`).
- The `claude -p` invocation used by the `exercise` fresh-install substrate.
- `Bash(mkdir *)`, `Bash(cp *)`, `Bash(rm *)`, `Bash(ls *)` if still needed for fixture work.
- `AskUserQuestion`.

## Session-CWD integration — leverage `EnterWorktree` where it fits

Today: `open <feature-id>` ends by telling the user to `cd <sibling-path> && claude` — start a fresh session manually.

Target: when invoked inside Claude Code, `open` (and the tail of `new` / `pack`) calls `EnterWorktree(path=<sibling>)` to switch the current session into the sibling. Fall back to the "cd && claude" instruction outside Claude Code.

What does NOT change:

- Worktree *creation* stays in the Python module. `EnterWorktree` bundles create + session-switch and hardcodes placement at `.claude/worktrees/`, which is the wrong shape for the sibling-path convention.
- `ExitWorktree` is session-scoped and won't manage worktrees from prior sessions, so `close` / `unpack` continue to use the Python primitives.

Net effect: built-in handles entry ergonomics where it shines; the durable/feature-scoped lifecycle stays in the skill's own primitives.

## Python module — public surface

Whatever invocation mechanism the rebuild adopts, the module's verbs stay roughly the same shape as today:

```
project setup <path>
project teardown <path>
worktree setup <topic>
worktree teardown <topic>
worktree-add <name> --branch <branch> [--base-ref <ref>] [--block-push]
worktree-remove <name> [--delete-branch] [--unblock-push]
worktree-status <name>
worktree-list
sibling-path <name>
cleanup inventory
cleanup remove [--sibling <path> ...] [--worktree <path> ...]
```

Add per the funneling decisions above:

- `update <feature-id>` — rebase the named sibling's branch onto current `origin/main`; report conflict state structurally.
- `unpack finalize <feature-id> --title <title> --body <body>` — run the full PR-driven reintegration sequence under try/finally.

## Invariants to preserve

These hold from the current design and should NOT be revisited during rebuild:

- **Sibling-path placement** at `<parent>/<project>--<name>/` (not nested under `.claude/worktrees/`) so `CLAUDE_PROJECT_DIR` binds correctly, the main session's filesystem walks don't descend into copies, and a single `<project>--*` permission glob covers everything.
- **Branch namespace** — `sandbox/<feature>` durable, `sandbox/tmp/<topic>` ephemeral. Renames break existing branches; only revisit if the skill is also renamed, and probably not even then.
- **`SANDBOX-TASKS.md`** at the sibling project root — seeded by `new` / `pack`, read by `tasks`, cleared by `unpack` before the PR. Main never carries one.
- **Push-blocking** via invalid pushurl during in-flight work; always unblocked on teardown even after a crash.
- **Durable vs ephemeral split**, and the **Interactivity criterion** that decides `exercise` routing.
- Sibling-project and branched-worktree substrates remain **internal mechanics of `exercise`** — not separately exposed as user verbs.

## Open questions

- Final skill name (see Naming).
- Whether to rename the branch namespace if the skill is renamed.
- Whether `update` warrants the thin Python wrapper, or stays in markdown.
- Concrete invocation primitive replacing `ocd-run` — comes from the skill-authoring path chosen for the rebuild.
