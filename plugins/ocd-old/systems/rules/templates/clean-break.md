---
tagline: Refactors propagate fully — no compatibility shims or legacy aliases
---

# Clean Break

Refactors propagate completely — every reference is updated and the old form is deleted in the same change. No compatibility shims, migration code, legacy aliases, or dual-name support. A refactored system has one representation, not a new one layered over backward-compatible acceptance of the old.

- Before adding any backward-compatibility shim, migration path, or legacy alias during a refactor: ask the user if backward compatibility is needed; the default answer is no
- When renaming a field, column, or key: update every reference and delete the old form; do not accept both old and new
- When changing a schema: write the new schema; do not detect and migrate the old
- When a change breaks external consumers: surface the break to the user; do not paper over it with compatibility layers that create dead code paths
