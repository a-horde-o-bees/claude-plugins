# Pass 2 Refinements — Bin 1

Proposed refinements to `_CONSOLIDATED_breadth-then-depth.md` from rewriting samples in this bin. The reconciler integrates accepted refinements into the next consolidated revision.

## Proposed new paths

> Format: `<role> > <new-path>` — supporting samples — qualitative description draft

- `Tool-use enforcement` > `SubagentStop hard-block on missing structured result` — `AgentBuildersApp/eight-eyes` — A SubagentStop hook refuses to let a subagent finish without a structured result block matching its per-role JSON schema. Distinct from `TaskCompleted hard-block on missing memo/result` (which gates on sidecar API state) and from `decision: "block"` (which gates the tool call itself). Eight-eyes uses `COLLAB_RESULT_JSON_BEGIN ... COLLAB_RESULT_JSON_END` markers and per-role schemas in `skills/collab/schemas/*.schema.json`; missing or malformed blocks are a hard block, not a warning. Enforces an output contract on subagents that can't be enforced by prompting alone.

- `Tool-use enforcement` > `SubagentStart context exclusion (blind review)` — `AgentBuildersApp/eight-eyes` — A SubagentStart hook strips named upstream content from a subagent's context (e.g., the implementer's narrative summary withheld from the skeptic). Sibling to `SubagentStart context injection` but inverse: injection adds shared context the subagent doesn't have; exclusion removes context the subagent would otherwise inherit. Used for bias mitigation via context walls rather than prompt pleading.

- `Governance and self-audit` > `Enforcement-contract-as-inspectable-artifact` — `AgentBuildersApp/eight-eyes` — A YAML+JSON pair declares, for every hook, its gate class (`hard_gate`, `recovery`, `lifecycle`, `observability`), failure mode (`deny`, `block`, `fail_open`, `async_fail_open`, `warn`), and per-platform support. Compiled to JSON for runtime; surfaced via a CLI verb (e.g., `collabctl capabilities --json`); parity tests assert committed adapter manifests match the contract. Distinct from existing self-audit entries (which guard registration lists or derived artifacts) — this guards the *enforcement model* itself and is a substantive design pattern the consolidated currently subsumes inside one Tool-use enforcement path.

- `Bin entry mechanism` > `Opt-in user-PATH shim with absolute paths baked in at install` — `AgentBuildersApp/eight-eyes` — `install.py --add-to-path` flag generates a shim at `~/.local/bin/<plugin>` (POSIX bash `exec python3 "<abs path>"`) or `~/.local/bin/<plugin>.cmd` (Windows batch) that hardcodes the absolute path to the in-repo entry script at install time. Distinct from `Auto-generated Windows .cmd launchers` (which is SessionStart-driven, not install-time-driven, and Windows-specific) and from existing wrapper variants (which resolve via env vars or script-relative paths). The "absolute path baked at install time" is what makes it stable across cwd changes but stale on repo move. Cross-platform pair (POSIX shim + `.cmd`).

## Proposed description sharpenings

> Format: `<role> > <existing-path>` — what the existing description misses; supporting samples; sharpening suggestion

- `Version coordination > Multi-site sprawl (5+ locations)` — current description focuses on 5+ sites that ship release artifacts. `AgentBuildersApp/eight-eyes` exhibits a 7-site form *plus* the cross-format-encoding twist: `5.0.0-alpha` (semver), `5.0.0a1` (PEP 440), `v5.0.0-alpha` (tag) are three different surface forms of the same conceptual version, and downstream sorting rules may not reconcile them. The existing description mentions "Pre-release suffix handling (semver vs PEP 440 vs tag) compounds the inconsistency" but could sharpen by explicitly naming each as a *normalization gap* — different ecosystems demand different forms; the bump tool must emit each form correctly.

- `Marketplace manifest layout > Duplicated marketplace manifest at root and nested` — current description mentions "the same JSON object is placed at `.claude-plugin/marketplace.json` (for Claude Code) and `.github/plugin/marketplace.json` (for GitHub Copilot CLI)". `AgentBuildersApp/eight-eyes` exhibits the duplicate at `.github/plugin/` *without an obvious Copilot-CLI consumer* — likely vestigial / aspirational rather than deliberate cross-host. Both copies also carry `_description` private keys outside the schema. The sharpening: add a subcase distinguishing "deliberate cross-host duplicate (Claude + Copilot)" from "vestigial duplicate with no observable consumer" so the reader can spot which variant a given repo exhibits.

- `Hook failure posture > Fail-closed with circuit breaker (retry with backoff)` — current description names Erlang/OTP and resilience guidance. `AgentBuildersApp/eight-eyes` adds two specifics worth absorbing: (a) per-hook configurable failure mode (`deny` for pre-tool, `block` for subagent-stop, `warn` for stop) — the breaker is shared but the escalation is hook-scoped; (b) per-mission `manifest.fail_closed` toggle that flips the default — fail-open is the install-default, fail-closed is opt-in per mission. The sharpening: name the *failure-mode-per-hook* variability and the *per-mission opt-in* explicitly so the pattern is reproducible.

- `Plugin-component registration > Explicit per-component path arrays` — `777genius/claude-notifications-go` exhibits a partial-listing variant: 4 commands listed in `plugin.json` but 6 present in the directory. The existing description doesn't address what happens when the explicit list disagrees with directory contents. Sharpening: add the constraint that explicit listing is ambiguous — Claude Code's command discovery typically globs the directory, so explicit-list-with-orphans creates uncertainty about whether the list is authoritative or additive.

- `Tool-use enforcement > Scope enforcement (block out-of-scope writes)` — current description names the basic scope-allow/deny mechanism. `AgentBuildersApp/eight-eyes` shows the spec-driven variant where role declarations live in a YAML + compiled JSON pair (`spec/roles/builtin_roles.yaml` + `_compiled.json`) with their own JSON schema, and the hook reads from the spec at runtime. Sharpening: distinguish "scope rules inline in the hook script" from "scope rules in an external versioned spec the hook consults" — the latter pattern is more maintainable but adds a derived-artifact-drift surface (covered by `Derived-artifact drift detector`).

## Proposed new roles

> Format: `<new-role>` — what role this is, why it doesn't fit any existing role, supporting samples

(none from this bin — every fact found a home under an existing role with at most a path-level refinement)

## Proposed bucket splits

> Format: `<role> > <existing-path>` — why it should split, into what, supporting samples

(none from this bin)

## Structural concerns

> Anything that's hard to fit cleanly under any role/path; questions for the reconciler

- **Per-sample identification metadata (URL, stars, last commit date, default branch, license, sample origin) doesn't fit the role tree.** Each original sample opens with an Identification section. Per the operating instructions, I moved entity-identifying content into a one-line preamble after the level-1 heading, but star count, last-commit date, and default branch don't fit cleanly there. Currently I omitted the numeric metadata. Question for reconciler: should there be a structured preamble convention (frontmatter? a fixed leading bullet list?) for these per-entity facts so they're retrievable without polluting the role tree? They're observational about the entity, not about its choices.

- **Mid-release version drift inside `Multi-site sprawl` vs `Multi-site drift accepted as cosmetic`.** `AgentBuildersApp/eight-eyes` has `plugin.json: 5.0.0-alpha` and `marketplace.json: 4.2.0` — possibly deliberate ("marketplace only advances at stable release") or possibly drift. Both consolidated paths mention this scenario; the difference is intent. Without commit-message evidence I picked `Multi-site sprawl (5+ locations)` because the count fits, but the "marketplace lags during pre-release" pattern feels like it deserves either its own bullet inside `Multi-site drift accepted as cosmetic` or a sharpening. Defer to reconciler.

- **`pyproject.toml` declared but unused for deps.** Both `123jimin-vibe/plugin-prompt-engineer` (declares deps but version is dummy) and `AgentBuildersApp/eight-eyes` (declares no deps, only metadata + license + classifiers) ship `pyproject.toml` for non-runtime reasons. The first hit *Single source of truth (`plugin.json` only)* under Version coordination cleanly because the prose already addresses pyproject as a "may itself drift" surface. The second has no clear path under Dependency installation — `Zero dependencies / stdlib only` matches but doesn't address the `pyproject.toml`-as-PyPI-metadata-only choice. Could be a description sharpening on `Zero dependencies / stdlib only`: "may ship `pyproject.toml` for PyPI metadata only (no `[project.dependencies]`), preserving the option to publish to PyPI without committing to runtime deps."

- **`AgentBuildersApp/eight-eyes` hooks.json has 7 registrations including SubagentStart, SubagentStop, Stop.** I covered SubagentStart (blind-review context exclusion) and SubagentStop (hard-block on result) as proposed new paths. The Stop hook handler I have less visibility on (likely the lifecycle observer; covered in `Stop-event handlers for session-end aggregation` if it does session-end aggregation). I left it out rather than guessing.

- **Eight-eyes "no architecture.md despite substantial structure" is in `Documentation surface`.** I placed under `Sprawling root with many entry-point markdowns` because that path mentions PNG-only diagrams. But it could also fit `Multi-doc architecture (no separate ARCHITECTURE.md)`. The eight-eyes case is closer to the latter (architecture lives split across README + PNG + CONTRIBUTING, no top-level ARCHITECTURE.md). Defer to reconciler whether to move.
</content>
</invoke>
