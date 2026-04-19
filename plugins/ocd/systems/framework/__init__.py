"""Generic plugin framework.

Universal deployment, formatting, system/skill discovery, orchestration
for init and status operations, test-suite discovery, pytest dispatch,
and per-plugin venv resolution. No plugin-specific logic — skill
infrastructure lives in skill-level _init.py files.

Propagated to every plugin via pre-commit hook.
"""

from ._environment import *  # noqa: F403
from ._metadata import *  # noqa: F403
from ._deployment import *  # noqa: F403
from ._formatting import *  # noqa: F403
from ._system_discovery import *  # noqa: F403
from ._orchestration import *  # noqa: F403
from ._test_discovery import *  # noqa: F403
from ._test_runner import *  # noqa: F403
from ._venv import *  # noqa: F403
from ._errors import NotReadyError  # noqa: F401
