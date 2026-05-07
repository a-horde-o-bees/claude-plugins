---
tagline: Adopt existing tools and patterns before writing new code or abstractions
---

# Borrow Before Build

Before producing new code, abstractions, structures, or tools, examine what already exists — in the codebase, in the language standard library, in the framework, in the community ecosystem — and adopt or extend rather than invent. Novelty is justified only when continuity demonstrably can't carry the work, and the gap is named explicitly. Existing implementations are tested, understood, and maintained; new ones start with none of those properties. Conventional, maintained options exist for nearly every recurring problem.

- Adopt well-exercised tools and patterns over custom builds when they fulfill the purpose
- Prefer composition of existing components over new abstractions for one-time operations
- Before writing a new function: search the codebase first
- Before designing a new abstraction or helper: ask what existing pattern in the codebase should this match — mirror the call shape, role split, and return type of the closest existing analog rather than designing in isolation
- When two or more systems duplicate orchestration of existing primitives: extract the orchestration into a shared helper that mirrors the closest existing helper pattern; system declares, helper resolves
- Before building a tool, library, or helper for a recurring problem (linting, formatting, parsing, CLI argument-handling, schema validation, retry logic, test fixtures, file-watching, etc.): check what the language standard library, framework, and community already provide; the conventional option is the default
- Before introducing a non-conventional pattern, an unusual tool choice, or a custom abstraction with no community precedent: name what made the conventional option insufficient — the default is the ecosystem norm; deviations need affirmative justification, not silent adoption
- Before proposing alternatives for missing capabilities: research existing solutions first, then explain the gap; proceed after user directs
