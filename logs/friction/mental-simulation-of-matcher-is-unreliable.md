# Mental simulation of matcher behavior is unreliable

## What happened

While refining `description-authoring`, I drafted a description and wrote out 20 adversarial trigger-eval queries with predicted trigger / no-trigger outcomes for each. The predictions were presented to the user as if measured.

Later, a single-query pilot run (`claude -p "Help me write the description for this new skill"`, model: Haiku) showed the **matcher did not fire** for what I had confidently predicted as a should-trigger query. The agent answered directly without invoking the Skill tool.

## Why mental simulation failed

- The matcher is the model's forward-pass decision over the skill list. It doesn't enumerate keyword overlap; it weights semantic fit against all visible alternatives.
- A description that reads obviously-applicable to a human (or to my own simulation of reading) may not compel the model to invoke the skill — especially when the agent thinks it can answer the query directly without help.
- Model variance: Haiku's invocation threshold differs from Sonnet/Opus. The model running the test affects the result.
- The query's "weight" affects invocation. Lightweight requests ("help me write a description") may not feel skill-worthy to the matcher; heavier framing ("help me write a description that will reliably trigger Claude's matcher without false positives") might.

## How to apply

- **Don't substitute prediction for measurement** when claiming a description triggers. Either run the actual eval or label predictions as predictions.
- **Run a dry-test before extrapolating** to full eval cost. One `claude -p` subprocess call (~6 seconds, ~$0.24 in Opus) calibrates the prediction error rate before committing to 300 calls per skill.
- **Use the same model in eval that the user runs interactively.** Predictions and measurements alike depend on which model decides.
- **Mental simulation is not worthless** — it produces the draft. The error is asserting it as evidence.

## Related

- [logs/patterns/description-refinement-two-phase-loop.md](../patterns/description-refinement-two-phase-loop.md) — the two-phase pipeline that separates draft (where simulation belongs) from measurement.
- [logs/problem/description-authoring-fails-haiku-matcher.md](../problem/description-authoring-fails-haiku-matcher.md) — the specific instance.
- `honesty` skill body has the underlying principle as a bullet: "Before any quantitative claim: verify the number against its source. Never state 'X years' or 'N commits' from memory — check." Trigger-rate predictions are quantitative claims.
