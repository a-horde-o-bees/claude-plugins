# Non-Obvious Documentation Surfaces

Documentation is not confined to README.md / architecture.md / CLAUDE.md / SKILL.md. It lives in many surfaces scattered through code. Each surface has the same discipline: structural match against fact bundle, surgical edit on contradiction, unverifiable content preserved. Regeneration applies only to canonical docs where prose coherence matters; surfaces use surgical edits.

## Surfaces in Scope

For a given system, the per-system agent checks all of these within the system's file tree:

### 1. Module Docstrings

File-level `"""..."""` blocks at the top of each `.py` file. Serve as module purpose statements (per `design-principles.md` Purpose Statement: applies to modules as well as documents).

Verification: compare against module's actual content — public symbols, imports, primary responsibility. The Python ast module parses these directly via `ast.get_docstring(module)`.

Generation: if absent and module has non-trivial content, populate with a purpose statement derived from the public symbols and primary responsibility.

### 2. Function and Method Docstrings

Every public function, method, and class has a docstring. Per the Purpose Statement guidance, these are purpose statements at the function scale — scope + role at that abstraction level.

Verification: compare against signature and body.
- Docstring parameter claims vs signature parameters
- Docstring return-type claims vs annotations or observed return behavior
- Docstring behavior claims vs observable code paths

Generation: if absent, populate with a purpose statement derived from signature + body for agent-facing needs. Heavy token cost at first run, mitigated by hash caching on re-runs.

### 3. CLI Help Text

Descriptions set via `argparse.ArgumentParser(description=...)`, `argparse.add_argument(help=...)`, `click.command(help=...)`, `click.option(help=...)`.

Verification: argparse/click declarations ARE the ground truth for these. Help text that contradicts the argument's actual name or behavior is drift.

Extracted from `__main__.py` primarily; `cli.py` as graceful fallback for systems that haven't migrated.

### 4. MCP Tool Descriptions

The `description` parameter on `@mcp.tool(description="...")` decorators and the `instructions=` field on `FastMCP("name", instructions="...")` server initializations.

Verification: compare against tool function signature, registered tools in the server, and the server's domain scope.

### 5. Frontmatter `description:` Fields

YAML frontmatter `description:` on SKILL.md, rule files, convention files, pattern files. These are used by Claude Code for skill discovery and by navigator for search — high-impact drift.

Verification: SKILL.md `description:` vs the skill's actual body; rule/convention `description:` vs file purpose statement paragraph.

### 6. Frontmatter `argument-hint:` Fields

SKILL.md `argument-hint: "--target <...>"` declares accepted arguments. Must match the skill's Route section which references those arguments.

### 7. Header Purpose Statements

The first paragraph after the H1 in rule, convention, and skill markdown files. Per `markdown.md`'s Heading and Purpose Statement rule.

Verification: compare against the file's actual content scope.

### 8. Section Purpose Statements (NEW)

The first paragraph after each `##`-level heading within canonical docs. These serve two purposes:

- Purpose statement for the section itself (per multi-scale Purpose Statement guidance)
- Source for the architecture.md Contents table (a derived projection)

Verification: compare against the section's actual content — a section whose purpose statement describes "components" but contains only relationship diagrams is drift.

Generation: if a section lacks a well-formed purpose statement (single paragraph conveying scope + role), the skill flags this as an unresolved question for user rather than fabricating one.

### 9. SKILL.md Body

SKILL.md itself is a canonical doc. Inner sections (Scope, Rules, Route, Workflow) contain claims about arguments, operations, exit paths. Each is a claim subject to verification.

### 10. Rule / Convention Tables

Rules and conventions often contain tables with claims (e.g., `skill-md.md` Body Structure table lists sections with Prescribed/Common categories). Claims verifiable against the sibling conventions they describe.

## Surface Discovery

Per-system agent enumerates surfaces by:

```
1. For each .py file in system:
    1. ast.parse the file
    2. Extract module docstring → surface: module-docstring
    3. For each FunctionDef/AsyncFunctionDef at module level: extract docstring → surface: function-docstring
    4. For each ClassDef: extract class docstring + method docstrings → surface: class-docstring, method-docstring
    5. Walk for argparse setup: each add_argument call → surface: cli-help
    6. Walk for click decorators: each @click.option / @click.command → surface: cli-help
    7. Walk for @mcp.tool decorators: extract description param → surface: tool-description
    8. Walk for FastMCP(...) construction: extract instructions param → surface: server-instructions
2. For each .md file in system with YAML frontmatter:
    1. Parse frontmatter
    2. If description: present → surface: frontmatter-description
    3. If argument-hint: present → surface: frontmatter-argument-hint
    4. Extract first paragraph after H1 → surface: header-purpose-statement
    5. For each ## heading: extract first paragraph → surface: section-purpose-statement
```

## Surface Update Flow

Each surface is treated as a mini-document:

```
1. Extract claims from surface content (same prompt as full docs, but smaller input)
2. Verify each claim against fact bundle (same verification prompt)
3. Apply surgical edits via Edit tool (quote-then-replace discipline)
4. For .py files: Edit targets the docstring content between """ delimiters or the decorator's string argument
5. For frontmatter: Edit targets the YAML value after the key
```

Missing surfaces that should exist (e.g., public function with no docstring) are populated via a per-surface generation call.

## Hash Caching via Navigator

Navigator tracks file content hashes for change detection. Extension for this skill: a `doc_verified_at` marker per file recording the hash at last successful doc-verification pass.

Re-run optimization:

```
1. For each file in system:
    1. current_hash = file content hash
    2. verified_hash = navigator.get_doc_verified_at(file)
    3. children_changed = any child summary has changed since last run
    4. If current_hash == verified_hash AND not children_changed:
        - Skip fact-extraction + surface verification for this file
    5. Else:
        - Process file; on success, update navigator with new doc_verified_at = current_hash
```

This dramatically reduces re-run cost on stable codebases. First run processes everything and seeds the hash markers.

Navigator schema extension needed; v1 can ship without it and pay full token cost per run.

## Reporting

Non-obvious surfaces counted separately in the final Report per surface type:

- Module docstrings: {updated} / {created} / {verified} / {total}
- Function/method docstrings: {updated} / {created} / {verified} / {total}
- CLI help text: ...
- MCP tool descriptions: ...
- Frontmatter descriptions: ...
- Header purpose statements: ...
- Section purpose statements: ...

Section-purpose-statement count is cross-referenced with architecture.md Contents table generation — any section the skill couldn't extract a purpose for appears in unresolved questions.
