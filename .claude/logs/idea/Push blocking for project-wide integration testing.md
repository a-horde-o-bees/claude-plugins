# Push blocking for project-wide integration testing

Push blocking (`git config remote.origin.pushurl "file:///dev/null"`) is currently used narrowly — evaluate-skill wraps runtime agents with it as a safety boundary. The mechanism has broader potential for integration testing across the whole project.

## Opportunity

Any integration test that exercises skills, hooks, or commands that might attempt git push could benefit from push blocking wrapping the test environment. This gives integration tests the same safety envelope as worktree-isolated evaluation without requiring worktrees.

## Refactor direction

- Extract push blocking into a reusable test fixture (pytest fixture or similar)
- Audit integration test suites for places where push could accidentally fire
- Consider whether certain test categories should be wrapped by default
