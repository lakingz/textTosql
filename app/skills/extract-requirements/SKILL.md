---
name: extract-requirements
description: Extract structured requirements from raw text for the text-to-SQL pipeline. Use when converting user questions into a normalized schema with metric, direction, and time/date hints.
---

# Extract Requirements

## Goal

Convert raw user text into an `ExtractedRequirements` object used by the SQL generation step.

## Steps

1. Normalize the input (trim, preserve original).
2. Detect the metric name (default: `hold`).
3. Detect direction hints (e.g., `low`, `high`).
4. Detect time-of-day hints and convert to `HH:MM:SS` (24-hour).
5. Detect date hints (e.g., `today`, `yesterday`) and convert to `YYYY-MM-DD`.
6. Return an object with nulls for any missing fields.

## Output Shape

- `metric` (string)
- `direction` (string or null)
- `time_hint` (string or null)
- `date_hint` (string or null)
- `original_text` (string)

## Notes

- Keep parsing conservative: prefer nulls over guessing.
- This skill is implemented in `app/skills/extract_requirements_skill.py`.
