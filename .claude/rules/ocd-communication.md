# Communication

Interaction style between agent and user.

## Alignment

- Before proposing a workaround that changes what's delivered: **align**, **wait**.
- Before spawning multiple agents: **align** (include expected agent count and token impact), **wait**.
- Before creating or modifying files: **check** conventions.
- Before writing new functions: **check** codebase for existing implementations.
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
- When user asks a question: **wait**.
- When evaluating conventions, architecture, or rules: treat existing rules as context rather than constraints — flag conflicts but evaluate which should yield; during normal execution, follow rules without re-litigating.
- After all file-modifying agents complete: **review** changes before presenting.
- When a rule has failed to appropriately trigger its actions: **align**, **wait**.
- When the user fails to address or acknowledge all questions: **align**, **wait**.

Actions:

- **check** — verify a precondition yourself (run a command, search code, read a file); no user involvement
- **align** — explain what you see (the conflict, constraint, or gap) and propose options to the user
- **research** — investigate current solutions before presenting; do not rely on memory or training alone
- **wait** — do not act until user directs next steps
- **review** — examine output or changes before presenting to user

## Feedback

- When user gives feedback or directives, incorporate them — but push back if they seem based on misunderstanding or would introduce problem
