"""PreToolUse hook: enforce settings.json rules with inline guidance.

Two layers, fixed evaluation order:

1. Hardcoded blocks — CLAUDE.md rules that don't stick as prose. Block with
   inline redirection so the agent self-corrects without user intervention.

2. Dynamic settings.json enforcement — reads global (~/.claude/settings.json)
   and project (.claude/settings.json), merges allow/deny lists and allowed
   directories. Approves operations that settings would allow.
"""

from tools.environment import get_project_dir  # noqa: F401

from ._checking import *  # noqa: F403
from ._matching import *  # noqa: F403
from ._matching import _glob_match, _strip_env_assignments  # noqa: F401
from ._output import *  # noqa: F403
from ._parsing import *  # noqa: F403
from ._paths import *  # noqa: F403
from ._settings import *  # noqa: F403
