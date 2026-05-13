# Rebuild

> Workflow component for the rebuild skill. Anti-patching: extract target's identity (scope + role + callable surface + declared rules), set the original aside, compose fresh applying the target's own deps, diff against original to verify identity preserved. The rules applied come from the target — not from this skill.

### Variables

- {artifact} — file path, section heading, function, frontmatter field, or other addressable scope named by the user

### Rules

- Identity = scope + role + callable surface (what the artifact carries downstream). Form may change; function does not.
- Compose fresh from identity alone — do not anchor on the original's prose, structure, or examples during composition. The original is reference only for the post-composition diff.
- Gate on structural divergence — renames, splits, schema changes, callable-surface changes affecting downstream consumers.
- Empty diff (no meaningful change) is a no-op, not a forced rewrite.

### Process

1. If {artifact} is ambiguous (multiple files match, scope unclear, target doesn't resolve uniquely): Exit to user — present candidate interpretations as Q# with lettered options; ask which to rebuild.

2. {original}: Read {artifact}.

3. {identity}: extract from {original}:
    - Scope + role (what the artifact's purpose is, what it carries downstream)
    - Callable surface (frontmatter name, declared variables, return shape, public interface)
    - Declared dependencies (the target's own `## Dependencies` section, if present)

4. If {identity} has declared dependencies: follow the target's `## Dependencies` block — it expresses the dependency-resolution convention as embedded PFN steps, loading each declared rule into context.

5. Set {original} aside. Compose {fresh} from {identity} alone, applying every loaded rule throughout. No referencing {original}'s prose, ordering, or section structure during composition.

6. {diff}: compare {original} vs {fresh}:
    - **Inline changes**: prose, wording, intra-section order
    - **Structural changes**: section renames, splits, schema or callable-surface changes affecting downstream consumers

7. If {diff} is empty: Exit to user — "artifact already conforms to its declared discipline; no rebuild needed."

8. If {diff} contains structural changes: Exit to user — present the structural changes; gate on approval before writing.

9. Write {fresh} to {artifact}.

10. Return to caller:
    - Artifact rebuilt: {artifact}
    - Structural changes: list (empty when only inline changes were made)
    - Inline-change summary: count of sections rewritten + brief characterization
