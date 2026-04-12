# Description Guidelines

Navigator-specific guidance for path tree entry descriptions during `/navigator` scan/describe workflows. What to include and exclude in a description follows the Purpose Statement section of the design principles — scope and role, not internal mechanics, content listing, or history.

## Description Semantics

- NULL description — entry not yet reviewed; shows as `[?]`
- Empty string description — self-explanatory name, marks as reviewed
- Non-empty description — entry reviewed, description provided

## Markers

- `[?]` — new entry, needs description written from scratch
- `[~]` — stale entry, file contents changed since description was written; re-evaluate against current file scope
