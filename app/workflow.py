from __future__ import annotations

from app.config import load_config
from app.logging_utils import log_event
from app.mcp.client import MCPClient
from app.models import ReportResponse, SQLRequest
from app.skills.extract_requirements_skill import extract_requirements
from app.skills.report_generator_skill import generate_report


def run_report_pipeline(raw_text: str, output_sql_only: bool) -> ReportResponse:
    log_event("workflow", "input", {"raw_text": raw_text, "output_sql_only": output_sql_only})
    requirements = extract_requirements(raw_text)
    config = load_config()
    mcp = MCPClient()

    sql_request = SQLRequest(requirements=requirements)
    sql_response = mcp.generate_sql(sql_request)

    if output_sql_only:
        rendered_sql = sql_response.sql
        for key, value in sql_response.parameters.items():
            rendered_sql = rendered_sql.replace(f":{key}", f"'{value}'")
        response = ReportResponse(
            requirements=requirements,
            sql=rendered_sql,
            data=[],
            report={},
            warnings=[],
        )
        log_event("workflow", "output", response.model_dump())
        return response

    query_response = mcp.run_query(sql_response)
    report = generate_report(query_response.rows, metric_key=config.metric_column)

    warnings: list[str] = []
    if not query_response.rows:
        warnings.append("No data returned. Check DB connection string and schema mapping.")

    response = ReportResponse(
        requirements=requirements,
        sql=sql_response.sql,
        data=query_response.rows,
        report=report,
        warnings=warnings,
    )
    log_event("workflow", "output", {"row_count": len(response.data), "warnings": response.warnings})
    return response
