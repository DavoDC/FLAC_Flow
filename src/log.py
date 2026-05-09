import logging
from datetime import datetime
from pathlib import Path

_LOG_DIR = Path(__file__).parent.parent / "data" / "logs"


def setup_logging() -> Path:
    """Configure file-only logging. Returns the log file path."""
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = _LOG_DIR / f"run_{timestamp}.log"

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

    return log_file
