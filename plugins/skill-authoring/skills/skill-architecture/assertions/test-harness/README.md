# Test harness

Assertions about the runtime we verify everything else with: `claude -p` invocations, their measurement model, and cost.

## Assertions

| File | Status | Verdict |
|---|---|---|
| [`token-volume-invariance.md`](./token-volume-invariance.md) | Confirmed | Total token volume is cache-invariant across identical calls; it — not cost — is the cross-phase efficiency metric |

The cost-floor question (cheapest `claude -p` flags that keep capabilities) is quarantined pending rebuild with `runner.py` + init-event ground truth.
