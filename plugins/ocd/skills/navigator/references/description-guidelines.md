# Description Guidelines

Guidelines for writing path tree entry descriptions during `/navigator` scan/describe workflows.

## Core Question

Each description answers: **should I read this file?** An agent scanning entries makes an include-or-skip decision per entry. Description must convey scope — what domain and responsibility the file covers — so agents can route to the right file without opening it.

## What to Include

- **Scope** — what domain or responsibility the file covers
- **Role** — what kind of thing it is (business logic, CLI, config, convention)

## What to Exclude

- **Internal mechanics** — how algorithms work, what patterns are used, implementation details
- **Content listing** — section names, function names, class names
- **History** — why the file exists, what it replaced, when it was added

## Description Semantics

- NULL description — entry not yet reviewed; shows as `[?]`
- Empty string description — self-explanatory name, marks as reviewed
- Non-empty description — entry reviewed, description provided

## Markers

- `[?]` — new entry, needs description written from scratch
- `[~]` — stale entry, file contents changed since description was written; re-evaluate against current file scope

## Quality Test

If two files have the same description, description is too vague. If description would change when file internals are refactored but responsibility stays the same, description is too detailed.
