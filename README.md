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

Clone the repo and install the marketplace from your local path:

```
/plugin marketplace add a-horde-o-bees --path /path/to/claude-plugins
```

Then install individual plugins:

```
/plugin install ocd
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

Plugin versions follow `0.x.y` format:

- `0` — leading zero until a change breaks previous setups
- `x` — increments on public release (cohesive, ready for consumers); resets `y` to `0`
- `y` — increments on every development commit; required for local plugin reload to detect changes

## License

MIT. See [LICENSE](LICENSE).
