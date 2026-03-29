"""Module launcher with package context.

Adds the plugin root to sys.path and runs the target module via
runpy.run_module, establishing proper __package__ context for
relative imports within packages.

Usage:
    python3 run.py scripts.plugin_cli init
    python3 run.py skills.research get stats --db path/to/db
"""

import sys
from pathlib import Path

plugin_root = str(Path(__file__).parent)
if plugin_root not in sys.path:
    sys.path.insert(0, plugin_root)

module = sys.argv[1]
sys.argv = sys.argv[1:]

import runpy  # noqa: E402

runpy.run_module(module, run_name="__main__")
