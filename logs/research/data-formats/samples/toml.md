# TOML

Section-based configuration format designed for explicit semantics and human readability. Standard for Python project metadata (`pyproject.toml`), Rust's `Cargo.toml`, and many language ecosystems' config files.

## Metadata

- **File extensions:** `.toml`
- **MIME type:** `application/toml` (de facto)
- **Spec:** TOML 1.0.0 (toml.io), released 2021. Versions back to 0.x had breaking changes; current spec is stable
- **Primary use cases:** Python project metadata (`pyproject.toml`, PEP 518/621), Rust crate manifests (`Cargo.toml`), application config where explicit typing matters, anywhere YAML's silent-coercion hazards are unacceptable

## Token efficiency

Comparable to YAML for flat data; less efficient than YAML for deeply nested data because TOML uses dotted-key or table-array syntax rather than indentation. For typical config-file workloads (mostly flat with shallow grouping) the difference is negligible.

## LLM parse reliability

Strong. TOML's syntax is unambiguous and types are explicit (no boolean coercion of bareword strings). What the LLM sees in the text is what the parser produces.

## LLM generation reliability

Acceptable. The most common error mode is malformed section headers (`[tool.pytest.ini_options]`) — bracket matching and dot-path correctness must be tracked. Within sections, `key = value` lines are simple and reliable.

## Modification ergonomics

Section-grain edits are tight. Changing a value within a section is a single-line edit. Cross-section refactors (moving a key from one section to another) are harder because section context matters.

## Diff and human readability

Strong on both. Section headers create natural visual chunks; line-grain diffs are easy to review.

## Tooling and ecosystem

Standardized in the Python ecosystem via `pyproject.toml` (PEP 518, PEP 621) — every modern Python project uses TOML for build/dependency declaration. Parsers are universal (`tomllib` in Python 3.11+ stdlib, `toml` and `tomli` for older Python, `toml` crate in Rust, `@iarna/toml` in JS).

## Random access and queryability

Weak — like JSON and YAML, lookup requires whole-file parse. `tq` (toml-query) and `tomlq` exist but are less mature than `jq`/`yq`.

## Scale ceiling

Not designed for large data files. Past a few hundred lines, the section-based structure becomes hard to navigate. For large structured data, JSON or SQLite is appropriate.

## Failure mode

Loud parse errors with line/column reporting. Type strictness eliminates the silent-coercion class of bugs YAML carries.

## Claude-specific notes

No Anthropic guidance specific to TOML. Used in this project for `pyproject.toml` and pytest config under `[tool.pytest.ini_options]`. The choice is ecosystem convention.

## Pitfalls and anomalies

- Inline tables (`{ key = value, ... }`) and nested tables (`[a.b.c]`) can express the same data; mixing styles in one file is confusing
- Array-of-tables syntax (`[[items]]`) is uncommon enough that authors and reviewers misread it
- Multiline strings (`"""..."""`, `'''...'''`) have whitespace-handling rules similar to YAML's `|`/`>`, with similar misuse risk
- The dotted-key syntax (`a.b.c = "v"`) creates ambiguity with section headers (`[a.b.c]`) — both forms are valid and produce the same result, but mixing them is confusing
- TOML 0.x parsers may still be deployed and have spec differences

## Open questions

- Has Anthropic published any guidance on TOML for prompt or tool definitions? (Not found.)
- Is there a Claude-specific token-efficiency comparison between TOML, YAML, and JSON for the same flat config data?
- What's the conventional escape from TOML when configuration grows past the format's comfort zone — split into multiple TOML files, or migrate to JSON?
