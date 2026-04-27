"""needs-map facade.

Public interface over the needs-map domain — components and needs
linked by dependency and addressing edges, with per-component source
paths. The facade re-exports CRUD and query functions from internal
modules (_entities, _edges, _queries, _db); the CLI in __main__.py
dispatches to these names.

Data is accumulated evaluation work: rationales, need-tree refinements,
and addressing claims that survive across sessions. Not regenerable by
scan — the audit state IS the output. See needs-map's ARCHITECTURE.md
for the data model and design rationale.
"""

from ._db import *  # noqa: F401,F403
from ._entities import *  # noqa: F401,F403
from ._edges import *  # noqa: F401,F403
from ._queries import *  # noqa: F401,F403
from ._init import ready, ensure_ready, init, reset, status  # noqa: F401
