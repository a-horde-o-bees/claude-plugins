"""Project-level test orchestration.

Discovers project-level and per-plugin test suites, resolves each
suite's venv, runs pytest per suite, and compiles a unified report.
Also provides the detached-worktree wrapper that runs tests against an
arbitrary ref while keeping the main working tree clean.
"""

from ._discovery import *  # noqa: F403
from ._runner import *  # noqa: F403
from ._sandbox import *  # noqa: F403
from ._venv import *  # noqa: F403
