---
includes: "*"
---

# Convention as Documentation

Structure communicates intent — organization itself conveys meaning, so readers can locate relevant content without needing explanatory documentation. Names, locations, patterns, and hierarchies encode meaning that should be readable without a guide.

- File naming and ordering encode relationships without needing a separate guide
- Names are verbose and convey purpose — not truncated for visual format
- Script names match the domain concept they implement
- Each type of content has one home — rules govern behavior, conventions govern file content, CLAUDE.md governs project procedures
- Before authoring any name (verb, function, file, identifier): check the candidate against the actual behavior — does the term literally describe what happens? If the term is broader than the function (e.g. `gate` for code that watches without blocking; `manage` / `handle` / `process` when the function is more specific), name down to the behavior or pick a tighter term. Apply during initial drafting, not after user review
