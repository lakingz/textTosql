from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    log_path = os.getenv("LOG_PATH", "app.log")

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setLevel(logger.level)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def log_event(module: str, event: str, payload: dict[str, Any]) -> None:
    logger = get_logger("text_to_sql")
    record = {
        "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "module": module,
        "event": event,
        "payload": payload,
    }
    logger.info(json.dumps(record, ensure_ascii=True))
