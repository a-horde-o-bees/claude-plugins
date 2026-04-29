"""transcripts facade.

Public interface over Claude Code transcript analysis. Re-exports DB helpers,
ingestion, scope navigation (projects/sessions/exchanges), settings, derived
stats, and the init/status/ready contract from internal modules. The CLI in
__main__.py dispatches to these names.

Data is the events table (one row per JSONL event, idempotent on file+line)
plus two derived views: events_with_gaps (exchange + gap_s columns) and
chat_messages (filtered to user/assistant text). Re-runs of ingest only add
newly-appended lines from active transcripts. See ARCHITECTURE.md for the
full schema, time-accounting model, and event catalog.
"""

from ._db import *  # noqa: F401,F403
from ._ingest import *  # noqa: F401,F403
from ._purposes import *  # noqa: F401,F403
from ._scope import *  # noqa: F401,F403
from ._settings import *  # noqa: F401,F403
from ._stats import *  # noqa: F401,F403
from ._init import ready, ensure_ready, init, reset, status  # noqa: F401
