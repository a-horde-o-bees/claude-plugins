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

1. `/ocd:setup` — usage banner shows meta verbs (`purposes`, `statuses`, `permissions`) and `rules` in the migrated-systems list
2. `/ocd:setup purposes` — lettered list with `A. rules — <purpose statement>`; no other systems shown (un-migrated systems invisible)
3. `/ocd:setup rules` — system usage prints purpose, lists `status`, `install`, `uninstall` verbs with first-paragraph descriptions
4. `/ocd:setup rules install honesty --scope project` — file lands at `<project>/.claude/rules/ocd/honesty.md`; output shows `absent → current`
5. `/ocd:setup rules install honesty --scope user` — file lands at `~/.claude/rules/ocd/honesty.md`; output shows `absent → current`
6. `/ocd:setup rules uninstall honesty --scope user` — file removed from `~/.claude/rules/ocd/`; output shows `current → absent`
7. `/ocd:setup rules status` — report shows `honesty.md` as `current` at project scope, `absent` at user scope

Additional spot checks:

- `/ocd:setup rules install --all --scope project` — all 28+ rule templates deploy
- `/ocd:setup rules install bogus_rule --scope project` — error output names the rule as unknown and lists available
- `/ocd:setup rules install honesty` (missing `--scope`) — error: `--scope` required

## Decisions

- Validation runs against the cached plugin install (`~/.claude/plugins/cache/...`), not the in-tree copy. The cache only updates after `/checkpoint` runs successfully on main, so the order is: commit → push → checkpoint → restart → validate
- Both scopes must be exercised independently; per-scope isolation is the headline change versus the prior all-or-nothing model
- An error-handling path failing (step 8 or 9 spot checks) blocks propagation just like a happy-path failure — the operator-facing surface needs to fail informatively, not silently

## Open questions

- The setup skill SKILL.md uses `Read:` to load the system's `workflows/<verb>.md` and follow it inline. Verify this works through the cached plugin install — the path is `${CLAUDE_PLUGIN_ROOT}/systems/{system}/workflows/{verb}.md` and depends on `CLAUDE_PLUGIN_ROOT` being set in the skill execution context
- The interactive workflows in `workflows/install.md` and `workflows/uninstall.md` use `AskUserQuestion`. Verify scope-prompt and lettered target selection render correctly when the skill executor runs through the markdown
- The rules system's `__init__.py` is at the package root (not under `setup/`). Verify `importlib.import_module("systems.rules")` resolves the facade functions correctly through the cached install — the discovery scan in setup's `__main__.py` reads the file content for the four required function names

## Status

Pending — runs immediately after the next `/checkpoint` lands the project-root reorganization on main.
