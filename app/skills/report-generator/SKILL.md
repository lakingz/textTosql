---
name: report-generator
description: Generate a JSON report summary from query rows. Use when turning SQL results into aggregate metrics (count, average, min, max) for a chosen metric column.
---

# Report Generator

## Goal

Create a compact JSON report from query results for downstream consumption.

## Steps

1. Accept `rows` as a list of dicts and a `metric_key` string.
2. If no rows, return a report with `count=0` and a short summary.
3. Extract numeric values for `metric_key`.
4. If no numeric values, return a report with a warning summary.
5. Otherwise, compute `count`, `average`, `min`, and `max`.

## Output Shape

- `summary` (string)
- `count` (int)
- `average` (float, optional)
- `min` (float, optional)
- `max` (float, optional)

## Notes

- Do not mutate input rows.
- Keep output JSON stable; add new fields only when needed.
- This skill is implemented in `app/skills/report_generator_skill.py`.
