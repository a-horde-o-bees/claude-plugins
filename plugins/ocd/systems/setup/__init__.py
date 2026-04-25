"""Install/init/status orchestration for plugin systems.

Deployment, formatting, system/skill discovery, and orchestration for
init, status, enable, and disable operations. No plugin-specific logic
— skill infrastructure lives in each system's `_init.py`.

Environment and error primitives that hooks need on the critical path
live under `<plugin>/tools/` rather than here, because setup is opt-in
and dormant by default. The canonical sources at project-root `tools/`
propagate into every plugin's own `tools/` via `.githooks/pre-commit`.

This package itself is also propagated to every plugin via pre-commit
hook — plugins share the same install/init/status surface.
"""

from ._enabled import effective_enabled, read_enabled, write_enabled  # noqa: F401
from ._metadata import *  # noqa: F403
from ._deployment import *  # noqa: F403
from ._formatting import *  # noqa: F403
from ._system_discovery import *  # noqa: F403
from ._orchestration import *  # noqa: F403
