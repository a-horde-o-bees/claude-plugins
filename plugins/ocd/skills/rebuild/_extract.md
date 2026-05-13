# Extract

> Agent brief for the extract phase of rebuild. Read `{artifact}`; write a complete identity specification to `{extract-path}`. The composer agent will compose the new artifact from this specification alone — the original will not be available to it. The specification is the contract.

### Variables

- {artifact} — path to the source artifact
- {extract-path} — path where the identity specification is written

### What identity means

Identity is everything the composer needs to recompose the artifact without reading it. Insufficient extraction is the failure mode — anything not in the spec is lost when the composer fresh-composes.

This is broader than visible structure:

- **Scope and role** — what the artifact is, what consumers it serves, what it carries downstream
- **Callable surface** — frontmatter name, declared variables and their shapes, return shape, public interface, every name a downstream consumer might reference
- **Declared rules** — content of any `## Rules`, `## Dependencies`, `## Constraints`, or equivalent section. The artifact's self-declared discipline
- **Accumulated knowledge** — edge cases, special-case handling, workarounds for specific bugs. Per Spolsky's caveat: messy-looking code is often crystallized bug fixes. These must survive the rebuild
- **Disciplines applied** — what rules (loaded via `## Dependencies` or implicit) the artifact's content reflects. The composer will apply these forward; you capture them as observed

### Authoritative-stance cue

You are writing the spec the next agent will treat as the true description of this artifact. If the spec is incomplete, the rebuilt artifact will be incomplete. There is no recovery — the composer does not have access to the original.

### Output shape

Write the specification to {extract-path}. Use this structure verbatim — the composer reads it as the authoritative source:

```
# Identity Specification: <artifact-name>

## Scope and Role
<one paragraph: what this artifact is, what it carries downstream, who consumes it>

## Callable Surface
- name: <frontmatter name or equivalent>
- variables: <list with shapes; one per line>
- return: <shape of return value, or N/A>
- consumers: <known callers / dependents>

## Declared Rules
<verbatim or close-paraphrased — every rule the artifact declares about its own behavior. Do not summarize away; the composer needs the substance>

## Accumulated Knowledge
<edge cases, special handling, bug-fix crystallizations, non-obvious behaviors the next composer must preserve>

## Disciplines Applied
<list of rules / disciplines (loaded dependencies and implicit ones) the artifact's content reflects. The composer applies these forward>
```

### Process

1. Read {artifact}
2. Walk every section; do not summarize away content that may be load-bearing for downstream consumers
3. Write the specification to {extract-path}
4. Return to caller: one-line confirmation that {extract-path} was written; one-line characterization of what was extracted
