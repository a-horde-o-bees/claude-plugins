# Gotchas

Project-facing observations about upstream or environmental behavior that this project navigates around because the root cause sits outside our control. Each entry names the cause, the impact on how agents and users operate, and the workaround. Entries stay until the upstream situation changes.

If this file grows past ~3 entries and a shared structure emerges across them, promote to a `logs/gotcha/` log type so every entry is individually discoverable and the lifecycle discipline matches the other log types.

## PATH shadowing after plugin update

**Cause.** Claude Code's `claude plugins update` registers a new version's cache directory but leaves prior versions' `bin/` directories on PATH in inherited subprocess environments. `--plugin-dir` loads the plugin module but does not prepend its `bin/` to PATH ahead of the marketplace cache's bin directories. Over time, `~/.claude/plugins/cache/<author>/<plugin>/` accumulates historical versions (60+ observed locally) that are never garbage-collected.

**Impact.** When an agent invokes a plugin's bin script — e.g. `ocd-run` — through Bash, PATH may resolve to a stale cached version rather than the current install. Observed case: registered install at `0.0.284` but `ocd-run` resolved to `…/0.0.282/bin/ocd-run`, whose internal path layout predated a rename and so silently no-op'd rule/convention/pattern/log deployment. MCP tools (loaded through the plugin module) were unaffected — the issue is purely PATH-based binary resolution.

**Workaround.**

- Run `/checkpoint` (commit + push + plugin update) before sandbox-testing plugin behavior so the marketplace install is current.
- Invoke binaries by absolute path (`plugins/ocd/bin/ocd-run ...`) rather than relying on PATH lookup when correctness is essential.
- `hash -r` does not help — the issue is PATH ordering, not shell hash cache.

**Why not a fix we own.** Claude Code controls PATH ordering and cache lifecycle; neither `--plugin-dir` semantics nor `claude plugins update`'s cache management is configurable from within the plugin. A self-verify step in `bin/ocd-run` (check that `script_real` matches the currently-registered install and re-exec otherwise) would mask the symptom at the cost of every invocation's latency, and it would not help bin scripts other plugins ship.
