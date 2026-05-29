# Confirmed facts about Claude Code platform behavior

Terse digest of platform-behavior assertions that load-bearing skill-architecture decisions depend on. Each fact backlinks to its source assertion in [`assertions/`](assertions/README.md). When `reassert` re-verifies an assertion and the result flips, this digest updates first; downstream recommendations in [`architecture.md`](architecture.md) follow.

## Skill runtime

**Idempotent loading works.** Declaring a skill in `## Dependencies` with the canonical phrasing loads it once per session and is a no-op on subsequent reachings (nested chains, multiple dependents). See [[skill-runtime/dep-test-iterations]], [[skill-runtime/multi-dep-declaration]].

**Skill bodies re-inject on every call.** Whenever a skill is invoked directly, its full body is re-emitted into context — there is no body cache. See [[skill-runtime/skill-caching]].

**Bodies persist after loading.** Once injected, a skill body remains visible in the session's context window across subsequent prose generation; idempotent checks rely on this. See [[skill-runtime/body-persistence]].

**Directives leak by default.** Skill directives apply to all downstream prose generation in the session unless an explicit release mechanism scopes them. See [[skill-runtime/scope-leak]].

**Variant D closing release line scopes at single level.** A trailing `End of /skill-name. The preceding directives apply during this skill's invocation AND during the execution of any skill that loads this one as a dependency. They do NOT apply to subsequent unrelated agent output.` reliably bounds directives in single-level direct invocation and single-level dep-load. See [[skill-runtime/encapsulation-grammar]], [[skill-runtime/direct-invocation-after-dep-load]].

**Variant D leaks at depth.** In nested chains (outer → middle → inner) with prose composition steps after the chain, Variant D fails to bound the innermost skill's directive. See [[skill-runtime/nested-encapsulation]].

**Variant F (hybrid) is the robust nested pattern.** Caller-side scope grammar in `## Dependencies` combined with Variant D closing line on the called skill bounds the directive end-to-end. Confirmed at single-level; depth verification pending. See [[skill-runtime/variant-f-hybrid]].

**Step-level inline mentions are soft references.** Writing `Apply /skill-name` inside a workflow step does NOT trigger a re-load; the skill must already be loaded via `## Dependencies`. The mention acts purely as a procedural reminder and costs nothing. See [[skill-runtime/surgical-step-apply]].

**Sub-agents inherit fresh context, share skill registry.** Spawned sub-agents do not see the parent's loaded skill bodies in context but can re-invoke skills by name. General-purpose sub-agents lack the Agent tool — no nested sub-agents. See [[skill-runtime/sub-agent-context-inheritance]].

**Direct invocation after dep-load re-injects.** Calling a skill directly after it was previously loaded as a dependency re-emits the body; scope releases correctly at single level. See [[skill-runtime/direct-invocation-after-dep-load]].

**Multiple skills in one Dependencies section all load on first reach, idempotently skip on re-reach.** Multi-dep declarations behave as the single-skill case extended. See [[skill-runtime/multi-dep-declaration]].

## Platform discovery

**Project directory is resolvable from session ID + JSONL `cwd` field.** Every Claude Code bash subprocess inherits `CLAUDE_CODE_SESSION_ID`. The session's JSONL at `~/.claude/projects/*/<session-id>.jsonl` carries authoritative `cwd` per user-message line. Verified in both interactive (v2.1.146) and headless (`claude -p`) contexts. See [[platform-discovery/project-dir-resolution]].

**`CLAUDE_PROJECT_DIR` is hook-only.** This env var is set only inside hook execution contexts; not present for general Bash tool subprocesses. The resolver chain treats its presence as an explicit override signal, its absence as the normal case. See [[platform-discovery/project-dir-resolution]].

**JSONL directory-name encoding is lossy.** `~/.claude/projects/<encoded-cwd>` collapses `/` and `.` to `-` — reverse-decoding is unreliable. Always resolve via session-id glob, not directory-name parsing. See [[platform-discovery/project-dir-resolution]].

## Untested-but-relevant gaps

Not facts yet — captured here as the load-bearing topics still missing verification, so architecture.md callers know where recommendations are softer:

- **Variant F at depth (≥ 2 nested levels)** — single-level confirmed; nested behavior not yet probed. Recommendations using Variant F for depth defaults rest on Variant D's single-level success plus the leak pattern from [[skill-runtime/nested-encapsulation]].
- **Context-compaction effect on idempotent checks** — what happens when a previously-loaded body gets evicted from context? Re-load on next reach is the expected behavior but mechanically unverified.
- **Cross-platform `CLAUDE_CODE_SESSION_ID` propagation** — verified on Linux + WSL; macOS/native-Windows untested.
- **Better frontmatter scope wording** — [[skill-runtime/variant-c-frontmatter-scope]] confirmed frontmatter IS honored; finding wording that means "apply during wrappers, release after" would yield the cleanest grammar of the family.

Re-running `reassert` against the current platform should be the first move whenever a recommendation in [`architecture.md`](architecture.md) feels uncertain.
