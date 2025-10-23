import sys
import os

# ✅ Ensure the current directory is on the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app  # ✅ this will now work
