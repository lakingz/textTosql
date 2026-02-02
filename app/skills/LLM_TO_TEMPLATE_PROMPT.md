# LLM → Template Prompt (Structured Intent)

Purpose
-------
This prompt instructs the LLM to convert user natural language into a small, structured JSON intent that maps to server-side SQL templates. The server will validate and render parameterized SQL from this structured output.

System message (high-level)
---------------------------
You are a structured SQL intent generator. Respond ONLY with valid JSON that follows the Output Schema below. Do not output raw SQL. Use ISO datetimes (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS) for date/time values. Do not include commentary, markdown, or code fences.

Constraints
-----------
- Only use allowed column names: event_time, player_id, reward, totalwin, totalbet, hold_time_seconds, last_activity
- Use only template names: time_window_select, mom_drop, inactive_players, big_wins
- If you cannot confidently map to a template, set `confidence` < 0.7 and add a short `explain` string.
- Stick to simple, serializable types (strings, numbers, arrays, objects, booleans).

Output Schema
-------------
{
  "template": "<string>",      // one of the allowed templates
  "columns": ["col1","col2"], // optional, subset of allowed columns
  "filters": { },                // simple key->value filters (start_dt, end_dt, date, min_reward, drop_pct, inactive_days)
  "aggregations": { },           // optional (e.g., {"metric":"monthly_gains","agg":"SUM"})
  "order": "col DESC",         // optional
  "limit": 100,                  // optional
  "confidence": 0.0,            // 0.0 - 1.0
  "explain": "short_reason"    // optional for human review
}

Prompt (user message)
---------------------
Given the user request: "<USER_TEXT>", map it to one of the allowed templates. Output only the JSON intent that follows the Output Schema.

Few-shot examples
-----------------
1) MoM drop
User: "Show players whose monthly winnings dropped more than 30% vs last month"
JSON:
{
  "template":"mom_drop",
  "columns":["player_id","monthly_gains","prev_month_gains"],
  "filters":{"reference_month":"2026-01-01","drop_pct":0.30},
  "order":"mom_drop DESC",
  "limit":100,
  "confidence":0.92
}

2) Inactive players
User: "List players who have been inactive for 30 days"
JSON:
{
  "template":"inactive_players",
  "columns":["player_id","last_activity"],
  "filters":{"inactive_days":30},
  "order":"last_activity ASC",
  "limit":500,
  "confidence":0.95
}

3) Lucky big wins
User: "Who had unusually large single-session wins (> 10000) in the last 7 days"
JSON:
{
  "template":"big_wins",
  "columns":["player_id","reward","event_time"],
  "filters":{"min_reward":10000,"start_dt":"2026-01-26 00:00:00","end_dt":"2026-02-02 00:00:00"},
  "order":"reward DESC",
  "limit":50,
  "confidence":0.92
}

4) Time-window select
User: "Why did we have a low hold around 3:00 am today?"
JSON:
{
  "template":"time_window_select",
  "columns":["event_time","hold_time_seconds"],
  "filters":{"start_dt":"2026-02-02 03:00:00","end_dt":"2026-02-02 04:00:00"},
  "order":"hold_time_seconds ASC",
  "confidence":0.9
}

Temperature & settings
----------------------
- Use low temperature (0.0–0.2) to favor deterministic outputs.
- Ask the model to always return `confidence` to indicate certainty.

Validation notes (server-side)
------------------------------
- Server must validate allowed columns and type formats (ISO datetimes, numeric ranges).
- Server should reject unknown templates or columns with HTTP 400 and a helpful message.

Troubleshooting
---------------
- If the LLM returns invalid JSON, re-prompt with: "Output must be valid JSON only and conform to the Output Schema."  
- If ambiguous user text, return `confidence` < 0.7 and include human-friendly `explain` for review.
