# Markdown

Lightweight prose-with-structure format that renders to HTML. Primary text format for documentation, agent-facing instructions, and human-readable structured content.

## Metadata

- **File extensions:** `.md`, `.markdown`
- **MIME type:** `text/markdown` (RFC 7763)
- **Spec:** CommonMark (commonmark.org), GitHub Flavored Markdown (GFM), MultiMarkdown — multiple competing specs, CommonMark is the closest to canonical
- **Primary use cases:** README files, documentation, prose with light structure (headings, lists, code blocks, tables), LLM-facing instructions

## Disposition

**Endorsed** — default format for prose-first content where structure is light. Skills, rules, conventions, log entries, READMEs, ARCHITECTURE docs.

## Token efficiency

Minimal delimiter overhead — `#` for headings, `-` for list items, backticks for code. Per the third-party 2025 nested-data benchmark, Markdown was 34-38% cheaper in tokens than JSON for the same data on the tested non-Claude models. Not Claude-specific.

### Read-path inefficiency

Markdown is prose-with-structure, but the structure is invisible to the consumer until parsed. Concrete waste modes when an agent works against markdown without help:

- **Whole-file read for one section.** A 4000-line skill or research doc gets loaded in full when only the section under one `## heading` is needed. Claude Code's `Read` defaults to a 2000-line cap and 25k-token-per-call ceiling — guardrail, not affordance. Hitting the cap forces offset/limit pagination by line number, which presupposes knowing the right line, which presupposes having read once.
- **Whole-file read for metadata only.** Frontmatter is the most common structured slice — `description`, `log-role`, `model`. Reading the whole file to learn one frontmatter key is the worst-case ratio.
- **Whole-file read to enumerate structure.** "What sections does this file have" is answered by the heading tree, not the body. No built-in tool surfaces tree-only views.
- **Re-emission as tool output.** MCP servers that return raw markdown for inspection tasks ("does this file mention X?") when a boolean answer plus matching line numbers would suffice bill tokens twice.
- **Cross-file searches that emit hits as full files.** Without context-controlled grep, the consumer either gets too little (just paths) or too much (whole files); the right answer is hits with N lines of surrounding context.

### Write-path inefficiency

The token tax on writes is the agent re-emitting context just to land an edit:

- **Whole-file rewrites for one-line changes.** Models without a partial-edit tool emit the full document with one line changed. This is the failure mode `str_replace_based_edit_tool` was designed to eliminate.
- **Section-level rewrites when an inline edit suffices.** Without a section-targeting affordance, the agent re-emits a `## heading` block to land a one-sentence change inside it.
- **Frontmatter rewrites for one key change.** Rewriting the whole frontmatter to flip `log-role: queue` to `log-role: reference` re-emits every other key.
- **Indentation cascades.** Editing a nested list item under a parent often reflows neighbors when spaces miscount; the safe move is re-emitting the parent block.
- **Multi-file mass edits without a codemod.** Renaming a heading across 20 files via 20 individual `str_replace` calls carries per-call boilerplate; AST-aware codemods compress this to one operation.

## LLM parse reliability

Excellent for prose-with-structure. LLMs handle markdown natively because their training corpora are markdown-heavy. Headings, lists, and tables are interpreted reliably; nested deeply-indented lists become harder to track past 3-4 levels.

## LLM generation reliability

Among the most reliable formats for LLM output — no closing tokens to match, no indentation to count, malformations are tolerated by readers. Tables are the one weak point: column alignment is easy to break.

## Modification ergonomics

Line-oriented — single-line edits are tight, section appends are trivial, Edit-tool replacements rarely cascade. The flat structure means the model can edit a heading without re-emitting the document.

## Diff and human readability

Strong on both. Diffs are line-grain and easy to review. Renders attractively in IDEs, GitHub, and terminal viewers (`mdcat`, `glow`).

## Tooling and ecosystem

### Tool catalog

| Name | URL | Type | Maturity | Primary capability | Token reducer |
|---|---|---|---|---|---|
| Anthropic text-editor (`str_replace_based_edit_tool`) | [platform.claude.com](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool) | First-party tool spec | `text_editor_20250728` per Anthropic docs (verified) | `view`/`str_replace`/`create`/`insert` against any text file | Whole-file rewrites collapse to one `old_str`/`new_str` pair; `view_range` reads slices |
| `mdq` | [github.com/yshavit/mdq](https://github.com/yshavit/mdq) | CLI (Rust, jq-for-markdown) | v0.10.0 dated 2026-03-22 (verified) | Filter-based selection over CommonMark elements (sections, lists, tables, links, frontmatter, code blocks) | Returns only matched elements; JSON output for chaining |
| `mq` | [github.com/harehare/mq](https://github.com/harehare/mq) | CLI + LSP (Rust) | v0.5.27 (April 2026), 410 stars (verified). Project lists "mcp" as a topic but `mq-mcp` as a separate component is not separately confirmed | jq-style query language for markdown ASTs | Selects substructures rather than emitting full files |
| `cyanheads/obsidian-mcp-server` | [github.com/cyanheads/obsidian-mcp-server](https://github.com/cyanheads/obsidian-mcp-server) | MCP server (Obsidian-specific) | Version 3.1.0 | 14 tools: `obsidian_get_note` with section/document-map views, `obsidian_patch_note` (heading/block-ref-anchored), `obsidian_manage_frontmatter` (atomic per-key) | Document-map view returns heading tree alone; patch operations target a heading anchor |
| `safurrier/mcp-filesystem` | [github.com/safurrier/mcp-filesystem](https://github.com/safurrier/mcp-filesystem) | MCP server (filesystem-agnostic) | Active | `read_file_lines`, `head_file`/`tail_file`, `grep_files` with `-A/-B/-C` context, `edit_file_at_line` | Line-targeted reads; grep with context windows; line-anchored edits skip unique-string requirement |
| LangChain `MarkdownHeaderTextSplitter` | [docs.langchain.com](https://docs.langchain.com/oss/python/integrations/splitters/markdown_header_metadata_splitter) | Python library (RAG chunking) | Part of LangChain core | Splits markdown into chunks keyed by heading hierarchy | Retrieval returns one heading-bounded chunk |
| `python-frontmatter` | [github.com/eyeseast/python-frontmatter](https://github.com/eyeseast/python-frontmatter) | Python library | v1.0.0; widely adopted in Jekyll/Hugo/Pelican | `frontmatter.parse(text)` returns `(metadata_dict, body_str)` | Read frontmatter without parsing the body |
| `remarkjs/remark` | [github.com/remarkjs/remark](https://github.com/remarkjs/remark) | JavaScript library (markdown AST) | 150+ plugin ecosystem | Parse markdown to mdast AST, mutate, serialize back | Programmatic mutation of subtrees instead of LLM-emitted rewrites |
| Pandoc Lua filters | [pandoc.org/lua-filters.html](https://pandoc.org/lua-filters.html) | CLI + filter API | Long-lived | Element-typed AST traversal with mutation | Out-of-band programmatic transforms |
| `mistletoe` / `marko` | [mistletoe](https://github.com/miyuchina/mistletoe) / [marko](https://github.com/frostming/marko) | Python libraries | Active | AST traversal with custom token extension | Programmatic structural extraction |

### Capability matrix

| Tool | Slice load | Tree-only view | Frontmatter-only access | Section-targeted read | Section-targeted write | Leaf-targeted write | Cross-file query |
|---|---|---|---|---|---|---|---|
| Anthropic text-editor | `view` with `view_range` | — | — (line-range only) | — (string match) | — (string match) | `str_replace` (must be unique) + `insert` | — |
| `mdq` | Filter selects matched | Section filters via `# title` | `front matter` selector | `# heading` filter, regex on title | — (read-only) | — | Stdin-piped multi-file via shell glob |
| `mq` | jq-style query selects sub-AST | Heading-tree extraction | Frontmatter selector | Heading-keyed sub-AST | Transform-and-emit via mq lang | — | Yes (built for batch) |
| Obsidian MCP server | `section` view | `document-map` view | `manage_frontmatter` get/set/delete | `section` view | `obsidian_patch_note` at heading | `obsidian_replace_in_note` | `obsidian_search_notes` |
| `safurrier/mcp-filesystem` | `read_file_lines` offset/limit | — | — | — (line-anchored) | — | `edit_file_at_line` replace/insert/delete | `grep_files` with `-A/-B/-C` |
| `python-frontmatter` | Parse splits header from body | — | `frontmatter.parse(text)` | — | — | — | — |

### Recommended starter set

For this project (Claude Code plugins, markdown-heavy skill/rule/log content):

1. **Lean on `str_replace_based_edit_tool` discipline as the default write path.** Claude Code's `Edit` already implements this shape. Discipline: pick `old_str` long enough to be unique and short enough to avoid re-emission of unchanged context. The mitigation for multiple-match errors is a smaller unique anchor, not a wider one.
2. **Adopt `mdq` as a bash CLI for read-path slicing.** Single Rust binary, easy to allowlist. Use cases: heading-tree view of a long file, cross-file frontmatter queries via shell glob, single-section extraction from a long ARCHITECTURE.md.
3. **Keep `python-frontmatter` for in-process frontmatter work.** Already conventional; lets verbs touch frontmatter without paying for body parse.

Deliberately not in the starter set: `remark`/`unified` (JavaScript; project is Python-first), Obsidian MCP server (vault-bound), LangChain header splitter (no embedding store in project), Pandoc/marko/mistletoe (out-of-band batch transforms; project's edits are mostly in-loop).

### Gaps

- **Heading-anchored str_replace** as a first-class operation. The Obsidian server has the closest analog (`obsidian_patch_note`) but is vault-bound. No format-agnostic MCP server surveyed exposes this for plain markdown.
- **Frontmatter-key edits as a single tool call.** Atomic per-key writes don't exist as a generic markdown-aware MCP tool.
- **Multi-file structural codemods.** A markdown-AST equivalent to `/ocd:refactor` (libcst-based) doesn't exist in surveyed tooling.
- **Tree-only view as a first-class read.** No "give me only the heading tree" mode in Claude Code's `Read`. `mdq` plus a heading filter approximates it.
- **Section-aware diff.** Available diff is line-based; no semantic markdown diff (heading-keyed) in surveyed tools.

## Random access and queryability

Weak natively — to find a specific section the consumer parses the whole file. `grep` works for content search; structural queries require an AST parser. `mdq` and `mq` close this gap when allowlisted as bash CLIs.

## Scale ceiling

Practical ceiling around the LLM's context window — files past ~10K lines become hard to load entirely. Splitting into multiple files is the standard escape valve.

## Failure mode

Silent and prose-tolerant. A malformed list still renders as something the reader can decode. Excellent for human consumption; risky when machine consumers expect a specific structure.

## Claude-specific notes

- No Anthropic guidance specifically prescribes or rejects markdown for storage. Anthropic's prompt-engineering docs treat markdown as a normal substrate; XML tags are the recommended structural delimiter inside prompts (see `samples/xml.md`).
- The text editor tool (`str_replace_based_edit_tool`, version `text_editor_20250728`) is the canonical first-party shape for markdown writes — verified at [platform.claude.com](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool). Claude Code's `Edit` mirrors it.

## Pitfalls and anomalies

- Multiple competing specs (CommonMark vs GFM vs MultiMarkdown) — table syntax, task-list syntax, footnote syntax differ
- Nested code fences require backtick-count escalation
- Indented blocks under list items must align consistently or the renderer reparents them
- Headings inside lists are commonly misrendered

## Open questions

- Are there Claude-specific token efficiency measurements for markdown vs JSON storage?
- Does Claude have a measurable preference between markdown tables and markdown KV-pair lists, as the GPT-4.1-nano benchmark showed?
- What's the practical ceiling for Claude reading large markdown files (>5K lines) compared to splitting?
- Is `mq-mcp` a separately-installable MCP server or only a topic tag on the parent `mq` repo?
- Would a heading-anchored `str_replace` MCP tool (the Obsidian shape generalized) be a worthwhile project investment?

## Sources

- [Anthropic text editor tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool) — `str_replace_based_edit_tool`, `text_editor_20250728`
- [github.com/yshavit/mdq](https://github.com/yshavit/mdq) — verified v0.10.0 (2026-03-22), Rust binary
- [github.com/harehare/mq](https://github.com/harehare/mq) — verified v0.5.27 (April 2026), 410 stars
- [github.com/cyanheads/obsidian-mcp-server](https://github.com/cyanheads/obsidian-mcp-server) — Obsidian MCP server, 14 tools
- [github.com/safurrier/mcp-filesystem](https://github.com/safurrier/mcp-filesystem) — line-targeted filesystem MCP
- [docs.langchain.com — Markdown header splitter](https://docs.langchain.com/oss/python/integrations/splitters/markdown_header_metadata_splitter) — header-bounded chunking
- [github.com/eyeseast/python-frontmatter](https://github.com/eyeseast/python-frontmatter) — frontmatter parse/write split
- [improvingagents.com — table format benchmark](https://www.improvingagents.com/blog/best-input-data-format-for-llms/) — markdown KV vs CSV (non-Claude)
- [improvingagents.com — nested data format](https://www.improvingagents.com/blog/best-nested-data-format/) — markdown 34-38% cheaper than JSON in tokens (non-Claude)
