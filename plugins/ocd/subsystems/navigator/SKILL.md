---
name: navigator
description: Sync navigator database with filesystem and describe entries that need descriptions.
argument-hint: "[directory-path]"
allowed-tools:
  - Read
  - Bash(python3 *)
  - mcp__plugin_ocd_navigator__*
---

# /navigator

Sync the navigator database with the filesystem, then work through entries that need descriptions. Structural sync is deterministic (CLI `scan`); description writing is agent judgment (driven by the `paths_undescribed` / `paths_upsert` MCP tools).

## Process Model

Navigator maintains a SQLite index of project files and directories, each with a human-written description agents use to decide whether to open the file. Two concerns are separated:

- **Structural sync** — deterministic. The `scan` CLI walks the filesystem, adds new paths with NULL description, removes deleted paths, flags changed files as stale, and cascades staleness to parent directories (parent descriptions summarize children, so a child change invalidates the parent). Files matching seed-rule glob patterns receive prescribed descriptions automatically.
- **Description writing** — agent judgment. The `paths_undescribed` tool returns the deepest directory with undescribed or stale entries, one at a time. Children are finalized before parents — parent descriptions are derived from their children's.

The loop terminates when `paths_undescribed` returns `done=true`.

## Rules

- Preserve existing descriptions that already conform to Description Guidelines — do not overwrite
- No description length limit — follow Description Guidelines, not brevity constraints
- Directories with `traverse=0` are listed but not entered — describe the directory itself, not its contents
- `paths_upsert` always clears the stale marker and updates the stored hash — running it marks the entry as reviewed against current contents, whether the description changed or not
- Depth-first is guaranteed by `paths_undescribed` — all children in a returned listing are leaves (files or `traverse=0` directories). If a child directory still shows `description=null` in the listing, treat as unexpected output and break the loop

## Workflow

1. {target} = $ARGUMENTS if provided, else project root
2. Read `${CLAUDE_PLUGIN_ROOT}/subsystems/navigator/references/description-guidelines.md`
3. Sync structure — bash: `ocd subsystems.navigator scan {target}`
4. While work remains:
    1. {work} = paths_undescribed
    2. If {work}.done: Break loop
    3. If {work}.listing is not a directory structure (error, malformed): Break loop — surface to user for review
    4. For each {child} in {work}.listing.children where description is null:
        1. Read {child}
        2. Write description following Description Guidelines
        3. paths_upsert: entry_path={child.path}, description=<new description>
    5. For each {child} in {work}.listing.children where stale is true:
        1. Read {child}
        2. Compare current scope against existing description
        3. If existing description still accurately reflects scope and role:
            1. paths_upsert: entry_path={child.path}, description=<existing description>
        4. Else:
            1. Write updated description following Description Guidelines
            2. paths_upsert: entry_path={child.path}, description=<new description>
    6. Describe {work}.target — informed by all children now visible in listing
        1. paths_upsert: entry_path={work}.target, description=<directory description>

### Report

- Scan results — added, removed, changed counts
- Entries described — total count of files and directories described
