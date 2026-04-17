"""Governance library facade.

Public interface for governance operations — matching files to
applicable conventions, listing governance entries, and computing
the level-grouped dependency order.

Reads directly from disk — no database, no MCP server. Consumed
by the convention_gate hook, the governance CLI, and evaluation skills.
"""

from ._frontmatter import *  # noqa: F401,F403
from ._governance import *  # noqa: F401,F403
