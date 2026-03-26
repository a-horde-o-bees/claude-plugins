# Criteria

Convention and best-practice criteria for judgment-based review. Agent evaluates assigned categories across scope. Deterministic checks (type checking, linting, reference validation) belong in separate tooling.

## Unnecessary Indirection

- Pass-through wrappers that call single command and return output without adding value
- Extra abstraction layers for one-time operations
- Wrapping composed sequences already handled by existing tools

## Redundant Operations

- Pre-checking state before calling function that already checks internally
- Back-to-back commands where first is subset of second
- Duplicate logic across multiple scripts for same operation

## Scattered Responsibility

- Same type of operation split across multiple scripts
- Skill steps assembling multi-step sequences that should be single CLI call
- Ad-hoc shell commands in skills when CLI wrapper exists for that tool

## Convention Violations

- Wrong naming convention for file type
- Inconsistent error handling or exit code patterns within same scope
- Safety anti-patterns: mutable default arguments, bare exception clauses, missing context managers
- Missing or inconsistent type hints on public APIs

## Cargo-Cult Patterns

- Copying pattern from one context where it made sense into another where it does not
- Applying rule broadly when it was scoped to specific situation
- Backwards-compatibility shims or renamed variables for removed code

## Naming and Discoverability

- Names that do not convey enough to find or understand without reading implementation
- Inconsistent terminology for same concept across files
- Functions with hidden side effects not reflected in name or docstring

## Error Handling and Failure Semantics

- Bare or overly broad exception catching that swallows diagnostic information
- Error messages that do not identify what failed, where, or what to do about it
- Missing exit codes or exit codes that do not distinguish failure types
- No graceful degradation — partial failures cause full operation abort without cleanup

## Security and Input Validation

- Unsanitized external input passed to shell commands, file paths, or queries
- Hardcoded credentials, tokens, or secrets in source code
- Missing input validation at system boundaries (user input, API responses, file contents)

## Structural Readiness

- Code that has grown beyond single file's natural scope but has not been split
- Functions doing multiple unrelated things (low cohesion)
- Missing boundary definitions (no clear interface between layers)
- Destructive operations without confirmation guards; commands not safe to re-run

## Dependency Direction

- Lower layers importing from or depending on higher layers
- Shared libraries referencing project-specific concepts
- Circular dependencies between modules
- Stable modules depending on frequently-changing modules

## Complexity and Cohesion

- Functions with high cognitive complexity — deeply nested conditionals, multiple break/continue paths
- Mixed abstraction levels within single function
- Multiple functional seams in single file that should be separated based on functional boundaries
- Parameter lists that bundle unrelated concerns

## Output and Format Anti-patterns

- CLI producing output in different format than underlying tool
- Inconsistent output conventions within same CLI
- Exit codes that do not distinguish success from failure
- Dumping full output by default when progressive disclosure is more appropriate

## Stale Artifacts

- Documentation referencing removed functions, old output formats, or deprecated patterns
- Dead imports, unused functions, or variables left after refactoring
- Documentation that does not match current implementation

## Agent Ergonomics

- Available commands or operations not surfaced at boundary
- Missing or incomplete CLI help text that agents depend on for discovery
- No navigator entry for file that agents are expected to use
- Functions with excessive parameter counts

## Project Architecture

Evaluate structural decisions that span entire project. These patterns are invisible to per-directory agents because they emerge from relationships between units. Only included for `project` scope.

- Libraries not installable via standard tooling, relying on runtime hacks that break static analysis
- Imports not resolvable by standard tools without workarounds
- Structural decisions that require per-tool workarounds to function with standard toolchain
- Dependencies declared in formats that tooling cannot consume
- Non-standard setup steps that require tribal knowledge
- Seams between units that rely on convention and runtime behavior not enforced by language or tooling
