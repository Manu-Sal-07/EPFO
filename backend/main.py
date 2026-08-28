import sys
import os

# Ensure backend directory is in Python module search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pfcompass.main import app  # noqa: F401
