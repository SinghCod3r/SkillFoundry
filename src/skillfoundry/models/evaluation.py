"""Data models for evaluation, scoring, and comparison."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class EvaluationType(StrEnum):
    """Type of evaluation judge."""

    EXACT_MATCH = "exact_match"
    CONTAINS = "contains"
    REGEX = "regex"
    STRUCTURED = "structured"
    LLM_JUDGE = "llm_judge"
    COMMAND_RESULT = "command_result"
    FILE_DIFF = "file_diff"
    PYTHON_AST = "python_ast"


class EvaluationTask(BaseModel):
    """A single evaluation task used to benchmark skill quality."""

    id: str
    description: str
    prompt: str
    expected_capabilities: list[str] = Field(default_factory=list)
    evaluation_type: EvaluationType = EvaluationType.LLM_JUDGE
    criteria: list[str] = Field(default_factory=list)
    expected_output: str | None = None
    expected_pattern: str | None = None
    category: str = ""
    difficulty: str = "medium"


class TaskResult(BaseModel):
    """Result of running a single evaluation task."""

    task_id: str
    response: str = ""
    scores: dict[str, float] = Field(default_factory=dict)
    passed: bool = False
    errors: list[str] = Field(default_factory=list)
    latency_ms: float = 0.0
    token_usage: dict[str, int] = Field(default_factory=dict)
    judge_reasoning: str = ""
    label: str = ""  # "observed", "model-judged", "deterministic"
    measured_dimensions: list[str] = Field(default_factory=list)


class ScoringWeights(BaseModel):
    """Configurable scoring weights for evaluation dimensions."""

    correctness: float = 0.30
    task_success: float = 0.25
    instruction_following: float = 0.15
    safety: float = 0.20
    efficiency: float = 0.10

    def validate_sum(self) -> bool:
        total = (
            self.correctness
            + self.task_success
            + self.instruction_following
            + self.safety
            + self.efficiency
        )
        return abs(total - 1.0) < 0.01

    def normalize(self) -> None:
        total = (
            self.correctness
            + self.task_success
            + self.instruction_following
            + self.safety
            + self.efficiency
        )
        if total > 0:
            self.correctness /= total
            self.task_success /= total
            self.instruction_following /= total
            self.safety /= total
            self.efficiency /= total


class DimensionScore(BaseModel):
    """Score for a single evaluation dimension."""

    name: str
    score: float = Field(ge=0.0, le=1.0)
    weight: float = Field(ge=0.0, le=1.0, default=1.0)
    label: str = "observed"  # "observed", "estimated", "model-judged"


class Score(BaseModel):
    """Aggregate score across all evaluation dimensions."""

    overall: float = Field(ge=0.0, le=100.0)
    dimensions: list[DimensionScore] = Field(default_factory=list)
    task_count: int = 0
    passed: int = 0
    failed: int = 0
    mean: float = 0.0
    min: float = 0.0
    max: float = 0.0
    variance: float = 0.0
    num_runs: int = 1
    single_run_warning: bool = False

    @property
    def pass_rate(self) -> float:
        if self.task_count == 0:
            return 0.0
        return self.passed / self.task_count


class EvaluationRun(BaseModel):
    """A single evaluation run (one pass through all tasks)."""

    run_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    model: str = ""
    provider: str = ""
    temperature: float = 0.0
    task_results: list[TaskResult] = Field(default_factory=list)
    score: Score = Field(default_factory=lambda: Score(overall=0.0))
    errors: list[str] = Field(default_factory=list)
    latency: float = 0.0


class EvaluationResult(BaseModel):
    """Complete evaluation result for a skill."""

    version: str = "1"
    skill_name: str = ""
    skill_hash: str = ""
    evaluation_version: str = "1.0"
    config_hash: str = ""
    runs: list[EvaluationRun] = Field(default_factory=list)
    baseline_runs: list[EvaluationRun] = Field(default_factory=list)
    aggregate_score: Score = Field(default_factory=lambda: Score(overall=0.0))
    baseline_score: Score | None = None
    mean_scores: dict[str, float] = Field(default_factory=dict)
    score_range: dict[str, tuple[float, float]] = Field(default_factory=dict)

    @property
    def run_count(self) -> int:
        return len(self.runs)


class ImprovementWarning(BaseModel):
    """Warning about a potential issue with an improvement."""

    dimension: str
    old_score: float
    new_score: float
    message: str
    severity: str = "warning"  # "warning", "critical"


class ComparisonResult(BaseModel):
    """Comparison between baseline and skill-enabled evaluation."""

    baseline: EvaluationResult
    with_skill: EvaluationResult
    improvement_points: float = 0.0
    dimension_changes: dict[str, float] = Field(default_factory=dict)
    warnings: list[ImprovementWarning] = Field(default_factory=list)
    recommendation: str = ""
