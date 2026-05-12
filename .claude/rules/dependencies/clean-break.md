# Clean Break

Refactors propagate completely — every reference updated and the old form deleted in the same change. No compatibility shims, migration code, legacy aliases, or dual-name support.

- Before adding a backward-compatibility shim, migration path, or legacy alias: ask the user; default is no
- When renaming a field, column, or key: update every reference and delete the old form
- When changing a schema: write the new schema; do not detect and migrate the old
- When a change breaks external consumers: surface the break; do not paper over it with compatibility layers
