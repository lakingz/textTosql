from __future__ import annotations

import re
from datetime import datetime

from app.logging_utils import log_event
from app.models import ExtractedRequirements


TIME_RE = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", re.IGNORECASE)


def extract_requirements(raw_text: str) -> ExtractedRequirements:
    log_event("extract_requirements", "input", {"raw_text": raw_text})
    normalized = raw_text.strip()
    metric = "hold"
    direction = None
    time_hint = None
    date_hint = None

    if "low" in normalized.lower():
        direction = "low"

    time_match = TIME_RE.search(normalized)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or "0")
        meridiem = time_match.group(3).lower()
        if meridiem == "pm" and hour != 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0
        time_hint = f"{hour:02d}:{minute:02d}:00"

    if "today" in normalized.lower():
        date_hint = datetime.now().strftime("%Y-%m-%d")

    result = ExtractedRequirements(
        metric=metric,
        direction=direction,
        time_hint=time_hint,
        date_hint=date_hint,
        original_text=raw_text,
    )
    log_event("extract_requirements", "output", result.model_dump())
    return result
