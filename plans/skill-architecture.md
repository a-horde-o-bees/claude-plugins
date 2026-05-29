# `skill-architecture` — build plan

Active workstream to stand up a new skill inside `plugins/skill-authoring/` that consolidates confirmed Claude-Code platform-behavior facts into authoritative skill-structure guidance, hosts the relocated assertion library, and exposes a `reassert` sub-verb that re-verifies assertions against the running platform. Authored 2026-05-21 against current main.

This plan is the canonical "what's being done and why" for skill-architecture. Read cold without prior conversation context. Cross-references at the bottom.

> **Status (2026-05-21)** — Phase 1 + Phase 2 complete (W1+W2+W3+W4 landed in one execution pass). Skill is on-disk and structurally complete; awaiting user review before Phase 3 (W5 runner + W6 decommission) begins. Phase 3 is gated by Open Questions S2 (scratch-dir destination), S3 (test-design parseability format), S4 (detection-method automation approach). Phase 4 (W7 wire `skill-creator` + `skill-composer` as consumers) can start in parallel with or before Phase 3 — lighter weight, depends only on the architecture.md content being stable, which it now is.
>
> **Transcripts unblocked.** `assertions/platform-discovery/project-dir-resolution.md` carries the verified resolver chain (status: confirmed, last-verified: 2026-05-21). Transcripts Workstream A1 can now proceed referencing the assertion as the canonical source of truth.

## Review checklist — Phase 1+2 outputs

Files to inspect before greenlighting Phase 3 / Phase 4:

| File | Purpose | Why read it |
|---|---|---|
| `plugins/skill-authoring/skills/skill-architecture/SKILL.md` | Thin dispatcher (entry point) | Routes between dep-load default → `architecture.md` and verb invocation → `_reassert.md`. Carries Variant D closing release line. |
| `plugins/skill-authoring/skills/skill-architecture/architecture.md` | Substantive recommendation matrix | The load-bearing doc that authoring consumers will read. Covers dep declarations, encapsulation grammars, when to embed which discipline, project-dir resolver, state location, workflow vs script, sub-agent considerations. |
| `plugins/skill-authoring/skills/skill-architecture/confirmed-facts.md` | Digest of facts backing the recommendations | Each fact linked to its source assertion. Untested-gaps section captures known uncertainties. |
| `plugins/skill-authoring/skills/skill-architecture/_reassert.md` | Verb stub for the W5 runner | Documents the intended verb surface; exits to user as not-yet-implemented for now. |
| `plugins/skill-authoring/skills/skill-architecture/assertions/README.md` | Top-level topic index + framework doc | Carries the file-anatomy spec previously at `logs/assertions/README.md`. |
| `plugins/skill-authoring/skills/skill-architecture/assertions/platform-discovery/README.md` | New topic README | Lists pattern-confirmed (project-dir resolver chain) + untested gaps. |
| `plugins/skill-authoring/skills/skill-architecture/assertions/platform-discovery/project-dir-resolution.md` | First platform-discovery assertion | Full test design (3 probes), expected-outcomes table, 2026-05-21 historical-result row. |
| `plugins/skill-authoring/skills/skill-architecture/assertions/skill-runtime/*` | 17 relocated assertions + README | Moved from `logs/assertions/skill-runtime/`; relative links work; no edits needed. |
| `logs/assertions/README.md` | Relocation stub | Three-link forward to the new home. |

---

## Background

Two recurring frictions motivated this skill:

### Friction 1 — Skill-structure decisions are ad-hoc

`skill-creator` and `skill-composer` (the two authoring skills in `plugins/skill-authoring/`) make structural calls during every skill draft: should this skill embed `/concise-prose` as a dependency? Should PFN be loaded? Should dependencies use Variant D, Variant F, or none? These decisions today rely on the agent recalling the right answers from training or from the assertion-library README, which lives outside `skill-authoring/` and isn't a natural dependency target.

### Friction 2 — Confirmed facts are scattered and verification drifts

`logs/assertions/skill-runtime/` holds 17 assertions about Claude Code's Skill-tool runtime behavior (caching, body persistence, scope-leak, encapsulation grammar, etc.). The assertions are durable; the tests that verified them are reconstitutable. But:

- Running the tests is a manual, multi-step orchestration (write fixture skills to `.claude/skills/`, spawn a sub-agent, drive the right prompts, inspect side-effect logs).
- New platform-behavior facts (e.g. the `CLAUDE_CODE_SESSION_ID` + JSONL `cwd` project-dir resolver verified 2026-05-21) don't have an obvious home yet — they're "skill-runtime adjacent" but not strictly skill-runtime.
- Architecture recommendations derived from confirmed facts aren't surfaced to the authoring skills that need them.

### What this skill solves

A single discoverable load-point that:

1. **Carries the architecture recommendations** that skill-creator/skill-composer apply during authoring (loaded as a dep).
2. **Hosts the confirmed-facts digest** — the digest informs the recommendations; the digest is informed by the assertion library.
3. **Hosts the assertion library** — moved from `logs/assertions/skill-runtime/` into the skill, expanded to cover non-skill-runtime topics (platform-discovery, etc.).
4. **Provides a `reassert` sub-verb** — re-runs assertions against the current platform. Fixtures are materialized ephemerally from each assertion's `Test design` section, eliminating drift between the documented test and the fixture skill on disk.

---

## Decisions captured

### A. Skill name and home

- Name: `skill-architecture`.
- Home: `plugins/skill-authoring/skills/skill-architecture/`.
- Discoverability: declared in `plugins/skill-authoring/plugin.json` (or whatever the plugin's skill manifest is). Consumed by `skill-creator` and `skill-composer` via `## Dependencies` declarations.

### B. File layout

```
plugins/skill-authoring/skills/skill-architecture/
├── SKILL.md                    # Thin dispatcher: frontmatter + routing
├── architecture.md             # Substantive guidance — what skill-creator/composer load
├── confirmed-facts.md          # Digest of confirmed assertions backing architecture.md
├── _reassert.md                # PFN workflow for the test-runner sub-verb
├── assertions/                 # Moved from logs/assertions/skill-runtime/, expanded
│   ├── README.md                # Topic index + dependency graph
│   ├── skill-runtime/
│   │   ├── skill-caching.md
│   │   ├── body-persistence.md
│   │   ├── ... (17 existing)
│   └── platform-discovery/
│       └── project-dir-resolution.md   # NEW — captures CLAUDE_CODE_SESSION_ID + JSONL chain
└── scripts/                    # Test-runner implementation
    ├── __main__.py
    ├── reassert.py
    └── ...
```

Notes:

- `SKILL.md` is a thin dispatcher (description + "see architecture.md for guidance, see _reassert.md for re-verification") so its loaded body is small. The substantive content lives in `architecture.md` (one Read-tool hop from consumers).
- `architecture.md` cross-references `confirmed-facts.md`; `confirmed-facts.md` cross-references `assertions/<topic>/<assertion>.md`. Three layers: recommendations → facts → tests.
- Assertions are topic-subdirectored. The existing 17 become `assertions/skill-runtime/`; new topics add their own subdirectories.

### C. Test orchestration — sub-verb `reassert`

- Verb: `skill-architecture reassert [<assertion-path> | <topic>]`.
- Mechanic: reads the target assertion's `Test design` section, materializes any required fixture skills into a scratch `.claude/skills/<name>/` location (or a similarly Skill-tool-discoverable temp directory), spawns a sub-agent or `claude -p` driver with the assertion's run procedure, captures detection-method results, appends a row to the assertion's `Historical results` log.
- Cleanup: fixtures are removed after the run unless `--keep-fixtures` is passed.
- Bulk: invoking without arguments re-runs all assertions; with a topic name, re-runs the topic's assertions.

### D. Fixtures — ephemeral, derived from assertion `Test design`

- Standing fixture skills currently at `<project>/.claude/skills/` (`f-deep-*`, `flat-*`, `g1-*`, `g2-*`) are decommissioned once `reassert` materializes them on demand.
- Single source of truth: each assertion's `Test design` section contains the full fixture body. Drift between assertion doc and runtime fixture becomes structurally impossible.
- Migration: walk existing fixture skills, fold their content into the corresponding assertion's `Test design` if not already there, then delete the standing folder.

### E. Assertion library relocation

- Move `logs/assertions/skill-runtime/` → `plugins/skill-authoring/skills/skill-architecture/assertions/skill-runtime/`.
- `logs/assertions/README.md` either stays as a stub pointing into the skill, or `logs/assertions/` empties entirely. Author lean: stub stays for discoverability from outside the skill.
- New assertions land directly inside the skill from now on.

### F. New topic — `platform-discovery`

- First entry: `project-dir-resolution.md` capturing the `CLAUDE_CODE_SESSION_ID` env var + JSONL `cwd` lookup chain, validated 2026-05-21 in both interactive and headless `claude -p` contexts.
- Establishes the topic; future platform-discovery findings land here (e.g. env-var inventory, session-state surfaces, settings/state file conventions).

---

## Consumer integration

`skill-creator` and `skill-composer` declare the dependency:

```markdown
## Dependencies

If not already loaded, call (and apply during all prose generation within this skill's execution): /skill-authoring:skill-architecture
```

The loaded SKILL.md dispatches to `architecture.md` via Read tool — the consumer then has the recommendations available throughout its authoring flow. `architecture.md` carries the recommendation matrix: when to embed PFN, when to use Variant F vs Variant D scope grammar, when to load `/concise-prose`, etc.

---

## Workstreams

### W1 — Scaffold the skill ✓ done 2026-05-21

- W1.1 — Create `plugins/skill-authoring/skills/skill-architecture/` folder + SKILL.md frontmatter. ✓
- W1.2 — Author SKILL.md as thin dispatcher. ✓
- W1.3 — Plugin manifest uses `"skills": ["./skills/"]` directory-pattern auto-discovery — no per-skill registration needed. (Answers former Open Question S1.) ✓
- W1.4 — Smoke-test discoverability: requires session restart; deferred to post-compact session.

### W2 — Relocate the assertion library ✓ done 2026-05-21

- W2.1 — Moved `logs/assertions/skill-runtime/` → `plugins/skill-authoring/skills/skill-architecture/assertions/skill-runtime/`. ✓
- W2.2 — Relative links inside moved files use `./` paths — no edits required. ✓
- W2.3 — Stub at `logs/assertions/README.md` points at new home (three forward links). ✓
- W2.4 — `assertions/README.md` authored as topic-level index + framework doc (file anatomy spec moved here from the old top-level README). ✓

### W3 — Capture platform-discovery topic ✓ done 2026-05-21

- W3.1 — `assertions/platform-discovery/` created + topic README authored. ✓
- W3.2 — `project-dir-resolution.md` authored with full test design (3 probes), expected-outcomes table, and 2026-05-21 historical-result row. ✓
- W3.3 — Topic listed in `assertions/README.md`'s Topics table. ✓

### W4 — Author architecture.md and confirmed-facts.md ✓ done 2026-05-21

- W4.1 — `confirmed-facts.md` authored — sections by topic (skill-runtime, platform-discovery), each fact backlinked, untested-gaps section included. ✓
- W4.2 — `architecture.md` authored — sections: dependency declarations, encapsulation grammar matrix, inline step mentions, when to embed which authoring-discipline dep, project-dir resolution, state location, workflow vs script, sub-agent considerations, cross-references. ✓

### W5 — Build the `reassert` sub-verb

- W5.1 — Design the runner architecture: parse assertion frontmatter + Test-design markup; materialize fixtures; orchestrate `claude -p`; detect outcomes; append historical-results row.
- W5.2 — Define a structured `Test design` parseable format (block delimiters, fixture-skill markup, run-procedure markup, detection-method markup). Update existing assertion files to conform.
- W5.3 — Implement `scripts/reassert.py`.
- W5.4 — Implement CLI surface: `python3 -m scripts reassert [<target>]`.
- W5.5 — `_reassert.md` PFN workflow file documenting the verb for agent consumers.
- W5.6 — Initial smoke: re-verify one assertion (`skill-caching` is foundational; good first target).

### W6 — Decommission standing fixtures

- W6.1 — Walk `<project>/.claude/skills/<fixture-name>/` folders; fold any content not in the assertion `Test design` into the assertion.
- W6.2 — Delete the standing fixture folders.
- W6.3 — Update `.gitignore` / repo conventions if these were tracked.

### W7 — Wire consumer skills

- W7.1 — Update `skill-creator/SKILL.md` with the `## Dependencies` declaration.
- W7.2 — Update `skill-composer/SKILL.md` similarly.
- W7.3 — Verify the architecture recommendations actually reach the authoring agent during an end-to-end skill-create flow.

---

## Sequencing

```
W1 (scaffold) ─→ W2 (relocate assertions) ─→ W3 (platform-discovery) ─→ W4 (facts + architecture docs)
                                                                              ↓
                                              W5 (reassert verb) ──────────────┤
                                                                              ↓
                                              W6 (decommission fixtures) ─────┤
                                                                              ↓
                                              W7 (wire consumers)
```

W1 is the prerequisite. W2 + W3 can parallelize once W1 lands. W4 needs W2 + W3 done. W5 needs the assertion content stable (W2 + W3). W6 follows W5 (don't decommission until the runner works). W7 is final.

---

## Open questions

1. **~~Manifest registration~~** — resolved 2026-05-21. `plugins/skill-authoring/.claude-plugin/plugin.json` uses `"skills": ["./skills/"]` directory-pattern auto-discovery. No per-skill registration; the new folder is picked up on next session restart.

2. **Scratch dir for ephemeral fixtures** (gates W5). `<project>/.claude/skills/__reassert-scratch/<assertion-id>/` vs. `/tmp/skill-architecture-fixtures/<run-id>/` vs. `~/.claude/skills/__reassert/<run-id>/`. First option keeps Skill-tool discovery automatic; third option is user-scope so fixtures persist across project switches; second sidesteps `.claude/` namespace pollution but requires Skill-tool to discover from `/tmp` (likely doesn't). Lean: first option with cleanup discipline.

3. **Test-design parseability** (gates W5). Assertion files today are markdown; `Test design` sections are prose. To make `reassert` mechanical, fixture skills, run procedures, and detection methods need to live in parseable blocks (fenced code with language tags, or YAML inserts). Decide format before W5.2 — every existing assertion gets a small structural update.

4. **Detection-method automation** (gates W5). Some current assertions detect outcomes by "agent confirms the AARDVARK directive applied" — i.e. by reading sub-agent prose. Automating this needs either (a) the assertion to provide a regex/pattern the runner matches, or (b) the runner to spawn its own analytical sub-agent that returns structured pass/fail. Decide between (a) cheap-deterministic and (b) flexible-LLM-judged before W5.

5. **~~logs/assertions/ stub fate~~** — resolved 2026-05-21. Stub stays at `logs/assertions/README.md` with three forward links.

6. **~~Cross-plugin platform-discovery~~** — resolved 2026-05-21. `assertions/platform-discovery/project-dir-resolution.md` is now the source of truth. Transcripts Workstream A1 references it directly; navigator's future move references it. No further coordination needed.

---

## Cross-references

- **Existing infrastructure to relocate:** `logs/assertions/skill-runtime/` (17 assertions + README).
- **Adjacent plan:** `plans/transcripts.md` Workstream A1 (project-dir resolver) — needs the platform-discovery assertion's verified mechanism. Sequencing TBD: capture-then-execute, or parallel.
- **Consumer skills:** `plugins/skill-authoring/skills/skill-creator/SKILL.md`, `plugins/skill-authoring/skills/skill-composer/SKILL.md` — both gain `## Dependencies` declarations in W7.
- **Architecture-decision baseline:** `plugins/skill-authoring/ARCHITECTURE.md` and `README.md` describe the plugin's existing scope; this skill extends rather than replaces.

---

## Out of scope

- Re-running every assertion as part of W5 — only the smoke target (`skill-caching`) is re-verified during build. Bulk re-run happens after the verb is stable.
- Authoring new assertions beyond `project-dir-resolution.md` — the "untested gaps" listed in the existing skill-runtime/README.md (Variant F at depth, transitive in-wrapper scope, context-compaction effect, better frontmatter scope wording) remain captured-but-deferred.
- Modifying `skill-creator`'s or `skill-composer`'s authoring flow beyond adding the dependency declaration. Updates to their workflow files (`_new.md`, `_refine.md`, etc.) are downstream of architecture.md stabilizing.
- Generalizing `reassert` to non-skill-authoring contexts. Stays inside this plugin until at least one external consumer proves the need.
