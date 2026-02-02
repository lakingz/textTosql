from __future__ import annotations

import requests

from app.config import load_config
from app.logging_utils import log_event
from app.models import QueryResponse, SQLRequest, SQLResponse


class MCPClient:
    def __init__(self) -> None:
        self.config = load_config()

    def generate_sql(self, payload: SQLRequest) -> SQLResponse:
        log_event("mcp.client.generate_sql", "input", payload.model_dump())
        if self.config.mcp_mode == "http":
            url = f"{self.config.mcp_base_url}/mcp/sql/generate"
            response = requests.post(url, json=payload.model_dump())
            response.raise_for_status()
            result = SQLResponse(**response.json())
            log_event("mcp.client.generate_sql", "output", result.model_dump())
            return result

        from app.mcp.server import generate_sql

        result = generate_sql(payload)
        log_event("mcp.client.generate_sql", "output", result.model_dump())
        return result

    def run_query(self, payload: SQLResponse) -> QueryResponse:
        log_event("mcp.client.run_query", "input", payload.model_dump())
        if self.config.mcp_mode == "http":
            url = f"{self.config.mcp_base_url}/mcp/sql/query"
            response = requests.post(url, json=payload.model_dump())
            response.raise_for_status()
            result = QueryResponse(**response.json())
            log_event("mcp.client.run_query", "output", {"row_count": len(result.rows)})
            return result

        from app.mcp.server import run_query

        result = run_query(payload)
        log_event("mcp.client.run_query", "output", {"row_count": len(result.rows)})
        return result
