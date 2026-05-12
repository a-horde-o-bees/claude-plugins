# Workflow vs Script

Triggers whenever an author writes a PFN Process step. For every action, decide: workflow markdown or script the workflow invokes? Same trigger fires when adding helpers behind existing workflows, when reviewing a step that "feels mechanical," and when migrating legacy verb files where inline bash blurred the line.

Workflow markdown is the bridge between agent-facing instruction and mechanical code. Each step belongs on one side of that bridge.

Always encode in workflow:

- Reasoning, judgment, contextual decision-making, sequencing the agent must steer.
- Orchestrating disparate systems (e.g. skill calls, tool invocations, agent spawns) whose composition depends on intermediate results.
- User-facing surface — review gates, clarifying questions, error-recovery dialogues.

Always delegate to a script:

- Mechanically resolvable operations (e.g. lookups, mutations, generation, transformations) — JSON parsing, string slicing, list filtering, aggregation, format conversion, deterministic classification.

Antipatterns:

- Scripts that dictate agent actions or require agent intervention mid-execution — scripts are encapsulated operations with deterministic outcomes; if a script needs the agent to decide something, the decision belongs in the workflow.
- Workflow steps that parse, filter, aggregate, or transform data inline — that work belongs in a script the workflow invokes.

Tell which side of the bridge a step sits on by asking: could a deterministic function with no agent context produce this result correctly? If yes, script. If the step needs judgment, orchestration, or user-facing presentation, workflow.
