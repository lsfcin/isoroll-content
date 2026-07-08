#!/usr/bin/env python3
"""conftest.py — pytest path bootstrap: make src/cli and src/pipeline modules importable."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
for _sub in ("cli", "pipeline"):
    _p = str(_ROOT / "src" / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)
