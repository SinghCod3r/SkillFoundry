"""Domain data models for SkillFoundry."""

from skillfoundry.models.analysis import (
    APIEndpoint,
    Capability,
    CLICommand,
    CodeExample,
    FileInfo,
    ProjectAnalysis,
    ProjectMetadata,
    Workflow,
)
from skillfoundry.models.evaluation import (
    ComparisonResult,
    DimensionScore,
    EvaluationResult,
    EvaluationRun,
    EvaluationTask,
    Score,
    ScoringWeights,
    TaskResult,
)
from skillfoundry.models.report import ReportData, ReportMetadata
from skillfoundry.models.skill import GeneratedSkill, ReferenceFile, SkillMetadata

__all__ = [
    "APIEndpoint",
    "CLICommand",
    "Capability",
    "CodeExample",
    "ComparisonResult",
    "DimensionScore",
    "EvaluationResult",
    "EvaluationRun",
    "EvaluationTask",
    "FileInfo",
    "GeneratedSkill",
    "ProjectAnalysis",
    "ProjectMetadata",
    "ReferenceFile",
    "ReportData",
    "ReportMetadata",
    "Score",
    "ScoringWeights",
    "SkillMetadata",
    "TaskResult",
    "Workflow",
]
