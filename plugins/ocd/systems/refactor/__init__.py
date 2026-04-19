"""Codemods — agent-callable tools for mass source transformations.

Today: `rename_symbol` for AST-aware Python identifier renames across a
scope of files. Future: other mechanical transforms (move a module,
restructure imports, rewrite a pattern) that currently require
iterative sed and surface false-positive risk.

The tools under this system are invoked both directly (`ocd-run refactor
<subcommand>`) and through the `/ocd:refactor` skill, which wraps them
in the Mass Rename workflow — pre-scan, plan, apply, verify, test.
"""

from ._rename_symbol import *  # noqa: F401,F403
