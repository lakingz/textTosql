from __future__ import annotations

from statistics import mean

from app.logging_utils import log_event


def generate_report(rows: list[dict[str, object]], metric_key: str) -> dict[str, object]:
    log_event("report_generator", "input", {"row_count": len(rows), "metric_key": metric_key})
    if not rows:
        result = {
            "summary": "No data returned for the query.",
            "count": 0,
        }
        log_event("report_generator", "output", result)
        return result

    metric_values: list[float] = []
    for row in rows:
        value = row.get(metric_key)
        if isinstance(value, (int, float)):
            metric_values.append(float(value))

    if not metric_values:
        result = {
            "summary": "No numeric metric values found in query results.",
            "count": len(rows),
        }
        log_event("report_generator", "output", result)
        return result

    avg_value = mean(metric_values)
    result = {
        "summary": "Report generated from query results.",
        "count": len(rows),
        "average": avg_value,
        "min": min(metric_values),
        "max": max(metric_values),
    }
    log_event("report_generator", "output", result)
    return result
