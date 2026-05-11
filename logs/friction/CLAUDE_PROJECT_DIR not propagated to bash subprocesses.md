---
log-role: queue
---

# CLAUDE_PROJECT_DIR not propagated to bash subprocesses

The Claude Code harness does not appear to set `CLAUDE_PROJECT_DIR` in the environment of bash tool subprocesses. Plugin scripts that read this env var to locate the active project hit their fallback path (typically `git rev-parse --show-toplevel`) which can land in the wrong directory when invoked from a plugin cache location.

Observed during `progressive-skill-composer` dogfooding: invoking `uv run --directory <cache-skill-folder> -m scripts.compose new ...` ran the script with cwd inside `~/.claude/plugins/cache/...`, which is itself a git checkout for some users. `git rev-parse` returned `~/.claude` and the script then built `~/.claude/.claude/skills/...` paths.

Fixed in-script via a defensive guard (reject project_dir resolutions inside Claude home) AND by the agent explicitly prefixing `CLAUDE_PROJECT_DIR=<project>` on every invocation. The agent-side prefix is the workaround; the friction is that it shouldn't be necessary.

Potential resolutions:

- Harness-side fix: propagate `CLAUDE_PROJECT_DIR` to all subprocess invocations (not actionable from plugins).
- Skill-side fix: detect plugin-cache invocation and refuse with a corrective error, forcing the explicit env var. Already implemented in `progressive-skill-composer` (`get_project_dir` defensive guard). Other plugins may need the same pattern.
- Documentation fix: capture the pattern as a component reference so future plugins use the same guard.

The skill-side guard is the conservative fix; the friction here is meta — every plugin that resolves a project root has to re-implement it.
