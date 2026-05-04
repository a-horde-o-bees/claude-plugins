# Phase 04 — Merge

Single-agent merger instructions for the breadth-then-depth methodology. The merger reads N partial consolidateds (each produced by an isolated `03-gather` agent on its own bin of samples) and produces a unified consolidated. The merger does NOT re-read raw samples; partials carry the qualitative descriptions, and `references` queries on-demand when verification is needed.

This same instruction set serves staged merging — intermediate mergers consuming subsets of partials, plus the final merger producing canonical unified output — all follow the same process.

## Variables

- {subject} — Research subject name (e.g. `mcp`)
- {subtopic} — Optional subtopic name; single-subtopic auto-resolves; multi-subtopic must pass it
- {input-partials} — Required. Ordered list of partial filenames to merge
- {output-file} — Required. Filename to write the merged result to (intermediate or canonical unified output)

## Operating principles

**Functional decomposition is the categorization layer, not technology.** When merging, top-level `##` sections must be ROLES (server runtime, transport, distribution, etc.), not technologies (Python, Docker). If a partial put `## Python` or `## Docker` at the top level, demote — surface those as choices under the relevant role(s).

**No inline citations in the output.** Some partials may have included citations (legacy practice from earlier methodology versions); strip them during merge. The merged consolidated describes each implementation path qualitatively; provenance is dynamic via `references`.

**Equivalent buckets merge by function+choice, not by wording.** Two partials describing the same path under different names ("Python with FastMCP" vs "FastMCP-based Python server") are the same (function, choice) pair. Merge into one canonical entry.

**Refine descriptions, don't enumerate.** When two partials describe the same path, the merged description integrates the nuances from both — sharper, more complete than either input. Do not list "partial 1 says X; partial 2 says Y." Synthesize into one description.

**Cross-role tools are linked, not duplicated.** When a tool surfaces under multiple roles (Docker as distribution + test stack + deployment artifact), name it in each role's section. The role-specific entry describes what the tool DOES in that role. The tool is not its own top-level branch.

## Process

### Orient

1. Read `logs/research/breadth-then-depth/METHODOLOGY.md` — operating philosophy
2. Read each partial in {input-partials}, in order. Note the functional roles each identified, the implementation paths under each role, and the canonical naming each chose

> Do NOT read raw sample files. Partials carry the qualitative synthesis; raw samples would duplicate evidence already abstracted and inflate context. Use `ocd-run log research references "<chain>" --subject {subject}` only when a specific claim needs verification (e.g., when two partials assign incompatible categorizations and you need to inspect to arbitrate).

### Build a function vocabulary map

3. Scan all input partials for the top-level roles each identified. Reconcile equivalent roles under different names:
    - "Authentication" / "Auth" / "Credential delivery" — same role
    - "Server runtime" / "Implementation language" / "Runtime stack" — same role (focus: where the server's logic executes)
    - "Distribution" / "Distribution channels" / "Package managers" — same role
4. Choose canonical role names per concept. Prefer:
    - The form most descriptive of the FUNCTION (what the role does)
    - Conventional vocabulary the industry uses for that role (e.g., "Authentication" over "Credential delivery")
    - The most frequent form across partials, breaking ties by descriptiveness
5. Record canonical role names in your report

### Identify the functional tree shape

6. Across all partials, what set of roles emerges? Some appear in many partials (high-confidence functional parts of the corpus); some appear in few (candidate roles to keep if the corpus shows them, or absorb if they're really sub-roles of larger ones)
7. For each role, scan the partials' sub-sections (implementation paths). Recognize equivalent paths across partials by **function + choice**, not by wording:
    - "Python + FastMCP" / "FastMCP-based Python server" — same path under "Server runtime" → choice "Python with FastMCP"
    - "stdio transport" / "JSON-RPC over stdin/stdout" — same path under "Transport" → choice "stdio"
    - "Static API key" / "API key in env var" — same path under "Authentication" → choice "Static API key"

### Build the merged tree

8. Starting from the canonical-named roles, construct the merged tree:
    - For each role, list the union of distinct implementation paths across partials, deduplicated by function+choice
    - For each path, write ONE qualitative description that integrates the nuances from all partials describing that path. Aim for the sharpest possible description: what is this path, when is it appropriate, what does it constrain
    - Where a path's description differs across partials in non-equivalent ways (one says "X enables Y," another says "X enables Z"), include both — the path may have multiple uses or constraints. Don't drop signal for the sake of brevity
    - Cross-role linking: when a tool fills multiple roles (Docker, Python, etc.), each role's section names it. The tool is not its own top-level branch

### Strip citations

9. **Drop all inline citations** from the merged output. If any partial included `` [`sample-name`] ``-style references, remove them. The merged consolidated describes paths qualitatively; provenance is via `references`

### Resolve conflicts

10. When two partials make incompatible claims about the same implementation path (e.g., one says "stdio is single-tenant," another says "stdio supports per-process multi-tenancy"), use `references "Sample > <chain>" --show-content --subject {subject}` to inspect the underlying samples. Pick the more accurate description; surface the alternative in the report
11. When two partials disagree on whether something is its own role or a sub-role of another, prefer the more granular treatment (split rather than absorb) when both have signal; otherwise use the partials' frequency to decide

### Write the merged output (incrementally)

12. Use Write to create the output file with just the level-1 heading and a one-line preamble:

    ```markdown
    # Sample

    Merge of {N} partials into {output-file}. Functional roles with implementation paths and qualitative descriptions; no inline citations (see `references` verb for provenance).
    ```

13. **Append each top-level `##` section as a separate Edit call.** Each Edit handles one role's full subtree (one heading + all its `###` paths + qualitative descriptions under each)
14. Verify structure after every 3-4 sections: `ocd-run log research check logs/research/{subject}/{subtopic-or-discovered}-samples/{output-file}`

## Report when returning to caller

- **Output filename** — the path you wrote to
- **Input partials processed** — list of partial filenames
- **Canonical role names** — the function vocabulary you adopted, with alternates dropped (audit trail)
- **Functional tree shape** — the top-level roles in your merged output, with one-line descriptions of each
- **Equivalent buckets recognized** — examples of (function, choice) pairs you merged across partials despite differing wording
- **Cross-role tools** — tools that appear under multiple roles in the merged output
- **Conflicts resolved** — places where partials disagreed and the choice made, with rationale
- **Citations stripped** — confirm the output has no inline `` [`sample-name`] ``-style citations (legacy from earlier partials, if present)
- **Categorization decisions worth flagging** — judgment calls about role boundaries; alternatives considered; oscillation risks for downstream merge stages or Pass 2
- **Notable corpus observations** — patterns or tensions worth surfacing to the next stage or Pass 2
