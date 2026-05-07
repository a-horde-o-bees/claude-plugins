---
tagline: Enforce correctness through structure, not documentation
---

# Make Invalid States Unrepresentable

Enforce correctness through structure, not documentation. When the system's structure prevents incorrect usage, documentation becomes confirmation rather than instruction. Prefer enforcement mechanisms over prose rules at every layer — data, schemas, tool interfaces, file organization.

- Database constraints reject invalid values rather than relying on callers to validate
- Purpose-built interfaces accept only meaningful inputs rather than generic parameters requiring documentation
- Structural and organizational decisions are deterministic — produce the same result regardless of who evaluates them
- Before defining a skill's argument surface: use positional verbs for mutually-exclusive modes (one-of-N required) and flags for independent modifiers that combine freely. Flags for mutually-exclusive options permit invalid combinations like `--list --install`; positional verbs make one-of-N structurally impossible to violate
