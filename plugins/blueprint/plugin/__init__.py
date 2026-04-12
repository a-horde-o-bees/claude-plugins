"""Generic plugin framework.

Universal deployment, formatting, skill discovery, and orchestration
for init and status operations. No plugin-specific logic — skill
infrastructure lives in skill-level _init.py files.

Propagated to every plugin via pre-commit hook.
"""

from ._environment import *  # noqa: F403
from ._metadata import *  # noqa: F403
from ._deployment import *  # noqa: F403
from ._formatting import *  # noqa: F403
from ._content import *  # noqa: F403
from ._discovery import *  # noqa: F403
from ._permissions import *  # noqa: F403
from ._orchestration import *  # noqa: F403
