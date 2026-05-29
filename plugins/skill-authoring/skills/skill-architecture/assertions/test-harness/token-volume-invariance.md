# token-volume-invariance

## Verdict

**Confirmed.** Server-reported total token volume — `input_tokens + cache_creation_input_tokens + cache_read_input_tokens + output_tokens` — is invariant across identical `claude -p` calls. The `cache_creation`/`cache_read` split and `total_cost_usd` are not: they vary with cache warmth and run order — the first call to see a given prefix writes cache and costs ~2× a later call that reads it. Token volume tracks content: a different prompt moves the sum by exactly the content delta. Therefore token volume, not cost, is the cache-invariant efficiency metric for cross-variant and cross-phase comparison. Verified on single-turn calls (Opus 4.7); multi-turn workflows add run-to-run variance from model nondeterminism, so sample-average there. Last verified 2026-05-23.

## Canonical artifact

```
volume(call) = usage.input_tokens
             + usage.cache_creation_input_tokens
             + usage.cache_read_input_tokens
             + usage.output_tokens

marginal_cost(mechanism) = volume(variant) − volume(baseline)
```

Read all four fields from each `claude -p` JSON return's `usage` block — they are server-reported and authoritative (each appears per API turn in `stream-json`; the `result` event carries the correct aggregate, so read it there rather than summing per-turn blocks, which repeat). To isolate a mechanism's cost — a skill-body injection, an extra dependency, a longer directive — subtract the baseline call's volume from the variant's. The subtraction is reproducible regardless of cache warmth or phase order. Do NOT use `total_cost_usd` for this: it is client-derived and warmth-dependent.

## Why this matters

Every efficiency assertion — `claude-p-cost-floor`, `dep-test-iterations`, any future "does mechanism X cost more" probe — compares measurements across variants or phases. If the metric moves with cache state, those comparisons are confounded: a phase run later in a sequence rides a warmer cache and looks cheaper regardless of its actual work. This exact artifact made `dep-test-iterations`' iter3 appear cheaper than iter1. Token volume is immune — it measures context processed, blind to the cache discount — so it is the only metric supporting baseline-subtraction across a sequential orchestration.

## Probe

Two arms, each a bare `claude -p` call — no control skill needed; the apparatus is the prompt itself. Each prompt embeds a fresh per-run nonce so the first call is guaranteed to hit a cold cache, reproducing the cold→warm transition rather than depending on a pre-warmed prefix.

### Arm A — identical calls (invariance)

Five calls with the same nonce-bearing prompt. The token-volume sum must be identical across all five; the create/read split and cost may differ (call 1 cold, calls 2–5 warm).

### Arm B — different prompt (sensitivity / positive control)

Two calls with a second, larger nonce-bearing prompt. Their volumes must equal each other but differ from Arm A's — confirming the metric tracks content and is not a constant artifact.

### Runner prompt

- Arm A: `Reply with exactly the word: ok [nonce=<uuidA>]`
- Arm B: `Reply with exactly these five words: alpha beta gamma delta epsilon [nonce=<uuidB>]`

The nonce is a per-run UUID — identical within an arm, different between arms.

## Procedure

Orchestrator (Bash loop + Python parse); no skill files to create or clean up, no scratch state, each call a fresh session:

1. Generate two UUID nonces, one per arm.
2. For each of A1–A5 and B1–B2: run `claude -p --output-format json --no-session-persistence "<arm prompt + nonce>" < /dev/null`, capture the JSON.
3. From each return's `usage`, compute `volume = input + cache_creation + cache_read + output`.
4. Assert: the five A volumes are identical; the two B volumes are identical; A-volume ≠ B-volume.
5. Record one A row, both B rows, and the per-call cost spread in the verification log.

## Detection method

The split/cost-variance checks apply to a prompt's first (cold) call vs its later (warm) calls — demonstrated by B1 vs B2 below, and by A1 vs A2–5 in any nonced re-run.

| Check | Pass condition | Meaning |
|---|---|---|
| Invariance | All Arm-A volumes equal | Sum is cache-invariant across identical calls |
| Split variance | A prompt's cold call `cache_create` > 0; its warm calls `cache_create` ≈ 0 | Warmth shifts the create/read split |
| Cost variance | Cold call cost > warm call cost (same prompt) | Cost is warmth-dependent — disqualifies it as the cross-phase metric |
| Sensitivity | Arm-A volume ≠ Arm-B volume | Sum tracks content; not a constant artifact |

All four must hold. Invariance + sensitivity establish the metric; split/cost variance establish why cost is unusable cross-phase.

## Verification log

| Date | Call | Prompt | input | create | read | output | volume | cost ($) | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 2026-05-23 | A1–A5 | "…the word: ok" | 3776 | 0 | 14641 | 4 | 18421 | 0.0268 | All 5 identical (prefix pre-warmed, no nonce this run); volume invariant ✓ |
| 2026-05-23 | B1 (cold) | "…five words…" | 3776 | 4339 | 10315 | 16 | 18446 | 0.0521 | First sight of prompt → create-heavy |
| 2026-05-23 | B2 (warm) | "…five words…" | 3776 | 0 | 14654 | 16 | 18446 | 0.0271 | Same volume as B1; cost halved — warmth shifts split+cost only |

A-volume (18421) ≠ B-volume (18446), differing by the +13 prefix / +12 output content delta — sensitivity confirmed. Arm A lacked a nonce this run so its calls were pre-warmed (no cold A1); the nonce in the Procedure fixes this for re-runs. The cold→warm-at-constant-volume transition is carried by B1 vs B2.
