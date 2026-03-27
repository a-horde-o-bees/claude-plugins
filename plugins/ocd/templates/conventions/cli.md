# CLI Conventions

Conventions for agent-facing CLI scripts. Internal scripts (called by plugin hooks or other scripts, never by agents) follow standard engineering practices but do not need agent-oriented help text or output formatting.

## Separation of Concerns

CLI scripts are presentation only — argument parsing, output formatting, and dispatch wrappers. No business logic, database connections, or domain operations in CLI files. Delegates to supporting modules (`{name}.py`, `_{purpose}.py`) for all operations. CLI docstring declares its supporting modules: `"Business logic lives in {name}.py."`.

## Flag and Argument Design

- Long-form flags only — `--description`, `--recursive`, not `-d`, `-r`
- Flag names state what they mean — no abbreviations, no ambiguous single-letter shortcuts
- Positional arguments for primary operand (path, target); flags for modifiers
- Required vs optional clearly expressed through CLI framework, not convention

## Help and Usage Text

Help text answers agent questions:

- **When to call** — conditions under which command is preferred over alternatives
- **What output looks like** — structure, markers, delimiters agent will parse
- **How to interpret results** — what markers mean, what empty results imply
- **What to call next** — workflow sequencing
- **Stop conditions** — explicit termination criteria for loops

Do not include:
- Installation instructions
- Human-oriented examples ("try running...")
- Flag syntax that CLI framework already shows

## Output Format

- Structured and consistent — predictable markers, clear delimiters, no decorative formatting
- Machine-parseable status indicators — symbolic markers (`[?]`, `[~]`), not prose ("needs description")
- No color codes, emoji, or terminal formatting
- Consistent structure across invocations — same command produces same output shape regardless of content

## Error Messages

Error output includes corrective guidance, not just failure description:

- **Bad**: `"Invalid argument"`
- **Good**: `"Expected path relative to project root, got absolute path. Use 'src/auth' not '/home/dev/projects/.../src/auth'"`
- **Bad**: `"File not found"`
- **Good**: `"No entry for 'src/auth/handler.py' in DB. Run 'scan' first to sync filesystem, then retry."`

Errors guide agent to self-correct without user intervention.

## Documentation as Code

`--help` output must be complete enough that agent reading it can use tool correctly without external reference:

- Help descriptions explain workflow context, not just syntax
- Subcommand help text includes output format and interpretation
