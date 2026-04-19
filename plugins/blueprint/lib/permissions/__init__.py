"""Permissions subsystem facade.

Public interface for auto-approve pattern management — list coverage,
install recommended patterns, analyze cross-scope health, clean
redundant entries. Consumed by plugin/__main__.py CLI and by the
/ocd:setup guided flow.
"""

from ._operations import *  # noqa: F403
from ._init import *  # noqa: F403
