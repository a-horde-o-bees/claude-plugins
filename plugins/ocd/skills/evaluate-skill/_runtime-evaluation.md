# Runtime Evaluation Workflow

Agent workflow for exercising a skill pathway in an isolated worktree and comparing actual behavior against documented claims.

## Context

You are running in a git worktree — an isolated copy of the repository. File changes, commits, and skill invocations stay contained without affecting the main working tree. The Agent tool is not available — execute any `Spawn agent with:` steps yourself within your own context.

Git push is blocked by the orchestrator before you were spawned. Any `git push` attempt will fail with `fatal: '/dev/null' does not appear to be a git repository` — this is expected safety behavior, not an error to investigate or work around.

## Steps

1. Read the target skill's SKILL.md at the path provided by the orchestrator
2. Note the skill's documented claims:
    - Workflow steps — what each step says will happen
    - Report section — expected output format and content
    - Error Handling section — prescribed failure behavior
    - Rules section — behavioral constraints
    - Description — what the skill says it does
3. If the route requires preconditions (e.g., uncommitted changes for a commit skill, specific file state):
    1. Set up the minimum preconditions needed in the worktree
4. Invoke the skill via the Skill tool with the arguments provided by the orchestrator
5. Follow the skill's instructions as loaded by the Skill tool
    - If the skill contains `Spawn agent with:` steps: execute those steps yourself
    - If the skill exits to user: record what would have been presented and note the exit point
    - If the skill attempts git push: the push will fail with the expected safety error — record "push blocked by worktree isolation" and continue
    - If the skill enters a convergence loop or recursive pattern: bail when you recognize repeated state — runtime evaluation aims to observe behavior, not exhaust iterations
6. After the skill completes (or exits), compare what happened against the documented claims from step 2:
    - CLI output accuracy — does actual output match what the Report section claims?
    - Workflow step correctness — did each step execute as described?
    - Error handling — if a failure occurred, did the Error Handling section cover it?
    - Description accuracy — does the purpose statement match what actually happened?
    - Exit behavior — did the skill exit at the expected point for this route?

## Return Format

Return a flat list of findings. Each finding names:

- Route exercised — skill name and arguments used
- Claim being verified — cite the SKILL.md section and specific text
- Expected behavior — what the skill documents
- Actual behavior — what happened
- Discrepancy — what differs, or "matched" if behavior aligns
- Proposed fix — concrete edit to the skill's files that would resolve the discrepancy, or `needs judgment` if the fix requires choosing between changing documentation vs changing implementation

If the exercised route produced no discrepancies, return a single finding with "matched" for all claims verified.
