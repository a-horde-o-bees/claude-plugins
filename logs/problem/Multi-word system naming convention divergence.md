# Multi-word system naming convention divergence

The skill-md.md convention says skill `name` and directory name match exactly with lowercase + hyphens only. Python packages cannot contain hyphens. needs-map is the project's first multi-word ocd system, and the two constraints fundamentally conflict — there is no name that satisfies both.

## Current workaround

needs-map ships with two names:

- Skill frontmatter `name: needs-map` (slash command `/ocd:needs-map`)
- Directory `plugins/ocd/systems/needs_map/` (Python package, what `framework._discover_systems` reports)

`plugins/ocd/run.py` rewrites bare-name hyphens to underscores so `ocd-run needs-map` resolves to `systems.needs_map`. `setup.deploy_files` and other framework discovery surfaces show the underscored directory name; the slash command uses the hyphenated skill name. Two-names-one-system is undocumented in the convention.

## What's wrong

- skill-md.md still says skill name **matches the directory name exactly** — this is now provably false for any multi-word DB-backed system
- There's no governing rule that says "for multi-word Python systems, skill name uses hyphen + dir uses underscore"; the discipline lives in one project's run.py and was discovered ad-hoc
- A reader of `/ocd:setup status` sees `needs_map`; a user invoking `/ocd:needs-map` sees the hyphenated form. No documentation explains the relationship
- Future multi-word systems will have to re-derive the same workaround unless this lands as a documented rule + convention update

## Suspected fix shapes

- Update skill-md.md convention to acknowledge the divergence: hyphen-named skill ↔ underscore-named Python package, with run.py rewrite as the bridge
- OR: standardize on underscores for all skill names with multi-word identifiers (matches Python; gives up the hyphen ergonomics)
- OR: rework `framework._discover_systems` to read the skill name from frontmatter, so setup status output matches the slash command (eliminates the surface inconsistency at the cost of name-source-of-truth complexity)

## Origin

Surfaced during the purpose-map → needs-map sandbox (PR #8) when needs-map became the first multi-word system. Workaround landed as one-line `module.replace("-", "_")` in run.py; no convention update accompanied it. Logging here so the divergence isn't permanent technical debt.
