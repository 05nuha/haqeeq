"""Local dev server on :5328 (next dev proxies /api/* here). Run: python -m api.dev"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _lib.app import app  # noqa: E402

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5328)), debug=True)
