---
log-role: reference
---

# Hook Scoping

Decisions governing how hooks attach to skills — frontmatter declaration (lifecycle-scoped) versus body-deployed installer (persistent). Determines whether a skill needing continuous enforcement (like permissions) requires plugin packaging or can ship as a standalone skill.

## Pattern A vs Pattern B

### Context

The permissions skill enforces hooks on every Bash call (continuous enforcement). The architectural question: can a permissions skill live as a standalone skill, or does it require plugin packaging because of its hook dependency? Two distinct patterns surfaced during research:

- **Pattern A** — skill frontmatter declares `hooks:`. Per the [Hooks doc](https://code.claude.com/docs/en/hooks): "hooks can be defined directly in skills and subagents using frontmatter. These hooks are scoped to the component's lifecycle and only run when that component is active." Lifecycle-bound to skill activation; cleaned up when skill finishes.
- **Pattern B** — skill body, on invocation, deploys hook configuration to `<scope>/.claude/settings.json`. Once written, hooks fire continuously regardless of skill activation. The skill is an installer for a hook configuration that lives independently in settings.json.

Research findings on hook locations (per the Hooks doc): hooks register at six locations — `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, managed policy, plugin `hooks/hooks.json`, and skill or agent frontmatter (while the component is active). The first three are accessible to a Pattern B skill via file modification; the latter is Pattern A territory.

### Options Considered

**Permissions as a plugin (with `hooks/hooks.json`).** Rejected: forces plugin packaging just to get continuous enforcement; conflicts with the skills-atomic-unit architecture.

**Permissions as a Pattern A skill (frontmatter `hooks:`).** Rejected: per the Hooks doc, frontmatter hooks fire only while the skill is active. "Active" is ambiguous in the docs (likely means invoked, not loaded for discovery), but in either interpretation a permissions skill that isn't being invoked won't enforce. Continuous Bash enforcement requires hooks to fire decoupled from skill lifecycle.

**Permissions as a Pattern B skill (body deploys to settings.json).** Adopted. Once the skill runs once and writes the hook config to settings.json, the hook fires on every Bash call regardless of whether the skill is currently active.

### Decision

Two hook patterns coexist, each appropriate for different needs:

| Pattern | Mechanism | Lifecycle | Use case |
|---|---|---|---|
| A | Frontmatter `hooks:` declaration | Bound to skill activation; cleaned up when skill finishes | Skill-internal observation; ephemeral hooks tied to a specific operation |
| B | Skill body deploys hook config to `<scope>/.claude/settings.json` on invocation | Persistent; independent of skill activation | Installer skills that establish enforcement (permissions, audit hooks, etc.) |

Permissions becomes a standalone Pattern B skill. Its body, when invoked, modifies settings.json to install enforcement hooks. The hook config lives in settings.json after invocation; firing is continuous; the skill itself doesn't need to stay active. The skill ships as a standalone unit — no plugin packaging required for hook continuity.

### Consequences

- **Enables:** permissions stays as a standalone skill; aligns with skills-as-atomic-unit; aligns with the "skills themselves have opt-in features once installed" model — invoking the skill IS the install action for its hook config
- **Constrains:** Pattern B skills must be designed to be safe to re-invoke (idempotent settings.json edits); user must know to invoke once per scope to deploy hooks; uninstall semantics need consideration (does invoking again with a remove flag clean up?)
- **Audit signal:** distinguish "the skill HAS a hook in frontmatter" (Pattern A) from "the skill INSTALLS a hook to settings.json" (Pattern B) when authoring or reviewing — they're different mechanisms with different lifecycles

## Hook lifecycle empirical verification deferred

### Context

The Hooks doc says frontmatter hooks "scope to the component's lifecycle and only run when that component is active" but doesn't precisely define "active." Two plausible interpretations:

- Active = invoked (skill content rendered into the conversation; hook fires only during the invocation)
- Active = loaded for discovery (skill description in always-on context; hook fires whenever the skill is enabled)

The interpretation matters for any future Pattern A skill that expects hook firing across the session even when the skill itself isn't currently being invoked.

### Decision

Verification deferred until a concrete Pattern A skill needs always-on-feeling behavior. For permissions specifically (Pattern B), the question doesn't arise — settings.json hooks fire regardless. If a future skill design wants always-active hooks via Pattern A, run an empirical test (write a skill with a `PreToolUse` hook in frontmatter, install it, observe whether the hook fires on tool calls when the skill hasn't been invoked) before relying on the behavior.

### Consequences

- **Enables:** permissions architecture proceeds without blocking on the empirical question
- **Constrains:** any future skill author wanting Pattern A always-on behavior needs to verify before relying — the docs are silent on the precise semantics
