---
log-role: queue
---

# Plugin dev iteration requires marketplace refresh and restart cycle

Each round-trip for a plugin fix (especially when the agent is dogfooding the plugin itself) takes 3–4 minutes of mechanical operations and at least one session restart:

1. Code change in `plugins/<plugin>/`
2. Run tests
3. Commit + push to main
4. `claude plugins marketplace update <marketplace>` to refresh the cache
5. `claude plugins update <plugin>@<marketplace>` to advance the cached copy
6. `/exit` + `claude --continue` to load the new cached code into the agent

This session went through this cycle 5+ times for progressive-skill-composer (collision fix → project-dir guard → schema cleanup → --destination rename → any-depth probe → rename). Each cycle is correct in isolation, but the aggregate cost is high enough that batching fixes into bigger commits becomes tempting (and counterproductive — multiple concerns in one commit fights the topic-grouped commit discipline).

Potential mitigations:

- A dev-mode plugin install that symlinks the source directory rather than caching a fetched version. Existing plugin tooling may already support this; investigate.
- A `/checkpoint --skip-restart` flag (or the inverse — make restart opt-in for cases where the agent isn't depending on the new code).
- Tighter `ocd:sandbox` integration so plugin development can iterate against a working tree directly, no marketplace round-trip.

This is operational friction more than architectural — but the loop cost shapes how plugin development feels, so it's worth tracking.
