# Normalize operation

Turn a raw instruction set into a **target-normalized** operation-file the queue can drive — or exit naming why it can't. Runs once, before flattening; its output is the per-item instruction baked into the cache-warm payload, so a target left un-abstracted here busts the prefix on every spawn and forfeits the entire saving.

## Variables

- {raw} — the raw instruction set (path or text): what to do to a target
- {items} — the queue's target tokens (or a representative sample), so the target's *kind* is known
- {out} — path to write the normalized operation-file

## The target contract

A normalized operation operates on **exactly one TARGET per spawn**, supplied at runtime by `queue.py next`. The file must open with the contract, then state the procedure against the abstract target:

```
# Operation

You will be given exactly one TARGET — {target-kind} — emitted by the queue.
Operate only on that TARGET; do not reference, read, or depend on any other item.

{the procedure, phrased against TARGET}

Output: {where output lands, expressed purely as a function of TARGET}
```

## Reshapeability gate

The instruction qualifies only if all four hold. Judge each against {raw} + {items}; if one fails irreducibly (can't be rewritten to satisfy it), **Exit process** naming the failed criterion and what to change.

1. **Single target axis** — exactly one thing varies per item; the procedure and disciplines are invariant. (Fails: two independent things vary per run and can't collapse to one token.)
2. **Opaque-token-expressible** — the target is one token a queue can yield (path, id, string). (Fails: the "target" is a structured bundle of unrelated inputs.)
3. **Independence** — processing one target needs nothing from another target's output or ordering. (Fails: item N consumes item N−1's result — sequential spawns are independent by design.)
4. **Self-contained output** — where output lands is a function of the target alone. (Fails: output location depends on aggregate/cross-item state.)

## Process

1. Read {raw} and inspect {items} to identify the **varying target** and its kind.
2. Run the reshapeability gate:
    - For each criterion, decide pass / reshapeable / irreducible-fail.
    - If any criterion is an irreducible fail: **Exit process** — `cannot normalize: {criterion} — {what about {raw} violates it} — {how to adjust}`.
3. Rewrite {raw} into the target contract:
    1. Abstract every concrete target reference to the TARGET role.
    2. Preserve the procedure and any disciplines/criteria verbatim in intent.
    3. State the output as a function of TARGET (a path derived from it, DB rows keyed by it, a file in a named output dir).
    4. Apply /process-authoring to the procedure and /concise-prose to the whole — no target literals, no cross-item language ("for each", "all of them", "the rest") survive.
4. Write the result to {out}. Return {out}.

## Note

The gate protects the cache contract, not correctness of the operation itself — a normalized file can still describe a bad operation. Normalization only guarantees the operation is *shaped* for independent, per-target, cache-warm fan-out.
