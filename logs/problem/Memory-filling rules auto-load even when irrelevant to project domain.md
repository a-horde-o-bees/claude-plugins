# Memory-filling rules auto-load even when irrelevant to project domain

The OCD plugin's `.claude/rules/ocd/*.md` files auto-inherit into every spawned subagent's memory regardless of whether the agent's work is plugin-development-shaped. In a non-plugin-development project, this is dead overhead — agents pay 25–30K tokens of memory floor before opening a single workflow component.

## Observed in

Job-search project (`~/projects/job-search`). Slim project-level CLAUDE.md is ~3.7K tokens. Component files (`_voice.md`, `_skill-buckets.md`, `_working-profile-evidence.md`, etc.) load on-demand per workflow.

`/context` snapshot from a working session showed memory files totaling **33.1K tokens** auto-inherited at session start:

| File | Tokens |
|---|---|
| `.claude/rules/ocd/process-flow-notation.md` | 5.2K |
| `.claude/rules/ocd/design-principles.md` | 9K |
| `.claude/rules/ocd/markdown.md` | 0.8K |
| `.claude/rules/ocd/systems/log.md` | 1.2K |
| `.claude/rules/ocd/systems/navigator.md` | 0.3K |
| `.claude/rules/ocd/systems/refactor.md` | 0.6K |
| `.claude/rules/ocd/workflow.md` | 0.8K |
| `.claude/rules/ocd/system-docs.md` | 2.1K |
| `.claude/rules/ocd/testing.md` | 6.5K |
| `CLAUDE.md` (project) | 5.1K |
| `MEMORY.md` | 1.1K |
| `~/.claude/CLAUDE.md` | 0.4K |

The `ocd/*` rules are ~26.6K of that. Two empirical role-research agent runs (Spotify AiKA, Workday FDE) showed 115–116K total token consumption per agent; the rules were paying overhead on every one even though the work was JD parsing + qualifications classification, with no plugin authoring, no PFN editing, no governance-spec work.

## Suspected root causes

1. **Memory rule files are scoped at project, not at task-shape.** Once a rule file is registered as memory, it loads everywhere. There's no signal saying "this rule applies to plugin authoring; ignore for application-material drafting."
2. **Some rules are heavy because they bundle reference + procedure + examples** in one file. `design-principles.md` (9K) is most-loaded because it's the foundation; `testing.md` (6.5K) is universal but most invocations don't touch tests; `process-flow-notation.md` (5.2K) is only relevant when authoring agent-readable instructions.
3. **No project-level disable mechanism for OCD content the project doesn't want.** Projects that don't need OCD's governance can still inherit its memory footprint just by having the plugin installed at user level. (Removing the project-level `.claude/rules/ocd/` directory does drop the memory load, which is the workaround used in job-search — but that means losing access to the rules entirely, not selectively.)

## Two investigation paths

1. **Reduce per-file token cost.** Audit each rule file for content that could split into reference (loaded on-demand) vs trigger-shaped guidance (compact, always-on). E.g., `design-principles.md` could split principles into name + one-line summary always-on, with full case-bullets readable on-demand. Target: cut auto-inherited rule tokens by 50%+.
2. **Dynamic plug-and-play memory.** Investigate a mechanism where rules declare a *trigger condition* (file pattern, skill invocation, agent-type, declared task-shape) and only load when relevant. E.g., `testing.md` loads when a test file is in scope; `process-flow-notation.md` loads when a workflow or skill file is being authored. Likely requires plugin-side machinery (manifest declaration of conditional memory) plus Claude-Code-side support for conditional inclusion.

Both directions cut the per-agent floor. Path 1 is content reorganization; Path 2 is structural and would benefit every plugin that ships memory rules. Path 2 likely requires Anthropic-side coordination (Claude Code's memory loader) since the conditional-include hook doesn't exist today; Path 1 is plugin-internal.

## Workaround in the meantime

In job-search the project-level `.claude/rules/ocd/` + `.claude/conventions/ocd/` + `.claude/ocd/` directories were removed entirely (2026-05-05). User-level plugin install at `~/.claude/plugins/cache/...` was retained so skills (`/ocd:pdf`, `/ocd:retrospective`) and MCP servers (navigator, transcripts) still load on demand. This is destructive — the project loses access to the rule content as guidance — but it's the only project-side lever available.

## Constraints to remember during investigation

- Memory rules exist for a reason: they're agent-facing discipline that fires reliably across sessions. Wholesale "load less" can quietly turn into "discipline drifts." Reduction must preserve the trigger-strength of the guidance.
- The user-level vs project-level split matters. A plugin used across many projects shouldn't make every project pay for its full memory footprint; the right axis is *what task is the agent doing*, not *which project is this*.
