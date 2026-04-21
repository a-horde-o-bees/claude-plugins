"""Project-local setup operations.

Configures this project's dev-time git wiring and any other one-shot
setup steps that used to run inside the ocd plugin's `install` but are
properly project-local concerns (not something ocd should auto-wire
when installed into an unrelated downstream project).
"""

from ._hookspath import *  # noqa: F403
from ._orchestration import *  # noqa: F403
