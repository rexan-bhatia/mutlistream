"""Run the local MusicStream development server."""

import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import app  # noqa: E402


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8083, debug=False)
