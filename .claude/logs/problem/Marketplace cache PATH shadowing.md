# Marketplace cache PATH shadowing

Plugin `bin/` binaries (e.g. `ocd-run`) resolve against Claude Code's cached marketplace install rather than the `--plugin-dir`-loaded dev copy, leading to stale behavior when invoked from agent Bash subprocesses.

## Reproduction

1. Install a plugin via marketplace (creates `~/.claude/plugins/cache/<author>/<plugin>/<version>/bin/`)
2. Iterate on the dev tree and invoke a child `claude -p --plugin-dir <dev-tree>` session
3. In that session, have the agent run the plugin's `<plugin>-run` binary via Bash
4. PATH resolves against a cached version (often not the latest) rather than the dev tree

## Observed

- `~/.claude/plugins/cache/a-horde-o-bees/ocd/` currently holds 60+ historical versions (0.0.164 through latest), never cleaned up between updates
- During full-plugin sandbox validation, agent's `ocd-run` resolved to `.../ocd/0.0.282/bin/ocd-run` despite the registered install being 0.0.284
- The stale binary's internal paths (e.g. `lib/<cat>/templates/`) do not match the pre-rename layout — so rule/convention/pattern/log deployment silently no-ops
- MCP tools (loaded through the `--plugin-dir` plugin module) work correctly; the issue is purely PATH-based binary resolution

## Suspected root cause

- `--plugin-dir` loads the plugin module but does not prepend its `bin/` to PATH ahead of the marketplace cache's bin directories
- Claude Code's `claude plugins update` registers a new version but leaves prior versions' `bin/` on PATH in inherited subprocess environments

## Workarounds

- Always run `/checkpoint` (commit + push + plugin update) before sandbox-testing plugin behavior so the marketplace install is current
- Invoke binaries by absolute path rather than relying on PATH lookup
- Manual `hash -r` won't help because the issue is PATH ordering, not shell hash cache

## Impact

Blocks reliable iteration using `--plugin-dir` alone for any test that spawns a sub-session to invoke the plugin's scripts. `/ocd:sandbox project` now requires checkpoint first to sidestep this.
