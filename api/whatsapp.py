import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _lib.app import app  # noqa: E402,F401  (Vercel serves the WSGI `app`)
