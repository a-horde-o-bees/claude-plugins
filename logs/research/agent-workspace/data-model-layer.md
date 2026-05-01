# Data model layer

Landscape survey of how panel-organized agent workspaces structure their content — the unit-of-content abstraction beneath the UI. Scope is the data model only: how content units are identified, persisted, mutated, and exposed to AI agents. Sibling layers (synchronization, transport, UI binding) appear only where they constrain the data model itself.

This is a focused survey of options the user could adopt, extend, or borrow from rather than reinvent. The goal upstream is reducing the risk of building something an existing project already provides.

## Landscape survey

### Cell-based notebooks

**Jupyter** (covered in background). Stable cell IDs landed in nbformat 4.5 via [JEP 62](https://jupyter.org/enhancement-proposals/62-cell-id/cell-id.html) — `id` is required on every cell, alphanumeric plus `-` and `_`. JupyterLab persists the IDs across saves. The unit is a typed cell (code, markdown, raw); mixed content is the format's defining feature. Sync via Yjs through [jupyter-collaboration](https://github.com/jupyterlab/jupyter-collaboration) and `jupyter_ydoc`. AI integration through [jupyter-ai](https://github.com/jupyterlab/jupyter-ai) v3.0.0 (April 2026, BSD-3, ~4.2k stars) supports Claude, Codex, Copilot, Gemini, Goose, Kiro, Mistral Vibe, OpenCode through a built-in MCP server and the Agent Client Protocol — agents read and write notebooks, run terminal commands, with a permission system gating writes and executions ([repo](https://github.com/jupyterlab/jupyter-ai)). Self-host: trivial (the Jupyter server is self-hosted by default).

**Marimo** ([marimo.io](https://marimo.io/), [GitHub](https://github.com/marimo-team/marimo)). 20.7k stars, v0.23.4 (April 28, 2026), Apache-2.0. Reactive Python notebook stored as **pure Python**, not JSON — every cell is a function decorated `@app.cell`, so the file is git-friendly and importable as a module. Stable cell IDs are the subject of [issue #3177](https://github.com/marimo-team/marimo/issues/3177) — currently positional/derived; an opt-in stable `id` parameter on the cell decorator is the proposed direction. Mixed content: code cells, markdown cells (markdown is a Python f-string under the hood). AI integration is unusually mature — `marimo agents` runs AI agents as **first-class cells**, and `marimo pair` lets external agents (Claude Code, Gemini, Codex, OpenCode) read variables, test logic in a scratchpad, run cells, add and remove cells, and manipulate UI elements through ACP ([Agent Client Protocol](https://docs.marimo.io/guides/editor_features/agents/), [Marimo Agents PyPI](https://pypi.org/project/marimo-agents/)). Sync: file-based; reactivity is the dataflow graph the runtime computes from AST analysis. Self-host: trivial.

**Observable Notebooks 2.0 / Notebook Kit** ([notebook-kit](https://observablehq.com/notebook-kit/system-guide), [observablehq/notebook-kit](https://github.com/observablehq/notebook-kit)). 2.0 abandons the prior closed JSON format for HTML-with-cells, ISC-licensed and open. Cells carry an optional positive-integer `id` attribute giving stable identity for editing. Mixed content: JavaScript, SQL, Markdown, HTML cells, plus Python/R/Node data loaders. Sync: file-based, reactive runtime computes the dependency DAG. AI integration: not yet found in the open Notebook Kit codebase (Observable's hosted product has its own AI; not part of the open-source kit). Self-host: yes via the open-source kit + Observable Desktop.

**Quarto** ([quarto.org](https://quarto.org/)). Multi-language scientific publishing, BSD-2-Clause. `.qmd` files are markdown with YAML frontmatter and code chunks; chunks are typed by language (`{python}`, `{r}`, `{julia}`, `{ojs}`). Engines: knitr, Jupyter, Observable. Stable per-chunk identifiers: `label:` chunk option (optional, human-authored), not auto-assigned UUIDs. AI integration: not a first-class feature; users invoke AI tooling through Jupyter/RStudio editors that wrap Quarto. Self-host: trivial (CLI tool, file-based).

**Pluto.jl** ([plutojl.org](https://plutojl.org/), [GitHub](https://github.com/JuliaPluto/Pluto.jl)). 5.3k stars, v0.20.24 (March 2026), MIT. Reactive Julia notebooks saved as pure Julia. Each cell carries a UUID embedded in a comment — `# ╔═╡ <uuid>` delimiters separate cells in the file, giving stable identity that survives reordering. Mixed content: Julia code cells with markdown supported via `md"..."` literals (single content type at the storage level; presentation is per-cell). AI integration: not yet found as a first-class feature. Self-host: trivial.

**Polynote** ([polynote.org](https://polynote.org/), [GitHub](https://github.com/polynote/polynote)). Netflix's polyglot notebook (Scala + Python + SQL with Apache Spark integration). Open-sourced 2019. Activity since: search results don't surface 2025-2026 releases — directional signal of dormancy, not confirmed archived. From training data, may be stale: project status is unverified for current viability. Recommendation: treat as historical reference, not adoption candidate.

**Apache Zeppelin** ([zeppelin.apache.org](https://zeppelin.apache.org/), [GitHub](https://github.com/apache/zeppelin)). Web-based notebook with the **interpreter abstraction** as the architectural standout — each paragraph is associated with a named interpreter (Spark, SQL, Python, Scala, Markdown, etc.) running in a shared JVM group. The interpreter pattern is the most relevant lesson for an agent-orchestrated workspace where panel types map to handlers. Mixed content: yes by interpreter. AI integration: not yet found as a first-class feature. Adoption: strongest in Big Data / Spark contexts; Jupyter dominates the broader notebook market.

**Databricks notebooks**. Closed proprietary platform, source unavailable. Architecturally informative: cells with magic-prefix language switching (`%python`, `%sql`, `%scala`, `%md`), tightly integrated with Delta Lake and Spark. From training data, may be stale: not a candidate for adoption — listed for completeness.

### Block editor frameworks

**ProseMirror** ([prosemirror.net](https://prosemirror.net/)). The schema-driven document model underlying most modern rich-text editors. Documents are trees of typed nodes against an explicit schema; marks attach to nodes for inline formatting. Position-based addressing means **no native stable node IDs** — y-prosemirror adds them via Yjs CRDT, and editors built on top (Tiptap, BlockNote) layer their own ID plugins. Mixed content: yes via custom node types. AI integration: not at the framework level — left to the application. Self-host: not applicable; library.

**Tiptap** ([tiptap.dev](https://tiptap.dev/), [GitHub](https://github.com/ueberdosis/tiptap)). 35.2k stars, MIT. Headless wrapper over ProseMirror with a clean extension API. Node IDs come from the official `UniqueID` extension or `y-prosemirror`'s CRDT IDs when collaboration is on. Sync: Yjs via `@tiptap/y-tiptap`, with Hocuspocus as the recommended backend. Mixed content: yes — extensions register custom nodes. AI integration: Tiptap has shipped Tiptap AI as a hosted product; the framework itself remains AI-agnostic.

**Lexical** ([lexical.dev](https://lexical.dev/), [GitHub](https://github.com/facebook/lexical)). 23.0k stars, MIT. Meta's editor framework powering Facebook, Instagram, WhatsApp Web. Tree of typed nodes (`ElementNode`, `TextNode`, `DecoratorNode`); `DecoratorNode` is the escape hatch for arbitrary React/DOM widgets. Each node carries a key, but keys are session-local — not stable across reloads without an application-supplied ID layer. Sync: `@lexical/yjs` for Yjs collaboration. Mixed content: yes. AI integration: framework-agnostic.

**BlockNote** ([blocknotejs.org](https://www.blocknotejs.org/), [GitHub](https://github.com/TypeCellOS/BlockNote)). MPL-2.0 (XL packages GPL-3.0 / commercial). Block-based React editor on top of Tiptap/ProseMirror. Stable block IDs are first-class — the Unique ID plugin coordinates with y-sync transactions to avoid double-assignment ([Yjs integration deepwiki](https://deepwiki.com/TypeCellOS/BlockNote/8.1-yjs-integration)). Mixed content: yes — Notion-style blocks (paragraph, heading, list, image, table, custom). Sync: Yjs first-class with Liveblocks, PartyKit, Y-Sweet providers. Upcoming Yjs 14 work brings attributed version history and track changes ([FOSDEM 2026 talk](https://fosdem.org/2026/schedule/event/8VKQXR-blocknote-yjs-prosemirror/)). AI integration: [blocknote-llm](https://github.com/numerique-gouv/blocknote-llm) is a community PoC of in-browser LLM editing through the BlockNote API; not a shipped feature of BlockNote core.

**Slate** ([docs.slatejs.org](https://docs.slatejs.org/)). MIT. Schema-loose tree model — only `children` is required on element nodes; everything else, including IDs, is developer-defined. Sync: `slate-yjs` for Yjs binding. Mixed content: yes by convention. AI integration: framework-agnostic.

**Editor.js** ([editorjs.io](https://editorjs.io/)). Apache-2.0. Block-style editor with **clean JSON output** as the explicit selling point — every block is `{id, type, data}`, with the `id` a short alphanumeric like `oUq2g_tl8y` retrievable via `editor.blocks.getById()`. Mixed content: yes via block tools. Sync: not built-in (no Yjs binding shipped); state is per-client. AI integration: not at framework level. The clean JSON shape makes it the most agent-legible block format among the editor frameworks — but absence of CRDT sync is a step down for collaboration.

**Quill** ([quilljs.com](https://quilljs.com/)). BSD-3. Delta-based editor (operations, not nodes). No node IDs — Deltas are flat operation sequences. Mixed content: limited. Reasonable choice for simple rich-text panels, weak fit for the agent-as-block-participant pattern.

**BlockSuite** ([blocksuite.io](https://blocksuite.io/), [GitHub](https://github.com/toeverything/blocksuite)). 5.8k stars, v0.22.4 (July 2025), MPL-2.0. Underlies AFFiNE. **Native Yjs from the ground up** — every Doc is a Yjs subdocument; every block is a Yjs map; props are Yjs types ([CRDT-Native Data Flow](https://block-suite.com/blog/crdt-native-data-flow.html)). Block model is the abstraction layer that hides Yjs from typical block-author code while keeping CRDT semantics as the single source of truth. Mixed content: yes — text, rich text, custom blocks, inline embeds, database/table blocks, media. Sync: Yjs; subdoc-per-Doc gives fine-grained loading. AI integration: BlockSuite itself ships no AI; AFFiNE (its consumer) does, with multi-provider support including Claude. Self-host: yes (the framework is a JS library; AFFiNE Community Edition is MIT and self-hostable).

**Notion editor**. Closed. Architecturally informative: every content unit is a block with a UUID v4, stored in PostgreSQL on RDS partitioned by workspace ID, with a real-time sync pipeline using optimistic local apply and `/saveTransactions` server validation ([Exploring Notion's Data Model](https://www.notion.com/blog/data-model-behind-notion), [HowWorks](https://howworks.ai/blog/how-notion-was-built)). Pattern lessons: UUID-per-block, content-pointer + parent-pointer, generic block model with type-switched render. Listed for the architectural pattern; not adoptable.

### Knowledge graph / personal knowledge management

**Roam Research**. Closed. Datascript datalog under the hood — every block is a datom `[entity-id attribute value tx-id]` with `:block/uid` as a 9-character stable identifier; `:block/string` holds content; `:block/parents` and `:block/order` carry hierarchy ([Datalog Cheatsheet](https://gist.github.com/2b3pro/231e4f230ed41e3f52e8a89ebf49848b)). Block references `((uid))` are the original block-as-quotable-unit pattern that Logseq, Obsidian (via plugin), Anytype, and Tana inherit. Mixed content: blocks are text-typed by convention, with embeds for tables/queries.

**Logseq** ([logseq.com](https://logseq.com/), [GitHub](https://github.com/logseq/logseq)). 42.5k stars, AGPL-3.0. Outliner — every bullet is a block with a UUID; references via `((block-uuid))`; pages stored as Markdown or Org-mode files with `property:: value` lines for structured fields. The 2026 architectural pivot is the **DB version**: SQLite-backed graphs to fix the file-based system's performance limits, in beta as of early 2026 (see [Self Hosting Logseq Patches Mar 2026](https://gist.github.com/4shutosh/33af33932c3d5e776368bc30b59d0aa6)). AI integration: rich third-party plugin ecosystem including [logseq-plugin-ai-assistant](https://github.com/ahonn/logseq-plugin-ai-assistant), [logseq-copilot](https://github.com/jarodise/logseq-copilot), and a Logseq MCP server enabling AI agents to interact with pages and blocks via Datalog queries. Sync: file-based primary; DB version adds RTC (real-time collaboration) in alpha.

**Obsidian**. Closed core, plugin ecosystem. Markdown-files-on-disk with `^block-id` anchors as Obsidian's native block-reference mechanism — short stable IDs (auto-suggested) referenced as `[[Note#^block-id]]`. UUID generation available via plugins (e.g., [taylow/obsidian-uuid](https://github.com/taylow/obsidian-uuid), [Note UID Generator](https://www.obsidianstats.com/plugins/note_uid_generator)) for stable note identifiers across renames. **AI agent integration is the standout:** [Smart Connections](https://github.com/brianpetro/obsidian-smart-connections) provides RAG against the vault; [Obsidian CLI](https://obsidian.md/) (Feb 2026) is the documented bridge for external agents (Claude Code, terminal AIs) to read and write the vault. Multiple MCP server implementations exist — [aaronsb/obsidian-mcp-plugin](https://github.com/aaronsb/obsidian-mcp-plugin) (HTTP on localhost:3001, wikilinks + Dataview + Bases, March 2026 commits) and [msdanyg/smart-connections-mcp](https://github.com/msdanyg/smart-connections-mcp) (reads precomputed embeddings) per [Krzysztof's blog](https://3sztof.github.io/posts/obsidian-smart-connections-mcp/). Self-host: vault is local files; sync via Obsidian Sync (paid) or third-party (Syncthing, git, etc.).

**Tana**. Closed. Outliner + database hybrid — every node has a Supertag assigning it a semantic type with typed fields, enabling structured queries across an outline. Live searches drive dashboards. Multi-model AI in 2026: GPT-5.1, Gemini 3 Pro, Claude Sonnet 4.5 ([Tana Review 2026](https://aiproductivity.ai/guides/tana-supertags-guide/)). Listed for the Supertag pattern (typed-block + outline) that's a strong precedent for typed panels.

**Anytype** ([anytype.io](https://anytype.io/), [GitHub](https://github.com/anyproto/anytype-ts)). MIT (protocols), source-available (apps). 7k+ stars. Local-first, P2P-encrypted block store with Types and a graph view. Composable blocks: text, databases, kanban, calendar, custom Types. The P2P + E2E-encrypted angle is unusual — content lives only on user devices, synced via the Anytype protocol. AI integration: not yet found as first-class. Self-host: peer is the user's device by design.

**Capacities**, **Reflect**, **RemNote**, **Mem.ai**. Closed. Each adds a variation on the typed-block / spaced-repetition / AI-augmented theme. Not adoption candidates; mention for completeness.

**AFFiNE** ([affine.pro](https://affine.pro/), [GitHub](https://github.com/toeverything/AFFiNE)). 45k+ stars (March 2026), MIT (Community Edition), v0.26.x. BlockSuite-powered knowledge OS combining docs, whiteboards (Edgeless), and databases. AI Copilot supports Claude with model ID overrides ([self-host AI docs](https://docs.affine.pro/self-host-affine/administer/ai)). Self-host: documented Docker Compose path; CE is MIT and free for ≤10 users when self-hosted.

### Spreadsheet/database hybrids

**Notion databases**, **Coda**, **Airtable**, **Glide**. Closed. Architecturally: row = block-with-typed-fields (Notion's data model), or row = record-against-schema (Airtable). All ship AI features; none are open. Listed for pattern lessons.

**Baserow** ([baserow.io](https://baserow.io/)). MIT (core), proprietary (premium/enterprise). Self-hosted Airtable alternative — relational tables, real-time collaboration, stable record IDs. From training data, may be stale: ~10k+ stars, well-maintained.

**NocoDB** ([nocodb.com](https://nocodb.com/)). **License changed in 2026** — v0.301.0 moved from AGPL-3.0 to "Sustainable Use License" (fair-code, source-available) per [openalternative.co comparison](https://openalternative.co/compare/baserow/vs/nocodb). Visual layer over existing SQL databases (Postgres, MySQL). Lighter-weight than Baserow. The license shift matters for pure-OSS adoption.

For an agent workspace where panels need spreadsheet-like surfaces, the question is whether to embed a hybrid (heavy) or compose simpler primitives (SQLite + a grid view). Baserow's value is mostly the UI; the data model is a relational schema with auto-IDs.

### Document-tree models

**mdast** ([syntax-tree/mdast](https://github.com/syntax-tree/mdast)). Spec for representing markdown as an abstract syntax tree built on unist. Latest release 5.0.0. Nodes have `type` and (for non-leaves) `children`; **no native `id` field** — adding stable IDs is an application concern. The unified/remark ecosystem is the practical home: parse markdown to mdast, mutate, stringify back. Pairs with `mdast-util-from-markdown` and friends.

**tree-sitter** ([tree-sitter.github.io](https://tree-sitter.github.io/)). Incremental parser generator. For markdown specifically, [tree-sitter-grammars/tree-sitter-markdown](https://github.com/tree-sitter-grammars/tree-sitter-markdown) gives a CST with byte-precise positions but no semantic node IDs. Strength: edits are localized — `tree.edit()` updates only affected ranges. Useful where panels render code/text with structure-aware operations; weak as a primary persistence model since the tree isn't semantically addressed.

**Rich text editor ASTs** (ProseMirror schema, Lexical node tree, Slate schema-loose tree). Each is a document tree with editor-specific shape. Common pattern: typed nodes, attributes, children — same shape as mdast at a higher level of abstraction.

### Specialty

**BlockSuite** is the genuinely interesting outlier in the editor-framework category and was treated above. The differentiating claim — CRDT-native single source of truth, with Yjs as the substrate rather than a binding — is verified by the [blocksuite.io guide](https://blocksuite.io/guide/store.html). For a workspace whose panel content is shared between agent and user with live collaboration, this is the most direct architectural precedent.

## Comparison table

| Project | URL | Type | Content-unit model | Stable IDs | Mixed types | AI-integration | Sync | Fit |
|---|---|---|---|---|---|---|---|---|
| Jupyter + jupyter-ai | [jupyter.org](https://jupyter.org/) | Notebook | Typed cells (code/md/raw) | nbformat 4.5 cell `id` (alnum) | Yes | Shipped — agent reads/writes via MCP, supports Claude | Yjs | High — proven panel-of-cells pattern with shipped agent integration |
| Marimo | [marimo.io](https://marimo.io/) | Reactive notebook | Python functions per cell | Positional today; opt-in proposed | Code + markdown via fstrings | Shipped — agents as first-class cells, ACP for Claude Code | File (pure Python) | High for Python panels; strong agentic precedent |
| Observable Notebook Kit | [notebook-kit](https://observablehq.com/notebook-kit/) | Reactive notebook | JS/SQL/MD/HTML cells | Optional integer `id` attribute | Yes | Not yet found in OSS kit | File (HTML) | Medium — open format, less mature agent story |
| Quarto | [quarto.org](https://quarto.org/) | Publishing | Code chunks in markdown | Optional `label:` chunk option | Yes (multi-language) | Not first-class | File (.qmd) | Low — publishing focus, not workspace |
| Pluto.jl | [plutojl.org](https://plutojl.org/) | Reactive notebook | Julia cells | UUID per cell in file | Code + md literals | Not yet found | File (pure Julia) | Low — Julia-bound |
| Polynote | [polynote.org](https://polynote.org/) | Polyglot notebook | Typed cells | Likely UUIDs (unverified) | Yes | Not yet found | Custom | Low — unverified maintenance |
| Apache Zeppelin | [zeppelin.apache.org](https://zeppelin.apache.org/) | Notebook | Paragraphs + interpreter binding | Per-paragraph IDs | Yes via interpreters | Not first-class | Custom | Low for adoption; high for the interpreter pattern |
| ProseMirror | [prosemirror.net](https://prosemirror.net/) | Editor lib | Schema-typed node tree | Position-based; IDs added via Yjs | Yes via schema | Framework-agnostic | y-prosemirror | High as a node primitive |
| Tiptap | [tiptap.dev](https://tiptap.dev/) | Editor lib | ProseMirror nodes + extensions | UniqueID extension or Yjs | Yes | Framework-agnostic (Tiptap AI is hosted) | y-tiptap (Yjs) | High for prose panels |
| Lexical | [lexical.dev](https://lexical.dev/) | Editor lib | Element/Text/Decorator tree | Session-local keys | Yes | Framework-agnostic | @lexical/yjs | High for prose panels |
| BlockNote | [blocknotejs.org](https://www.blocknotejs.org/) | Editor lib | Notion-style blocks | First-class block UUID | Yes | Community PoC ([blocknote-llm](https://github.com/numerique-gouv/blocknote-llm)) | Yjs (Liveblocks/PartyKit/Y-Sweet) | High — closest precedent for block-with-ID + Yjs |
| Slate | [docs.slatejs.org](https://docs.slatejs.org/) | Editor lib | Schema-loose tree | Developer-defined | Yes | Framework-agnostic | slate-yjs | Medium — flexible but unopinionated |
| Editor.js | [editorjs.io](https://editorjs.io/) | Editor | `{id, type, data}` blocks | Native short alnum ID | Yes | Framework-agnostic | Not built-in | Medium — agent-legible JSON, no CRDT |
| BlockSuite | [blocksuite.io](https://blocksuite.io/) | Editor framework | CRDT-native blocks (Doc = Yjs subdoc) | Yes (Yjs map per block) | Yes | None in framework; AFFiNE consumer adds it | Yjs (native) | Very high — best architectural fit if Yjs accepted |
| Notion (closed) | [notion.com](https://notion.com/) | App | UUID-keyed blocks in Postgres | UUID v4 | Yes | Shipped (Notion AI) | Custom | Reference only |
| Roam (closed) | [roamresearch.com](https://roamresearch.com/) | App | Datom blocks | 9-char `:block/uid` | Limited | Shipped (Claude support) | Custom | Reference only |
| Logseq | [logseq.com](https://logseq.com/) | PKM | Outline blocks (UUID) | UUID per block | Limited | Plugin ecosystem + MCP server | File / SQLite (DB beta) | Medium — outliner mismatch with arbitrary panels |
| Obsidian (closed) | [obsidian.md](https://obsidian.md/) | PKM | Markdown notes + `^block-id` | `^id` anchors | Yes via plugins | MCP servers + Obsidian CLI (Feb 2026) | File + Sync product | High for file-on-disk + agent integration |
| Anytype | [anytype.io](https://anytype.io/) | PKM | Typed composable blocks | Yes | Yes | Not yet found | P2P custom | Low — P2P unusual for our use |
| Tana (closed) | [tana.inc](https://tana.inc/) | PKM | Supertagged outline nodes | Yes | Yes | Multi-model AI shipped | Custom | Reference only |
| AFFiNE | [affine.pro](https://affine.pro/) | App | BlockSuite blocks + Edgeless | Yjs map IDs | Yes (docs/canvases/DBs) | Shipped — AI Copilot incl. Claude | Yjs | High if a full app is acceptable |
| Baserow | [baserow.io](https://baserow.io/) | DB hybrid | Relational rows | Auto-PK | Tabular + views | Limited | DB-backed | Niche — for explicit DB panels |
| NocoDB | [nocodb.com](https://nocodb.com/) | DB hybrid | Visual layer over SQL | Auto-PK | Tabular | Limited | DB-backed | Niche; license shift in 2026 |
| mdast | [syntax-tree/mdast](https://github.com/syntax-tree/mdast) | AST spec | Typed unist nodes | None native | Yes | n/a | n/a | High as primitive for markdown panels |
| tree-sitter | [tree-sitter.github.io](https://tree-sitter.github.io/) | Parser | CST with positions | Position-based | Per-grammar | n/a | Incremental | Medium — code panels with structure-aware ops |

## Pitfalls and lessons learned

**Position-based identity decays under concurrent edit.** ProseMirror, Lexical, Slate, mdast, and tree-sitter all default to addressing nodes by tree-position. With agents and users editing concurrently, position references go stale between an agent's read and its write. Every editor that takes collaboration seriously layers stable IDs — Tiptap's UniqueID, BlockNote's first-class block UUID, BlockSuite's per-block Yjs map IDs, Yjs's CRDT IDs through y-prosemirror. **Lesson:** if agent participation matters, stable IDs at the unit-of-content level are non-negotiable. Position-based addressing is a footgun the moment two writers exist.

**File format vs. CRDT format is a forking decision.** Marimo (pure Python), Pluto (pure Julia), Quarto (.qmd), Observable Notebook Kit (HTML) chose file-as-source-of-truth for git-friendliness. Notion, AFFiNE/BlockSuite, jupyter-collaboration chose CRDT-as-source-of-truth for live collaboration, with file export as a derived view. Both are coherent. The hybrid (file with embedded CRDT state) is rare and brittle — dual sources of truth invite drift. **Lesson:** pick one. If files are primary, accept that real-time collab requires a layer outside the file (OT/CRDT in memory, persisted on save). If CRDT is primary, accept that diff-friendliness suffers and "file" becomes an export.

**Stable IDs added late are stable in name only.** Jupyter shipped cell IDs in nbformat 4.5 (JEP 62), but the VS Code duplicate-cell bug ([microsoft/vscode#143396](https://github.com/microsoft/vscode/issues/143396)) shows how a late-added ID field gets violated by tooling that didn't update its assumptions. Marimo's discussion in [#3177](https://github.com/marimo-team/marimo/issues/3177) explicitly raises copy-paste as the dedup challenge. **Lesson:** stable IDs need a uniqueness invariant enforced at every write boundary, not just at create — every importer, copier, splitter, merger has to participate. Plan for it from the start, not as a retrofit.

**Block-references-by-UUID are an enabling primitive.** Roam's `((uid))`, Logseq's `((uuid))`, Obsidian's `^block-id`, Notion's content/parent pointers, BlockSuite's Yjs map keys all converge on the same idea: a content unit is a thing you can quote from elsewhere. Agents benefit doubly — references are stable across edits, and the agent can manipulate "this block" rather than "the third paragraph." **Lesson:** if panels need cross-references (one panel quotes content from another), bake the addressable-unit pattern in early.

**Generic block types beat specific schemas at scale.** Notion's "everything is a block" pays off because the renderer dispatches on `type` and the storage shape is uniform. Editors that bake too many specific types into schema (early Slate examples) hit walls when extending. **Lesson:** for an agent workspace where the panel taxonomy will grow, a `{id, type, props, children}` shape with type-driven rendering is the path of least resistance.

**Yjs is the ecosystem standard for the panel sync problem.** jupyter-ydoc, BlockNote, Tiptap, Lexical, Slate, Quill, Monaco, CodeMirror, BlockSuite, Milkdown, Superdoc all bind to Yjs for collaboration. Picking a non-Yjs sync substrate cuts off most of the editor-binding ecosystem. **Lesson:** the default for cross-panel sync should be Yjs unless a specific reason rules it out.

**Reactive-dataflow notebooks (Marimo, Observable, Pluto) impose constraints worth understanding.** Each cell becomes a node in a static dataflow DAG; cyclic dependencies are errors; cell order is derived not authored. This is great for reproducibility and bad for free-form exploration where you don't want every save to recompute downstream. **Lesson:** reactivity is a strong opinion — adopt it for compute panels, not for prose panels.

**Closed AI features in PKM tools rarely solve the agent-as-first-class-participant problem.** Tana's, Notion's, Reflect's AI is a chat sidecar — it reads context and writes outputs, but it doesn't coexist with the user as a peer editor on the same blocks. The projects that actually solve agent-as-participant — Marimo, jupyter-ai, AFFiNE Copilot, Obsidian via MCP — are the ones with explicit cell/block addressability and a mutation API. **Lesson:** "has AI" is not "is agent-friendly"; check whether agents can address and mutate units at the same level the user does.

## Agent-integration precedents

Projects that ship AI as a cell-or-block-level participant rather than a chat sidecar.

**Marimo Agents + marimo pair** ([marimo agents](https://docs.marimo.io/guides/editor_features/agents/), [marimo-agents PyPI](https://pypi.org/project/marimo-agents/)). The Agent mode adds tools to add, remove, update cells and run stale ones. `marimo pair` lets external agents (Claude Code, Gemini, Codex, OpenCode) read variables, test logic in a scratchpad, run cells, add and remove cells, manipulate UI elements via the **Agent Client Protocol (ACP)**. This is the most direct precedent for "agent participates as a peer at the cell level" — agents aren't chat partners; they're co-editors with a tool surface mirroring the user's. The blog post [Turning Python notebooks into AI-Accessible Systems](https://marimo.io/blog/beyond-chatbots) frames the design principle.

**jupyter-ai v3.0.0** ([repo](https://github.com/jupyterlab/jupyter-ai)). Built-in Jupyter MCP server gives any ACP-compatible agent the ability to read and write notebooks, run terminal commands, fix detected cell errors. Permission system gates writes and executions. Multi-agent: Claude, Codex, Copilot, Gemini, Goose, Kiro, Mistral Vibe, OpenCode through ACP. Inline cell-level chat via sparkle icon / keyboard shortcut. The ACP standard is the architectural lesson — pick a protocol that's editor-side, not agent-vendor-side, so swapping models doesn't require workspace rework.

**AFFiNE AI Copilot** ([self-host docs](https://docs.affine.pro/self-host-affine/administer/ai)). Multi-provider including Claude (default `claude-sonnet-4@20250514` per recent docs). Self-host configuration takes API keys + baseUrls in `config.json`. AI integrates at the BlockSuite block level — generated content slots into the same Yjs-backed block tree the user edits, not a separate response panel.

**Obsidian + MCP** ([Krzysztof's blog](https://3sztof.github.io/posts/obsidian-smart-connections-mcp/)). Obsidian CLI (Feb 2026) is the documented bridge for external agents — Claude Code reads and writes the vault as files, with MCP plugin servers (e.g., [aaronsb/obsidian-mcp-plugin](https://github.com/aaronsb/obsidian-mcp-plugin)) extending the surface to wikilink graph traversal, Dataview queries, and Bases. The vault-as-files model means the agent's tool surface is filesystem operations, not in-app block primitives — a different design point from Marimo / jupyter-ai / AFFiNE.

**Logseq MCP servers** ([HarrisonTotty/logseq-ai](https://glama.ai/mcp/servers/@HarrisonTotty/logseq-ai), [aibase listing](https://mcp.aibase.com/server/1471642251817132692)). Tools for AI agents to search/manage pages and blocks, execute Datalog queries, manage journal entries. Block-level mutation via the existing block-UUID primitive.

**BlockNote-LLM** ([numerique-gouv/blocknote-llm](https://github.com/numerique-gouv/blocknote-llm)). Proof-of-concept of in-browser LLM editing through BlockNote's block API. Demonstrates the block-as-mutation-target pattern for an editor framework that hasn't shipped first-class AI.

**Common pattern across the precedents that work:** the agent's tool surface mirrors the user's editing operations at the same level of granularity (cell, block, file), and an explicit protocol (MCP, ACP) defines how the agent invokes them. The agent doesn't see a chat-only surface — it sees the same content units the user does, identified the same way.

## Recommended path for our design

Three coherent paths exist; the choice depends on which constraints bind hardest.

**Path A — Adopt Yjs + BlockSuite (or BlockNote), Yjs as the substrate, blocks as the unit.**

Best fit if real-time collab between agent and user matters and the panel taxonomy includes prose, lists, tables, and custom widgets that should mix in one document. BlockSuite is the more architecturally aligned choice (CRDT-native, AFFiNE proves the multi-panel pattern works); BlockNote is the easier on-ramp (smaller scope, more docs, MPL-2.0). Both give first-class block IDs, mixed content, Yjs sync, and a mutation API the agent can target. Inherits the entire Yjs ecosystem of editor bindings for specialized cells (Monaco/CodeMirror code cells, Tiptap rich-text, custom panels).

Cost: Yjs commits you to a CRDT mental model (state lives in memory + a binary update log; "file format" becomes an export concern). The user's "panel content persists as files" goal needs a converter layer.

**Path B — Adopt jupyter-ai's MCP/ACP pattern, files as primary, panels as file types.**

Best fit if file-on-disk is non-negotiable (the user explicitly says "panel content persists as files"). Each panel type maps to a file type with a known structure: markdown (mdast), Python (Marimo-style or Jupyter), CSV/SQLite for tabular, PDF/image for read-only. The agent operates through a file-level MCP surface plus per-format tools (notebook MCP for .ipynb, mdast tools for markdown, sql_query for SQLite).

This is closer to what jupyter-ai + marimo-agents actually do at the agent boundary: the agent operates on cells via a structured API, but the on-disk artifact is the file. Real-time collab is a separate concern (Yjs at the editor binding layer per panel type, or no real-time at all and collaboration through file-watch).

Lower architectural risk because it composes existing tools (one Marimo file per Python panel, one .md file per prose panel, one .ipynb per mixed panel) rather than introducing a new content store. Stable IDs come from the file format: nbformat cell `id`, marimo cell variable name, Pluto UUID comment, mdast custom `id` attribute via remark plugin.

Cost: cross-panel references become inter-file references; live collab on a single panel needs per-format CRDT bindings.

**Path C — Borrow the Notion/AFFiNE block model, build a thin store atop SQLite, expose via MCP.**

Best fit if the user wants direct architectural control. Schema: `blocks(id, parent_id, prev_id, type, props_json, doc_id)` plus `panels(id, layout_position, doc_id)`. UUID v4 per block; type-driven rendering; agent MCP tools for `block_create`, `block_update`, `block_move`, `block_delete`, `block_query`. Real-time sync added later via Yjs or a custom op log.

Cost: every editor binding has to be wired in (no Tiptap-Yjs equivalent for a custom store). Most of the cost BlockSuite has already paid; Path C re-pays it.

**Default recommendation: Path B with selected Path A escape hatches.**

The user's stated constraint — "panel content persists as files; users can save layouts for reopening in future sessions" — points strongly at file-primary. The richest agent-integration precedent (Marimo + jupyter-ai through ACP/MCP) is also file-primary. The interpreter pattern from Apache Zeppelin maps cleanly: each panel type registers with a handler that knows how to read, write, render, and expose the unit-of-content abstraction to the agent. For a Python compute panel, that's Marimo. For a markdown panel, that's a remark/mdast pipeline with a stable-ID extension. For a tabular panel, that's a SQLite-backed grid (the project already has `sql_query` MCP tooling). For a free-form mixed-content document panel where real-time collab + multiple block types matter together, drop in BlockNote-on-Yjs and bridge to the file system through a Y.js-to-mdast or Y.js-to-JSON round-trip on save (Path A as a panel-type, not the whole architecture).

The unit-of-content abstraction across panel types needs three properties:

1. **Stable ID per unit** — cell id (nbformat 4.5), marimo cell name, mdast node with id attribute, BlockNote block UUID, SQLite row PK. Different concrete IDs per format; same contract.
2. **Type-driven dispatch** — the workspace knows what kind of unit it's looking at and routes mutations through the panel-type's handler.
3. **MCP-shaped agent surface per panel type** — `notebook.cell_update`, `markdown.heading_insert`, `table.row_upsert`, etc. Modeled on the Marimo agent tool surface and the Jupyter MCP server.

This avoids inventing the unit-of-content primitive — every concrete primitive already exists in a maintained ecosystem — and concentrates the new work on the *interpreter abstraction* (Zeppelin's pattern) that lets the workspace dispatch across them. That abstraction is the genuinely workspace-specific contribution; the panel-internal data models are borrowed.

## Gaps and open questions

- **No verified Claude-specific benchmarks for cell-vs-block addressability accuracy.** Whether agents perform better when given block UUIDs vs. cell positions vs. line ranges hasn't been measured for Claude on agentic editing tasks. Worth a small evaluation if the choice between Path A and Path B turns on agent reliability.
- **BlockSuite's adoption signal is mixed.** 5.8k stars and v0.22.4 (July 2025 — almost a year old) suggest slower release cadence than AFFiNE itself. Status of the framework as a standalone consumable (vs. an internal AFFiNE library) is unclear; not yet found whether external projects beyond AFFiNE depend on it. Worth a check before committing to Path A with BlockSuite specifically.
- **Marimo's stable cell ID work is open.** Issue #3177 is not yet shipped (verified December 2024 origin; current status not yet found). If Marimo is the Python-panel backbone, the timing of stable IDs matters for cross-session reference patterns.
- **ACP (Agent Client Protocol) maturity is unclear.** Multiple projects cite it (Marimo, jupyter-ai), but its specification status, governance, and overlap with MCP haven't been verified. Worth a fetch before designing the workspace-agent interface around it.
- **Yjs file-format export story.** The mature path is binary update log → snapshot → JSON; round-tripping to human-editable formats (markdown, ipynb) is a per-binding concern. Each binding (y-prosemirror, jupyter-ydoc, BlockNote) handles its own export; the user's "save layout" goal needs a workspace-level layout-state format that's separate from per-panel content state.
- **Apache Zeppelin's interpreter pattern adoption status.** Zeppelin's own activity in 2025-2026 is not yet verified. The pattern is sound regardless; whether to treat Zeppelin as a current reference or historical inspiration depends on its release cadence, which the search didn't surface.
- **Polynote status.** No 2025-2026 release evidence surfaced; treat as historical.
- **"Could we just be Logseq DB?"** The 2026 Logseq DB version is SQLite-backed with RTC in alpha. A workspace-as-Logseq-graph mapping is at least conceivable; the question is whether Logseq's outliner-first model fits "configurable panel layouts" or fights it. Not investigated; left as an open avenue.

## Sources

- [Anthropic — Claude Code docs (project)](https://code.claude.com/docs/en/plugins-reference)
- [Jupyter — JEP 62: Cell ID Addition to Notebook Format](https://jupyter.org/enhancement-proposals/62-cell-id/cell-id.html)
- [jupyter/nbformat](https://github.com/jupyter/nbformat)
- [microsoft/vscode#143396 — Duplicate cell IDs in nbformat 4.5](https://github.com/microsoft/vscode/issues/143396)
- [jupyterlab/jupyter-ai](https://github.com/jupyterlab/jupyter-ai)
- [marimo-team/marimo](https://github.com/marimo-team/marimo)
- [marimo-team/marimo#3177 — Optional stable cell IDs](https://github.com/marimo-team/marimo/issues/3177)
- [marimo agents documentation](https://docs.marimo.io/guides/editor_features/agents/)
- [marimo pair documentation](https://docs.marimo.io/guides/generate_with_ai/marimo_pair/)
- [marimo-agents PyPI](https://pypi.org/project/marimo-agents/)
- [Marimo blog — Beyond chatbots](https://marimo.io/blog/beyond-chatbots)
- [Observable Notebook Kit](https://observablehq.com/notebook-kit/)
- [Observable Notebooks 2.0 System guide](https://observablehq.com/notebook-kit/system-guide)
- [observablehq/notebook-kit](https://github.com/observablehq/notebook-kit)
- [Quarto](https://quarto.org/)
- [JuliaPluto/Pluto.jl](https://github.com/JuliaPluto/Pluto.jl)
- [Polynote](https://polynote.org/)
- [Apache Zeppelin](https://zeppelin.apache.org/)
- [ProseMirror Guide](https://prosemirror.net/docs/guide/)
- [Tiptap docs — ProseMirror core concepts](https://tiptap.dev/docs/editor/core-concepts/prosemirror)
- [ueberdosis/tiptap](https://github.com/ueberdosis/tiptap)
- [Lexical Nodes documentation](https://lexical.dev/docs/concepts/nodes)
- [facebook/lexical](https://github.com/facebook/lexical)
- [BlockNote](https://www.blocknotejs.org/)
- [TypeCellOS/BlockNote](https://github.com/TypeCellOS/BlockNote)
- [BlockNote Yjs integration deepwiki](https://deepwiki.com/TypeCellOS/BlockNote/8.1-yjs-integration)
- [FOSDEM 2026 — BlockNote, ProseMirror, Yjs 14](https://fosdem.org/2026/schedule/event/8VKQXR-blocknote-yjs-prosemirror/)
- [numerique-gouv/blocknote-llm](https://github.com/numerique-gouv/blocknote-llm)
- [Slate — Nodes](https://docs.slatejs.org/concepts/02-nodes)
- [codex-team/editor.js](https://github.com/codex-team/editor.js)
- [BlockSuite](https://blocksuite.io/)
- [toeverything/blocksuite](https://github.com/toeverything/blocksuite)
- [BlockSuite Block Model](https://docs.affine.pro/blocksuite-wip/store/block-model)
- [BlockSuite — CRDT-Native Data Flow](https://block-suite.com/blog/crdt-native-data-flow.html)
- [toeverything/AFFiNE](https://github.com/toeverything/affine)
- [AFFiNE self-host AI documentation](https://docs.affine.pro/self-host-affine/administer/ai)
- [Notion — Exploring the Data Model](https://www.notion.com/blog/data-model-behind-notion)
- [HowWorks — How Notion Was Built](https://howworks.ai/blog/how-notion-was-built)
- [Roam Research Datalog cheatsheet](https://gist.github.com/2b3pro/231e4f230ed41e3f52e8a89ebf49848b)
- [logseq/logseq](https://github.com/logseq/logseq)
- [Self Hosting Logseq Patches — March 2026](https://gist.github.com/4shutosh/33af33932c3d5e776368bc30b59d0aa6)
- [ahonn/logseq-plugin-ai-assistant](https://github.com/ahonn/logseq-plugin-ai-assistant)
- [Obsidian Block ID Processing](https://deepwiki.com/l1xnan/obsidian-better-export-pdf/7.4-block-id-processing)
- [taylow/obsidian-uuid](https://github.com/taylow/obsidian-uuid)
- [Note UID Generator (Obsidian plugin)](https://www.obsidianstats.com/plugins/note_uid_generator)
- [brianpetro/obsidian-smart-connections](https://github.com/brianpetro/obsidian-smart-connections)
- [Krzysztof — Obsidian + AI: From Plugin to Full Agent](https://3sztof.github.io/posts/obsidian-smart-connections-mcp/)
- [aaronsb/obsidian-mcp-plugin](https://github.com/aaronsb/obsidian-mcp-plugin)
- [Tana — Knowledge Graph](https://tana.inc/knowledge-graph)
- [Anytype](https://anytype.io/)
- [anyproto/anytype-ts](https://github.com/anyproto/anytype-ts)
- [Baserow](https://baserow.io/)
- [Baserow vs NocoDB 2026 (openalternative.co)](https://openalternative.co/compare/baserow/vs/nocodb)
- [syntax-tree/mdast](https://github.com/syntax-tree/mdast)
- [tree-sitter-grammars/tree-sitter-markdown](https://github.com/tree-sitter-grammars/tree-sitter-markdown)
