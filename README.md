# a-horde-o-bees Claude Code Plugins

Claude Code plugin marketplace for agent discipline, workflow conventions, and project navigation tools.

## Disclaimer

This is a personal development project. It is experimental, actively evolving, and provided as-is with no stability guarantees, support commitments, or backwards compatibility promises. Plugins may be added, removed, renamed, or fundamentally restructured at any time.

Use at your own discretion. If something breaks, the LICENSE applies.

## Plugins

| Plugin | Status | Description |
|--------|--------|-------------|
| [ocd](plugins/ocd/) | Active | Deterministic enforcement of permissions, rules, and structural conventions with agent-facing project navigation |

## Installation

### Local development

Clone the repo and add the marketplace from your local path:

```
/plugin marketplace add a-horde-o-bees --path /path/to/claude-plugins
/plugin install ocd
```

After making changes to plugin source, sync and reinstall:

```
/plugin marketplace update a-horde-o-bees
/plugin install ocd
```

Reload plugins without restarting the session:

```
/reload-plugins
```

Remove a plugin or the marketplace:

```
/plugin uninstall ocd
/plugin marketplace remove a-horde-o-bees
```

### External users

Add this marketplace by URL (requires access to the repository):

```
/plugin marketplace add a-horde-o-bees --url https://github.com/a-horde-o-bees/claude-plugins.git
```

Then install individual plugins:

```
/plugin install ocd
```

> **Note:** This repo is currently private. External installation requires repository access.

## Versioning

Plugin versions follow `x.y.z` format:

- `x` — major version; starts at `0` until a change breaks previous setups
- `y` — increments on public release (cohesive, ready for consumers); resets `z` to `0`
- `z` — increments on every development commit; required for local plugin reload to detect changes

## License

MIT. See [LICENSE](LICENSE).
