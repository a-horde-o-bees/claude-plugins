---
tagline: Dormancy contract — systems are invisible and silent until installed
---

# System Dormancy

Every plugin system stays invisible and silent until the user installs it. An uninstalled system costs no tokens, fires no hooks, registers no tools, and contributes no rules — its presence in the plugin source has zero observable impact on a session that has not opted in. Dormancy is the contract every system author must satisfy at every surface the system exposes.

## Surfaces and enforcement

Each surface a system exposes has its own dormancy mechanism, matched to how that surface reaches the agent. `ARCHITECTURE.md` System Dormancy is the long-form description; this convention codifies the contract.

| Surface | Dormancy mechanism |
|---|---|
| Setup CLI discovery | `_discover_systems` lists only systems whose `__init__.py` exposes the migration facade; un-migrated systems are absent from `setup list` / `setup status` output |
| Rule contributions | System-specific rule files ship with their system; absent install means absent file means absent rule load |
| MCP server | Server starts but registers zero tools until its readiness check passes |
| Skill `Route` | Routes to `/ocd:setup <system> install` if dependencies absent; never acts on missing state |
| Hook | First executable line bails to a noop response when the owning system's status is absent |

## Hook bail-out pattern

Hooks tied to a specific system must gate on that system's install state at the very top of dispatch:

```python
def main() -> None:
    from systems.<this_system> import status as _system_status
    state = _system_status()
    if not any(f["before"] == "current" for f in state.get("files", [])):
        return  # dormant — emit nothing, take no actions
    # real dispatch only past the gate
```

The gate is the first executable statement; nothing — no logging, no path resolution, no database open — runs before it. Any side effect before the gate violates dormancy.

Plugin-wide hooks (those that operate regardless of any one system's state, e.g., an auto-approval hook that gates Bash calls) are exempt: there is no specific system whose absence makes them moot. Every hook tied to a specific system must bail.

## Why this matters

Every system in the catalog is a potential source of cost: tokens for loaded rules, latency for hook execution, attention diverted to surfaces the user does not need. Dormancy is what lets the plugin grow without each new system imposing on every user. Users opt in surface by surface; uninstalled surfaces are zero-cost.
