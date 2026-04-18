"""Sandbox orchestration — substrate setup/teardown primitives and verb implementations.

Interactive planning for `project`, `worktree`, and `exercise` remains in
`SKILL.md` (user confirms the plan via `AskUserQuestion`); the mechanical
steps that follow — substrate lifecycle, subprocess orchestration,
cleanup — live here as Python so skill-side bash invocations stay simple
and don't trigger permission heuristics on compound shell patterns.

`tests` is fully non-interactive and has no planning phase. The skill
delegates its whole lifecycle to `ocd-run sandbox tests`.
"""

from ._cleanup import *  # noqa: F401,F403
from ._project import *  # noqa: F401,F403
from ._tests import *  # noqa: F401,F403
from ._worktree import *  # noqa: F401,F403
