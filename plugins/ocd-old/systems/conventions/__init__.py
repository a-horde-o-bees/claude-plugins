"""Conventions library facade.

Public interface for the conventions system — both the deployment
side (init/status/clean) and the matching side (governance_match,
governance_list, frontmatter parsing). The matching infrastructure
moved here from the former systems/governance/ — conventions is now
the backbone for both file-content governance and per-file convention
discovery.

Reads directly from disk on every matching call — no database, no
caching. Consumed by the convention_gate hook, the conventions CLI,
the navigator's scope_analyze tool, and evaluation skills.
"""

from ._frontmatter import *  # noqa: F401,F403
from ._init import *  # noqa: F401,F403
from ._matching import *  # noqa: F401,F403
