# YAML

Indentation-based structured data format prioritizing human readability over parser strictness. Common in configuration (CI pipelines, Kubernetes manifests) and as the substrate for markdown frontmatter.

## Metadata

- **File extensions:** `.yaml`, `.yml` (both used; no community consensus)
- **MIME type:** `application/yaml` (RFC 9512, 2023)
- **Spec:** YAML 1.2 (yaml.org). YAML 1.1 is the older spec many parsers still implement, with notable differences (`no`/`yes` boolean coercion is a 1.1 quirk)
- **Primary use cases:** CI/CD configuration, Kubernetes/Docker Compose manifests, Ansible playbooks, application configs, markdown frontmatter

## Disposition

**Acceptable for frontmatter; warned for full-file YAML.** Project's heaviest use is markdown frontmatter — fine. For any code path that loads YAML, mutates it, and writes it back, **require `ruamel.yaml` round-trip mode and forbid `PyYAML.dump`**. Verified: `PyYAML` default sorts keys alphabetically and discards comments; `ruamel.yaml` round-trip preserves both. Silent comment loss across edits is a real ongoing hazard.

## Token efficiency

The most token-efficient nested structured format per the 2025 third-party benchmark — YAML's indent-and-colon syntax avoids the brace/quote tax of JSON. Won on GPT-5 Nano (62.1% accuracy) and Gemini 2.5 Flash Lite (51.9%). Not Claude-specific.

### Read-path inefficiency

YAML reads waste tokens primarily by forcing whole-document loads when only a path matters. The format has no built-in selective-access affordance; lookup of a single value at depth requires the parser to walk the document.

- **Whole-file reads for one key.** Skills frontmatter, log entries, rule headers are typically read in full because the canonical Read tool is byte-range/line-range, not path-aware.
- **Body re-emission for header-only queries.** "What's the `description` of skill X?" commonly reads the entire `SKILL.md`. Frontmatter-aware tools (`python-frontmatter`, `gray-matter`) split the file deterministically.
- **Schema discovery without affordance.** Without a schema-aware reader the agent reads sibling files to learn the shape of a YAML doc by induction. A schema-attached reader collapses that to one schema read.
- **Verbose scalars in a listing slice.** A `paths_get`-style index can surface "what files exist and their purposes" without reading every body if the purpose is in frontmatter — but only if a tool makes the projection.
- **YAML 1.1 vs 1.2 parser drift.** Silent type coercion (`country: NO` → `False`, `version: 2.0` → float) means the agent re-verifies or re-quotes, sometimes by re-reading with a different parser. Token cost is real but invisible in the file.

### Write-path inefficiency

Two costs stacked: the universal nested-format leaf-rewrite cost, plus YAML-specific comment/key-order loss across round-trip.

- **Whole-file rewrites.** An agent using a generic Edit/Write tool to change one frontmatter field commonly emits the entire file because YAML's indentation makes single-line targeting feel risky.
- **Comment loss across round-trip.** `PyYAML`'s `safe_load`/`safe_dump` cycle silently strips comments and reorders keys. Any "load, mutate, dump" tool built on PyYAML destroys human-authored structure. `ruamel.yaml` fixes this with `YAML(typ='rt')` round-trip mode, but the default Python install reaches for PyYAML first; the failure is invisible until someone notices comments are gone in the next git diff. Verified: PyYAML default `sort_keys=True`; comments documented as not-preserved across multiple sources.
- **Key-order shuffle.** Same root cause; same fix. Round-trip mode preserves insertion order. Cache-relevant: if the YAML is part of a tool definition or system prompt, key reorder invalidates Claude's prompt cache for everything downstream (Anthropic explicitly flags this for tool-use JSON; mechanism is identical for cached YAML).
- **Indentation drift on partial edits.** A regex/sed substitution at depth corrupts indentation if the replacement and original don't match exactly. AST-aware tools (`ruamel.yaml`, `yamlpath`, `yq -i`) sidestep this entirely.
- **Norway-class booleans on regeneration.** An agent rewriting `country: NO` may unquote it on the second pass, silently turning the string into `False`. `strictyaml` refuses implicit typing entirely.

The distinctive YAML write-path hazard: **silent damage outlives the edit.** JSON's brace tax is honest cost; YAML's comment-loss is invisible until later.

## LLM parse reliability

Strong when well-formed. The risk is silent type coercion under YAML 1.1 semantics — `description: no` becomes `False`, `version: 2.0` becomes a float. The model sees values correctly but downstream code may not.

## LLM generation reliability

The riskiest format to generate freehand. Indentation depth must match exactly; tabs and spaces cannot mix; long string values tempt multi-line scalar forms (`|`, `>`) that are easy to misindent. The model has no syntax checker mid-emit.

## Modification ergonomics

Weak for nested edits — changing a leaf at depth requires correctly preserving indentation, and edit tools that work on text (rather than YAML AST) can introduce subtle indent drift. Top-level keys are easier.

## Diff and human readability

Strong on both. Diffs are line-grain; the format is the most readable of the structured options for humans. This is YAML's chief reason to exist.

## Tooling and ecosystem

### Tool catalog

| Name | URL | Type | Maturity | Primary capability | Token reducer |
|---|---|---|---|---|---|
| `yq` (mikefarah) | [github.com/mikefarah/yq](https://github.com/mikefarah/yq) | CLI / Go binary | 15.3k stars; v4.53.2 (April 2026) verified | Path-based read/write across YAML/JSON/XML/TOML/CSV with in-place edit (`-i`) | Selective read avoids whole-file load; `-i` writes touch only the targeted node |
| `ruamel.yaml` | [pypi.org/project/ruamel.yaml/](https://pypi.org/project/ruamel.yaml/) | Python library | v0.19.0 (Jan 2025); the Python round-trip standard | YAML parse/emit with `typ='rt'` preserving comments, key order, quote style | Programmatic targeted edit — load tree, mutate one node, dump |
| `PyYAML` | [pypi.org/project/PyYAML/](https://pypi.org/project/PyYAML/) | Python library | The historical default; ubiquitous | YAML parse/emit | None for write path — strips comments and reorders keys (verified). **Anti-pattern for round-trip** |
| `strictyaml` | [github.com/crdoconnor/strictyaml](https://github.com/crdoconnor/strictyaml) | Python library | Active; opinionated subset | Schema-validated YAML with no implicit typing | Eliminates Norway-class re-quoting churn |
| `python-frontmatter` | [python-frontmatter.readthedocs.io](https://python-frontmatter.readthedocs.io/) | Python library | v1.0+; canonical Python frontmatter parser | Parse/dump frontmatter from markdown, returning `(metadata, body)` | Header-only access — agent reads YAML dict without body |
| `gray-matter` | [github.com/jonschlinkert/gray-matter](https://github.com/jonschlinkert/gray-matter) | JS library | Vitepress, Astro, Gatsby consume this | Same as python-frontmatter (JS) | Same role for JS consumers |
| `yamlpath` | [github.com/wwkimball/yamlpath](https://github.com/wwkimball/yamlpath) | Python library + CLI | Active; built on ruamel.yaml | Path-language (XPath-style and dot-style) get/set/merge/diff | Selective edit at depth without re-emitting parents |
| `yamllint` | [github.com/adrienverge/yamllint](https://github.com/adrienverge/yamllint) | CLI / Python | v1.38; widely packaged | Lint for syntax + cosmetic rules incl. `truthy` (Norway) | Pre-write validation reduces edit-then-verify-then-re-edit |
| `yaml-language-server` | [github.com/redhat-developer/yaml-language-server](https://github.com/redhat-developer/yaml-language-server) | LSP server | Red Hat; de-facto YAML LSP | Schema-driven autocomplete, hover, diagnostics | Schema-attached editing surface |
| `dasel` | [github.com/TomWright/dasel](https://github.com/TomWright/dasel) | CLI / Go library | v3 (Dec 2025) | Single query syntax across JSON/YAML/TOML/XML/CSV with put/delete | yq-class affordance with stricter unified syntax |
| JSON Schema for YAML | [json-schema-everywhere.github.io/yaml](https://json-schema-everywhere.github.io/yaml) | Spec / pattern | Mature | Validate YAML documents against JSON Schemas | Validate before commit eliminates write-fail-rewrite |
| K8s strategic merge patch | [kubernetes.io](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/) | Pattern | K8s ecosystem standard | Field-aware merging that knows lists vs maps vs primary-keyed sequences | Pattern, not library — the design idea reduces re-emission cost |
| `sops` | [github.com/getsops/sops](https://github.com/getsops/sops) | CLI | CNCF graduated | Encrypted YAML with selective-field encryption (`encrypted_regex`) | Tangential to token waste, but precedent for "operate on a subset of fields, leave the rest pristine" |

### Capability matrix

`✓` = supported; `~` = partial / has caveats; `✗` = not supported; blank = not applicable.

| Tool / pattern | Path read | Path write | Comment preserve | Key-order preserve | Schema validate | Frontmatter split | Multi-format | In-place edit | AST-aware |
|---|---|---|---|---|---|---|---|---|---|
| yq (mikefarah) | ✓ | ✓ | ~ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| ruamel.yaml | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | (lib) | ✓ |
| PyYAML | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | (lib) | ~ |
| strictyaml | ✓ | ✓ | ✓ | ✓ | ✓ (own schema) | ✗ | ✗ | (lib) | ✓ |
| python-frontmatter | ~ | ~ | inherits | inherits | ✗ | ✓ | ✗ | (lib) | ~ |
| yamlpath | ✓ | ✓ | ✓ | ✓ | ~ | ✗ | ~ | ✓ | ✓ |
| yamllint | ✗ | ✗ | n/a | n/a | ~ (rules, not JSON Schema) | ✗ | ✗ | ✗ | ~ |
| yaml-language-server | ~ | ✗ | n/a | n/a | ✓ | ✗ | ✗ | ✗ | ✓ |
| dasel | ✓ | ✓ | ~ | ~ | ✗ | ✗ | ✓ | ✓ | ✓ |

Two reads:

1. Strongest comment+key-order preservation lives in `ruamel.yaml`, `strictyaml`, `yamlpath` (built on ruamel), and `tree-sitter-yaml`. These are libraries — they need wrapping to be agent-callable.
2. Strongest agent-callable surfaces (CLI, MCP) are `yq`, `dasel`, frontmatter CLIs, and generic file-edit MCP servers. None is purpose-built for YAML+frontmatter+round-trip-perfect editing in one package.

### Recommended starter set

This project's YAML use is dominated by markdown-frontmatter on `SKILL.md`, log entries, rules, conventions. The starter set matches that profile.

1. **`python-frontmatter` for header-only operations.** When agent or plugin code reads/writes only frontmatter (`description`, `argument-hint`, `log-role`), `python-frontmatter` is the right reach. Parse returns `(metadata_dict, body_str)`; the agent never has the body in its response. For writes, `dumps(post)` re-emits the file with new frontmatter and the body untouched.
2. **`ruamel.yaml` (round-trip mode) as the YAML library backing any plugin code that mutates YAML.** The default Python install reaches for `PyYAML`; this is a footgun for any code path that loads, mutates, and writes back. Set the project default to `ruamel.yaml` with `YAML(typ='rt')` and forbid `PyYAML.dump` in code review.
3. **`yq` (mikefarah) as the agent-allowlist CLI for ad-hoc YAML queries.** When the agent reads a value out of a non-frontmatter YAML file, `yq '.path.to.key' file` is the smallest token surface. Caveat: yq's comment-preservation has had regressions across history (issues #2516 Nov 2025, #2592 Feb 2026, #497, #524, #127); for production write paths, prefer `ruamel.yaml`.

Worth knowing as next steps: JSON Schema validation against frontmatter (turns "write, fail, re-write" into "validate-pre-write"); `yamllint` in pre-commit (catches Norway-class booleans before they hit the file).

### Gaps

- **MCP server for frontmatter-only operations.** No MCP server found that exposes "read frontmatter dict / write frontmatter field" as a tool. A purpose-built one backed by `python-frontmatter` would be small and would close the dominant read-path gap directly.
- **MCP server for round-trip-safe YAML edits.** No found MCP server wraps `ruamel.yaml` or `yamlpath`. yq has CLI surface but isn't packaged as an MCP server; file-edit MCP servers don't preserve comments.
- **Schema-validated frontmatter at the project boundary.** The project has frontmatter conventions (`log-role` enum, skill `description` requirements) but no JSON Schema attached at the file level. Plumbing exists (jsonschema for Python, yaml-language-server for editors); schemas don't.
- **Strategic-merge-patch for non-K8s YAML.** The K8s pattern (declare merge keys; merge at field/list-element level) lives inside `kubectl`/`kustomize`. No general-purpose library found that lets a project declare merge keys for arbitrary YAML.
- **Cache-impact guidance for YAML.** Anthropic's prompt-caching docs note key-order matters for tool-use JSON. No documented analog for cached YAML.

## Random access and queryability

Weak. Like JSON, lookup requires whole-file parse. `yq`/`dasel`/`yamlpath` enable ad-hoc query. `python-frontmatter` makes the frontmatter slice cheap.

## Scale ceiling

Painful past ~3 levels of nesting (indentation gets visually unmanageable). Single-file YAML degrades at the megabyte scale.

## Failure mode

Two-mode: syntax errors fail loudly (parser refuses); type coercion fails silently (parser accepts but produces a different type). Silent failures are YAML's distinguishing hazard.

## Claude-specific notes

- No Anthropic guidance specifically endorses or rejects YAML.
- Heavily used in the Claude Code ecosystem via markdown frontmatter for skill descriptors and log entries — convention, not prescription.
- The cache-invalidation parallel from Anthropic's prompt-caching tool-use JSON guidance is mechanism-based inference, not a documented Anthropic claim about YAML.

## Pitfalls and anomalies

- YAML 1.1 boolean coercion: `yes`, `no`, `on`, `off` become booleans unless quoted (Norway Problem: `country: NO` becomes `False`)
- Tabs are not permitted as indentation (spaces only); editors that auto-insert tabs break files silently
- Multi-line scalars (`|` literal, `>` folded) are commonly misused
- Anchors and aliases (`&`, `*`) introduce a referencing system most users never need
- Comments are preserved by `ruamel.yaml` but stripped by `PyYAML` — round-trip safety depends on the parser (verified)

## Open questions

- Does Claude have a measurable preference for YAML over JSON for nested config? The ImprovingAgents benchmark suggests yes for smaller models, but Claude wasn't tested.
- Is there a token-cost or cache-invalidation cost when YAML key order shuffles in cached prompt prefixes (mechanism inferred but not measured)?
- What's the recommended escape from full-file YAML when frontmatter grows nested — sidecar JSON, or escalate to TOML?

## Sources

- [yaml.org — YAML 1.2 spec](https://yaml.org/spec/1.2.2/)
- [yq (mikefarah) — GitHub](https://github.com/mikefarah/yq) — verified 15.3k stars, v4.53.2
- [yq comment-preservation regression issues](https://github.com/mikefarah/yq/issues?q=is%3Aissue+comment+preservation) — #2516, #2592, #497, #524, #127
- [ruamel.yaml — PyPI](https://pypi.org/project/ruamel.yaml/) — round-trip mode preserves comments + key order (verified)
- [PyYAML default behavior](https://pyyaml.org/wiki/PyYAMLDocumentation) — `sort_keys=True` default, no comment preservation (verified)
- [strictyaml — GitHub](https://github.com/crdoconnor/strictyaml)
- [The Norway Problem — HitchDev](https://hitchdev.com/strictyaml/why/implicit-typing-removed/)
- [python-frontmatter — Read the Docs](https://python-frontmatter.readthedocs.io/)
- [yamlpath — GitHub](https://github.com/wwkimball/yamlpath)
- [Red Hat yaml-language-server](https://github.com/redhat-developer/yaml-language-server)
- [dasel — GitHub](https://github.com/TomWright/dasel) — v3 Dec 2025
- [Kubernetes — kubectl strategic merge patch](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/update-api-object-kubectl-patch/)
- [JSON Schema Everywhere — YAML](https://json-schema-everywhere.github.io/yaml)
- [Anthropic — Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Anthropic — Tool use with prompt caching](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-use-with-prompt-caching)
