"""
pytest configuration for the tests/ directory.

Adds src/ (the application package root) to sys.path so that app.py,
i18n.py, etc. can be imported without modification regardless of where
pytest is invoked.
"""
import sys
from pathlib import Path

# src/ = sibling of tests/ inside the project root
SRC_ROOT = Path(__file__).parent.parent / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
