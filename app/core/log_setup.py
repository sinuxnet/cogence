import json
import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

_TEHRAN_TZ = ZoneInfo("Asia/Tehran")

_SKIP_ATTRS = frozenset(
    "args exc_info exc_text levelname levelno message msg name pathname "
    "filename module funcName created msecs relativeCreated thread threadName "
    "processName process stack_info lineno".split()
)


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry: dict = {
            "timestamp": datetime.now(tz=_TEHRAN_TZ).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _SKIP_ATTRS and not key.startswith("_"):
                entry[key] = value
        if record.exc_info:
            entry["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False, default=str)


def setup_logging(level: str = "INFO", log_file: str | None = None) -> None:
    formatter = _JsonFormatter()

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    root = logging.getLogger("cogence")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.addHandler(stream_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"cogence.{name}")
