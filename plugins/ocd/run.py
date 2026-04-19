"""Module launcher with package context.

Adds the plugin root and its systems/ directory to sys.path and runs the
target module via runpy.run_module, establishing proper __package__
context for relative imports within packages.

Auto-promotes bare names to `systems.<name>` when that submodule exists,
so the CLI surface reads as `ocd-run pdf` rather than `ocd-run
systems.pdf`. Top-level modules (hooks.*) stay as-is because no
`systems.hooks` exists to promote to.

systems/ on sys.path is what makes `import framework` resolve to
`systems/framework/` in consumer modules across the plugin — the
framework package is hosted under systems/ rather than plugin root so it
aligns with every other system's location.

Usage:
    python3 run.py pdf --src foo.md          # resolves to systems.pdf
    python3 run.py navigator scan .          # resolves to systems.navigator
    python3 run.py hooks.auto_approval       # left as-is (dotted, not promoted)
    python3 run.py framework init            # framework CLI via systems.framework
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
# module paths and pass through unchanged.
if "." not in module and importlib.util.find_spec(f"systems.{module}") is not None:
    module = f"systems.{module}"

sys.argv = sys.argv[1:]

import runpy  # noqa: E402

runpy.run_module(module, run_name="__main__")
