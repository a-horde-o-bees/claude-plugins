"""Path setup for navigator tests."""

import sys
from pathlib import Path

# Insert at position 0 to ensure navigator's _db.py is found before
# any other plugin's _db.py that may also be on sys.path.
_scripts_dir = str(Path(__file__).resolve().parent.parent)
if _scripts_dir in sys.path:
    sys.path.remove(_scripts_dir)
sys.path.insert(0, _scripts_dir)
