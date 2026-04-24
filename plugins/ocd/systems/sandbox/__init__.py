"""Sandbox orchestration — substrate setup/teardown primitives and verb implementations.

Interactive planning for `project`, `worktree`, and `exercise` remains in
`SKILL.md` (user confirms the plan via `AskUserQuestion`); the mechanical
steps that follow — substrate lifecycle, subprocess orchestration,
cleanup — live here as Python so skill-side bash invocations stay simple
and don't trigger permission heuristics on compound shell patterns.

Project-level test orchestration via detached worktrees lives at
`tools/testing/_sandbox.py` (invokable as `bin/project-run sandbox-tests`)
rather than here — it depends on this project's test infrastructure and
should not ship with the plugin.
"""

from ._cleanup import *  # noqa: F401,F403
from ._project import *  # noqa: F401,F403
from ._worktree import *  # noqa: F401,F403
