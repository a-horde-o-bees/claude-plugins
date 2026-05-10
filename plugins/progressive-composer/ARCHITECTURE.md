# progressive-composer architecture

Internal design reference for developers maintaining the plugin. User-facing documentation lives in `README.md`; agent-facing operational procedures live in `skills/progressive-composer/SKILL.md` and the `_<verb>.md` workflow files.

## Layers

```
plugins/progressive-composer/
├── .claude-plugin/
│   └── plugin.json
├── README.md
├── ARCHITECTURE.md
├── LICENSE
├── skills/
│   └── progressive-composer/        # entry point — Claude Code loads SKILL.md from here
│       ├── SKILL.md                 # triggers + verb topography
│       ├── _<verb>.md               # workflow files reachable via Call:
│       └── scripts/                 # python implementation as importable package
│           ├── __init__.py
│           ├── _paths.py            # scope/folder/embed path helpers
│           ├── _spec.py             # composition.md schema, parse, serialize
│           ├── _clone.py            # sparse-checkout + ls-remote primitives
│           ├── _config.py           # generic JSON helpers (currently unused)
│           └── compose.py           # compose verb (new/refine/build/list + sub-ops)
└── tests/                           # pytest fixtures + verb tests
```

The skill folder is hyphenated (`progressive-composer/`) and matches the plugin name per Anthropic's 1:1 convention (cf. `frontend-design/skills/frontend-design`, `skill-creator/skills/skill-creator`). Python implementation lives in `scripts/` so the parent folder is never imported as a Python package. SKILL.md invokes scripts as `uv run -m scripts.compose <subverb>` with cwd at the skill folder.

No `bin/<plugin>-run` dispatcher, no plugin-level `run.py`, no vendored `tools/` package. Path resolution and env access happen inline in `scripts/_paths.py`. See project-root `logs/decision/skill-authoring.md` § *Dependencies via `uv run`* for the rationale.

## Storage discipline

Each composed skill is self-contained at `<scope>/.claude/skills/<name>/`:

```
<scope>/.claude/skills/<name>/
├── SKILL.md                          # Claude Code's entry point (PFN-structured body)
├── composition.md                    # recipe + provenance (always present for our deploys)
├── sources/                          # embedded exemplars during active development
│   └── <source-slug>/                # sparse-checkout of upstream skill at pinned commit
├── _<verb>.md                        # workflow scaffolds (from compose build)
└── scripts/                          # composition's own implementation
```

**No shared cache directory.** Each composition embeds the exact upstream skill folders it depends on, sparse-checked at pinned commits. Multi-version is the default — two compositions needing different refs of the same upstream repo each get their own pinned snapshot.

**No central registry.** Each composition.md IS the per-skill provenance record. Walking `<scope>/.claude/skills/*/composition.md` enumerates every composition the plugin owns.

**Plugin data dir is reserved but unused.** No transient state currently goes through `~/.claude/plugins/data/progressive-composer-a-horde-o-bees/`. Reserved per Claude Code convention for future verbs that might need disk space.

State location follows project-root `logs/decision/state-location.md`. The plugin-namespaced extension (`<scope>/.claude/<plugin>-<author>/<concern>/`) remains a valid pattern for plugins that need plugin-managed user-edited content separate from any specific skill; progressive-composer doesn't currently use it.

## Sparse-checkout primitive

`scripts/_clone.py:sparse_checkout_skill(url, skill_path, ref, dest)`:

1. `git clone --filter=blob:none --no-checkout --depth 1 --branch <ref> <url> <tmpdir>` — fetch tree blobs only, no working tree
2. `git sparse-checkout init --cone` + `git sparse-checkout set <skill_path>` — restrict working tree to the named skill folder
3. `git checkout` — populate the sparse working tree
4. `git rev-parse HEAD` — capture the resolved commit
5. `shutil.copytree(<tmpdir>/<skill_path>, <dest>)` — move the resolved subtree into place
6. tmpdir cleaned up automatically

Returns the captured commit SHA. The destination receives just the skill folder's content (no `.git/`).

`scripts/_clone.py:ls_remote_head(url, ref)`:

`git ls-remote <url> <ref>` returns the SHA at upstream's named ref without touching any local clone state. Compare against composition.md's pinned `commit` field for non-mutating drift detection.

## composition.md schema

```yaml
---
spec_version: 1
name: <skill-name>
description: <one-line>
scope: user                 # OR project
sources:
  - url: https://github.com/anthropics/skills.git
    skill: slack-formatting
    ref: main               # branch / tag / refs/heads/<x>
    commit: abc123def...    # pinned at build time
goal_summary: <one-line>
last_build: 2026-05-10T14:00:00Z
build_status: built         # draft | built
---

# Goal
# Source mapping
# Design refinements
```

Stdlib-only YAML subset implemented in `_spec.py` (no pyyaml dep). Schema is bounded — top-level scalars, one list of dicts (`sources`). No `type` discriminator; every composition.md describes a composition.

## Verb dispatch

`compose.py` uses argparse subparsers — one subparser per subverb. User-facing subverbs (`new`, `refine`, `build`, `list`) and agent-internal sub-ops (`add-source`, `remove-source`, `update-sources`, `purge-sources`) all live in the same module; `main()` dispatches via a verb-to-handler dict.

## Workflow shape — compose

`compose new --scope` and `compose refine <name> --scope` are **orchestration entry points**: the script prints state + guidance; the agent reads the orchestration and drives dialogue. The workflow files (`_compose_new.md`, `_compose_refine.md`) document what the agent does at each step. Sub-ops (`add-source`, `update-sources`, etc.) are deterministic operations the agent invokes during the workflow.

`compose build` is the **terminal materialize step**. The output skill scaffold conforms to PFN + progressive-disclosure discipline automatically — SKILL.md body shape, `_<verb>.md` workflow files using PFN notation, `scripts/` Python package skeleton. The agent fleshes out details via Edit tool after build.

`compose list` is the **status overview**. Default shows last-known status from composition.md frontmatter (no network); `--drift` adds a `git ls-remote` pass per source per composition for live drift detection.

## What this plugin doesn't do

- **Install unmodified upstream skills** — Vercel's `npx skills` covers this surface; mature, npm-distributed, polished. progressive-composer doesn't compete.
- **Plugin-level operations** — `/plugin install` handles atomic plugin bundles; `ccpi` package-manager-style CLI handles plugin-level lifecycle. progressive-composer is skill-grained, composition-focused.

## Compositions of compositions

A user could in principle add a previously-composed skill as a source for a new composition. We document this is not recommended — the source's transitive recipe history would entangle with the new composition's goal articulation, producing confusing provenance. The script doesn't enforce this; the recommendation lives in SKILL.md and the decision log.
