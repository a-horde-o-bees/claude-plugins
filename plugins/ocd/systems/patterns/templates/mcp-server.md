# MCP Server

When to expose functionality as an MCP server versus a CLI script, Python library, or file-based storage.

## Decision Framework

Does the agent need to reach for this capability ad-hoc, at unpredictable moments, with complex parameters?

- **Yes** — MCP server. The typed schema and always-available discoverability justify the context cost.
- **No, it's called during specific workflows** — CLI invocation in the skill's workflow steps. The skill tells the agent exactly what command to run.
- **No, the data is simple text** — file-based storage. Markdown files in folders are transparent, greppable, diffable, and survive plugin absence.

## MCP Server

### Benefits

- **Typed schema in context**: agent sees parameter names, types, descriptions without reading docs. Correct calls without trial-and-error.
- **Ad-hoc discoverability**: tools are always available in the agent's tool list. The agent reaches for them without being told to in a workflow step.
- **Long-lived process**: stays warm across calls. Connection pools, loaded state, and caches persist.
- **Structured JSON output**: every call returns parseable structured data.

### Costs

- **Context tokens every session**: tool descriptions load whether or not the agent uses them. 10 tools ≈ 1000 tokens of permanently consumed context.
- **Silent failure on server crash**: if the MCP server fails to start (import error, missing dep, config problem), all its tools disappear from the agent's tool list with no error message. The agent proceeds without the capability and may not realize it's missing.
- **All-or-nothing**: one broken import in the server package kills every tool in the server.
- **Opaque to user**: data in SQLite databases can't be browsed in an editor, diffed in PRs, or grepped with standard tools.
- **Transport overhead**: JSON-RPC stdio round-trip for every call.
- **Infrastructure weight**: schema, connection factory, init bootstrap, _init.py contract — maintenance cost proportional to capability surface.

## CLI via Bash Tool

### Benefits

- **Zero context cost**: no tool descriptions loaded. The agent constructs the command when needed.
- **Visible failure**: when a CLI command fails, the agent sees the traceback in bash output and can diagnose. Errors are actionable.
- **No persistent process**: each invocation is independent. No server lifecycle to manage.
- **Skill-prescribed**: a SKILL.md workflow step documents the exact command. The agent doesn't need schema discovery.

### Costs

- **No schema assistance**: the agent constructs command strings manually. Error-prone without documentation.
- **Cold start per call**: each invocation spawns a new process.
- **Unstructured output**: text unless the CLI prints JSON explicitly.

## File-Based Storage

### Benefits

- **Zero tool cost**: agent uses built-in Read/Write/Grep/Glob — no MCP tools loaded.
- **Transparent**: user can browse in any editor, grep, diff in PRs.
- **Git-friendly**: text files version naturally. History, blame, and review work out of the box.
- **Survives plugin absence**: files are readable without any plugin installed.
- **Simplest queue**: add = write file, resolve = delete file, review = list directory.

### Costs

- **No structured queries**: filtering by metadata requires parsing frontmatter across files.
- **No atomic operations**: tag renaming means editing every file individually.
- **ID management**: needs a naming/numbering convention.

## When Each Approach Earns Its Place

| Signal | Approach |
|---|---|
| Agent reaches for it ad-hoc at unpredictable moments | MCP server |
| Complex parameters with many options | MCP server |
| Data is relational with joins and aggregations | MCP server (SQLite) |
| Called only during specific skill workflows | CLI in workflow steps |
| Simple inputs (path, name, flag) | CLI |
| Data is text notes with optional metadata | Files in folders |
| User needs to browse, diff, or review the data | Files in folders |
| Queue semantics (add, review, delete when done) | Files in folders |
| Must survive plugin absence or MCP failure | Files or CLI |

## Anti-Patterns

- **MCP for simple CRUD at low volume**: 14 tools for a system with 25 records is over-engineered. Files in folders with `ls` and `grep` outperform SQL at that scale.
- **MCP as the only interface**: if the hook or skill can import the library directly, the MCP wrapper adds transport overhead without value. Use library imports for in-process consumers; reserve MCP for agent-facing interactive access.
- **Silent data store**: SQLite databases are opaque to both user and agent without tool calls. If the data benefits from human review (decisions, friction, ideas), files are more transparent.
