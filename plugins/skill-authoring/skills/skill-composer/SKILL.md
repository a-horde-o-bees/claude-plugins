---
name: skill-composer
description: Use this skill when the user wants to design a new skill from one or more exemplar source skills, iterate on an in-progress composition, or list deployed compositions with optional upstream-drift detection. Each composed skill is self-contained — composition.md + embedded sources + SKILL.md live together in one folder. For installing an unmodified upstream skill kept as-is, use Vercel's `npx skills` instead — this skill focuses on composition, not installation.
---

# skill-composer

Compose new skills from one or more exemplar sources, with PFN + progressive-disclosure authoring discipline applied automatically. Drift detection against pinned upstream commits via non-mutating `git ls-remote`.

## Triggers

| Cognitive moment | Verb |
|---|---|
| User wants to design a new skill drawing on one or more exemplars | `compose new` |
| User wants to iterate on an in-progress composition (drift check + refinement dialogue) | `compose refine` |
| User asks what compositions exist and whether sources have drifted | `compose list` (with `--drift` for live network check) |

For installing an unmodified upstream skill kept as-is, use Vercel's [`npx skills`](https://skills.sh) — this plugin doesn't bundle that capability.

## Verbs

Each verb is a Python module under `scripts/`. Invoke from the skill folder via `uv run`:

```
uv run -m scripts.compose <subverb> [args]
```

| Verb | Workflow file | Subverb | Purpose |
|---|---|---|---|
| `compose new` | `_compose_new.md` | `scripts.compose new` | Open new-composition workflow; agent collects name, intent, Surface, and sources via dialogue, then scaffolds composition.md + live SKILL.md + `_<verb>.md` workflow files directly |
| `compose refine` | `_compose_refine.md` | `scripts.compose refine` | Re-enter an existing composition; auto drift check; agent drives refinement of design intent and edits the live skill files in place |
| `compose list` | `_compose_list.md` | `scripts.compose list` | Walk deployed compositions; report deployed/draft state per composition (with `--drift` for network drift check) |

For each verb's procedure, `Call:` the corresponding `_<verb>.md` workflow file. `uv` is a soft prerequisite — install via [astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) when missing. All scripts are stdlib-only.

### Agent-internal sub-ops

The compose workflow uses sub-ops the agent invokes during dialogue (not user-facing primary verbs):

| Sub-op | Purpose |
|---|---|
| `compose add-source <name> <url>:<skill>[@<ref>] --destination` | Sparse-checkout source skill into `<skill>/sources/<source-slug>/`; append to composition.md frontmatter |
| `compose remove-source <name> <source-slug> --destination` | Delete from sources/, remove from composition.md frontmatter |
| `compose update-sources <name> [--source <slug>] --destination` | Re-sparse-checkout source(s) at current upstream HEAD; advance pinned commit |
| `compose purge-sources <name> --destination` | Delete sources/ subfolder when finalized; pinned commits remain in composition.md |

These are documented inside `_compose_new.md` and `_compose_refine.md` workflow files as steps the agent follows; users do not invoke them directly.

## Storage

Each composed skill is self-contained:

```
<destination-parent>/<name>/
├── SKILL.md                      # what Claude Code loads (PFN-structured body)
├── composition.md                # frontmatter (sources + pins) + body (goal + recipe)
├── sources/                      # embedded exemplars during active development
│   ├── <source-slug-a>/          # sparse-checkout of upstream skill at pinned commit
│   └── <source-slug-b>/
├── _<verb>.md                    # PFN-structured workflow files (generated as scaffolds at build)
└── scripts/                      # composition's own implementation
    └── __init__.py
```

`sources/` is present during active development; `compose purge-sources` reclaims disk after finalization (pinned commits in composition.md persist; `compose refine` auto-rehydrates by re-fetching at pinned commits).

No shared cache directory; no central registry. Each composition.md IS the per-skill provenance record. Walking `<destination-parent>/*/composition.md` enumerates every composition the plugin owns.

## Authoring discipline baked in

`compose new` and `compose refine` scaffold and edit live skill files directly from bundled templates at `assets/skill-template.md`, `assets/verb-workflow-template.md`, and `assets/composition-template.md`. The disciplines that shape the output:

- **SKILL.md body shape** — /progressive-disclosure: frontmatter description as cognitive trigger, body holds Triggers + Verb topography pointing at `_<verb>.md` workflow files
- **Workflow files** (`_<verb>.md`) — /process-flow-notation: numbered steps, indentation-scoped blocks, `Call:` refs to components, `bash:` / `skill:` invocation prefixes
- **Python implementation** — `scripts/` package skeleton; mechanically resolvable work goes there per /workflow-vs-script
- **Frontmatter descriptions** — /description-authoring: scope + role, exclude internals / contents / history

`composition.md` tracks intent and source provenance; `SKILL.md` + `_<verb>.md` are the live implementation. The agent edits both in place.

## Compositions of compositions

Composing a new skill that uses one of your previously-composed skills as a source is not recommended — provenance entanglement makes the recipe history hard to follow. Use upstream sources directly instead. Not enforced by the script; surfaced here for awareness.

## Complementary tools

- **Vercel's `npx skills`** ([skills.sh](https://skills.sh)) — for installing unmodified upstream skills. Symlinks into `~/.claude/skills/`; auto-fresh via upstream.
- **`/plugin install`** — for atomic plugin bundles. Bundle-grained, not skill-grained.
- **`/skill-authoring:skill-composer` (this skill)** — for designing new skills from exemplars with authoring discipline applied. Drift tracking against pinned snapshots.
- **`/skill-authoring:skill-creator` (sibling skill)** — for designing new skills from scratch via interview-driven dialogue. Same authoring disciplines applied at every step.
