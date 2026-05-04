# Depth Pass Refinements — Sample > Extension points

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

`Sample > Extension points > Middleware module slot` — current description is FastMCP-specific and homogenizes two genuinely different mechanisms. The two supporting samples are not parallel implementations of one pattern:

- ClickHouse--mcp-clickhouse: env-var-loaded Python module that hooks FastMCP protocol events (tool calls, resource reads, prompts, listings) — a cross-cutting *interceptor* slot.
- awslabs--mcp-lambda-handler: pluggable session-management *backend interface* (NoOp / DynamoDB / consumer-implemented) selected at framework construction — an SPI on a single concern, not a protocol-event interceptor.

Either the path should describe what is actually shared across both samples (a typed extension slot loaded by name, with the *concern* varying) or the awslabs sample should be moved to a new sibling path (see "Proposed bucket splits"). If kept together, suggested sharpening:

> A typed extension slot the server publishes for users to inject behavior. Two distinct mechanisms in the corpus: (a) a protocol-event interceptor module loaded by name from an env var (FastMCP middleware contract) and (b) a backend SPI selected at framework construction (e.g., session-storage NoOp/DynamoDB/custom). Both bind a user-supplied class/module to a stable extension contract; neither requires forking.

`Sample > Extension points > Per-tool enablement file` — current description is accurate. The lone sample (HenkDz--postgresql-mcp-server) confirms the framing exactly. No sharpening proposed beyond the existing cross-role reference.

`Sample > Extension points > Runtime tool registration API` — zero supporting samples in this role; the description references `Sample > Capability surface > Capability authoring style`, which itself returned no samples in the cross-reference probe. If the underlying Capability-surface path has empty content too, this Extension-points anchor is doubly hollow — flagging for the reconciler.

`Sample > Extension points > User-publishable tools meta-tool` — zero supporting samples here, but the cross-referenced `Sample > Capability surface > User-publishable tools` is populated (riza-io--riza-mcp). The description on the Extension-points side is consistent with the riza evidence (`create_tool` / `edit_tool`). Suggested minor sharpening to anchor it concretely without duplicating the canonical entry:

> Server provides a meta-tool that lets the user register or edit tools at runtime, mutating the LLM-visible surface without redeploy. Canonical evidence under *Capability surface — User-publishable tools*; cross-listed here because the mechanism functions as an extension point as well as a capability shape.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

`Sample > Extension points > Middleware module slot` — two samples cluster on different sub-axes:

- *Protocol-event interceptor* (ClickHouse, 1 sample) — mutates per-request context, observes every protocol message
- *Backend SPI* (awslabs lambda handler, 1 sample) — replaces the implementation of one concern (session storage) behind a stable interface

Sample count is too small (1 each) to justify a split on its own, but the divergence is real. Recommend folding the sub-axis into the path description (see Sharpenings) rather than splitting at this corpus size.

## Proposed bucket merges

> Format: `<path-A> + <path-B>` — why same; supporting samples; canonical name suggestion

None. The four paths are genuinely distinct in mechanism (interceptor module vs. enablement toggle file vs. programmatic registration vs. meta-tool), even where some are sparsely populated.

## Proposed bucket splits

> Format: `<role-chain> > <path>` — why split; into what; supporting sample distribution

`Sample > Extension points > Middleware module slot` — split candidate, not strong recommendation. If the corpus expands and more samples surface either pattern, the split would be:

- *Protocol-event interceptor module* (current ClickHouse sample) — env-var-loaded module hooking FastMCP / SDK protocol events
- *Pluggable backend SPI* (current awslabs sample) — typed backend interface where the concern is one capability (session storage, persistence layer, queue, etc.) and the consumer supplies the implementation

At 1+1, splitting now creates two paths with single samples each — likely premature given the depth-pass principle that structural changes require strong evidence. Reconciler call.

## Mis-placed samples

> Format: `<sample-name>` currently under `<path-A>` better fits `<path-B>` because <evidence>

`awslabs--mcp-lambda-handler.md` currently under `Sample > Extension points > Middleware module slot` is a partial mis-placement. Its content describes a *session-storage SPI* (NoOp / DynamoDB / custom-backend interface), not a FastMCP middleware module. The sample fits the broader concept of "extension points" but does not fit the specific "middleware module slot" framing the current path description uses. Two reconciliation options:

- A) Broaden the path description to cover both interceptor modules and backend SPIs (path stays one bucket; see Sharpenings).
- B) Split into two paths (see Proposed bucket splits) and move awslabs to a "Pluggable backend SPI" bucket.

No suitable sibling currently exists for option B without creating it.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

- **Role is severely under-populated.** 3 supporting samples across 124+ corpus entries. Two of the four paths (Runtime tool registration API, User-publishable tools meta-tool) carry zero direct samples and exist as cross-reference anchors to other roles. If the convention is to keep cross-listed-only paths, the role's adoption table is misleading — readers see "0 / 0%" and may assume the pattern is rare in the corpus, when in fact a sample exists, just under another role. Surfaced for the reconciler — the existing Cross-role footer pattern handles this for sample readers, but the path-level listing under Extension points still implies absence.

- **The role straddles two definitions.** Some paths describe "user-pluggable code that runs in-process" (Middleware module slot, Runtime tool registration API), others describe "config artifacts that change which tools are exposed" (Per-tool enablement file). Both are "modify behavior without forking" but operate on different layers (code injection vs. capability gating). At 4 paths the dual-definition is tolerable; if the role grows, splitting into "Code-pluggable extension points" vs. "Surface-shaping config" may be warranted. Not actionable at current corpus size.

- **No sample uses *more than one* extension point mechanism.** Each of the 3 supporting samples picks exactly one. Either (a) extension points are mutually exclusive in practice, or (b) the corpus is too small to surface multi-mechanism cases. Worth noting but not actionable.

- **The role does not appear to overlap with `Capability surface`'s gating paths** (Capability gating flags, Tools plus toolset gating, etc.) which are themselves a kind of extension point — they let deployers reshape the surface without forking. Whether those paths *should* be cross-listed here is a reconciler-level question; right now they aren't, and that's defensible because the gating-flag mechanism is per-server-fixed (set at launch), whereas this role's paths emphasize swappable code or post-launch mutation. The line is blurry and worth a single reconciler note in the role description.
