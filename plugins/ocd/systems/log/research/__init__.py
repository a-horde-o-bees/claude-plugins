"""Research-log analysis subpackage of the log system.

Provides heading-tree parsing, duplicate-heading detection, and cross-
sample aggregation helpers for markdown samples under a project's
`logs/research/<subject>/samples/` directory. Exposed via CLI as
`ocd-run log research <verb>` and via the `/log research` skill route;
the tools also import directly for Python callers (e.g., future
retrofit engines, test fixtures).
"""

from ._sample_tools import *  # noqa: F401,F403
from ._compliance import *  # noqa: F401,F403
