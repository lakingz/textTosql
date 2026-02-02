from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    raw_text: str = Field(..., description="Raw user text input")
    output_sql_only: bool = Field(False, description="Return only the generated SQL")


class ExtractedRequirements(BaseModel):
    metric: str
    direction: Optional[str] = None
    time_hint: Optional[str] = None
    date_hint: Optional[str] = None
    original_text: str


class SQLRequest(BaseModel):
    requirements: ExtractedRequirements


class TemplateRequest(BaseModel):
    template: str
    columns: Optional[list[str]] = None
    filters: dict[str, Any] = Field(default_factory=dict)
    order: Optional[str] = None
    limit: Optional[int] = None


class SQLResponse(BaseModel):
    sql: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class QueryResponse(BaseModel):
    rows: list[dict[str, Any]]


class ReportResponse(BaseModel):
    requirements: ExtractedRequirements
    sql: str
    data: list[dict[str, Any]]
    report: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)
