---
name: navigator
description: Sync navigator database with filesystem and populate purposes for paths that need them.
argument-hint: "[directory-path]"
allowed-tools:
  - Read
  - Bash(ocd-run *)
  - mcp__plugin_ocd_navigator__*
---

# /navigator

Sync the navigator database with the filesystem, then work through paths that need purpose description. Structural sync is deterministic (CLI `scan`); purpose writing is agent judgment (driven by the `paths_undescribed` / `paths_upsert` MCP tools).

## Process Model

Navigator maintains a SQLite index of project paths, each with a human-written purpose that agents use to decide whether to open the file. Two concerns are separated:

- **Structural sync** — deterministic. The `scan` CLI walks the filesystem, adds new paths with NULL purpose, removes deleted paths, flags changed files as stale, and cascades staleness to parent directories (parent purposes summarize children, so a child change invalidates the parent). Paths matching a rule in `path_patterns` receive their purpose from the rule automatically and are never stale.
- **Purpose writing** — agent judgment. The `paths_undescribed` tool returns the deepest directory with paths that still need purpose description, one at a time. Children are finalized before parents — a parent's purpose summarizes its children.

The loop terminates when `paths_undescribed` returns `done=true`.

## Rules

- Preserve existing purposes that already conform to Description Guidelines — do not overwrite
- No purpose length limit — follow Description Guidelines, not brevity constraints
- Directories with `traverse=0` are listed but not entered — describe the directory itself, not its contents
- `paths_upsert` always clears the stale marker and updates the stored hash — running it marks the path as reviewed against current contents, whether the purpose changed or not
- Depth-first is guaranteed by `paths_undescribed` — all children in a returned listing are leaves (files or `traverse=0` directories). If a child directory still shows `purpose=null` in the listing, treat as unexpected output and break the loop

## Workflow

1. Verify navigator ready — bash: `ocd-run navigator ready`
    1. If non-zero exit: Exit to user: navigator is dormant — run `/ocd:setup init` to initialize
2. {target} = $ARGUMENTS if provided, else project root
3. Read `${CLAUDE_PLUGIN_ROOT}/systems/navigator/references/description-guidelines.md`
4. Sync structure — bash: `ocd-run navigator scan {target}`
5. While work remains:
    1. {work} = paths_undescribed
    2. If {work}.done: Break loop
    3. If {work}.listing is not a directory structure (error, malformed): Break loop — surface to user for review
    4. For each {child} in {work}.listing.children where purpose is null:
        1. Read {child}
        2. Populate the purpose of the path using the Purpose Statement principle
        3. paths_upsert: entry_path={child.path}, purpose=<new purpose>
    5. For each {child} in {work}.listing.children where stale is true:
        1. Read {child}
        2. Compare current scope against existing purpose
        3. If existing purpose still accurately reflects scope and role:
            1. paths_upsert: entry_path={child.path}, purpose=<existing purpose>
        4. Else:
            1. Populate the purpose of the path using the Purpose Statement principle
            2. paths_upsert: entry_path={child.path}, purpose=<new purpose>
    6. Populate the purpose of {work}.target — informed by all children now visible in listing
        1. paths_upsert: entry_path={work}.target, purpose=<directory purpose>

### Report

- Scan results — added, removed, changed counts
- Paths described — total count of files and directories given a purpose
