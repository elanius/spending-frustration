"""Central logging setup for the backend.

Creates a `.logs` directory at the project root and configures a rotating
file handler plus a console handler. The log level is controlled by the
`LOG_LEVEL` environment variable (defaults to INFO).
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Compute project root (two parents up from this file: backend/app -> backend -> project root)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = PROJECT_ROOT / ".logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"
_FORMATTER = logging.Formatter(_FORMAT, _DATEFMT)


def setup_logging() -> None:
    """Configure root logging handlers.

    Safe to call multiple times; it will not duplicate handlers for the
    same file or add multiple console handlers.
    """
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)

    # File handler (rotating)
    existing_file = False
    for h in root.handlers:
        if isinstance(h, RotatingFileHandler) and getattr(h, "baseFilename", None) == str(LOG_FILE):
            existing_file = True
            break

    if not existing_file:
        fh = RotatingFileHandler(str(LOG_FILE), maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(_FORMATTER)
        root.addHandler(fh)

    # Console handler (useful during development)
    has_stream = any(isinstance(h, logging.StreamHandler) for h in root.handlers)
    if not has_stream:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(_FORMATTER)
        root.addHandler(ch)

    # Reduce verbosity from some noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("pymongo").setLevel(logging.WARNING)


__all__ = ["setup_logging", "LOG_DIR", "LOG_FILE"]
