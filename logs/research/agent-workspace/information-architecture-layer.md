# Information architecture layer

How content references itself across panels — wikilinks, transclusion, backlinks, cross-document references, and reference-graph queries — surveyed across the tools whose architectures most directly bear on a panel-based agent workspace where edits in one surface must propagate to every other surface showing the same slice.

> Scope note. This research covers reference mechanics between content units. The companion data-model agent covers what a content unit *is* (block, cell, doc). Some overlap is intentional — reference design is constrained by the unit model — but identifier semantics, not unit-shape semantics, are the focus here.

## Landscape survey

### Wikilink and transclusion implementations

#### Roam Research

Block-first outliner; every paragraph is a block carrying a 9-character `:block/uid`. Two reference primitives, both UID-driven:

- `((block-uid))` — block reference. Renders the source block's text inline; clicking navigates to the source.
- `{{embed: ((block-uid))}}` and `{{embed: [[Page]]}}` — block embed and page embed. Editable surface that mutates the source.

Backlinks are intrinsic — every page renders a "Linked References" section computed from the graph. Roam exposes its full graph through a Datalog API (`window.roamAlphaAPI.q`) backed by [DataScript](https://github.com/tonsky/datascript), the in-memory ClojureScript Datalog implementation. Datoms are 5-tuples `[entity attribute value transaction added?]`, so a block reference is just `[?b :block/refs ?target]` in the index, and its inverse — backlinks — is `[?target :block/_refs ?b]` (DataScript exposes inverse navigation through underscore-prefix). The same primitive answers both directions; no separate backlink index.

Sources: [David Bieber — Datalog Queries for Roam](https://davidbieber.com/snippets/2020-12-22-datalog-queries-for-roam-research/), [Zsolt — Deep dive into Roam's data structure](https://www.zsolt.blog/2021/01/Roam-Data-Structure-Query.html), [Roam Datalog Cheatsheet (gist)](https://gist.github.com/2b3pro/231e4f230ed41e3f52e8a89ebf49848b).

#### Logseq

File-based markdown outliner originally; the team shipped a "DB version" alongside the markdown version, which uses SQLite + DataScript instead of plain `.md` files as the source of truth. Both versions share the same DataScript schema — the difference is persistence, not graph shape. Block-level identifiers are `:block/uuid` (full UUID). Reference syntax mirrors Roam: `((block-uuid))` for block references, `{{embed ((uuid))}}` for embeds, `[[Page]]` for page references, `#tag` for hashtag references.

Schema (verified at the [logseq DataScript schema gist](https://gist.github.com/tiensonqin/9a40575827f8f63eec54432443ecb929)) includes `:block/refs` with `:db.type/ref, :db/cardinality :db.cardinality/many`. The reference-extraction step parses each block's `:block/title` (content), resolves embedded `((...))` and `[[...]]` tokens, and updates `:block/refs` in the same transaction. Backlinks are queried through DataScript's inverse-attribute syntax `:block/_refs` — same single-source-of-truth pattern as Roam.

DB version (rolling out through 2025; v0.11.x supporting both file and DB graphs) replaces the parse-files-on-startup model with `@sqlite.org/sqlite-wasm` persistence and a Web Worker hosting DataScript transactions and search indexing. The shift addresses scaling complaints — large file-based graphs spent significant startup time re-parsing markdown to rebuild DataScript.

Sources: [DeepWiki — Logseq schema](https://deepwiki.com/logseq/logseq/4.2-database-schema-and-validation), [DeepWiki — Logseq query system](https://deepwiki.com/logseq/logseq/3.4-query-system), [Logseq DB docs](https://github.com/logseq/docs/blob/master/db-version.md), [How to install Logseq DB version (Preslav, Oct 2025)](https://preslav.me/2025/10/13/how-to-install-logseq-db-version-on-your-computer-sqlite/).

#### Obsidian

Page-first markdown editor; the file is the unit, with sub-page granularity bolted on through two reference syntaxes:

- `[[note]]`, `[[note#Heading]]`, `[[note#^block-id]]` — wikilink, heading link, block reference. Block IDs are six-character alphanumeric, written as `^abc123` at the end of a paragraph in the source markdown — they live in the file, not in a sidecar.
- `![[note]]`, `![[note#Heading]]`, `![[note#^block-id]]` — embeds (transclusion). Live read-only render of the source slice; edits go to the source file, which then propagates to all embed sites on the next render.

The reference graph lives in Obsidian's `MetadataCache` — an in-memory index of every file's parsed structure (links, backlinks, headings, frontmatter, tags, blocks). It is rebuilt from disk on each vault open and updated incrementally on file change. `app.metadataCache.getBacklinksForFile(file)` iterates every cached file's link list to find references to the target file — *not* a precomputed inverse index. The community plugin [Backlink Cache](https://github.com/mnaoumov/obsidian-backlink-cache) exists specifically because this O(N·refs) lookup becomes painful when called programmatically in plugins; for the UI's single-pane backlink panel the cost is invisible.

Rename cascade: when a file is renamed *through Obsidian's UI*, all wikilinks pointing at it are rewritten in-place across the vault. Rename outside Obsidian — through a file manager, git mv, an editor — and links break silently because Obsidian only knows to update what its rename event handler intercepted. Heading-link cascades (`[[note#Heading]]` when the heading text changes) are not handled; section IDs aren't tracked through edits.

Sources: [Obsidian Help — Internal links / Backlinks / Embed files](https://obsidian.md/help/), [Obsidian Forum — Backlinks in MetadataCache](https://forum.obsidian.md/t/store-backlinks-in-metadatacache/67000), [Backlink Cache plugin readme](https://github.com/mnaoumov/obsidian-backlink-cache), [DeepWiki — Obsidian metadataCache and link resolution](https://deepwiki.com/obsidianmd/obsidian-api/2.4-metadatacache-and-link-resolution).

#### Tana

Closed-source node graph; every node — including fields, views, commands, settings — is a node. References (`mirror copies`) are bidirectional by default: edits to any reference site propagate to all others, with a "References" section at the bottom of each node showing where it appears. Supertags are typed nodes that confer schema (fields, templates, commands) onto every node tagged with them — a supertag instance list functions as a typed query. Implementation details aren't published; references appear UID-driven from external behavior, but the storage substrate isn't documented publicly.

Sources: [Tana — Nodes and references](https://tana.inc/docs/nodes-and-references), [Tana — Supertags](https://tana.inc/docs/supertags).

#### Anytype

Local-first P2P knowledge tool. Block protocol ([anyproto/any-block](https://github.com/anyproto/any-block)) describes blocks via Protocol Buffers; `changes.proto` outlines CRDT changes of objects and their blocks; `events.proto` describes change events that double as CRDT changes in an object's tree. References between blocks/objects ride on this CRDT change stream — convergent on merge, no central source of truth. Storage is local SQLite + content-addressed object tree synced over the AnySync protocol on a private P2P network. Stable identifiers exist explicitly because the team found IPFS's content-addressed identifiers insufficient for the merge-friendly identity they wanted; they wrote a custom network layer.

Sources: [Anytype tech docs — Protocol overview](https://tech.anytype.io/any-sync/overview), [HN comment on AnyType + IPLD](https://news.ycombinator.com/item?id=38798196), [GitHub — anyproto/any-block](https://github.com/anyproto/any-block).

#### Foam (VS Code)

Markdown wikilink layer over a VS Code workspace. Forward links are `[[wikilink]]`. Backlinks are computed by a parsed markdown index maintained in extension memory; the Backlinks panel shows context excerpts. Auto-generated link reference definitions at the bottom of files keep wikilinks compatible with strict CommonMark tools that don't understand `[[...]]`. Renames update inbound links via the extension's rename command. Block-level references aren't a Foam primitive — file is the smallest reference unit.

Sources: [Foam — Backlinking](https://foambubble.github.io/foam/user/features/backlinking.html), [Foam GitHub](https://github.com/foambubble/foam).

#### Notion (synced blocks and mentions)

Notion's primitives are blocks and pages, both UUID-keyed. Two reference patterns:

- **Mentions** — `@page-name`, `@user`, `@date`. In the Notion API, a mention is a child of a rich-text object inside a paragraph block, carrying the target's UUID. Resolves by reference, not value, so a renamed page still mentions correctly.
- **Synced blocks** — explicit transclusion. A synced block has an "original" instance and N "duplicate" instances; all reference the original block's UUID and render the same content. The Notion API documents that synced-block content cannot be updated through the API directly — clients edit the original; duplicates re-render.

Implementation details aren't public, but the API shape implies a UUID-keyed block tree with reference pointers for mentions and a sync-block parent pointer for duplicates. The "editing in N other pages" indicator in the UI is a backlink-count surfaced at the original site.

Sources: [Notion — Designing Synced Blocks](https://www.notion.com/blog/designing-synced-blocks), [Notion API — Block reference](https://developers.notion.com/reference/block), [Notion — Synced blocks help](https://www.notion.com/help/synced-blocks).

#### mdBook

Rust-based static markdown book builder. Cross-references are `[link text](path/to/file.md#anchor)` — vanilla CommonMark, resolved at build time. No transclusion primitive; the `{{#include path}}` preprocessor directive splices file contents at build, but it's a build-time copy, not a live reference. Backlinks not provided. mdBook is included here as the floor — what falling back to "just CommonMark + build-time include" looks like.

### Backlink graph storage

Synthesizing across the tools above:

| Storage strategy | Examples | Tradeoffs |
|---|---|---|
| In-memory parsed index, rebuilt on open | Obsidian, Foam, Dataview | Simplest; fast queries on small/medium graphs; rebuild cost on cold start; iteration-based getBacklinks is O(N·refs) |
| In-memory DataScript / Datalog | Roam, Logseq (file mode), early Logseq | Inverse-attribute queries are first-class (`:block/_refs`); arbitrary query expressivity; loads slow on large graphs |
| SQLite + DataScript | Logseq DB version | Persistence avoids re-parse; web-worker isolation keeps UI responsive; SQL or Datalog over the same data |
| CRDT change tree | Anytype | Convergent under P2P merge; references survive concurrent edits; query expressivity inherits from the CRDT runtime, not a graph engine |
| Server-side database (proprietary) | Notion, Tana, Coda | Scales to teams; cross-doc resolution server-mediated; opaque to client tooling |
| RDF triplestore | Solid pods, semantic-web tools | SPARQL is standard and expressive; named graphs add provenance; ecosystem complexity is high relative to project sizes here |

Two patterns stand out: the **inverse-attribute** trick (one forward-reference attribute serves both directions, via DataScript `:attr/_inverse` or a SQL `(target, source)` index — no separate backlink table to maintain) and the **rebuild vs persisted** axis (Obsidian's rebuild-on-open is fine for personal vaults, painful at >100K files; Logseq's DB-version pivot is the case study of this ceiling being real).

### Cross-document references in collaborative tools

- **Notion mentions / synced blocks** — UUID-resolved; surface in the API as rich-text mention objects and sync-block parent pointers. Source-of-truth is server-side.
- **Coda** — `Cross-doc` tables (proprietary feature) and the user-built `FetchCodaData()` pack pull live data from another doc through formulas. Cross-doc supports two-way sync on table data with daily/hourly refresh; `FetchCodaData` returns JSON/CSV. Feature description from [Coda Help](https://help.coda.io/en/articles/3416442-set-up-cross-doc-sync-tables).
- **Roam queries** — Datalog over the in-memory graph. `[[A]]` is sugar for "link to a page named A"; Datalog queries are arbitrary patterns over `[entity attribute value]` triples.
- **Logseq queries** — same Datalog substrate; also a simpler "simple query" DSL that compiles to Datalog.
- **Tana super-tags** — every supertag instance is a queryable set; views are saved searches over instance-of relations. Effectively a typed-graph query without a query-language surface.
- **Obsidian Dataview** — community plugin that indexes inline fields, frontmatter, lists, and tasks across the vault, exposing a SQL-like DQL (and a JavaScript form) for queries. Indexing is in-memory, lazy-built; documented to scale to "hundreds of thousands of annotated notes."

### Knowledge graph standards

- **RDF + JSON-LD + schema.org** — W3C-standardized triples; SPARQL for queries. Used in Solid pods, where each user has a personal datastore expressed as an RDF knowledge graph (per [What's in a Pod?](https://ceur-ws.org/Vol-3279/paper6.pdf)). Strong on interop and provenance (named graphs); weak on developer ergonomics relative to property graphs in 2026.
- **Property graphs (Cypher / Neo4j / openCypher)** — nodes and edges with key-value properties; pattern-match query language. Dominant in graph-database commercial tooling.
- **GQL** — [ISO/IEC 39075:2024](https://www.iso.org/standard/76120.html), the first new ISO database language since SQL (1987). Standardizes property-graph queries; AWS Neptune, Microsoft Fabric, and others adopting through 2025-2026. Verified at [AWS GQL announcement](https://aws.amazon.com/blogs/database/gql-the-iso-standard-for-graphs-has-arrived/).
- **Custom ontologies** — every PKM tool above effectively defines its own micro-ontology (`:block/refs`, `:block/parent`, etc.) without committing to RDF or property-graph standards. The pragmatic precedent is "name your half-dozen attributes, expose them queryable, don't standardize."

### Reference resolution patterns

Five orthogonal axes the surveyed tools land on differently:

1. **Identity substrate** — name-based (Obsidian, Foam) vs UUID-based (Roam, Logseq, Notion, Anytype). Name-based reads cleanly in source files, rots on rename. UUID-based survives rename trivially.
2. **Rename cascade** — automatic in-tool (Obsidian UI rename, Notion title edit), nonexistent on out-of-band edits, irrelevant under UUID identity. Unison takes this to the limit: code is referenced by AST hash, names are metadata, renames are 100% accurate by construction (per [Unison docs](https://www.unison-lang.org/docs/the-big-idea/)).
3. **Broken-link detection** — Obsidian highlights unresolved wikilinks; Logseq DB structurally cannot have a broken UUID reference unless the target was deleted; RDF triplestores have no inherent integrity check.
4. **Reference cardinality** — uniformly 1:N forward, N:1 inverse. Datalog `:block/refs` cardinality-many plus inverse-attribute query is the cleanest expression.
5. **Live transclusion vs cached** — live in Roam, Logseq, Tana, Notion synced blocks, Obsidian embeds (re-rendered on view); cached only in mdBook's build-time `{{#include}}`. Live is the dominant pattern.

## Comparison table

| Tool | URL | Transclusion approach | Backlink storage | Rename handling | Agent integration |
|---|---|---|---|---|---|
| Roam Research | [roamresearch.com](https://roamresearch.com) | `((uid))` ref + `{{embed: }}` block, UID-resolved | DataScript in-memory; `:block/_refs` inverse-attribute query | UID stable; page rename updates name attribute, refs unaffected | Datalog API exposed as `roamAlphaAPI.q`; community MCP wrappers exist |
| Logseq | [logseq.com](https://logseq.com) | `((uuid))` + `{{embed }}`, UUID-resolved | DataScript in-memory (file mode) or SQLite + DataScript (DB mode) | UUID stable; markdown-mode rewrites links on rename via tooling | Datalog query API; advanced-queries surface; no first-party MCP yet (community efforts) |
| Obsidian | [obsidian.md](https://obsidian.md) | `![[note]]`, `![[note#H]]`, `![[note#^id]]` — name + heading + block-id | `MetadataCache` in-memory, rebuilt on open; iteration-based backlink lookup | Auto-update wikilinks on UI rename; out-of-band rename breaks; headings not tracked | Plugin API (TypeScript) reads `metadataCache`; community MCP servers (Smart Connections, etc.) |
| Tana | [tana.inc](https://tana.inc) | Bidirectional node references (mirror copies) | Proprietary; not documented externally | UID-stable references | Closed; HTTP API but no first-party agent surface |
| Anytype | [anytype.io](https://anytype.io) | Block tree references over CRDT changes | Local SQLite + CRDT change log; merged across P2P peers | Stable IDs by design; CRDT merges concurrent renames | Open protocol; no first-party agent surface yet |
| Foam (VS Code) | [foambubble.github.io/foam](https://foambubble.github.io/foam/) | None first-class; CommonMark links resolve at view time | In-memory parse over workspace files | Extension's rename command updates references | LSP-style integration via VS Code; agent integration through editor automation |
| Notion | [notion.so](https://notion.so) | Synced blocks (block-UUID) + page mentions | Server-side database; client receives resolved tree | UUID-stable; renaming a page updates display, refs unaffected | Notion API (REST); supports `block_id`, mention objects; commercial MCP servers |
| Coda | [coda.io](https://coda.io) | Cross-doc tables; `FetchCodaData()` for live formula sync | Server-side; cross-doc periodic sync (hourly/daily default) | Server-managed; cross-doc keeps source-of-truth at the origin | Coda API + Packs; agent integration via Pack-built tools |
| mdBook | [rust-lang.github.io/mdBook](https://rust-lang.github.io/mdBook/) | Build-time `{{#include}}` only | None | None — names embedded in source markdown | None; build-time tool |
| Solid pods + RDF | [solidproject.org](https://solidproject.org) | RDF triples, named graphs | SPARQL over triplestore (server-side) | URI-stable; rename = mint new URI typically | SPARQL endpoints; no PKM-style first-party agent surface |
| Unison codebase | [unison-lang.org](https://www.unison-lang.org) | Content-hash references; names are metadata | Hash-keyed dependency graph in codebase DB | 100% accurate by construction (names ≠ identity) | `ucm` codebase manager exposes graph queries; no agent-tool ecosystem yet |

## Pitfalls and lessons learned

**Name-as-identity collapses on out-of-band edits.** Obsidian's "rename through the UI updates wikilinks" is the cleanest UX given filename-as-identity, but every such tool inherits the same chicken-and-egg problem when something other than the tool moves the file. A panel-based agent workspace where the agent edits through `Edit`/`Write`, users move files in their shell, and git's rename detection acts heuristically will hit this constantly unless identity is stable across name changes.

**In-memory rebuild ceilings are real at predictable scales.** Obsidian's `MetadataCache` is fast at thousands of files and slow at hundreds of thousands; Logseq's DB-version pivot is the response to the same ceiling. A workspace aggregating session content over months should plan for this.

**Iteration-based backlink lookup is fine for one panel, painful at scale.** `getBacklinksForFile` iterating every cached file is O(N·refs) per call — the Backlink Cache plugin exists because the cost surfaces in plugin code paths. A persisted inverse index (DataScript inverse attribute, SQLite `(target, source)` index, SPARQL) pushes this down.

**Rename without a cascade silently rots the graph.** Fix paths: (a) make the rename do the cascade (Obsidian, fragile), (b) make identity independent of the name (Roam, Logseq DB, Notion, Unison), (c) detect and report broken links proactively.

**Heading-level references rot faster than file-level** because heading text is editable inline without firing a rename event. Obsidian does not update `[[note#Heading]]` when the heading text changes. Block-level references with stable IDs avoid this — the price is the ID lives somewhere parseable.

**Live transclusion has a sync model whether you design one or not.** Two surfaces on the same slice need answers: when source changes, does target re-render eagerly or lazily? Are concurrent edits possible, and how is conflict resolved? CRDTs (Yjs, Automerge, Anytype) answer convergently; non-CRDT systems answer through last-write-wins or single-canonical-source. The question doesn't go away by being silent.

**A reference graph without a query surface is barely a graph.** Roam/Logseq expose Datalog because their substrate is DataScript; Dataview built SQL-like DQL on Obsidian's in-memory index and users took to it widely; Notion exposes REST and the agent walks the tree. The query surface dominates what agents and users can do with the graph.

## Agent-integration precedents

- **Roam Research MCP** ([2b3pro/roam-research-mcp](https://github.com/2b3pro/roam-research-mcp)) — community MCP wrapping Roam's Datalog API. Exposes block read/write, page lookup, search, graph queries. Works because Roam exposes the underlying Datalog surface; the MCP is essentially a query passthrough.
- **Logseq and Obsidian community MCPs** — multiple community efforts; Logseq mirrors Roam's surface and gains SQL as DB-version stabilizes; Obsidian MCPs (Smart Connections, Obsidian-MCP) expose vault search, note read/write, and backlink queries through `app.metadataCache`.
- **Notion API + agent tools** — first-party REST API; synced-block reads return rich-text trees with embedded mention objects; the agent walks the tree.
- **Language-server precedents for code references.** The closest analog to "introspect and mutate the reference graph" is LSP's `textDocument/references` and `textDocument/rename`. [Kiro's blog on AI agents + program analysis](https://kiro.dev/blog/refactoring-made-right/) and [Multi-Agent Coordinated Rename Refactoring (arXiv 2601.00482)](https://arxiv.org/pdf/2601.00482) both argue that LLMs alone cannot reliably rename symbols — they pattern-match without symbol resolution. Reliable rename requires the agent to call into a precise reference graph. The lesson transfers: "rename across all references" in our workspace needs a symbol-table-equivalent, not regex sweeps.
- **Unison `ucm`** — codebase manager exposing "find usages," "rename" (metadata-only), "view dependencies of." Cleanest agent-integration story surveyed — because rename is metadata-only and references are by hash, every operation is structurally safe.

*Not yet found*: a panel-aware reference graph where the agent can ask "which panels currently render content referencing block X." The panel layer is novel relative to PKM tools and isn't a primitive surveyed tools expose. Agents in Roam/Logseq/Obsidian operate over the document graph, not over the rendering surfaces displaying it.

## Recommended path for our design

Tying back to the workspace's central property — *panel A and panel B show the same content slice; edits propagate* — the survey suggests the following architecture:

### Identity layer: stable IDs, not names

Every addressable content unit (file, block, range) carries a stable identifier independent of filename, heading text, or position. Roam (`:block/uid`), Logseq (`:block/uuid`), Notion (block-UUID), Anytype (CRDT-stable), and Unison (content-hash) all converge on this for the same reason: name-as-identity rots under edits, especially the out-of-band edits an agent workspace produces constantly. Practical shape: small frontmatter or sidecar mapping `{stable-id → current-path/range}`. Two panels referring to "block X" both resolve through the indirection and survive the source being renamed.

### Reference layer: forward-only, inverse-queryable

Store one forward-reference table or attribute (`source → target`). Get the inverse for free through DataScript-style inverse-attribute syntax (Datalog substrate) or a SQL index on `(target, source)` (SQLite). Roam and Logseq's `:block/refs` / `:block/_refs` is the verified precedent; SQLite's index covers the same ground without adopting Datalog. Per the project's `Single Source of Truth` principle, backlinks are a *projection* of forward references, not a parallel table.

### Propagation layer: pick a sync model deliberately

Three options, each verified in production:

- **Single canonical source, re-render on view** (Obsidian embed, Notion synced block) — simplest; panels re-read from source on display. Works when display is cheap and no offline-merge is needed.
- **CRDT shared substrate** (Yjs, Automerge, Anytype) — strongest correctness; merges concurrent edits; pays in conceptual complexity and binary storage. Verified library: [Yjs](https://github.com/yjs/yjs).
- **File-as-source + filesystem watch** (Obsidian, Foam, Logseq markdown) — cheapest infrastructure; OS file events drive change detection; loses fidelity on rapid edits.

For our context — local, single-user-at-a-time, agent + human both editing — option (a) is the verified-fit choice. Panels register interest in a slice; orchestrator notifies on source change; panels re-render.

### Query layer: SQL over a small schema, not RDF

Three pointers to SQLite + thin schema (paths, references, optional embeddings) over RDF:

1. The project's `Data formats for LLM-read storage` finding endorses SQLite for "indexed structured data with relationships, constraints, or scale beyond a single file."
2. Logseq's 2025 DB-version pivot moved *from* DataScript-only *to* SQLite + DataScript for exactly the persistence and tooling reasons that favor SQL at this scale.
3. The project already has a navigator MCP exposing path-and-purpose queries over SQLite; adding a `references` table to that schema beats introducing an RDF triplestore alongside.

GQL is verified as a standard but at this project's scale the win over `JOIN ... ON references.target = ...` is theoretical, not measured. *Borrow before build* — SQLite, mirror navigator's pattern.

### Rename / link-rot handling

If identity is stable IDs, rename collapses to "update the path attribute on the identity row" — references still resolve. Work moves to the *display* layer (showing the new name) and the *capture* layer (when the agent or user types `[[Name]]`, resolve to ID at parse time). The Roam/Logseq architecture. Obsidian's "rewrite all wikilinks on rename" is the name-keyed alternative — fragile under out-of-band edits.

### Agent surface

Mirror the navigator MCP's shape — structured tools returning references and resolved targets in a compact format:

- `references_outgoing(id)` — what does this content unit reference
- `references_incoming(id)` — what references this content unit
- `panels_showing(id)` — bridges the reference graph and the panel layout (novel relative to surveyed tools)
- `rename(id, new_name)` — metadata-only; no cascade needed

This shape mirrors Unison's `ucm`, Roam's Datalog API, and LSP's `textDocument/references`. All three converge on the same primitive set.

## Gaps and open questions

- **Panel-as-first-class-citizen of the reference graph.** None of the surveyed tools models the rendering layout as part of the queryable graph — Roam/Logseq/Obsidian model the document graph, panels are an editor/UI concern. *Not yet found*; may exist in a tool not surfaced by my searches.
- **Reference granularity for agent-generated content.** Surveyed tools assume blocks/headings/files; a Claude conversation produces messages, tool-use blocks, and code spans. Whether to assign IDs at the message-unit level, at heading-extracted spans, or at user-marked ranges is undetermined. The data-model agent's report should constrain this.
- **CRDT vs single-source for our use case.** The "single canonical source" recommendation assumes one editor at a time. If the workspace evolves toward concurrent agent + human edits, CRDT becomes more attractive. Cost of adopting Yjs later vs designing for it now is unmeasured.
- **Out-of-band edit handling.** If a user renames a content file in a separate editor, the workspace needs to detect and reconcile. File-watcher infrastructure is understood; the reconciliation rule (rebuild ID-to-path map, surface broken refs, prompt user) is undecided.
- **Backlink performance at the project's actual scale.** Obsidian-style in-memory rebuild fits a session-scoped workspace; Logseq-style persisted SQLite fits a corpus growing across sessions. Which scale we're designing for is a project-level decision.
- **Cross-workspace references.** Surveyed tools assume a single graph. Whether our workspace supports references across saved-layouts is open. RDF/Solid is the only surveyed model where cross-workspace reference is first-class; the cost is high.
- **Direct verification of Obsidian embed propagation latency, Notion synced-block conflict resolution, and Roam graph rebuild times** — inferred from documentation, not measured. *Not yet found* in measured form.

## Sources

### Tools and primary documentation

- [Roam Research](https://roamresearch.com)
- [Logseq](https://logseq.com)
- [Logseq DB version docs](https://github.com/logseq/docs/blob/master/db-version.md)
- [Obsidian Help](https://obsidian.md/help/)
- [Obsidian Help — Internal links](https://obsidian.md/help/Linking+notes+and+files/Internal+links)
- [Obsidian Help — Backlinks](https://obsidian.md/help/Linking+notes+and+files/Backlinks)
- [Obsidian Help — Embed files](https://obsidian.md/help/Linking+notes+and+files/Embed+files)
- [Obsidian Developer Docs — MetadataCache](https://docs.obsidian.md/Reference/TypeScript+API/MetadataCache)
- [Tana — Nodes and references](https://tana.inc/docs/nodes-and-references)
- [Tana — Supertags](https://tana.inc/docs/supertags)
- [Anytype tech docs](https://tech.anytype.io/any-sync/overview)
- [anyproto/any-block GitHub](https://github.com/anyproto/any-block)
- [Foam](https://foambubble.github.io/foam/)
- [Foam — Backlinking](https://foambubble.github.io/foam/user/features/backlinking.html)
- [Notion API — Block reference](https://developers.notion.com/reference/block)
- [Notion — Designing Synced Blocks](https://www.notion.com/blog/designing-synced-blocks)
- [Notion — Synced blocks help](https://www.notion.com/help/synced-blocks)
- [Coda — Set up Cross-doc sync tables](https://help.coda.io/en/articles/3416442-set-up-cross-doc-sync-tables)
- [Coda — Cross-doc actions](https://help.coda.io/en/articles/3506663-how-to-use-cross-doc-actions)
- [mdBook docs](https://rust-lang.github.io/mdBook/)
- [Solid Project](https://solidproject.org)
- [Unison — The big idea](https://www.unison-lang.org/docs/the-big-idea/)

### Architecture deep-dives

- [DeepWiki — Logseq schema and validation](https://deepwiki.com/logseq/logseq/4.2-database-schema-and-validation)
- [DeepWiki — Logseq block parsing](https://deepwiki.com/logseq/logseq/6.1-format-and-block-processing)
- [DeepWiki — Logseq query system](https://deepwiki.com/logseq/logseq/3.4-query-system)
- [DeepWiki — Obsidian metadata cache and link resolution](https://deepwiki.com/obsidianmd/obsidian-api/2.4-metadatacache-and-link-resolution)
- [Logseq DataScript schema gist](https://gist.github.com/tiensonqin/9a40575827f8f63eec54432443ecb929)
- [David Bieber — Datalog Queries for Roam](https://davidbieber.com/snippets/2020-12-22-datalog-queries-for-roam-research/)
- [David Bieber — More Datalog Queries for Roam](https://davidbieber.com/snippets/2021-01-04-more-datalog-queries-for-roam/)
- [Roam Datalog Cheatsheet](https://gist.github.com/2b3pro/231e4f230ed41e3f52e8a89ebf49848b)
- [Zsolt — Deep dive into Roam's data structure](https://www.zsolt.blog/2021/01/Roam-Data-Structure-Query.html)
- [How to install Logseq DB version (Preslav, Oct 2025)](https://preslav.me/2025/10/13/how-to-install-logseq-db-version-on-your-computer-sqlite/)

### Plugins, MCP servers, and agent tooling

- [obsidian-backlink-cache plugin (mnaoumov)](https://github.com/mnaoumov/obsidian-backlink-cache)
- [Blockreffer plugin (Obsidian)](https://www.obsidianstats.com/plugins/blockreffer)
- [Dataview plugin (blacksmithgu)](https://github.com/blacksmithgu/obsidian-dataview)
- [roam-research-mcp (2b3pro)](https://github.com/2b3pro/roam-research-mcp)

### Knowledge graph standards and CRDT libraries

- [GQL ISO/IEC 39075:2024](https://www.iso.org/standard/76120.html)
- [AWS — GQL announcement](https://aws.amazon.com/blogs/database/gql-the-iso-standard-for-graphs-has-arrived/)
- [Neo4j — RDF vs Property Graphs](https://neo4j.com/blog/knowledge-graph/rdf-vs-property-graphs-knowledge-graphs/)
- [What's in a Pod? (CEUR-WS, Solid + RDF)](https://ceur-ws.org/Vol-3279/paper6.pdf)
- [Yjs](https://github.com/yjs/yjs)
- [Automerge](https://automerge.org)
- [Peritext (Ink & Switch)](https://www.inkandswitch.com/peritext/)

### Agent + reference-graph papers

- [Kiro — Refactoring made right](https://kiro.dev/blog/refactoring-made-right/)
- [Multi-Agent Coordinated Rename Refactoring (arXiv 2601.00482)](https://arxiv.org/pdf/2601.00482)
- [RefAgent: A Multi-agent LLM-based Framework for Automatic Software Refactoring (arXiv 2511.03153)](https://arxiv.org/html/2511.03153)

### Project-internal references

- `/home/dev/projects/claude-plugins/logs/research/data-formats/consolidated.md` — companion synthesis on storage formats; SQLite endorsement and rationale carried into this report
