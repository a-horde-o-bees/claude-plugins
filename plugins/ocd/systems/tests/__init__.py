"""ocd-run tests — plugin-venv-aware test runner.

Discovers project-level and per-plugin pytest suites in the current
working directory and runs each under its own venv. Each plugin's tests
execute under the plugin's installed venv (where its declared
requirements live), so tests that import plugin-venv-only packages
(mcp, weasyprint, markdown) work without leaking those dependencies
into the project venv.

Stateless — no worktree creation, no ref resolution, no cleanup.
Worktree isolation at a clean ref is provided by `/ocd:sandbox tests`,
which creates a detached worktree and invokes this CLI inside it.
Running `ocd-run tests` directly exercises the current working tree for
fast dev feedback.
"""

from ._runner import *  # noqa: F401,F403
