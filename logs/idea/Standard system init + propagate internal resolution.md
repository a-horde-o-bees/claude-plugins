---
tags: ["priority:high"]
---

# Standard system init + propagate internal resolution

Two coupled refactors of the plugin framework's deployment surface. Captured at high priority because the alternative — every newly-added system writing duplicated init boilerplate and freshly-written framework-helper calls perpetuating the anti-pattern — actively grows the cleanup target.

## Driver

Today every system's `_init.py` (6 files, 683 lines total) writes near-identical boilerplate to deploy three artifact classes the framework already knows how to deploy:

- `templates/<type>/*.md` — via `framework.deploy_files`
- `rules/*.md` — via a system-local `_deploy_rules` helper that's near-duplicated across navigator and log
- `paths.csv` — via `framework.deploy_paths_csv`

A new system has to know all three patterns, write the boilerplate, and remember to call them. The framework helpers are too low-level — they leave the orchestration to each caller.

Separately, `framework.deploy_paths_csv` takes `plugin_root` and `project_dir` as args even though both are globally resolvable inside the framework module itself. Every legitimate caller fetches them via `framework.get_plugin_root()` / `framework.get_project_dir()` only to pass them right back — pure cognitive noise. This is the exact anti-pattern flagged in [`logs/decision/navigator.md`](../decision/navigator.md) (`## Navigator resolves project dir internally`); the principle was established but never propagated.

## Cleanup A — propagate internal resolution

**Scope:** `framework.deploy_paths_csv` and any sibling helper that takes globally-resolvable paths.

**Change:** drop `plugin_root` and `project_dir` parameters; resolve internally via `framework.get_plugin_root()` and `framework.get_project_dir()`. Keep `system_name` (not introspectable) and `force` (varies per call).

**Migration:** 2 call sites today (`navigator/_init.py`, `log/_init.py`). Both reduce from a 5-line block to a 2-line call.

**Test-first discipline:** existing `framework` tests (if any) cover deploy_paths_csv. Find them, articulate that the assertion still holds with the simplified signature, confirm RED on the new shape, refactor, GREEN.

## Cleanup B — `framework.standard_init`

**Scope:** Add a single helper that auto-deploys every standard artifact a system ships, replacing the per-system orchestration.

**Behavior:**

```python
def standard_init(force: bool = False) -> list[dict]:
    """Deploy every standard artifact the calling system ships.

    Auto-discovers from the calling system's directory:
      - templates/<type>/*.md  → logs/<type>/<file>     (via deploy_files)
      - rules/*.md             → .claude/rules/<plugin>/<file>
      - conventions/*.md       → .claude/conventions/<plugin>/<file>
      - paths.csv              → .claude/<plugin>/<system>/paths.csv (via deploy_paths_csv)

    Returns combined files list in the standard {path, before, after}
    shape. Domain-specific init work (DB creation, etc.) goes on top
    in the caller's init().
    """
```

System name resolution: infer from the caller's `__package__` (`systems.log._init` → `log`). Or accept as explicit arg if introspection is fragile across `runpy.run_module` / `importlib.import_module` invocation paths.

Each system's `init()` collapses to:

```python
def init(force: bool = False) -> dict:
    files = framework.standard_init(force=force)
    # Domain-specific additions (DB setup, etc.)
    return {"files": files, "extra": _status_extra()}
```

**Per-system conventions extension:** `standard_init` also picks up a system's `conventions/` directory and deploys to the project's conventions corpus — parallel to `rules/`. Today all conventions live centralized under `plugins/ocd/systems/conventions/templates/`, but several are domain-specific (e.g., `mcp-server.md` is conceptually owned by navigator). Extending `standard_init` lets each system ship its own conventions alongside its own rules.

**Migration scope:** 6 system inits to update (`refactor`, `permissions`, `conventions`, `rules`, `log`, `navigator`). Five collapse to ~3 lines; navigator retains its DB-specific work on top of standard_init.

**Test-first discipline:**
- Synthetic plugin fixture with templates/, rules/, conventions/, paths.csv. `standard_init()` produces the expected `files` list and writes the expected files to disk.
- Per-existing-system regression: invoking each system's init() before and after migration produces equivalent file deployment outputs.

## Per-system convention move

If `standard_init` supports per-system conventions, decide which existing centralized conventions move to which systems:

- `mcp-server.md` → navigator (only MCP server today)
- `audit-skill-md.md`, `audit-triage.md` → audit-skill systems (currently sandbox branches)
- `python.md`, `claude-md.md`, `architecture-md.md`, `readme-md.md`, `skill-md.md`, `governance-md.md` → universal; stay in the conventions system OR move to a `framework/conventions/` directory if framework owns the universal corpus

Decision per file deferred until standard_init lands — the move is a downstream consumer.

## Why now / priority

Currently writing fresh code that perpetuates the anti-pattern (the 4-arg `deploy_paths_csv` call I just landed in `log/_init.py`). Every new system increases migration cost. Better to land before the next system arrives (blueprint plugin parity is queued under Active sandbox features in ROADMAP).

## Suggested execution order

1. **Cleanup A** in isolation — small, scoped, two callers. Land first to validate the principle propagates cleanly.
2. **Cleanup B** — write `standard_init` with synthetic-fixture test. Migrate one system (rules or conventions — simplest). Validate. Migrate the rest in order of complexity (refactor, permissions, log, navigator). Per-system regression tests catch silent behavior changes.
3. **Per-system convention move** — separate session, after standard_init is stable. Inventory current conventions, decide owners, move sources, validate via auto_init.

## References

- [`logs/decision/navigator.md`](../decision/navigator.md) `## Navigator resolves project dir internally` — establishes the internal-resolution principle this propagates.
- [`logs/decision/framework.md`](../decision/framework.md) `## Plugin env vars raise vs fallback` — the framework helpers this builds on.
- [`plugins/ocd/systems/framework/_deployment.py`](../../plugins/ocd/systems/framework/_deployment.py) — current deployment primitives.
- [`logs/idea/Per-plugin permission contribution.md`](Per-plugin%20permission%20contribution.md) — adjacent idea (each plugin owns its permissions); standard_init's conventions extension is the same shape.
