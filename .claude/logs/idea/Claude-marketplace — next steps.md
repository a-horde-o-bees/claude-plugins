# Claude-marketplace — next steps

Queued work for the claude-marketplace pattern + diff refactor. Ordered so each step's gate is explicit. Stop at the marked gate and revalidate before proceeding.

## Context

- Pattern doc: `plugins/ocd/systems/patterns/templates/claude-marketplace.md` (deployed to `.claude/patterns/ocd/claude-marketplace.md`). Decisions and Features sections with ★ docs-prescribed / ☆ docs-shown-valid / blank silent annotations. Adoption counts per applicable subset. References section lists primary sample (18) and dep-management sample (20).
- Diff doc: `claude-marketplace--diff.md` at repo root. Project alignment audit; still reflects earlier framing and needs refresh against the current pattern.
- Unpushed state: caught up with origin; workflow-file commits deferred pending CI/CD research (see removal commit `70def06`).

## Research wave

Parallelizable. Run 22 first or alongside 14/15 — 22 may subsume them or surface new Decisions that change their scope.

**22. Discovery — missing design factors.** Find plugins that rank highly by quality or adoption signals (GitHub stars, featured placement in `claude-plugins-official`, visible engagement, maintainer reputation) and surface design factors NOT yet covered by the pattern doc's Decisions. Goal: answer "what are we missing?" Candidate signals: error handling in hooks, user-facing help text, skill description quality, MCP server architecture, agent delegation, cross-plugin dependencies, `userConfig` sensitive-value handling, release notes format, test fixture conventions. Report with per-repo citations; expect surprises.

**14. `bin/` implementation patterns.** Find 10+ plugins that ship `bin/` and analyze what they put there, how they resolve venvs/runtimes, whether wrappers follow a pattern. Include Anthropic-owned plugins (figma ships a Bun-backed binary) as a reference point. Add a *Bin wrapper implementation* Decision to the pattern doc if clear patterns emerge.

**15. CI/CD patterns.** Research what tests run on push/PR, what tag-triggered workflows do, whether `claude plugin validate` runs in CI, matrix strategies (OS/Python versions), caching, release-automation shapes (`release-please`, manual bash, etc.). Add a *CI/CD* Decisions section to the pattern doc with adoption counts.

## Pattern fold-in

After each research wave completes, fold findings into `claude-marketplace.md` as new Decision subsections (or amendments to existing ones) with ★/adoption data and References updates for any new sample repos.

## 16. Diff refresh — **GATE: stop and revalidate after this lands**

Update `claude-marketplace--diff.md` to reflect:

1. SessionStart + `${CLAUDE_PLUGIN_DATA}` is ★ docs-prescribed with 17/20 dep-heavy adoption — flip the "novel-but-defensible" framing to "dominant convention + docs-prescribed."
2. Channel selection: this project matches community majority but is NOT ★ — docs prescribe two marketplaces with different `name` values.
3. Version authority: `plugin.json` only for relative-path source is NOT ★ — docs prescribe marketplace-entry version for relative sources.
4. New action items for `install_deps.sh` docs-prescribed gaps:
    - Manifest-diff change detection (`diff -q`)
    - Retry-next-session `rm` invariant on install failure
    - Structured failure output via `systemMessage` JSON
5. Fold in findings from research waves 22/14/15 where they affect alignment.

**Stop here.** Do not proceed to cleanup or implementation tasks until the user revalidates direction against the refreshed diff doc.

## Post-gate: cleanup + implementation (pending revalidation)

**17. Rename `v0.1.0` branch → `release/0.1`.** Resolve branch-vs-tag name collision. `git branch -m v0.1.0 release/0.1; git push origin release/0.1; git push origin :v0.1.0; git branch --set-upstream-to=origin/release/0.1`. Update references (README stable install command, etc.).

**18. Consolidate `tests/plugins/ocd/pytest.ini` into `pyproject.toml`.** Community convention is `[tool.pytest.ini_options]` in `pyproject.toml` (6/10); dedicated `pytest.ini` is 0/10 in the sample. Update `_test_discovery.py` if the `pytest_ini` path changes; run test suite to verify.

**19. Add `.github/workflows/release.yml`.** Tag-triggered release workflow, standard shape (5/14 release-cadence repos). Will reintroduce workflow files that were removed in `70def06` pending CI/CD research. Pairs with `scripts/release.sh`. Requires `workflow` scope on the GitHub PAT.

**20. Update `install_deps.sh` for docs-prescribed idioms.**
- Manifest-diff change detection: `diff -q` bundled `requirements.txt` against cached copy in `$CLAUDE_PLUGIN_DATA`, reinstall only when changed.
- Retry-next-session invariant: trailing `rm -f "$CLAUDE_PLUGIN_DATA/requirements.txt"` on install failure.
- Structured failure output: emit JSON `systemMessage` on failure rather than silent stderr.
- Optional: Python minor-version tracking and rebuild on change.

## Not in scope for this queue

- `research-and-refactor loop` for blueprint (separate idea log `.claude/logs/idea/Research-and-refactor loop for blueprint.md`)
- Blueprint plugin parity work (tracked in `_status.md` on `sandbox/blueprint-plugin` branch)
