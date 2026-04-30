# MCP — Research Synthesis

Cross-subtopic synthesis for the MCP research subject. Currently single-subtopic (`repos-samples/` — 104 MCP server repos retrofitted to canonical heading-tree shape). Reference sources informing the research live in `context/` (40 files: spec, SDK READMEs, host integration docs, registries, awesome lists, community best-practice writeups).

Form follows findings — this document is not bound to `_TEMPLATE.md`'s heading tree because the cross-subtopic story may need headings that don't exist in any one subtopic. As the research grows (additional subtopics, e.g. SDK libraries or hosting platforms studied separately), `RESEARCH.md` becomes the place where cross-cutting patterns and contradictions between subtopics surface.

Synthesis pending — author after `repos-samples/_CONSOLIDATED.md` lands. Initial structure will likely include:

- **Domain framing** — what MCP server repositories are, why this corpus, what the 104 repos cover and don't cover
- **Cross-cutting patterns** — findings spanning multiple sections of `_CONSOLIDATED.md` (e.g. transport choice × distribution channel × auth combinations forming canonical archetypes)
- **Spec vs corpus** — divergences between authoritative MCP documentation (in `context/`) and what the 104-repo corpus actually does
- **Open questions surfaced by the corpus** — unresolved tensions or design gaps the synthesis surfaces

User-facing takeaways derived from this research live in `ANALYSIS.md`.
