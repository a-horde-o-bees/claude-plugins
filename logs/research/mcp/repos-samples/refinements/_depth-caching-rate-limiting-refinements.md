# Depth Pass Refinements — Sample > Caching and rate-limiting infrastructure

Per-role cross-corpus refinement proposals from inspecting every sample's content under this role.

Role footprint: 4 paths, all 4 with supporting samples; 7 supporting-sample-section reads (2+2+2+1 = 7); ~1.4 KB of evidence content total. Small role, tight footprint.

## Description sharpenings

> Format: `<role-chain> > <path>` — what the existing description misses; cross-corpus evidence; sharpened text suggestion

`Sample > Caching and rate-limiting infrastructure > SQLite TTL cache` — the path name and description claim "in-process SQLite database … cache should survive process restarts," but only one of the two supporting samples (`mukul975--cve-mcp-server`) actually uses SQLite. The other (`awslabs--openapi-mcp-server`) explicitly uses `cachetools` — an in-memory dict-based TTL cache that does NOT survive process restarts and is not SQLite-backed. The awslabs sample's section text even calls this out: "not the persistent SQLite-backed variant the path name suggests." The current path name is a strict subset of what its supporting samples actually exhibit. Two reasonable directions:

- (A) **Rename the path** to a more general label that fits both samples — proposed: `In-process TTL cache` — and rework the description: "Server-side cache tier (per-call response or spec cache) with TTL eviction, used to absorb upstream rate limits or latency. Backing store varies — `cachetools` in-memory dict for ephemeral caches, SQLite (e.g., `aiosqlite`) when the cache should survive process restarts. Cache-hit status often surfaces in the audit log when one is present."
- (B) **Split into two paths** along the persistence axis: `In-memory TTL cache` (cachetools-style) and `Persistent SQLite TTL cache` (aiosqlite-style). Splitting only delivers value if more samples land in each bucket; with N=1 each, the rename in (A) is the lower-noise fix.

Recommend (A). Drop the audit-log claim from the path-level description (it's specific to the mukul975 implementation, not a universal property of in-process TTL caches) — or hedge it with "often" / "may" as in the proposed text.

`Sample > Caching and rate-limiting infrastructure > Token-bucket rate limiter` — the description says "Explicit rate-limiter module for upstream throttling (e.g., NVD's published quota). Appropriate when one upstream's quota is the binding constraint." This fits `mukul975--cve-mcp-server` precisely (NVD throttling is the named upstream), but `normaltusker--kotlin-mcp-server`'s evidence is generic "Server-side rate limiting for external API calls" with no specific upstream named, and the rate limiter in that sample is paired with a circuit breaker as a generic defensive layer — not driven by any one upstream's published quota. The current "one upstream's quota is the binding constraint" framing is too narrow and reads as if mukul975 is the only motivating case. Proposed sharpening: "Server-side rate limiter that throttles outbound calls to one or more upstreams. Implementations range from upstream-quota-driven (e.g., NVD's published quota) to generic defensive throttling paired with a circuit breaker. Appropriate when naive fan-out could exhaust an upstream's published quota or trip provider-side abuse heuristics."

Also: the path name asserts the algorithm is specifically "token-bucket," but neither supporting sample's section text confirms the algorithm. mukul975's text says "token-bucket" in the path name but the sample-section text just says "Explicit token-bucket rate-limiter module"; normaltusker's text says only "Server-side rate limiting." The path name may be over-specifying when the corpus only confirms "rate limiter" generically. Suggest renaming to `Outbound rate limiter` and folding "token-bucket" into the description as "commonly token-bucket."

`Sample > Caching and rate-limiting infrastructure > Circuit breaker for external calls` — description ("partial degradation is acceptable"; "many upstreams") is plausible but lightly grounded. The single supporting sample (`normaltusker--kotlin-mcp-server`) actually pairs circuit breaker with the rate limiter and audit logging as a single "defensive middleware stack," not as an independent choice motivated by upstream count. Proposed sharpening: "Circuit-breaker wrapping external API calls so a degraded upstream doesn't cascade into server failure. Often deployed alongside a rate limiter and audit logging as a defensive middleware stack. Appropriate when the server has external dependencies whose intermittent failures should not propagate as tool errors."

`Sample > Caching and rate-limiting infrastructure > Auto-cleanup of temporary export artifacts` — the current description blends two mechanisms that the supporting samples actually exhibit differently:

- `mongodb-js--mongodb-mcp-server` — resource (`exported-data://{name}`) with timed auto-cleanup (default 5 min). The artifact lives long enough for the client to fetch it; cleanup is deferred and TTL-driven.
- `samuelgursky--davinci-resolve-mcp` — exports deleted after response encoding. Cleanup is immediate, not TTL-driven; the artifact's lifetime is the response cycle.

The current description ("default 5 minutes") generalizes from mongodb and erases davinci-resolve's immediate-cleanup pattern. Proposed sharpening: "Server emits transient artifacts (export resources, scratch files) and deletes them automatically. Two cleanup disciplines observed: (1) TTL-bound resources that live long enough for the client to fetch (mongodb's `exported-data://{name}`, default 5 min); (2) immediate deletion after response encoding (davinci-resolve's exports). Cross-platform sandbox handling may be required when temp paths differ by OS. Appropriate when the server produces transient artifacts that shouldn't accumulate."

Also: this path is the only one in the role that doesn't fit the role description "modules that mediate how tools interact with upstreams" — auto-cleanup mediates how tools produce *outputs to the client*, not how they call *upstreams*. See "Cross-corpus observations" below.

## Sub-axis observations

> Format: `<role-chain> > <path>` — sub-pattern observed; supporting sample count; whether to fold into description or propose split

`Sample > Caching and rate-limiting infrastructure > SQLite TTL cache` — persistence sub-axis: in-memory (cachetools) vs persistent (SQLite). N=1 each. Too thin to justify a split; fold into the description per the rename proposal above.

`Sample > Caching and rate-limiting infrastructure > Auto-cleanup of temporary export artifacts` — cleanup-trigger sub-axis: time-bound TTL vs response-cycle bound. N=1 each. Too thin to split; fold into the description.

## Proposed bucket merges

None. The four paths describe distinct mechanisms (cache, rate limiter, circuit breaker, artifact cleanup) and the samples don't argue for any merging.

## Proposed bucket splits

None at this corpus size. The persistence sub-axis under SQLite TTL cache and the cleanup-trigger sub-axis under Auto-cleanup are real but each candidate bucket would have N=1. Hold for re-evaluation if the corpus grows.

## Mis-placed samples

`awslabs--openapi-mcp-server` is currently under `SQLite TTL cache` but does not implement SQLite — it uses `cachetools`. If path (A) above is adopted (rename to `In-process TTL cache`), the placement becomes correct. If split is preferred, this sample moves to a new `In-memory TTL cache` bucket. Either way: the placement is currently inaccurate against the path's literal name and needs reconciler attention.

## Cross-corpus observations

> Patterns visible only with full role visibility — surface even if not actionable now

**The role label "Caching and rate-limiting infrastructure" doesn't cover what the role actually contains.** The four paths split cleanly into two groups by mechanism:

- *Upstream-mediation* — SQLite TTL cache, Token-bucket rate limiter, Circuit breaker for external calls. All three throttle, cache, or guard the server's outbound call path. Matches the role's prose "how tools interact with upstreams."
- *Outbound-artifact lifecycle* — Auto-cleanup of temporary export artifacts. This guards what the server emits *back to the client*, not how it calls upstreams. Different mechanism, different purpose.

This is the largest cross-corpus signal: 3-1 split with auto-cleanup not fitting the role's stated scope. Possible reconciler responses:

- (A) Broaden the role description to "Cross-cutting modules that govern non-tool side effects — outbound throttling, response caching, artifact lifecycle." Lowest-cost fix; loses some sharpness.
- (B) Move `Auto-cleanup of temporary export artifacts` to a different role. The most plausible target is `Capability surface` or wherever resource lifecycle lives — both supporting samples expose the artifact as an MCP resource. Higher-cost fix; cleaner role boundaries. Worth flagging to reconciler; not actionable from inside this role.
- (C) Rename role to something like "Server-internal middleware and lifecycle" that explicitly accommodates both groups. Middle cost.

**Defensive-stack co-occurrence.** `normaltusker--kotlin-mcp-server` is the only sample under both `Token-bucket rate limiter` and `Circuit breaker for external calls`, and the sample's evidence frames them as one defensive middleware layer (rate limiter + circuit breaker + audit logging). This is consistent with industry idiom — the two patterns travel together — but the corpus is too thin for the consolidated to assert it. Worth folding into both descriptions ("often deployed alongside …") rather than proposing structure.

**Adoption is small (5 samples / role) but not noisy.** Each path's two samples are genuinely different upstreams/domains (CVE feeds, AWS APIs, MongoDB exports, DaVinci media exports) — the patterns generalize. The role isn't overrepresented by one ecosystem.

**Convergence assessment.** This is a small, lightly-populated role where Pass 1/2/3 produced reasonable bucket boundaries but the path-level descriptions were calibrated to the *first* supporting sample for each path. Cross-corpus inspection surfaces meaningful gaps in 3 of 4 path descriptions — most importantly, the SQLite TTL cache path name is literally wrong for half its evidence. The depth pass earned its keep here.
