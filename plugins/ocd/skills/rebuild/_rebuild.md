# Rebuild

> Workflow component for the rebuild skill. Audits an artifact against currently-loaded rules and rewrites it preserving identity (scope + role).

### Variables

- {artifact} — file path, section heading, function, frontmatter field, or other addressable scope named by the user

### Rules

- Preserve the artifact's identity (scope + role); form changes, function does not
- Gate before rebuilds that diverge structurally from the original — renames, splits, schema changes, callable-surface changes
- Empty audit (no gaps) is a no-op, not a forced rewrite

### Process

1. If {artifact} is ambiguous (multiple files match, scope unclear, the named target doesn't resolve uniquely): Exit to user — present candidate interpretations as Q# with lettered options; ask which to rebuild.
2. Read {artifact} to load its current content.
3. {applicable-rules} = the currently-loaded rules that bind to the artifact's type:
    - Any prose the agent generates → concise-prose
    - Markdown files → markdown
    - Descriptions, docstrings, commit messages, CHANGELOG entries, frontmatter `description:` fields → description-authoring
    - PFN workflows → process-flow-notation + workflow-vs-script
    - Skills, SKILL.md, workflow components, entry-point docs → progressive-disclosure
    - Test files → test-authoring (or test-driven-development when implementing-then-verifying)
    - Agent-facing tool output / error messages / return templates → agent-first-interfaces
    - File or directory structure decisions → file-decomposition + structure-as-documentation
    - Refactor scope → clean-break
    - Plus any deps the artifact's frontmatter or enclosing skill's frontmatter declares
4. Audit {artifact} against each rule in {applicable-rules}. {gaps} = list of (rule, observation) pairs naming where the current artifact misses or violates the discipline.
5. If {gaps} is empty: Exit to user — "artifact already meets all applicable discipline; no rebuild needed."
6. If applying {applicable-rules} would require structural divergence from the original (renames, splits, schema changes, callable-surface changes affecting downstream consumers): Exit to user — present {gaps} + proposed structural changes; gate on approval before proceeding.
7. Rewrite {artifact} applying each rule in {applicable-rules}.
8. Return to caller:
    - Artifact rebuilt: {artifact}
    - Gaps closed: list of (gap, rule-that-applied) pairs
    - Structural changes: any (renames, splits, format adjustments); empty when only inline edits were made
