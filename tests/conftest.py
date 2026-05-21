"""
pytest configuration for the tests/ directory.

Adds the project root to sys.path so that app.py, i18n.py, etc.
can be imported without modification regardless of where pytest is invoked.
"""
import sys
from pathlib import Path

# Project root = parent of this file's directory
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
