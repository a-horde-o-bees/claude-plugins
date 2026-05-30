---
name: skill-architecture
description: Skill-structure guidance backed by verified platform-behavior assertions. UNDER RECONSTRUCTION — the prior recommendations rested on a flawed measurement mechanic and have been withdrawn; this skill currently surfaces no guidance. Do not load it for authoring recommendations until the rebuild lands. See GOALS.md and assertions/README.md.
---

# skill-architecture

**Status: under reconstruction — no guidance to serve.**

The recommendations this skill used to ship (`architecture.md`, justified by `confirmed-facts.md`) rested on a flawed measurement mechanic: single-run observations, self-reported call counts, cache-confounded cost. Re-running with a sound mechanic showed key "facts" were artifacts of that method (e.g. idempotent dependency loading is actually nondeterministic). Those claims are quarantined and the recommendations are withdrawn rather than left to mislead callers.

Until the rebuild lands, this skill intentionally surfaces nothing. Loading it as a `## Dependencies` entry is a no-op.

- **Goals / north star:** [`GOALS.md`](GOALS.md)
- **Rebuild status + foundational ladder:** [`assertions/README.md`](assertions/README.md)
- **Suspect, do-not-cite:** [`confirmed-facts.md`](confirmed-facts.md), [`architecture.md`](architecture.md)
