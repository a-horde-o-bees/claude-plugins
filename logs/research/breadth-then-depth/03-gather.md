# Phase 03 — Gather

Per-bin agent instructions for the breadth-then-depth methodology. Each agent works in isolation on its bin of samples, writing to its own `_CONSOLIDATED_pass1-bin{N}.md` partial. The merger (`04-merge.md`) consumes those partials.

The phase goal is **functional decomposition**: identify the functional parts each sample exhibits, the implementation choice for each part, and a qualitative description of what each path is and how it's used. Coverage of branching paths matters; quantification does not (deferred to the final pass).

> **Dispatch default: sequential.** One bin at a time. See METHODOLOGY.md "Resource budgeting and dispatch" for budget calibration and the rationale for sequential default. Batch-parallel (3-4 concurrent) is opt-in when wall-clock matters and platform tolerance is known.

## Variables

- {subject} — Research subject name (e.g. `mcp`)
- {subtopic} — Optional subtopic name; single-subtopic auto-resolves; multi-subtopic must pass it
- {bin-id} — Required. Integer identifying this agent's bin
- {samples} — Required. Ordered list of sample filenames assigned to this spawn (orchestrator-bin-packed by file size)

## Operating principles

These are the methodology's load-bearing principles. Re-read whenever in doubt.

**Functional decomposition over technical attributes.** Don't categorize by language, framework, or tool. Categorize by *role* — what does this part DO. Python is a tool that fills the *server runtime* role; Docker is a tool that fills *distribution channel*, *test stack*, or *deployment artifact* depending on the sample. The same tool can fill different roles in different samples; the role is the category, the tool is the choice within it.

**Qualitative descriptions, no citations.** For each implementation path, describe the path qualitatively: what it is, when it's appropriate, what it constrains about other parts. Do NOT include inline citations like `` [`sample-name`] ``. Provenance is dynamic via the `references` verb. The consolidated is a knowledge tree, not an evidence list.

**Implementation paths refine, not duplicate.** When a second sample takes the same path, don't add another bullet — refine the existing description. New nuance, edge cases, or constraints not visible from the first sample go into the same path's description. The path's description grows richer as more samples demonstrate it; it doesn't grow longer with bullet repetition.

**Cross-role linking.** When a single tool fills multiple roles, name the tool under each role's section. Docker is named under distribution-channel choices AND under test-stack choices AND under deployment-artifact choices, where each shows what Docker does in that role. Don't give Docker its own top-level branch.

## Process

### Orient

1. Read `logs/research/breadth-then-depth/METHODOLOGY.md` — the methodology is your operating philosophy; pay close attention to the "Tree shape" section
2. **Do not read** `_CONSOLIDATED_breadth-then-depth.md` or any other partial. You're working fresh; the merger will combine your partial with others later

### Initialize your partial

3. Create `logs/research/{subject}/{subtopic-or-discovered}-samples/_CONSOLIDATED_pass1-bin{bin-id}.md` with a minimal stub:

    ```markdown
    # Sample

    Pass-1 Phase-1a partial for bin {bin-id}. Functional decomposition of {samples}, organized by role with implementation paths as sub-sections.
    ```

    Use `# Sample` as the level-1 heading.

### For each sample in {samples}

4. Read `logs/research/{subject}/{subtopic-or-discovered}-samples/{sample}` in full
5. **Identify functional parts** — what does this sample DO at each layer? What roles do its components play? Examples of roles you might find (don't treat this as a checklist; let the sample's content surface its own roles): server runtime, transport, capability surface, configuration delivery, authentication, multi-tenancy, distribution, entry point, testing, release, host integration, documentation. The sample's text describes things it has and does; group those into roles
6. **For each role, identify the implementation choice** — what alternative is the sample taking? "Python with FastMCP," "stdio transport," "OAuth 2.1," "Docker image as distribution," etc. The choice is what makes this sample distinguishable from another sample's choice for the same role
7. **Place the choice in your partial** under the role:
    - If your partial already has the role, add the implementation path as a sub-section if new, or refine the existing path's description if this sample takes the same path with new nuance
    - If your partial doesn't have the role yet, add it as a new top-level `##` section, then add this sample's choice as the first sub-section
8. **Write a qualitative description for the path**:
    - What is this path? (one-line summary of the choice)
    - How does it work in this context? (what does it do, what does it interact with)
    - What does it constrain about other parts? (e.g., stdio transport implies single-tenant; OAuth implies HTTP-mode)
    - When is it appropriate? (signals from samples about why an author chose it)
9. **No inline citations.** Don't write `` [`sample-name`] ``. Don't append filename references after observations. Description should stand alone qualitatively
10. **Cross-role linking when warranted.** If the sample uses Docker in multiple roles (e.g., as distribution channel + as test stack), name Docker under each role's section, not just one

### Verify

11. After processing all samples in {samples}, run `ocd-run log research check logs/research/{subject}/{subtopic-or-discovered}-samples/_CONSOLIDATED_pass1-bin{bin-id}.md` — confirm no sibling-duplicate headings within your partial
12. Skim your partial: do the top-level `##` sections describe FUNCTIONAL ROLES, not technologies? If you have a `## Python` or `## Docker` section, that's a smell — Python and Docker are choices, not roles. Refactor to put them under the roles they fill

### Continue

13. After all assigned samples processed, return to caller

## Report when returning to caller

- **Partial filename** — the path you wrote to
- **Samples processed** — list with 1-2 sentences per sample on what roles and choices it surfaced
- **New roles created** — top-level `##` sections you added with rationale (why this is a distinct role; what makes it different from other roles)
- **Implementation paths refined** — paths whose description you grew because multiple samples in your bin took that path with different nuance
- **Cross-role tools** — tools that surfaced under multiple roles in your partial (e.g., Docker as distribution + test stack)
- **Categorization decisions worth flagging for the merger** — places you weren't sure about role boundaries, alternatives considered, judgment calls
- **Open questions** — sample content that didn't fit any role you'd identified; instruction ambiguities
- **Notable corpus observations** — patterns spanning multiple samples in your bin worth the merger or Pass 2's attention
