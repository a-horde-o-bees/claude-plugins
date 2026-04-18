"""Centralized check system.

Runs universal discipline checks (dormancy today; additional dimensions
slot in as separate modules) against any system folder — this plugin's
systems or a foreign plugin's. Scanner detects which surfaces a system
exposes; per-dimension checkers run the applicable assertions.

Returns structured CheckResult objects. Presentation for CLI display
belongs in __main__.py.
"""

from ._scanner import *  # noqa: F401,F403
from ._dormancy import *  # noqa: F401,F403
