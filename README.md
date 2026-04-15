# a-horde-o-bees Claude Code Plugins

Claude Code plugin marketplace for agent discipline, workflow conventions, and project navigation tools.

## Disclaimer

This is a personal development project. It is experimental, actively evolving, and provided as-is with no stability guarantees, support commitments, or backwards compatibility promises. Plugins may be added, removed, renamed, or fundamentally restructured between versions.

Use at your own discretion. If something breaks, the LICENSE applies.

## Release Branches

This branch (`v0.1.0`) is the first public release snapshot. Development happens on `main`; consumer installs should target a release branch or tag so the content is stable. Future releases will get their own `v0.x.y` branches.

## Plugins

| Plugin | Description |
|--------|-------------|
| [ocd](plugins/ocd/) | Deterministic enforcement of permissions, rules, and structural conventions with agent-facing project navigation |

## Installation

Add the marketplace (pinned to this release) and install the plugin:

```
/plugin marketplace add https://github.com/a-horde-o-bees/claude-plugins.git#v0.1.0
/plugin install ocd@a-horde-o-bees
```

Restart the Claude session so hooks and commands load, then initialize the plugin in your target project:

```
/ocd:init
```

Restart the session once more so deployed rules auto-load into context.

### Updating

When a new release lands, refresh the marketplace cache and reload:

```
/plugin marketplace update a-horde-o-bees
/reload-plugins
```

Check whether deployed rules and conventions need refreshing:

```
/ocd:status
```

If any files show `divergent`, force-update and restart:

```
/ocd:init --force
/exit
claude --continue
```

Restarting after `init` is only needed when rule files change. Convention-only updates take effect immediately.

### Removing

```
/plugin uninstall ocd
/plugin marketplace remove a-horde-o-bees
```

## Architecture

See [architecture.md](architecture.md) for marketplace structure and how plugins are packaged. Each plugin documents its own internals:

- [ocd architecture](plugins/ocd/architecture.md) — hooks, rules, navigator, conventions engine, skill catalog

## Versioning

Plugin versions follow `x.y.z`:

- `x` — major; starts at `0` until a change breaks previous setups
- `y` — public release; cohesive set of changes ready for consumers; resets `z` to `0`
- `z` — every development commit; required for local plugin reload to detect changes

## License

MIT. See [LICENSE](LICENSE).
