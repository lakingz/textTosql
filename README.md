# Text to SQL Report Agent

Minimal FastAPI service that turns raw text into SQL, optionally queries SQL Server, and returns a JSON report.

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Example request

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/report -ContentType 'application/json' -Body '{"raw_text":"why we are having a low hold today around 3:00 am","output_sql_only":true}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/extract -ContentType 'application/json' -Body '{"raw_text":"why we are having a low hold today around 3:00 am","output_sql_only":false}'
```

### LLM → Template (recommended)

Have the LLM produce a structured intent (template + params) and call the render endpoint to produce validated, parameterized SQL:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/mcp/sql/render -ContentType 'application/json' -Body '{"template":"time_window_select","columns":["event_time","hold_time_seconds"],"filters":{"start_dt":"2026-02-02 03:00:00","end_dt":"2026-02-02 04:00:00"},"order":"hold_time_seconds ASC","limit":100}'
```

Then execute the returned SQL via `/mcp/sql/query` (server will bind parameters safely).

## Environment

Copy `.env.example` to `.env` and fill out `DB_CONNECTION_STRING` for SQL Server access.
Logging is JSON lines in `LOG_PATH` (default `app.log`) with `LOG_LEVEL` control.
