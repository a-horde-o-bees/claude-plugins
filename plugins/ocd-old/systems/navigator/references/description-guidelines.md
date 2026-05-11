# Description Guidelines

Navigator-specific guidance for populating path purposes during `/navigator` scan/describe workflows. What to include and exclude in a purpose follows the Purpose Statement section of the design principles — scope and role, not internal mechanics, content listing, or history.

## Purpose Semantics

- NULL purpose — path not yet reviewed; shows as `[?]`
- Empty string purpose — self-explanatory name, marks as reviewed
- Non-empty purpose — path reviewed, purpose populated per the Purpose Statement principle

## Markers

- `[?]` — new path, needs purpose populated from scratch
- `[~]` — stale path, file contents changed since purpose was written; re-evaluate against current scope
