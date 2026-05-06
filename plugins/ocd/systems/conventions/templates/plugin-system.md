---
includes:
  - "**/systems/*/setup/__init__.py"
  - "**/systems/*/setup/install.md"
  - "**/systems/*/setup/uninstall.md"
---

# Plugin System Setup Conventions

Every system in a plugin owns a `setup/` directory at its root that exposes its install, uninstall, status, and purpose surface to the setup orchestrator. This convention defines the shape that surface must take.

## Directory Shape

```
systems/<name>/setup/
├── __init__.py       Python facade — deterministic operations
├── install.md        Markdown workflow — interactive install verb
└── uninstall.md      Markdown workflow — interactive uninstall verb
```

`status` and `purpose` are deterministic Python functions called by setup-level aggregators. `install` and `uninstall` are interactive markdown workflows that prompt for scope and target, confirm with the user, and dispatch to per-system CLI commands. The split mirrors the read/write distinction — read-only ops are direct function calls; mutating ops orchestrate user interaction.

## Python Facade

`setup/__init__.py` exposes four functions with these exact signatures:

```python
def purpose() -> str: ...
def status(scope: str | None = None) -> dict: ...
def install(scope: str, target: str | None = None, force: bool = False) -> dict: ...
def uninstall(scope: str, target: str | None = None) -> dict: ...
```

- **`purpose()`** — one-line purpose statement; the `purposes` aggregator calls it for every system to assemble the lettered system list.
- **`status(scope=None)`** — reports install state per artifact at the requested scope. `None` reports across every supported scope. Each entry has the `{path, before, after}` shape from the Init/Status Contract.
- **`install(scope, target, force)`** — deploys at the chosen scope. `target='all'` or `None` installs every artifact this system owns; a specific target name installs one. `force=True` overwrites divergent deployed copies.
- **`uninstall(scope, target)`** — removes one or all deployed artifacts at the chosen scope.

Return shape from install/uninstall/status is `{"files": [...], "extra": [...]}` per the Init/Status Contract in `python.md`.

## Scope

Each system declares which scopes it supports via a `SUPPORTED_SCOPES` tuple. Calling install/uninstall with an unsupported scope returns an error in `extra`, not a crash:

```python
SUPPORTED_SCOPES = ("user", "project")  # or one of these alone

def install(scope: str, ...) -> dict:
    if scope not in SUPPORTED_SCOPES:
        return {
            "files": [],
            "extra": [{"label": "error", "value": f"unsupported scope: {scope}"}],
        }
    ...
```

Scope semantics:

- `user` — deploys under `~/.claude/<category>/<plugin>/...` (auto-loaded across every project)
- `project` — deploys under `<project>/.claude/<category>/<plugin>/...` (scoped to the active project)

Scope is required for install and uninstall — deny-by-default. `status` accepts `scope=None` to report across every supported scope.

## Targets

Some systems own multiple artifacts and accept a target name to operate on one (e.g., `rules` accepts a per-template name). Others are atomic — install/uninstall takes only scope, no meaningful target. Systems with sub-targets reject unknown names with an error entry; atomic systems ignore the target argument.

When `target` is `None` or `'all'`, install/uninstall operates on every artifact the system owns.

## Markdown Workflows

`setup/install.md` and `setup/uninstall.md` are PFN workflows the setup skill `Call:`s when the CLI dispatches `/ocd:setup <name> install` or `/ocd:setup <name> uninstall`. Each workflow:

1. If no arguments: present usage and the catalog of available targets at the relevant scopes
2. Resolve missing scope via `AskUserQuestion` — offer the scopes the system supports
3. Resolve missing target via `AskUserQuestion` — lettered multi-select for `all` or specific names
4. Confirm with the user — show scope, target, and what will deploy or remove
5. `bash:` to `ocd-run setup <name> <verb> {target} --scope {scope} [--force]`
6. Surface CLI output verbatim — per-file state transitions

The markdown workflow is the consumer-facing layer; the Python facade is the deterministic core. Both consumers (skill markdown and dev orchestration) reach the same Python.

## Hidden Until Migrated

Systems without a `setup/` folder are invisible to the setup skill — they do not appear in `purposes` or `statuses` output, and `/ocd:setup <name>` errors with "unknown system". This keeps the setup surface conformant: every system listed has the expected handler shape, and incremental migration leaves un-migrated systems silent rather than half-supported.
