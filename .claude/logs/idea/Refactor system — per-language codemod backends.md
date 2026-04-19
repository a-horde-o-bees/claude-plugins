# Refactor System — Per-Language Codemod Backends

Future expansion for `systems/refactor/`: grow language-specific codemod subcommands as cross-language rename needs surface, and rename the existing subcommand to make its scope explicit.

## Current state

`ocd-run refactor rename-symbol` uses libcst, which is Python-only. libcst parses Python source into a concrete syntax tree that preserves formatting through round-trip, and distinguishes code from string literals and comments — that's what lets the codemod rewrite `import plugin` while leaving `"plugin.json"` untouched. The machinery does not generalize to other languages because each language's AST and parser are different.

## Rename for clarity

`rename-symbol` reads as language-neutral but the implementation is Python-exclusive. Rename to `rename-python` so the subcommand name advertises its scope honestly. This frees `rename-symbol` (or a better-named verb) for a future dispatcher that combines multiple language-specific backends for a single rename operation.

## Per-language backends

Each language gets its own subcommand backed by a parser native to that language:

- `rename-python` — libcst (current `rename-symbol`)
- `rename-js` / `rename-ts` — jscodeshift or ts-morph
- `rename-go` — gopls or `go/ast`
- `rename-rust` — rust-analyzer or syn
- `rename-json-key` — jq or a JSON AST library
- `rename-yaml-field` — ruamel.yaml (preserves formatting and comments) or similar
- `rename-toml-key` — tomlkit

Each backend understands its language's identifier semantics — imports, references, nested access — and skips string literals, comments, and unrelated tokens. Regex-based approaches fail on exactly the false-positive surface the AST-aware tools prevent.

## Unified dispatcher

A top-level rename verb (`rename`, or reclaim `rename-symbol`) accepts a `{old, new}` pair and dispatches to every applicable backend for the scope. Rationale: a real-world rename often crosses languages — renaming a Python module `plugin` → `framework` also touches YAML config keys, JSON schema fields, shell scripts, and documentation. Running each backend manually loses the "one coordinated pass" discipline the mass-rename pattern exists to enforce.

Dispatch shape sketch:

- Inspect scope for file types
- Run each backend that matches a file type in scope
- Aggregate per-backend results into a single summary
- Re-scan verification runs once across all backends

## When to build

YAGNI until a concrete cross-language rename surfaces. The Python-only backend covers the cases this repo has hit. When the first cross-language rename comes up (most likely JSON/YAML config keys referenced from Python, or a Python module whose name also appears in a shell script), build the second backend and the dispatcher together — two concrete cases are enough to justify the generic shape.

## Prerequisite

Before adding a second backend, decide the subcommand naming convention:

- `rename-<language>` (per-language) with a top-level `rename` dispatcher, or
- `rename --language <lang>` flag form

Per-language subcommands align better with Make Invalid States Unrepresentable — each subcommand accepts only flags meaningful to its backend, no accidental `--python-specific-flag` on the JS backend.
