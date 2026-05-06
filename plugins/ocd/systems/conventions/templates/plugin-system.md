---
includes:
  - "**/systems/*/__init__.py"
  - "**/systems/*/workflows/install.md"
  - "**/systems/*/workflows/uninstall.md"
---

# Plugin System Setup Conventions

Plugin-specific addendum to `system-structure.md`. Every system in an ocd-style plugin participates in the setup surface — install, uninstall, status, purpose — through a fixed Python facade and a pair of workflow files. This convention documents what's required beyond the general system layout.

## Python Facade

The system's package `__init__.py` exposes four functions with these exact signatures:

```python
def purpose() -> str: ...
def status(scope: str | None = None) -> dict: ...
def install(scope: str, target: str | None = None, force: bool = False) -> dict: ...
def uninstall(scope: str, target: str | None = None) -> dict: ...
```

- **`purpose()`** — one-line purpose statement; called by the setup `purposes` aggregator to assemble the lettered system list.
- **`status(scope=None)`** — reports install state per artifact at the requested scope. `None` reports across every supported scope.
- **`install(scope, target, force)`** — deploys at the chosen scope. `target='all'` or `None` installs every artifact this system owns; a specific target name installs one. `force=True` overwrites divergent deployed copies.
- **`uninstall(scope, target)`** — removes one or all deployed artifacts at the chosen scope.

Return shape from install/uninstall/status is `{"files": [...], "extra": [...]}` per the Init/Status Contract in `python.md`.

## Setup Workflows

Two markdown files under the system's `workflows/` directory:

- `workflows/install.md` — interactive install workflow loaded by `/ocd:setup <system> install`
- `workflows/uninstall.md` — interactive uninstall workflow loaded by `/ocd:setup <system> uninstall`

Both follow `workflows-md.md`. The install flow prompts for scope, presents available targets (lettered selection for multi-pick or `all`), confirms with the user, and dispatches to the system's CLI. The uninstall flow mirrors that shape for removal.

The `status` verb is read-only; the setup CLI calls `status(scope=...)` directly without a markdown workflow. No `workflows/status.md` is required.

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

Scope is required for install and uninstall — deny-by-default. `status` accepts `scope=None` to report across every supported scope.

## Targets

Some systems own multiple artifacts and accept a target name to operate on one (e.g., the rules system accepts a per-template name). Others are atomic — install/uninstall takes only scope, no meaningful target. Systems with sub-targets reject unknown names with an error entry; atomic systems ignore the target argument.

When `target` is `None` or `'all'`, install/uninstall operates on every artifact the system owns.

## Hidden Until Migrated

Systems without a top-level `__init__.py` exposing the four facade functions are invisible to the setup skill — they do not appear in `purposes` or `statuses` output, and `/ocd:setup <name>` errors with "unknown system". This keeps the setup surface conformant: every system listed has the expected handler shape, and incremental migration leaves un-migrated systems silent rather than half-supported.

## Operational CLI Gating

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

The gate prevents agents from invoking operational commands on a system the user has not opted in to, matching the broader hide-until-installed principle. The setup CLI itself is always available — it is the bootstrap path for every system.
