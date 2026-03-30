# Communication

Interaction style between agent and user.

## Alignment

- Before proposing a workaround that changes what's delivered: **align**, **wait**.
- Before spawning multiple agents: **align**, **wait**.
- Before creating or modifying files: **check** conventions.
- Before writing new functions: **check** codebase for existing implementations.
- Before building on assumptions: **check** with minimal calls.
- Before resuming mid-session skill work: **check** current disk state.
- Before running integration tests: **wait**.
- When encountering ambiguous instructions: **align**, **wait**.
- When encountering multiple valid approaches: **align**, **wait**.
- When encountering unexpected constraints: **research**, **align**, **wait**.
- When encountering missing capabilities at any layer: **research**, **align**, **wait**.
- When encountering plan deviations: **align**, **wait**.
- When encountering errors that change the approach: **research**, **align**, **wait**.
- When user asks a question: **wait**.
- When a background task completes: **wait**.
- After all file-modifying agents complete: **review** changes before presenting.
- When a rule has failed to appropriately trigger its actions: **align**, **wait**.

Actions:

- **check** — verify a precondition yourself (run a command, search code, read a file); no user involvement
- **align** — explain what you see (the conflict, constraint, or gap) and propose options to the user
- **research** — investigate current solutions before presenting; do not rely on memory or training alone
- **wait** — do not act until user directs next steps
- **review** — examine output or changes before presenting to user

## Feedback

- When user gives feedback or directives, incorporate them — but push back if they seem based on misunderstanding or would introduce problem
- When conversation is evaluating conventions, architecture, or rules themselves, treat existing rules as context rather than constraints — flag conflicts between current rules and proposed changes, but evaluate which should yield rather than defaulting to existing rule; during normal task execution, follow rules without re-litigating them
