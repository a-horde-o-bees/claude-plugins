# Testing

External resources informing testing conventions and practices.

Each entry: URL followed by scope description — what domain the resource covers and what value it provides, sufficient to decide whether to visit without describing everything at the link.

- https://cliwatch.com/blog/can-ai-agents-use-your-cli — Analysis of what makes CLIs usable by AI agents; parseable output, discoverable help, predictable behavior
- https://coding-is-like-cooking.info/2025/12/test-desiderata-2-0/ — Emily Bache's reorganization of Beck's desiderata into four macro properties: fast, cheap, predictive, supports design changes
- https://datagrid.com/blog/4-frameworks-test-non-deterministic-ai-agents — Four frameworks for testing non-deterministic agent behavior; probabilistic validation approaches
- https://dev.to/nebulagg/how-to-test-ai-agents-before-they-burn-your-budget-53kl — Testing patterns for AI agent infrastructure; mock the LLM, test routing and safety logic, evaluate non-deterministic behavior separately
- https://dev.to/uenyioha/writing-cli-tools-that-ai-agents-actually-want-to-use-39no — CLI design for AI agent consumption; stdout as API contract, exit code semantics, error message structure for agent self-correction
- https://docs.pact.io/ — Pact contract testing documentation; consumer-driven contract testing patterns applicable to agent-CLI interfaces
- https://fsharpforfunandprofit.com/posts/property-based-testing-2/ — Property-based testing property hierarchy: no exception < type preservation < invariant < idempotence < roundtrip; choosing which properties to test
- https://interrupt.memfault.com/blog/testing-vs-overhead — Balancing test coverage against overhead; allocating testing effort proportionally to failure impact
- https://martinfowler.com/articles/nonDeterminism.html — Fowler on eradicating non-determinism in tests; why flaky tests erode suite trust and how to eliminate sources of non-determinism
- https://martinfowler.com/testing/ — Fowler's testing guide index; covers test pyramid, contract testing, test doubles, and testing strategies
- https://medium.com/@kentbeck_7670/test-desiderata-94150638a4b3 — Kent Beck's test desiderata; 12 properties of good tests with trade-off framework for when properties conflict
- https://testdesiderata.com/ — Interactive reference for Beck's test desiderata with property definitions and relationships
- https://www.equalexperts.com/blog/our-thinking/testing-infrastructure-as-code-3-lessons-learnt/ — Testing infrastructure-as-code; why testing configuration values is theater vs testing functional behavior
- https://www.sei.cmu.edu/blog/seven-recommendations-for-testing-in-a-non-deterministic-world/ — CMU SEI recommendations for testing non-deterministic systems; applicable to agent-driven workflows
- https://yrkan.com/blog/property-based-testing/ — Property-based testing for system invariants; practical examples of generative testing applied to infrastructure
