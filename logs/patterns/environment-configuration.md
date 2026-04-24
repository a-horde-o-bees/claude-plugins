# Environment Configuration

How agents and plugins persist, discover, and resolve configuration across session boundaries, scopes, and execution contexts. Each mechanism serves a different lifetime and visibility — choosing the wrong one causes silent misconfiguration or forces infrastructure to compensate.

## Mechanisms

| Mechanism | Lifetime | Scope | Set by | Discoverable via |
|-----------|----------|-------|--------|------------------|
| Claude env vars | Session | Process | Claude Code runtime | `${VAR}` in bash, `os.environ` in Python |
| Plugin settings | Persistent | User or project | User (settings.json) | Settings API, file read |
| Git config | Persistent | User (`--global`) or repo (local) | User or tooling | `git config --get key` |
| Shell env vars | Session | Process tree | User or shell profile | `${VAR}` in bash, `os.environ` in Python |
| File-based | Persistent | Project directory | User or tooling | File read at known path |

### Claude Env Vars

Set by Claude Code runtime before skill, hook, and MCP server execution. Not user-configurable — the runtime owns these values.

| Variable | Available in | Purpose |
|----------|-------------|---------|
| `CLAUDE_PROJECT_DIR` | Skills, hooks | Project root directory |
| `CLAUDE_PLUGIN_ROOT` | Skills, hooks, MCP servers | Plugin installation directory |
| `CLAUDE_PLUGIN_DATA` | Skills, hooks | Per-plugin persistent storage directory |
| `CLAUDE_SESSION_ID` | Skills, hooks, MCP servers | Current session identifier |

**Caveat:** `CLAUDE_PROJECT_DIR` is not propagated to MCP server subprocesses. MCP servers bootstrap it from cwd at import time — Claude Code guarantees the MCP server cwd matches the project directory. See `mcp-server.md` for the bootstrap pattern.

### Plugin Settings

Claude Code's own configuration in `settings.json` at two scopes:

- **Project** (`.claude/settings.json`) — version-controlled, shared with collaborators
- **User** (`~/.claude/settings.json`) — personal, applies to all projects

Used for: permission patterns (allow/deny), hooks, model preferences, plugin configuration. Read via Claude Code's settings API. Skill-facing — agents read these to understand what's permitted and how hooks are configured.

### Git Config

Standard git configuration at two scopes:

- **Global** (`~/.gitconfig`) — applies to all repos on the machine
- **Local** (`.git/config`) — applies to one repo only

Used for: persistent per-user preferences that git operations or pre-commit hooks need. Set once, survives sessions, inspectable with `git config --get`. Not version-controlled at either scope — local config lives inside `.git/`.

Examples:

- `user.claude-coauthor` — opt-in co-author trailer on commits
- `core.hookspath` — point git to version-controlled hooks directory

**When to use over plugin settings:** when the value is consumed by git operations (hooks, commit workflows) rather than Claude Code features, or when the value should be inspectable via standard `git config` tooling without Claude Code running.

### File-Based

Configuration stored as files in known project locations. Used when the configuration is inspectable content that users edit directly rather than key-value pairs.

Examples:

- `.claude/ocd/pdf/templates/<name>/` — template selection via filesystem (the directory IS the config; one subfolder with one `.css` plus assets)
- `.claude/ocd/navigator/navigator.db` — SQLite database as configuration + state

**When to use:** when the configuration is rich content (stylesheets, databases, templates) rather than scalar values, or when filesystem inspection is the natural discovery mechanism.

## Resolution Patterns

When a value could come from multiple sources, resolution follows a deterministic chain with no silent fallbacks. The Python convention's *Project, Plugin, and Data Directory Resolution* section codifies the specific chains for path resolution — the pattern generalizes:

1. **Primary source** — the most specific source (env var, local config, project setting)
2. **Fallback** — a deterministic derivation when the primary is absent (git root from repo structure, plugin root from code layout)
3. **Failure** — raise or report when neither source resolves; never silently default to a value that could be wrong (e.g., cwd as project root)

Silent fallbacks — values that resolve to something plausible but wrong — are worse than failures. A missing value that raises is immediately diagnosable; a wrong value that silently propagates corrupts downstream state.
