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

## What's auto-inherited vs. on-demand

After the rules removal in job-search (with the user-level plugin install retained), per-agent inheritance from the OCD plugin is much smaller than the rules-files alone. Categorizing what `/context` shows for OCD-attributable cost:

**Auto-inherits to every spawned agent:**

| Item | Tokens | Notes |
|---|---|---|
| `.claude/rules/ocd/*.md` | 26.6K (before removal) | Heaviest; fully removable per project |
| Skills metadata for discovery | ~1.5K | All OCD skills (sandbox, transcripts, retrospective, git, log, refactor, needs-map, setup, check, navigator, ocd-pdf) |
| MCP server instructions blocks | ~400 | The `## plugin:ocd:navigator` + `## plugin:ocd:transcripts` usage-guidance text blocks |

**Loaded on-demand only (no inheritance cost):**

- MCP tool schemas (parameter docs for each `mcp__plugin_ocd_*` tool) — `/context` notes "MCP tools · /mcp (loaded on-demand)"; agents fetch via `ToolSearch` only when needed
- Full skill SKILL.md content — only loads when the skill is invoked; the 1.5K is metadata for discovery (skill names + brief descriptions), not the procedure body
- Hook command bodies — loaded by Claude Code when a hook matcher fires, not by the agent

**Skills metadata breakdown** (from `/skills`, all OCD plugin):

| Skill | Tokens |
|---|---|
| sandbox | 144 |
| transcripts | 143 |
| retrospective | 98 |
| git | 67 |
| log | 65 |
| refactor | 64 |
| needs-map | 62 |
| setup | 40 |
| check | 28 |
| navigator | 25 |
| ocd-pdf | 14 |
| Discovery-registry overhead | ~750 |
| **Total** | **~1.5K** |

The biggest win — by ~30x — is on the rules files. The skills metadata + MCP instructions floor cost (~2K combined) is small enough that uninstalling the plugin at user level wouldn't move the needle meaningfully if the rules weren't already loading.

## Workaround in the meantime

In job-search the project-level `.claude/rules/ocd/` + `.claude/conventions/ocd/` + `.claude/ocd/` directories were removed entirely (2026-05-05). User-level plugin install at `~/.claude/plugins/cache/...` was retained so skills (`/ocd:pdf`, `/ocd:retrospective`) and MCP servers (navigator, transcripts) still register on demand. This is destructive at the rule-content level — the project loses access to that guidance — but it's the only project-side lever available.

Empirical floor change in job-search after rules removal:

| | Before | After |
|---|---|---|
| Memory files (project-attributable) | 33.1K | 6.6K (just CLAUDE.md + MEMORY.md + user-global) |
| Skills metadata | 1.5K | 1.5K |
| MCP server instructions | ~400 | ~400 |
| **Project-attributable inherited** | **~35K** | **~8.5K** |

## Adjacent context-cost optimizations

The same load-only-when-relevant axis applies beyond memory rules — agents pay token cost on any content that ships into context regardless of whether the current task touches it. Two project-wide surfaces worth auditing alongside the memory-rules investigation:

### Prose-style workflows that should be PFN

Anywhere a workflow is described as prose ("first do X, then Y, then if Z, do W..."), PFN would compress ~30–50% and sharpen the structure. Agents reading PFN can rely on numbered-step atomicity, indentation scoping, and mechanism prefixes; agents reading prose must parse intent each time. Sweep candidates: README operational sections, ARCHITECTURE.md execution-flow descriptions, CLAUDE.md procedures that drift into prose, skill workflows that mix PFN with prose paragraphs. The PFN spec itself loads once per session; converting prose to PFN amortizes that cost across more workflows.

### Conditional sub-flows that should extract via Spawn: / Call:

When a workflow component runs a sub-flow only on certain paths (specific verb, runtime condition, optional argument), inlining the sub-flow forces every invocation to load it. Extracting to a component file (`_subflow.md`) and invoking via `Spawn: Call:` (isolated agent context) or `Call:` (caller's context, on-demand) means callers that don't traverse the path never read the content. Same on-demand discipline the memory-rules investigation is targeting, applied at workflow-component granularity. Sweep candidates: long `_*.md` files with conditional branches that pull in optional-path content; SKILL.md files where the dispatcher already loads the whole verb table even though only one verb fires per invocation (current pattern uses `Call:` correctly for this — but worth confirming no skill carries inline branches that should be extracted).

## Constraints to remember during investigation

- Memory rules exist for a reason: they're agent-facing discipline that fires reliably across sessions. Wholesale "load less" can quietly turn into "discipline drifts." Reduction must preserve the trigger-strength of the guidance.
- The user-level vs project-level split matters. A plugin used across many projects shouldn't make every project pay for its full memory footprint; the right axis is *what task is the agent doing*, not *which project is this*.
- Skills + MCP-tool descriptions are already on-demand (the plugin's existing structure); the rules files are the outlier in that they auto-inherit by being placed in `.claude/rules/`. The same on-demand discipline could apply to rules if the loader supported it.
