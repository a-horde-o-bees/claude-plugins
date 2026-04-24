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

- **`dormancy`** — scopes to plugin systems. Scans a system's folder, detects which dormancy-relevant surfaces it exposes (init contract, readiness interface, MCP server, rule contribution), and runs the applicable assertions.
- **`markdown`** — scopes to project files. Walks `.md` files, uses a deterministic line+char state machine to detect characters (`{`, `}`, `<`, `>`, optionally `*`, `_`) outside backtick-protected inline/fenced code, and to enforce blank-line discipline around lists, headings, and blocks.
- **`python`** — scopes to project files. Walks `.py` files, parses each to AST, and flags parent-walking patterns: chained `.parent.parent…` accesses, `.parents[N]` with N ≥ 1, and nested `os.path.dirname(...)` calls.

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
2. {dimension} = first token of $ARGUMENTS
3. {remainder} = $ARGUMENTS after {dimension}
4. If {dimension} is `dormancy`: bash: `ocd-run check dormancy {remainder}`
5. Else if {dimension} is `markdown`: bash: `ocd-run check markdown {remainder}`
6. Else if {dimension} is `python`: bash: `ocd-run check python {remainder}`
7. Else if {dimension} is `all`:
    1. bash: `ocd-run check dormancy`
    2. bash: `ocd-run check markdown {remainder}`
    3. bash: `ocd-run check python {remainder}`
8. Else: Exit to user: unrecognized dimension {dimension} — expected dormancy, markdown, python, or all
9. Present CLI output to user — no summarization or reformatting
10. Return to caller

### Report

- Per-target pass/fail/skip with evidence lines from the CLI output
- Exit code from the CLI — 0 on full pass, 1 on any failure
