# a-horde-o-bees Claude Code Plugins

Claude Code plugin marketplace for agent discipline, workflow conventions, and project navigation tools.

## Disclaimer

This is a personal development project. It is experimental, actively evolving, and provided as-is with no stability guarantees, support commitments, or backwards compatibility promises. Plugins may be added, removed, renamed, or fundamentally restructured at any time.

Use at your own discretion. If something breaks, the LICENSE applies.

## Plugins

| Plugin | Description |
|--------|-------------|
| [ocd](plugins/ocd/) | Deterministic enforcement of permissions, rules, and structural conventions with agent-facing project navigation |

## Installation

Two channels ship from this repo — pick the one that matches how much churn you want to accept:

### Stable channel (recommended for use)

Pins to the most recent tagged release on a curated `release/*` branch. Dev artifacts (tests, CI configs) stripped. Updates only when a new release is cut.

```
/plugin marketplace add https://raw.githubusercontent.com/a-horde-o-bees/claude-plugins/main/.claude-plugin/marketplace.stable.json
/plugin install ocd@a-horde-o-bees
```

### Dev channel (early adopters and contributors)

Tracks `main`. Ships with tests, CI configs, and in-flight changes. Updates on every push to `main`; `0.0.z` version auto-bumps for cache invalidation.

```
/plugin marketplace add https://github.com/a-horde-o-bees/claude-plugins.git
/plugin install ocd@a-horde-o-bees-dev
```

### After install

Restart Claude session so hooks and commands load, then initialize in target project:

```
/ocd:setup init
```

Restart Claude session again so deployed rules auto-load into context.

Update plugins after upstream changes. Substitute the marketplace name for whichever channel you installed (`a-horde-o-bees` for stable, `a-horde-o-bees-dev` for dev):

```
/plugin marketplace update <marketplace-name>
/reload-plugins
```

After updating, check if deployed rules and conventions need updating:

```
/ocd:setup status
```

If any files show `divergent`, force-update and restart:

```
/ocd:setup init --force
/exit
claude --continue
```

Restart after init is only needed when rule files change. Convention-only updates take effect immediately.

Remove a plugin or the marketplace. Substitute the marketplace name for whichever channel you installed:

```
/plugin uninstall ocd
/plugin marketplace remove <marketplace-name>
```

### Local development

For contributors working on plugin source.

**After cloning, run `/ocd:setup init` in the cloned project to deploy local rules, conventions, and the navigator database.** These files are gitignored — every clone initializes its own. Skipping install leaves the working agent without the rules that govern development here, and the navigator database will be missing.

Two approaches:

#### Marketplace-based (recommended)

Develop within a clone that is also the marketplace source. Plugins load via the installed marketplace, so changes flow through git:

```
/push
```

Commits and pushes all changes. Then refresh the marketplace cache and reload (contributors typically work against the dev channel):

```
/plugin marketplace update a-horde-o-bees-dev
/reload-plugins
```

Restart (`/exit` then `claude --continue`) only required when `.claude/rules/` files changed. Skill and convention changes take effect after reload.

#### Plugin-dir (session-only)

Load plugins directly from a local clone without marketplace:

```
git clone https://github.com/a-horde-o-bees/claude-plugins.git
claude --plugin-dir ./claude-plugins/plugins/ocd
```

After making source changes, reload and restart:

```
/reload-plugins
/exit
claude --continue
```

`/reload-plugins` picks up script changes. Restart is required for skill content (SKILL.md) to take effect. `--continue` resumes the conversation with fresh context.

Check if deployed rules and conventions need updating:

```
/ocd:setup status
```

If any files show `divergent`, force-update and restart:

```
/ocd:setup init --force
/exit
claude --continue
```

Restart after init is only needed when rule files change. Convention-only updates take effect immediately.

Notes:

- `--plugin-dir` is session-only; no persistent setting exists
- When a `--plugin-dir` plugin shares a name with an installed marketplace plugin, the local copy takes precedence for that session
- `--debug` flag shows plugin loading diagnostics
- `claude plugin validate {PATH_TO_PLUGIN}` validates manifest without a session

## Architecture

See [architecture.md](architecture.md) for marketplace structure, shared infrastructure, and how plugins relate. Each plugin documents its own internals:

- [ocd architecture](plugins/ocd/architecture.md) — hooks, rules, navigator, conventions engine

## Versioning

Plugin versions follow `x.y.z` format. Main and release branches live in disjoint version spaces — no `(x,y,z)` tuple ever points at more than one commit.

- **Main** tracks `0.0.z` permanently. `z` is a monotonic dev build counter bumped on every commit to catch local reload detection. Main is never released from directly.
- **Release branches** own real semver. A new release is cut at `x.y.0` on a dedicated branch; patches on that branch bump `z`. Release branches are the install target for consumers; main is for development only.

## License

MIT. See [LICENSE](LICENSE).
