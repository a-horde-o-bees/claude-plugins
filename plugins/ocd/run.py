"""Module launcher with package context.

Adds the plugin root and its systems/ directory to sys.path and runs
the target module via runpy.run_module, establishing proper __package__
context for relative imports within packages.

Auto-promotes bare names to `systems.<name>` when that submodule
exists, so the CLI surface reads as `ocd-run pdf` rather than `ocd-run
systems.pdf`. Top-level modules (hooks.*) stay as-is because no
`systems.hooks` exists to promote to.

Plugin root on sys.path is what makes `from tools import environment`
and `from tools.errors import NotReadyError` resolve — the vendored
`tools/` package lives at plugin root so always-on primitives are
reachable from every module without depending on the opt-in setup
system being deployed.

Multi-word system names use hyphen on the CLI surface (`ocd-run
needs-map`) but underscore as their Python package (`systems.needs_map`)
because Python identifiers cannot contain hyphens. Hyphens in the bare
name are rewritten to underscores before the systems.<name> lookup.

Usage:
    python3 run.py pdf --src foo.md          # resolves to systems.pdf
    python3 run.py navigator scan .          # resolves to systems.navigator
    python3 run.py needs-map summary         # resolves to systems.needs_map (hyphen → underscore)
    python3 run.py hooks.auto_approval       # left as-is (dotted, not promoted)
    python3 run.py setup init                # install/init CLI via systems.setup
"""

import sys
from pathlib import Path

plugin_root = str(Path(__file__).parent)
systems_dir = str(Path(__file__).parent / "systems")
for entry in (systems_dir, plugin_root):
    if entry not in sys.path:
        sys.path.insert(0, entry)

import importlib.util  # noqa: E402

module = sys.argv[1]
# Only promote bare (no-dot) names — dotted forms are treated as explicit
# module paths and pass through unchanged. Hyphens rewrite to underscores
# so CLI surface `ocd-run needs-map` resolves to `systems.needs_map`.
if "." not in module:
    candidate = module.replace("-", "_")
    if importlib.util.find_spec(f"systems.{candidate}") is not None:
        module = f"systems.{candidate}"

sys.argv = sys.argv[1:]

import runpy  # noqa: E402

runpy.run_module(module, run_name="__main__")
