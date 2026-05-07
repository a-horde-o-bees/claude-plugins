---
includes:
  - "**/systems/*/__init__.py"
  - "**/systems/*/workflows/install.md"
  - "**/systems/*/workflows/uninstall.md"
---

# Plugin System Setup Conventions

Plugin-specific addendum to `system-structure.md`. Every migrated system in an ocd-style plugin participates in the setup surface (`/ocd:setup <system>`) through a Python facade. The facade declares minimum identity (`purpose()`) plus whatever verbs the system needs — either the standard set (status, list, install, uninstall) or its own verb shape via `dispatch()`. This convention documents the contract, the verb dispatch model, and the workflow files that pair with the standard CRUD verbs.

## Required identity

The system's package `__init__.py` must expose `purpose()`:

```python
def purpose() -> str: ...
```

Returns a one-line purpose statement consumed by the setup `list` aggregator to assemble the lettered system list. A system that does not export `purpose()` is invisible to setup discovery — it does not appear in `setup list` / `setup status` output, and `/ocd:setup <name>` errors with "unknown system."

## Verb shape — two models

Beyond `purpose()`, a system declares its verbs in one of two ways:

### Standard handlers

For systems that fit the install / uninstall / status / list shape, expose the matching functions. The setup CLI handles argparse and output formatting:

```python
def status(scope: str | None = None) -> dict: ...
def list_items() -> dict: ...
def install(scope: str, targets: list[str] | None = None, force: bool = False) -> dict: ...
def uninstall(scope: str, targets: list[str] | None = None) -> dict: ...
```

- **`status(scope=None)`** — reports state per artifact at the requested scope. `None` reports across every supported scope. Returns either of two shapes:
    - **Wide table** — `{"rows": [{"name", **{column: state}}, ...], "columns": [scope, ...], "extra": [...]}`. One row per artifact with one column per scope queried; the setup CLI renders a per-scope table. Use this when the same artifact has independent state per scope (e.g., rule templates deployable at user OR project independently).
    - **Flat list** — `{"files": [{"path", "before", "after"}, ...], "extra": [...]}`. One row per file; the setup CLI renders a path → state list. Use this for systems whose artifacts are inherently single-scope or whose summary belongs entirely in `extra`.
- **`list_items()`** — catalog of available items with one-paragraph purpose per item. Returns `{"items": [{"name", "purpose"}, ...], "extra": [...]}`.
- **`install(scope, targets, force)`** — deploys at the chosen scope. `targets=None` deploys all; otherwise each entry is a target name. `force=True` overwrites divergent deployed copies.
- **`uninstall(scope, targets)`** — removes deployed artifacts. `targets=None` removes all; otherwise each entry is a target name.

Each function is independently optional: a read-only system might expose only `status` and `list_items`; an atomic system might expose `install`/`uninstall` without `list_items`.

### Custom dispatch

For systems whose verbs do not fit the standard shape (e.g., permissions has `deploy` / `clean` / `analyze`), expose `dispatch()` instead:

```python
def dispatch(verb: str, args: list[str]) -> None: ...
```

The setup CLI routes every verb to `dispatch()` when present — standard handlers are bypassed. `dispatch()` parses its own argparse per verb and either prints output directly or returns. Systems that need it typically also expose `verbs()` so the usage display knows what verbs exist:

```python
def verbs() -> list[dict]:
    return [
        {"name": "deploy", "description": "..."},
        {"name": "analyze", "description": "..."},
        ...
    ]
```

A system declares EITHER standard handlers OR dispatch — not both. Dispatch always wins when present, so mixing the two would leave standard handler functions unreachable.

## Setup workflows

Standard `install` and `uninstall` verbs use markdown workflows under `workflows/`:

- `workflows/install.md` — interactive install workflow loaded by `/ocd:setup <system> install`
- `workflows/uninstall.md` — interactive uninstall workflow loaded by `/ocd:setup <system> uninstall`

Both follow `workflows-md.md`. The install flow prompts for scope, presents available targets (lettered selection for multi-pick or `all`), confirms with the user, and dispatches to the system's CLI. The uninstall flow mirrors that shape for removal.

The `status` and `list` verbs are read-only; the setup CLI calls them directly without a markdown workflow. Dispatch-based verbs are CLI-direct unless the system chooses to add its own workflow files.

## Scope

Each system declares which scopes it supports via a `SUPPORTED_SCOPES` tuple in `__init__.py`. Calling install/uninstall with an unsupported scope returns an error in `extra`, not a crash:

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

Scope is required for install and uninstall — deny-by-default. `status` accepts `scope=None` to report across every supported scope. Custom verbs declare scope requirements per verb in their dispatch.

## Targets

Standard `install`/`uninstall` accept multiple positional targets or `--all`:

```
ocd-run setup <system> install <target1> <target2> ... --scope <user|project>
ocd-run setup <system> install --all --scope <user|project>
```

`targets=None` (passed when `--all` is set) operates on every artifact. `targets=[<name>, ...]` operates on the named ones. Unknown target names produce an error entry; the system rejects the whole batch rather than partially deploying.

Atomic systems with no meaningful targets accept `targets=None` and ignore non-empty lists.

## Operational CLI gating

When a system has its own operational CLI separate from the setup surface (e.g., `ocd-run navigator scan`, `ocd-run transcripts query`), that CLI gates on install state. Each operational entry point calls the system's own `status()` early and refuses to run if the system is not installed at any scope:

```python
def main() -> None:
    from . import status as _system_status
    state = _system_status()
    if not any(f["before"] == "current" for f in state.get("files", [])):
        print(
            "<system> is not installed. Run `/ocd:setup <system> install --scope <user|project>` first.",
            file=sys.stderr,
        )
        sys.exit(1)
    ...
```

The gate prevents agents from invoking operational commands on a system the user has not opted in to, matching the broader hide-until-installed principle codified in `system-dormancy.md`. The setup CLI itself is always available — it is the bootstrap path for every system.
