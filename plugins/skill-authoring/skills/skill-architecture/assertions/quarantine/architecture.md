# Skill-architecture recommendations

Authoritative recommendations for skill-authoring decisions, derived from verified platform-behavior assertions. Cross-references to [`confirmed-facts.md`](confirmed-facts.md) (the digest of load-bearing facts) and [`assertions/`](assertions/README.md) (full evidence). When a load-bearing fact changes, this file updates accordingly.

## Dependency declarations

Use the canonical idempotent phrasing in every `## Dependencies` block. The phrasing loads each listed skill once per session and is a no-op on subsequent reachings. See [`confirmed-facts.md`](confirmed-facts.md) § "Idempotent loading works."

```markdown
## Dependencies

If not already loaded, call the following skills:

- /skill-name
- /other-skill
```

For Variant F's stricter form (caller-side scope grammar — see encapsulation matrix below):

```markdown
## Dependencies

If not already loaded, call (and apply during all prose generation within this skill's execution): /skill-name
```

## Encapsulation grammar — choose by depth

| Authoring scenario | Recommended grammar |
|---|---|
| Skill called only at single level (direct invocation OR loaded as one-level dep) | Variant D closing release line on the called skill, no caller-side grammar |
| Skill called in nested chain (depth ≥ 2) OR with strict scope discipline | Variant F: caller-side scope grammar in `## Dependencies` of every wrapper PLUS Variant D closing line on the called skill |
| Hub skill that may or may not be nested (e.g. `/concise-prose`) | Variant F (defensive default) |

**Rationale:** Variant D alone leaks at depth ([`confirmed-facts.md`](confirmed-facts.md) § "Variant D leaks at depth"). Variant F's redundancy bounds the directive end-to-end.

### Variant D closing line (verbatim)

Append below the skill body, after a `---` rule:

```markdown
---

End of /skill-name. The preceding directives apply during this skill's invocation AND during the execution of any skill that loads this one as a dependency. They do NOT apply to subsequent unrelated agent output.
```

### Variant F caller-side grammar

In each wrapper that loads the skill (see template above under "For Variant F's stricter form"). The tested form covers a single inline skill after the `:`. Multi-skill blocks within the same grammar are untested at depth.

## Inline step mentions

Use `Apply /skill-name` inside step text as a procedural reminder when the body should remind the agent WHEN to engage a loaded dep's directives. Inline mentions are soft references — they cost nothing and do not trigger re-load. See [`confirmed-facts.md`](confirmed-facts.md) § "Step-level inline mentions are soft references."

## When to embed which authoring-discipline dependency

| Discipline | Embed when |
|---|---|
| `/process-flow-notation` (PFN) | Workflow has conditionals, loops, variable binding, sub-routine calls, error handling, or nested indented blocks. Plain linear numbered steps don't need PFN. |
| `/concise-prose` | Skill outputs prose to the user (response text, descriptions, log entries, commit messages, error strings). Skip for pure script-orchestration skills. |
| `/description-authoring` | Skill produces description-like artifacts (frontmatter descriptions, navigator entries, tool help text, schema titles, docstrings). Skip for skills whose body is workflow-only. |
| `/reauthor` | Skill rewrites or regenerates content in place (replaces existing artifacts wholesale). Skip for additive skills. |

The pattern in every case: `## Dependencies` block declaring the discipline skill, plus inline `Apply /skill` mentions at steps where the discipline should engage.

## Project-directory resolution

When a skill's scripts need to know the calling project's directory, use this resolver chain. See [`confirmed-facts.md`](confirmed-facts.md) § "Platform discovery" and [`assertions/platform-discovery/project-dir-resolution.md`](assertions/platform-discovery/project-dir-resolution.md) for the verified mechanism.

1. `CLAUDE_PROJECT_DIR` env var — honors explicit override / hook setups; cheap
2. `CLAUDE_CODE_SESSION_ID` → tail-scan `~/.claude/projects/*/<session-id>.jsonl` for the latest line carrying a `cwd` field — authoritative; handles non-git projects, mid-session `cd`, sub-agents
3. `git rev-parse --show-toplevel` from cwd — tail safety net for very-early-session probes or non-Claude-Code invocations
4. Reject paths inside `~/.claude/` — plugin-cache git-checkout trap protection

Do NOT decode `~/.claude/projects/<encoded-cwd>` directory names — the encoding is lossy (`/` and `.` both collapse to `-`).

## State location

Follow [`logs/decision/state-location.md`](../../../../logs/decision/state-location.md). The four-category matrix:

| Category | Where state lives | Examples |
|---|---|---|
| Bin-mediated (scripts only; agent never touches via Read/Write/Edit) | `~/.claude/plugins/data/<plugin>-<author>/` (or a simpler top-level path under `~/.claude/<concern>/` for single-DB plugins on case-by-case allowance) | Navigator DB, transcripts DB, dep manifest cache, venv |
| User-edited (user + agent edit/read directly) | Project tree, outside `.claude/` | Logs, plans, sandbox tasks, project configs |
| Scope-required (Claude Code parses directly) | `<scope>/.claude/...` | Settings, rules, skill shims, discovery substrate stubs |
| Plugin-namespaced user-edited (plugin owns format; user + agent edit directly) | `<scope>/.claude/<plugin-name>-<author>/<concern>/` | Plugin-managed user-editable config or templates not tied to a specific skill |

The principle: path location is a function of access pattern, not data ownership.

## Workflow file vs Python script

Workflow lives in `_<verb>.md` (PFN-structured agent procedure); deterministic operations live in `scripts/` as importable Python modules invoked via `uv run python -m scripts.<module>` or `python3 -m scripts.<module>` if no `uv` dep.

Rule of thumb:

- **Workflow file** carries the cognitive choreography — when to ask the user, when to read, when to dispatch — and benefits from PFN when control flow is non-linear.
- **Python script** owns mechanical operations — git invocations, file walks, JSON parses, structured-output composition — that the agent should NOT re-derive from prose every invocation.

Mixing increases context cost and brittleness. Fully deterministic step → script the workflow calls; judgment-requiring step → workflow.

## Sub-agent considerations

Sub-agents spawned via the Agent / Task tools inherit fresh context — they do NOT see the parent's loaded skill bodies. They can re-invoke skills by name. See [`confirmed-facts.md`](confirmed-facts.md) § "Sub-agents inherit fresh context."

When designing a skill that uses sub-agents:

- Pass enough context in the sub-agent prompt that it can engage relevant skills itself (don't rely on the parent's loaded directives leaking in)
- General-purpose sub-agents lack the Agent tool — cannot spawn nested sub-agents
- Sub-agents DO inherit `CLAUDE_CODE_SESSION_ID`, so the project-dir resolver above works inside them naturally

## Cross-references

- [`confirmed-facts.md`](confirmed-facts.md) — the digest of load-bearing facts that justify the recommendations above
- [`assertions/`](assertions/README.md) — full evidence library, organized by topic (`skill-runtime/`, `platform-discovery/`)
- [`_reassert.md`](_reassert.md) — sub-verb workflow for re-verifying assertions
- [`logs/decision/state-location.md`](../../../../logs/decision/state-location.md) — full state-location decision (this doc digests its matrix)
