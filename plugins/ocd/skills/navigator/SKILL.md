---
name: ocd-navigator
description: Scan project directory and populate navigator database with file and folder descriptions
argument-hint: "[directory-path] [--delegate] (defaults to project root)"
---

# /ocd-navigator

Scan filesystem and populate navigator database. Deterministic operations (add/remove/change detection) are handled by `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator scan`. Description writing is handled by agent, working depth-first via `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator get-undescribed`.

## Process Model

Navigator maintains SQLite index of project files and directories with human-written descriptions. Two concerns are separated: structural sync (deterministic) and description writing (agent judgment).

1. Scan — CLI compares filesystem against database using git object hashes
  - New files are added with NULL description
  - Deleted files are removed
  - Changed files (hash differs from stored) are marked stale — description exists but may no longer reflect file scope
  - Files matching seed rules (glob patterns in CSV) receive prescribed descriptions automatically — both on initial add and when stale
  - Parent directories cascade to stale when any child changes, since directory descriptions summarize their children
2. Describe — agent works through entries needing attention, depth-first
  - `get-undescribed` returns one directory per call — deepest first, ensuring children are described before parents
  - `[?]` entries (NULL description) need descriptions written from scratch
  - `[~]` entries (stale) need re-evaluation — file changed but description may still be accurate
  - `set` records description and clears stale marker, updating stored hash to current — entry is now reviewed against current contents
  - Loop terminates when no NULL or stale entries remain

Depth-first ordering is structural, not preference — parent directory descriptions are derived from their children's descriptions, so children must be finalized first. Each `get-undescribed` call returns only leaf-level work within returned directory; child directories with their own undescribed entries appear in earlier iterations.

## Trigger

User runs `/ocd-navigator`

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
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator scan <target>` — syncs filesystem to database, reports added/removed/changed counts
3. While `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator get-undescribed` does not return "No work remaining.":
    1. If output is unexpected (not directory listing, error message, or unrecognized format):
        1. Break loop — report output to user for feedback before continuing
    2. Review returned directory listing — `[?]` entries need new descriptions, `[~]` entries have stale descriptions that need re-evaluation; described siblings provide context
    3. For each `[?]` entry:
        1. Read file
        2. Write description following Description Guidelines
        3. Run `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator set <path> --description "..."`
    4. For each `[~]` entry:
        1. Read file
        2. Compare current file scope against existing stale description
        3. If description still accurately reflects file scope and role:
            1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator set <path> --description "..."` with same description — `set` clears stale marker
        4. Else:
            1. Write updated description following Description Guidelines
            2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator set <path> --description "..."`
    5. Describe directory — informed by all children now visible in listing
        1. Run `python3 ${CLAUDE_PLUGIN_ROOT}/run.py skills.navigator set <directory> --description "..."`

### Report

- Scan results — added, removed, changed counts
- Entries described — total count of files and directories described

## Rules

- Depth-first by design — `get-undescribed` returns deepest directory first; describe children before parents so directory descriptions reflect contents. Depth-first guarantees all child entries within returned directory are leaf entries (files or `traverse=0` directories) — child directories with their own undescribed entries are processed in earlier iterations. If `[?]` child directory appears within returned directory listing, treat as unexpected output and Break loop.
- Preserve existing descriptions that already conform to guidelines — do not overwrite unless they violate Description Guidelines rules
- No description length limit — follow Description Guidelines guidance, not brevity constraints
- Directories with `traverse=0` are listed but not entered — describe directory itself, not its contents
- `set` always clears stale marker — whether description changes or stays same, running `set` marks entry as reviewed against current file contents
