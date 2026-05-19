---
name: borrow-before-build
description:
---

# Borrow Before Build

Before producing new code, abstractions, structures, or tools, examine what already exists — in the codebase, language standard library, framework, or community ecosystem — and adopt or extend rather than invent. Novelty is justified only when continuity can't carry the work and the gap is named. Existing implementations are tested, understood, and maintained; new ones start with none of those properties.

- Adopt well-exercised tools and patterns over custom builds when they fulfill the purpose
- Prefer composition of existing components over new abstractions for one-time operations
- Before writing a new function: search the codebase first
- Before designing a new abstraction or helper: mirror the call shape, role split, and return type of the closest existing analog rather than designing in isolation
- When two or more systems duplicate orchestration of existing primitives: extract a shared helper that mirrors the closest existing helper pattern; system declares, helper resolves
- Before building a tool or helper for a recurring problem (e.g., linting, parsing, CLI argument-handling, schema validation, retry logic, test fixtures): check what the standard library, framework, and community already provide; the conventional option is the default
- Before introducing a non-conventional pattern, unusual tool choice, or custom abstraction with no community precedent: name what made the conventional option insufficient — deviations need affirmative justification, not silent adoption
- Before proposing alternatives for missing capabilities: research existing solutions first, then explain the gap; proceed after user directs
