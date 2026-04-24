"""Parent-walking sample fixture.

Packs every pattern the scanner must flag, alongside chains that must
NOT be flagged (because they don't root at `__file__`), into one file
so scans can assert detection and non-detection in a single pass.

Not a real module — the scanner parses the AST only. Filename uses
the `fixture_*.py` convention so pytest's `collect_ignore_glob`
skips it. Tests locate assertions by identifier name (HERE, TWO_UP,
NESTED_DIRNAME, …) so edits to this docstring won't break them.

Violations flag under the rule `"Python - parent-walking"` when the
chain's leftmost expression is `__file__`. Any chain rooted in a
variable, a literal, or any other expression is legitimate.
"""

from __future__ import annotations

import os
from os.path import dirname
from pathlib import Path

# Arbitrary path values — NOT __file__. Used below to demonstrate that
# the scanner flags rooting-at-__file__, not arbitrary .parent usage.
SOME_PATH = Path("/etc/hosts")
OTHER_PATH = "/var/log/syslog"


# ───── Violations: chains rooted at __file__ (MUST flag) ─────

# single .parent rooted at __file__
HERE = Path(__file__).parent

# .parents[0] rooted at __file__
IMMEDIATE = Path(__file__).parents[0]

# single os.path.dirname of __file__
ONE_UP = os.path.dirname(__file__)

# chained .parent.parent — depth 2
TWO_UP = Path(__file__).parent.parent

# chained .parent four deep
FOUR_UP = Path(__file__).parent.parent.parent.parent

# .parents[N] with N >= 1
ONE_PARENTS = Path(__file__).parents[1]

# .parents[N] with N much greater
THREE_PARENTS = Path(__file__).parents[3]

# nested dirname (2 levels) — both calls root at __file__
NESTED_DIRNAME = os.path.dirname(os.path.dirname(__file__))

# deeper nested dirname
DEEP_DIRNAME = dirname(dirname(dirname(__file__)))


# ───── Non-violations: chains NOT rooted at __file__ (must NOT flag) ─────

# chain rooted at a variable, not __file__
VAR_PARENT = SOME_PATH.parent

# deeply chained but rooted at a variable
VAR_DEEP = SOME_PATH.parent.parent.parent

# .parents[N] on a non-__file__ base
VAR_PARENTS = SOME_PATH.parents[3]

# dirname of a non-__file__ value
VAR_DIRNAME = os.path.dirname(OTHER_PATH)

# dirname of a literal string
LITERAL_DIRNAME = dirname("/tmp/foo/bar")
