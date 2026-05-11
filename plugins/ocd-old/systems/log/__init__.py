"""Log system facade.

Deployment contract lives in `_init.py` (templates + rules deployment).
Runtime research-analysis helpers live in the `research` subpackage
and are re-exported here for library callers; CLI dispatch lives in
`__main__.py`. The legacy add/list/remove verbs remain skill-level
workflow fragments (`_add.md`, `_list.md`, `_remove.md`) — they don't
need Python runtime code.
"""

from ._init import *  # noqa: F401,F403
from .research import *  # noqa: F401,F403
