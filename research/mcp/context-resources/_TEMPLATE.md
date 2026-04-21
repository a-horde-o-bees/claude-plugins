# _TEMPLATE

Per-resource file structure for authoritative MCP build-guidance sources. Every field below must be filled in every resource file. Optional fields are marked. Preset values in `type` and `authority level` are prompts, not menus — describe what's actually there in free-form if reality doesn't fit.

This collection is distinct from `../repos/`. Those files describe individual MCP server implementations. Files in this collection describe **sources that inform how to build**: specifications, SDK documentation, framework docs, host integration guides, registries, curated awesome lists, and high-quality community best-practice writeups.

Filename convention: kebab-case slug describing the resource. Type-prefixed where helpful:

- `mcp-specification.md`, `python-sdk-readme.md`, `fastmcp-docs.md`
- `blog-<author>-<topic>.md` for community write-ups
- `registry-<name>.md` for registries
- `<host>-mcp-docs.md` for host integration docs
- `awesome-mcp-<curator>.md` for curated lists

Not-found / unresolvable records go to `_missing--<slug>.md` with a brief note on where the source was expected and what was tried.

---

# <Resource name>

## Identification

- url:
- type: spec / SDK docs / framework docs / host integration docs / registry / awesome list / blog post / video / talk / other
- author: (org or person)
- last-updated (if visible):
- authority level: official / semi-official / community

## Scope

One paragraph — what does this cover, what questions does it answer best, what depth.

## Takeaway summary

One paragraph summarizing the key guidance, patterns, or contents an MCP server author would extract from this source.

## Use for

Bulleted list of specific questions this source answers.

-

## Relationship to other resources

Optional. Note if this is derivative of, supplements, contradicts, deprecates, or mirrors another captured resource. If the source is a canonical form mirrored elsewhere (e.g., README rendered on both GitHub and a vendor docs site), name the mirror.

-

## Quality notes

Optional. Flag recency, depth, bias, or any caveats a reader should apply when consuming this source. Examples: "Written pre-FastMCP 2.x, APIs diverge"; "Vendor-authored, promotional tilt"; "Highly technical, assumes protocol fluency."

-
