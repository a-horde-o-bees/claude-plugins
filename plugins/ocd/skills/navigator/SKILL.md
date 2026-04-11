---
name: navigator
description: Scan project directory and populate navigator database with file and folder descriptions
argument-hint: "[directory-path] [--delegate] (defaults to project root)"
allowed-tools:
  - Read
  - Bash(python3 *)
  - mcp__plugin_ocd_navigator__*
---

# /navigator

Scan filesystem and populate navigator database. Deterministic operations (add/remove/change detection) are handled by CLI scan. Description writing is handled by agent, working depth-first via `paths_undescribed` MCP tool.

## Process Model

Navigator maintains SQLite index of project files and directories with human-written descriptions. Two concerns are separated: structural sync (deterministic) and description writing (agent judgment).

1. Scan — CLI compares filesystem against database using git object hashes
  - New files are added with NULL description
  - Deleted files are removed
  - Changed files (hash differs from stored) are marked stale — description exists but may no longer reflect file scope
  - Files matching seed rules (glob patterns in CSV) receive prescribed descriptions automatically — both on initial add and when stale
  - Parent directories cascade to stale when any child changes, since directory descriptions summarize their children
2. Describe — agent works through entries needing attention, depth-first
  - `paths_undescribed` returns one directory per call — deepest first, ensuring children are described before parents
  - Entries with `description=null` need descriptions written from scratch
  - Entries with `stale=true` need re-evaluation — file changed but description may still be accurate
  - `paths_upsert` records description and clears stale marker, updating stored hash to current — entry is now reviewed against current contents
  - Loop terminates when `paths_undescribed` returns `done=true`

Depth-first ordering is structural, not preference — parent directory descriptions are derived from their children's descriptions, so children must be finalized first. Each `paths_undescribed` call returns only leaf-level work within returned directory; child directories with their own undescribed entries appear in earlier iterations.

## Trigger

User runs `/navigator`

## Route

1. Strip `--delegate` from `$ARGUMENTS` if present
2. If remaining arguments empty:
    1. Target directory = project root
3. Else:
    1. Target directory = specified directory path
4. Dispatch
    1. If `--delegate`:
        1. Spawn single background agent with Workflow section, Rules section, and resolved arguments
        2. Present agent report as-is
    2. Else:
        1. Proceed to Workflow

## Workflow

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/navigator/references/description-guidelines.md` for Description Guidelines
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/run.py servers.navigator.cli scan <target>` — syncs filesystem to database, reports added/removed/changed counts
3. While not done:
    1. {work} = paths_undescribed:
    2. If {work}.done: Break loop
    3. If {work}.listing is unexpected (not directory structure, error):
        1. Break loop — report output to user for feedback before continuing
    4. Review {work}.listing — entries with description=null need new descriptions, entries with stale=true have descriptions needing re-evaluation; described siblings provide context
    5. For each child in {work}.listing.children where description is null:
        1. Read file
        2. Write description following Description Guidelines
        3. paths_upsert: entry_path={child.path}, description="..."
    6. For each child in {work}.listing.children where stale is true:
        1. Read file
        2. Compare current file scope against existing stale description
        3. If description still accurately reflects file scope and role:
            1. paths_upsert: entry_path={child.path}, description={existing description} — clears stale marker
        4. Else:
            1. Write updated description following Description Guidelines
            2. paths_upsert: entry_path={child.path}, description="..."
    7. Describe directory — informed by all children now visible in listing
        1. paths_upsert: entry_path={work}.target, description="..."

### Report

- Scan results — added, removed, changed counts
- Entries described — total count of files and directories described

## Rules

- Depth-first by design — `paths_undescribed` returns deepest directory first; describe children before parents so directory descriptions reflect contents. Depth-first guarantees all child entries within returned directory are leaf entries (files or `traverse=0` directories) — child directories with their own undescribed entries are processed in earlier iterations. If child directory with description=null appears within returned listing, treat as unexpected output and Break loop.
- Preserve existing descriptions that already conform to guidelines — do not overwrite unless they violate Description Guidelines rules
- No description length limit — follow Description Guidelines guidance, not brevity constraints
- Directories with `traverse=0` are listed but not entered — describe directory itself, not its contents
- `paths_upsert` always clears stale marker — whether description changes or stays same, running `paths_upsert` marks entry as reviewed against current file contents
