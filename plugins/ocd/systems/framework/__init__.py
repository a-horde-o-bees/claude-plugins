"""Generic plugin framework.

Universal deployment, formatting, system/skill discovery, and orchestration
for init and status operations. No plugin-specific logic — skill
infrastructure lives in skill-level _init.py files.

Test orchestration (discovery, runner, venv resolution) moved to
`tools/testing/` at project root — it depends on this project's test
layout and is not a plugin concern.

Propagated to every plugin via pre-commit hook.
"""

from ._enabled import effective_enabled, read_enabled, write_enabled  # noqa: F401
from ._environment import *  # noqa: F403
from ._metadata import *  # noqa: F403
from ._deployment import *  # noqa: F403
from ._formatting import *  # noqa: F403
from ._system_discovery import *  # noqa: F403
from ._orchestration import *  # noqa: F403
from ._errors import NotReadyError  # noqa: F401
