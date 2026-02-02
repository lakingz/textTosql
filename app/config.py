from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    db_connection_string: str
    mcp_mode: str
    mcp_base_url: str
    default_schema: str
    default_table: str
    time_column: str
    metric_column: str
    time_window_minutes: int



def load_config() -> AppConfig:
    return AppConfig(
        db_connection_string=os.getenv("DB_CONNECTION_STRING", ""),
        mcp_mode=os.getenv("MCP_MODE", "local"),
        mcp_base_url=os.getenv("MCP_BASE_URL", "http://localhost:8000"),
        default_schema=os.getenv("DEFAULT_SCHEMA", "dbo"),
        default_table=os.getenv("DEFAULT_TABLE", "calls"),
        time_column=os.getenv("TIME_COLUMN", "event_time"),
        metric_column=os.getenv("METRIC_COLUMN", "hold_time_seconds"),
        time_window_minutes=int(os.getenv("TIME_WINDOW_MINUTES", "60")),
    )
