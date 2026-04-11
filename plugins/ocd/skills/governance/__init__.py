"""Governance skill facade.

Public interface for governance operations — loading rules and
conventions from disk, matching files to applicable conventions,
and computing the level-grouped dependency order.

Consumed by the ocd-governance MCP server, the governance CLI
entry point, and the convention_gate hook.
"""

from ._db import get_connection, init_db, SCHEMA  # noqa: F401
from ._frontmatter import (  # noqa: F401
    matches_pattern,
    normalize_patterns,
    parse_governance,
    read_frontmatter,
)
from ._governance import (  # noqa: F401
    governance_list,
    governance_load,
    governance_match,
    governance_order,
)
