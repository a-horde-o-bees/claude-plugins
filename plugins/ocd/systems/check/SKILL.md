---
name: check
description: Run universal discipline checks (dormancy, markdown, python) against plugin systems or project files.
argument-hint: "<dormancy | markdown | python | all> [<args>]"
allowed-tools:
  - Bash(ocd-run:*)
---

# /check

Run universal discipline checks against plugin systems or project files. Dimensions today: `dormancy` (plugin system contracts), `markdown` (literal-character and blank-line discipline in .md files), `python` (parent-walking patterns in .py files). More dimensions slot in as separate check modules without changing this skill's shape.

## Process Model

Each check dimension verifies one universal discipline. Dimensions target different scopes:

- **`dormancy`** — scans a plugin system's folder, detects which dormancy-relevant surfaces it exposes (init contract, readiness interface, MCP server, rule contribution), and runs the applicable assertions.
- **`markdown`** — scans `.md` files for unprotected literal characters (`{`, `}`, `<`, `>`, optionally `*`, `_`) outside backtick-protected code spans, and enforces blank-line discipline around lists, headings, and blocks.
- **`python`** — scans `.py` files for parent-walking patterns: chained `.parent.parent…` accesses, `.parents[N]` with N ≥ 1, and nested `os.path.dirname(...)` calls rooted at `__file__`.

`all` runs every dimension at its default scope and aggregates exit codes — new dimensions register in the CLI's `DIMENSIONS` registry and `all` picks them up without any skill-level change.

Files matching `fixture_*.*` are suppressed across every dimension via a wildcard entry in `allowlist.csv` — scanner test inputs contain the anti-patterns by design, so flagging them would pit the check against its own fixtures.

Real systems and documents drift — checkers are tested against synthetic fixtures, not against any particular plugin's live content.

Dormancy dimension verifies:

- Systems with an init contract (`init()` + `status()`) transition correctly between absent and operational states.
- Systems with runtime operations (MCP server) expose the readiness interface (`ready()` + `ensure_ready()`) and guard their surface internally.
- Deploy-only systems (init/status without runtime operations) are accepted without a readiness requirement.
- Rule contributions deploy to the plugin's expected rule corpus location after init.
- MCP servers gate tool registration on a readiness predicate and emit a dormant-state instruction.

Markdown dimension verifies:

- `{`, `}`, `<`, `>` in prose appear inside backtick-delimited inline code or fenced code blocks (so renderers don't strip `<>` as HTML, template engines don't consume `{}` as variables).
- With `--strict`, also flags unescaped `*` and `_` outside backticks (often intentional emphasis — review each).
- Blank-line discipline: no blank line between same-indent list items (unless a heading or blockquote interrupts the list), blank line before every heading and fenced-code block, blank line after every heading, no more than one blank line in a row.

Python dimension verifies:

- No `.parent`, `.parents[N]`, or `os.path.dirname(...)` traversal whose expression chain roots at `__file__` — the anti-pattern is a file anchoring to its own location to reach an ancestor directory.
- Chains rooted at any other expression (`Path(some_var).parent`, `dirname(other_path)`) are ordinary path manipulation and not flagged.
- Files whose job is to be the anchor (conftest.py, plugin entry-points, per-system CLI dispatchers) are suppressed via `allowlist.csv` at the system root; `--show-allowed` surfaces the suppressed entries for audit.

## Rules

- `dormancy` runs against the invoking plugin's systems by default; `--plugin <path>` targets a different plugin
- `markdown` runs against the current working directory by default; positional paths target specific files or directories
- `python` runs against the current working directory by default; positional paths target specific files or directories
- `all` runs every implemented dimension at its default scope
- Exit code reflects overall pass/fail — 0 when every check passes, 1 otherwise
- Output is structured per target — pass lines prefixed `+`, fail lines `-`, skip lines `~`

## Workflow

1. If not $ARGUMENTS: Exit to user: skill description and argument-hint
2. bash: `ocd-run check $ARGUMENTS` — CLI dispatches the dimension; `all` fans out over every registered dimension
3. Present CLI output to user — no summarization or reformatting
4. Return to caller

### Report

- Per-target pass/fail/skip with evidence lines from the CLI output
- Exit code from the CLI — 0 on full pass, 1 on any failure
