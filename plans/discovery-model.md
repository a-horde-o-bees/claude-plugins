# Discovery model

A trigger-routed context-loading model that subsumes how rules, conventions, skills, MCPs, and other plugin contributions enter agent context. Replaces the broken `includes`/`excludes` path-glob mechanism.

## Goal

Reduce always-on context cost while preserving trigger-strength of guidance. Every plugin contribution is invisible until a cognitive trigger fires; only relevant content loads, and only the slice the moment needs. Plugins coexist without coordination beyond a shared mechanical contract; users extend with their own content using the same contract.

The motivating data: the `Memory-filling rules auto-load even when irrelevant to project domain` problem log measured ~26.6K tokens of OCD rule overhead in a non-plugin project. Target: ~93% reduction in always-on cost (to ~1.5K) by moving artifact-triggered guidance behind the discovery substrate.

## Output

Substrate at every install scope:

- `<scope>/rules/discovery-triggers.md` — always-on rule mapping rich-prose triggers to stub references. Single section: `## Triggers` with two columns (Trigger, Stubs). The trigger prose IS the recognition cue.
- `<scope>/discovery/manifest.md` — install/uninstall bookkeeping. Two sections: `## Index` (system → ID) and `## Dependencies` (file → IDs). Not auto-loaded; consumed by sync-router CLI.
- `<scope>/discovery/<id>-<n>.md` — stub files. H1 = source path, body = source's purpose statement (H1 + first paragraph). Loaded when the trigger row referencing them fires.
- `<scope>/dependencies/<name>.md` — shared content depended on by sources via `requires:` frontmatter. Loaded when sources requiring them are read.

System contract (in plugin source tree):

- `plugins/<plugin>/systems/<system>/discovery-triggers.md` — hand-crafted source stub. One section (`## Triggers`) listing trigger prose and the source files that apply.
- `plugins/<plugin>/dependencies/<name>.md` — bundled copy of any dependency the plugin ships
- Source files declare `requires:` in YAML frontmatter for any dependency they need at agent-read time

CLI surface (under `<plugin> setup conventions ...`):

- `install --scope <scope>` — assigns ID, generates stubs from sources, merges trigger rows into deployed router, deploys missing dependencies, updates manifest
- `uninstall --scope <scope>` — strips system's stubs and trigger references; reference-counts dependencies; removes the deployed router and manifest if empty
- `sync --scope <scope>` — idempotent refresh from current source state

## Sequence

1. **Capture the design** — this plan + `logs/decision/discovery-model.md`. Done in the commit landing this plan.
2. **Strip `triggers:` frontmatter** from the 23 convention files added speculatively in commit `815ebae`. System stubs become the single source of trigger declarations.
3. **Move PFN** — `plugins/ocd/systems/rules/templates/process-flow-notation.md` → `plugins/ocd/systems/rules/dependencies/process-flow-notation.md` (or wherever the dependency-bundling location lands). Note: PFN's authoring-side relevance (agent producing PFN-structured output) may need a separate cognitive trigger; defer until the move surfaces it concretely.
4. **Move 5 candidate-conventions** to `conventions/templates/`: `markdown`, `principle-not-symptom`, `trigger-specificity`, `tool-positioning`, `agent-first-interfaces`. Each gets `requires:` frontmatter where applicable.
5. **Author the conventions system's `discovery-triggers.md` source stub** — single hand-crafted file declaring all OCD conventions' triggers, mapping to source files.
6. **Implement deployment mechanics** — Python facade and CLI verbs (`install`, `uninstall`, `sync`). Generate stubs from sources, merge into deployed router, maintain manifest, deploy/cleanup dependencies.
7. **Author the model rule** — `plugins/ocd/systems/rules/templates/discovery-model.md` covering cognitive vs artifact, the four-artifact substrate, the trigger-prose convention, dependency declarations. Replaces the abandoned `governance.md` direction.
8. **Migrate other systems** — re-evaluate each system (rules, log, navigator, transcripts, pdf, skills, MCP servers) under the discovery model. Each migration is its own focused pass.

Steps 2–7 land in this workstream. Step 8 spans many follow-on workstreams.

## Decisions captured

See `logs/decision/discovery-model.md` for the full decision log. Headlines:

- **Cognitive vs artifact triggers** — the rule/convention distinction is by *trigger source*, not domain specificity. Cognitive triggers stay always-on (rules); artifact triggers go through the discovery substrate (conventions and beyond).
- **Trigger prose IS the recognition cue** — single-column trigger declaration; no separate short-token key. Merge across systems uses exact-prose match.
- **Index-based stub naming** — `<id>-<n>.md` keeps the deployed router compact; manifest holds the ID→system mapping for operational use.
- **Dependencies inferred from source frontmatter** — system authors don't list them in trigger-router stubs; install scans `requires:` declarations; reference-counted via manifest.
- **System self-ownership via `<id>`** — no Owner column in the runtime router; uninstall identifies its work by ID prefix on stub paths.
- **Manifest splits out** — runtime cost is just the Triggers section; Index + Dependencies are install/uninstall bookkeeping not loaded by agents.
- **Generalization** — the same kernel applies to skills, MCPs, navigator, pdf, and any context contribution that costs more in always-on form than in trigger-routed form.

## Open questions

- **Naming for the directory holding stubs** — `<scope>/discovery/` is current. Alternative: `<scope>/stubs/`. Defer pending broader naming pass.
- **Multi-plugin trigger coordination** — plugins contributing to the same conceptual trigger must use exact-prose match. May need a "canonical triggers" registry over time. Defer until cross-plugin contention surfaces.
- **Determinism of `<id>` assignment** — alphabetical based on `<plugin>/<system>` ordering at install time. May shift if a new system inserts alphabetically before existing ones; sync-router renumbers. Spec finalized at implementation time.
- **PFN's authoring side** — the cognitive trigger for "I'm authoring PFN-structured output" doesn't fire from a file edit. May need a separate cognitive rule for the authoring case while `requires:` handles parsing. Defer until step 3 surfaces it.
- **Migrating existing systems** — skills, MCPs, navigator have their own always-on costs the model could reduce. Each is its own pass under step 8.

## State

In flight. Plan + decision log captured. Implementation steps not yet started. Three commits unpushed at the start of this workstream (`b07bf01` task tracker, `3e0a450` show verb + tagline catalog, `815ebae` rules+conventions wipe + workflow.md restructure); resume `/checkpoint` after this plan lands so the substrate is built on a clean pushed slate.
