# Rules migration validation

End-to-end exercise of the rules system on the new setup CLI surface. Validates the exemplar before propagating the pattern to the other system migrations tracked in `system-migrations.md`. Runs after `/checkpoint` so the plugin cache reflects the migrated code.

## Goal

The rules system, on the new layout (`__init__.py` facade + `workflows/install.md` + `workflows/uninstall.md`), is provably installable, uninstallable, and inspectable at both user and project scope through the new `/ocd:setup` dispatch — invoked as a downstream user would invoke it, against the cached plugin install.

## Output

- A validation pass/fail report for each step below
- If any step fails: the specific defect captured here under "Open questions" with a fix path before any other system migrates
- Once green: `system-migrations.md` unblocks; rules' shape is the firmed template

## Sequence

Each step lands as a prompt the user issues in a fresh restarted session.

1. `/ocd:setup` — usage banner shows meta verbs (`list`, `status`) and the migrated systems list including `rules` and `permissions`
2. `/ocd:setup list` — lettered list with `A. permissions — ...`, `B. rules — ...`; only migrated systems shown
3. `/ocd:setup rules` — system usage prints purpose, lists `status`, `list`, `install`, `uninstall` verbs with descriptions
4. `/ocd:setup rules list` — catalog of available rule templates with one-paragraph purpose per row, sorted by name
5. `/ocd:setup rules install honesty --scope project` — file lands at `<project>/.claude/rules/ocd/honesty.md`
6. `/ocd:setup rules install honesty borrow-before-build --scope user` — both files land at `~/.claude/rules/ocd/`; output shows two `absent → current` rows
7. `/ocd:setup rules uninstall honesty --scope user` — only honesty removed; borrow-before-build still at user scope
8. `/ocd:setup rules status` — report distinguishes deployed state per scope per rule

Additional spot checks:

- `/ocd:setup rules install --all --scope project` — every rule template deploys
- `/ocd:setup rules uninstall --all --scope user` — every deployed rule removed from user scope; directory cleaned up
- `/ocd:setup rules install bogus_rule --scope project` — error: `unknown rule(s): bogus_rule — available: ...`
- `/ocd:setup rules install honesty bogus_rule --scope project` — error names the unknown one; nothing deployed
- `/ocd:setup rules install --scope project` (no targets, no --all) — error: specify targets or --all
- `/ocd:setup rules install honesty` (missing `--scope`) — error: `--scope` required

## Decisions

- Validation runs against the cached plugin install (`~/.claude/plugins/cache/...`), not the in-tree copy. The cache only updates after `/checkpoint` runs successfully on main, so the order is: commit → push → checkpoint → restart → validate
- Both scopes must be exercised independently; per-scope isolation is the headline change versus the prior all-or-nothing model
- An error-handling path failing (step 8 or 9 spot checks) blocks propagation just like a happy-path failure — the operator-facing surface needs to fail informatively, not silently

## Open questions

- ~~The setup skill SKILL.md uses `Read:` to load the system's `workflows/<verb>.md` and follow it inline. Verify this works through the cached plugin install — the path is `${CLAUDE_PLUGIN_ROOT}/systems/{system}/workflows/{verb}.md` and depends on `CLAUDE_PLUGIN_ROOT` being set in the skill execution context~~ — resolved by precedent. `needs_map/SKILL.md`, `navigator/SKILL.md`, `pdf/SKILL.md`, and `git/_release_bootstrap.md` all use the same `Read: ${CLAUDE_PLUGIN_ROOT}/...` pattern; agent expands it at execution time.
- The interactive workflows in `workflows/install.md` and `workflows/uninstall.md` rely on the agent picking `AskUserQuestion` when the workflow says "ask the user". `AskUserQuestion` is in setup's SKILL.md `allowed-tools` so it's available; whether the agent uses it correctly for scope-prompt and lettered target selection is agent-behavior-dependent and best surfaced by running the validation steps.
- ~~The rules system's `__init__.py` is at the package root (not under `setup/`). Verify `importlib.import_module("systems.rules")` resolves the facade functions correctly through the cached install — the discovery scan in setup's `__main__.py` reads the file content for the four required function names~~ — resolved. `_system_discovery.py` globs `*/__init__.py` and text-matches the four required function names; rules `__init__.py` defines all four at top level.

## Status

Pending — runs immediately after the next `/checkpoint` lands the project-root reorganization on main.
