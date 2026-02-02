from __future__ import annotations

from fastapi import FastAPI
from dotenv import load_dotenv

from app.mcp.server import router as mcp_router
from app.models import ExtractedRequirements, ReportRequest, ReportResponse
from app.skills.extract_requirements_skill import extract_requirements
from app.workflow import run_report_pipeline

load_dotenv()

app = FastAPI(title="Text to SQL Report Agent")
app.include_router(mcp_router)


@app.post("/report", response_model=ReportResponse)
def create_report(payload: ReportRequest) -> ReportResponse:
    return run_report_pipeline(payload.raw_text, payload.output_sql_only)


@app.post("/extract", response_model=ExtractedRequirements)
def extract_only(payload: ReportRequest) -> ExtractedRequirements:
    return extract_requirements(payload.raw_text)
