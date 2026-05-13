---
name: rebuild
description: Use whenever the user says "rebuild X" (or "redo X", "rewrite X from scratch", "reauthor X", "regenerate X") or asks to reconstruct an existing artifact from the ground up. Spawns a fresh-context agent to author X from scratch rather than spot-edit; convention skills matching X's type auto-fire in the spawned agent's `<available_skills>` registry alongside. Stackable on any prompt that names a target (file, section, function, or other addressable artifact).
allowed-tools:
  - Read
  - Bash(mkdir *)
  - Bash(diff *)
  - Bash(cp *)
  - Bash(rm *)
  - Task
  - AskUserQuestion
---

# rebuild

Anti-patching coordinator. `/rebuild X` spawns a fresh-context agent to author X from scratch and travels the behavioral guidance below as its spec. Convention skills matching X's type fire alongside via the spawned agent's `<available_skills>` registry — `/rebuild` carries no domain ruleset of its own; file-specific concerns belong in their own convention skills.

## What "rebuild" means

Behavioral guidance the spawned agent receives:

**Do**

- Approach X as authoring it for the first time, as efficiently as possible
- Apply every loaded rule and every matched convention skill in unison to the whole artifact, not section by section
- Reorganize when reorganization doesn't change the outcome
- Output the complete artifact — every section, every line, every paragraph

**Don't**

- Spot-clean one issue at a time
- Edit the original in place — write the fresh artifact to the workspace path
- Lean on the existing phrasing as a guide; the file's identity is what survives, not its surface
- Treat sections in isolation; matched conventions apply to all sections simultaneously
- Elide; produce no `...`, no `[unchanged]`, no implied continuation

## Triggers

| Cognitive moment | Phrasing |
|---|---|
| Reauthor with current discipline | "rebuild X", "redo X", "regenerate X", "rewrite X from scratch", "reauthor X" |
| Audit-and-rewrite after rule evolution | "reapply rules to X", "X needs to follow [discipline]" |
| Discipline-drift cleanup | "X still uses old terminology", "audit X against [discipline]" |
| Anti-patching modifier on any rebuild request | User wants the target reconstructed from scratch, not surgically patched |

## When NOT to use

- Adding a new rule or discipline that didn't previously exist — content change, not a rebuild
- Fixing a localized bug in one workflow step — targeted edit; rebuild's overhead isn't warranted
- Verifying conformance without changing the artifact — audit the file in place instead
- Renaming a symbol or moving a file — refactor, not a rebuild

## Workflow

1. Identify target from the user's `/rebuild` invocation. If ambiguous (multiple files match, scope unclear), ask which to rebuild
2. `mkdir -p tmp/rebuild-workspace`; workspace path is `tmp/rebuild-workspace/<basename>.fresh`
3. Spawn one agent with a clean session context. The spawn prompt instructs it to (a) read the target at its source path, (b) read this skill's `## What "rebuild" means` section as its behavioral spec, (c) compose the complete fresh artifact and write it to the workspace path. The original is never edited in place
4. Diff the target against the workspace artifact
5. Present the diff. If it contains structural changes (section renames, splits, callable-surface or schema changes affecting downstream consumers), gate on user approval. Inline-only diffs proceed
6. On approval (or inline-only): `cp` the workspace artifact over the target, `rm -rf` the workspace, emit `<rebuild-complete>`
