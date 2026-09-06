"""Data models for report generation."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from skillfoundry.models.evaluation import ComparisonResult, EvaluationResult


class ReportMetadata(BaseModel):
    """Metadata recorded for reproducibility."""

    skillfoundry_version: str = ""
    evaluation_version: str = "1.0"
    model_provider: str = ""
    model_identifier: str = ""
    skill_hash: str = ""
    task_set_hash: str = ""
    config_hash: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ReportData(BaseModel):
    """Structured data used to generate both JSON and HTML reports."""

    skill_name: str
    source_path: str = ""
    metadata: ReportMetadata = Field(default_factory=ReportMetadata)
    evaluation: EvaluationResult | None = None
    comparison: ComparisonResult | None = None
    recommendations: list[str] = Field(default_factory=list)
    generated_files: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
