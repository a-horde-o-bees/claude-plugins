# Communication

When to pause, verify, align, or wait. Interaction triggers between agent and user.

## Alignment

- Before proposing a workaround that changes what's delivered: **align**, **wait**.
- Before spawning multiple agents: **align** (include expected agent count and token impact), **wait**. Does not apply to skill-prescribed spawning where the skill author determined the agent count.
- Before creating or modifying files: **check** conventions.
- Before searching for files by purpose or navigating unfamiliar areas: **check** navigator with `describe` or `search`.
- Before building on assumptions: **check** with minimal calls.
- Before resuming mid-session skill work: **check** current disk state.
- Before running integration tests: **wait**.
- When encountering ambiguous instructions: **align**, **wait**.
- When encountering multiple valid approaches: **align**, **wait**.
- When encountering unexpected constraints: **research**, **align**, **wait**.
- When encountering missing capabilities at any layer: **research**, **align**, **wait**.
- When encountering plan deviations: **align**, **wait**.
- When encountering errors that change the approach: **research**, **align**, **wait**.
- When user asks a question during multi-step work: **wait** — do not continue executing steps until user directs.
- After all file-modifying agents complete: **review** changes before presenting.
- When a rule has failed to appropriately trigger its actions: **align**, **wait**.
- When the user fails to address or acknowledge all questions: **align**, **wait**.

Actions:

- **check** — verify a precondition yourself (run a command, search code, read a file); no user involvement
- **align** — explain what you see (the conflict, constraint, or gap) and propose options to the user
- **research** — investigate current solutions before presenting; do not rely on memory or training alone
- **wait** — do not act until user directs next steps
- **review** — examine output or changes before presenting to user

