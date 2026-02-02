from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
import re

import pyodbc
from fastapi import APIRouter, HTTPException

from app.config import load_config
from app.logging_utils import log_event
from app.models import QueryResponse, SQLRequest, SQLResponse, TemplateRequest

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.post("/sql/generate", response_model=SQLResponse)
def generate_sql(payload: SQLRequest) -> SQLResponse:
    log_event("mcp.generate_sql", "input", payload.model_dump())
    config = load_config()
    req = payload.requirements

    schema = config.default_schema
    table = config.default_table
    time_col = config.time_column
    metric_col = config.metric_column

    where_clauses: list[str] = []
    parameters: dict[str, Any] = {}

    if req.date_hint and req.time_hint:
        start_dt = datetime.fromisoformat(f"{req.date_hint}T{req.time_hint}")
        end_dt = start_dt + timedelta(minutes=config.time_window_minutes)
        where_clauses.append(f"{time_col} >= :start_dt AND {time_col} < :end_dt")
        parameters["start_dt"] = start_dt.strftime("%Y-%m-%d %H:%M:%S")
        parameters["end_dt"] = end_dt.strftime("%Y-%m-%d %H:%M:%S")
    elif req.date_hint:
        where_clauses.append(f"CAST({time_col} AS date) = :date")
        parameters["date"] = req.date_hint
    elif req.time_hint:
        start_time = datetime.strptime(req.time_hint, "%H:%M:%S")
        end_time = start_time + timedelta(minutes=config.time_window_minutes)
        where_clauses.append(f"CAST({time_col} AS time) >= :start_time AND CAST({time_col} AS time) < :end_time")
        parameters["start_time"] = start_time.strftime("%H:%M:%S")
        parameters["end_time"] = end_time.strftime("%H:%M:%S")

    sql = f"SELECT {time_col}, {metric_col} FROM {schema}.{table}"
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    if req.direction == "low":
        sql += f" ORDER BY {metric_col} ASC"

    response = SQLResponse(sql=sql, parameters=parameters)
    log_event("mcp.generate_sql", "output", response.model_dump())
    return response


@router.post("/sql/render", response_model=SQLResponse)
def render_template(payload: TemplateRequest) -> SQLResponse:
    """Render a server-validated SQL template from a structured intent.

    Keeps the LLM output structured while enforcing whitelists and safe params.
    """
    log_event("mcp.render_template", "input", payload.model_dump())
    config = load_config()

    allowed_columns = {config.time_column, config.metric_column}
    columns = payload.columns or [config.time_column, config.metric_column]
    for c in columns:
        if c not in allowed_columns:
            raise HTTPException(status_code=400, detail=f"Column not allowed: {c}")

    schema = config.default_schema
    table = config.default_table

    select_cols = ", ".join(columns)
    if payload.limit:
        sql = f"SELECT TOP ({payload.limit}) {select_cols} FROM {schema}.{table}"
    else:
        sql = f"SELECT {select_cols} FROM {schema}.{table}"

    where_clauses: list[str] = []
    parameters: dict[str, Any] = {}

    if payload.filters.get("start_dt") and payload.filters.get("end_dt"):
        where_clauses.append(f"{config.time_column} >= :start_dt AND {config.time_column} < :end_dt")
        parameters["start_dt"] = payload.filters["start_dt"]
        parameters["end_dt"] = payload.filters["end_dt"]
    elif payload.filters.get("date"):
        where_clauses.append(f"CAST({config.time_column} AS date) = :date")
        parameters["date"] = payload.filters["date"]

    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)

    if payload.order:
        sql += f" ORDER BY {payload.order}"

    response = SQLResponse(sql=sql, parameters=parameters)
    log_event("mcp.render_template", "output", response.model_dump())
    return response


@router.post("/sql/query", response_model=QueryResponse)
def run_query(payload: SQLResponse) -> QueryResponse:
    log_event("mcp.run_query", "input", payload.model_dump())
    config = load_config()

    if not config.db_connection_string:
        response = QueryResponse(rows=[])
        log_event("mcp.run_query", "output", response.model_dump())
        return response

    connection = pyodbc.connect(config.db_connection_string)
    cursor = connection.cursor()

    # Build positional params from named :param placeholders and use driver binding
    sql = payload.sql
    params: list[Any] = []
    placeholder_re = re.compile(r":([a-zA-Z_][a-zA-Z0-9_]*)")
    matches = placeholder_re.findall(sql)
    if matches:
        for name in matches:
            if name not in payload.parameters:
                cursor.close()
                connection.close()
                raise HTTPException(status_code=400, detail=f"Missing parameter: {name}")
            params.append(payload.parameters[name])
        # replace all named placeholders with ? for pyodbc
        sql = placeholder_re.sub("?", sql)

    cursor.execute(sql, params)
    columns = [col[0] for col in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    response = QueryResponse(rows=rows)
    log_event("mcp.run_query", "output", {"row_count": len(rows)})
    return response
