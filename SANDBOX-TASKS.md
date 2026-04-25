# Sandbox: ocd/sandbox-tasks

Add `SANDBOX-TASKS.md` to the sandbox skill — a per-sandbox file at the sibling's project root that captures goal, pointers, the running task checklist, and open questions, replacing the previous system-rooted `_status.md`. New verb `/ocd:sandbox tasks` reads it; `unpack` clears it before merging.

## Pointers

- (none captured during build-out — the addon's own design conversation is its source)

## Tasks

- [x] Create the template at `plugins/ocd/systems/sandbox/templates/SANDBOX-TASKS.md` with `{feature-id}` placeholder and the four canonical sections
- [x] Update `_new.md` to seed `SANDBOX-TASKS.md` from the template, commit, and push
- [x] Update `_pack.md` to write `SANDBOX-TASKS.md` at sibling root in place of system-rooted `_status.md`; reshape migrated content into checkbox tasks
- [x] Update `_unpack.md` to require sibling existence and clear `SANDBOX-TASKS.md` in a final commit before opening the PR
- [x] Add the `tasks` verb (`SKILL.md` dispatch + `_tasks.md` component)
- [x] Update `ROADMAP.md` and `lifecycle-test.md` references from `_status.md` to `SANDBOX-TASKS.md`
- [x] Eager-migrate the 4 active sandboxes (`blueprint-plugin`, `ocd/audit-governance`, `ocd/audit-static`, `ocd/update-system-docs`) — open each, reshape `_status.md` into project-root `SANDBOX-TASKS.md`, push, close
- [x] Add the template contract test under `tests/plugins/ocd/systems/sandbox/integration/test_sandbox_tasks_template.py`
- [ ] Update sandbox before unpacking to verify branch sits on top of current `origin/main`
- [ ] Unpack via `/ocd:sandbox unpack ocd/sandbox-tasks` — exercises the new cleanup-before-PR step end-to-end

## Open Questions

- (none yet)
