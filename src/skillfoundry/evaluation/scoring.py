from __future__ import annotations

from skillfoundry.models.evaluation import (
    DimensionScore,
    EvaluationRun,
    Score,
    ScoringWeights,
    TaskResult,
)


def calculate_score(results: list[TaskResult], weights: ScoringWeights) -> Score:
    """Calculates overall and dimension-specific scores."""
    if not results:
        return Score(overall=0, passed=0, failed=0, dimensions=[])

    dim_totals: dict[str, float] = {}
    dim_counts: dict[str, int] = {}

    passed = 0
    failed = 0

    for res in results:
        if res.passed:
            passed += 1
        else:
            failed += 1

        for dim in res.dimensions:
            dim_totals[dim.dimension] = dim_totals.get(dim.dimension, 0.0) + dim.score
            dim_counts[dim.dimension] = dim_counts.get(dim.dimension, 0) + 1

    dimensions = []
    weighted_sum = 0.0
    total_weight = 0.0

    for dim_name, total in dim_totals.items():
        avg = total / dim_counts[dim_name]
        dimensions.append(DimensionScore(dimension=dim_name, score=avg))

        weight = weights.weights.get(dim_name, 1.0)
        weighted_sum += avg * weight
        total_weight += weight

    overall = int((weighted_sum / total_weight) * 100) if total_weight > 0 else 0

    return Score(overall=overall, passed=passed, failed=failed, dimensions=dimensions)


def aggregate_runs(runs: list[EvaluationRun]) -> tuple[Score, dict[str, float], dict[str, tuple[float, float]]]:
    """Aggregates multiple evaluation runs."""
    if not runs:
        raise ValueError("No runs provided.")

    overall_scores = [run.score.overall for run in runs]
    agg_overall = sum(overall_scores) // len(overall_scores)

    passed = sum(run.score.passed for run in runs)
    failed = sum(run.score.failed for run in runs)

    dim_values: dict[str, list[float]] = {}
    for run in runs:
        for dim in run.score.dimensions:
            dim_values.setdefault(dim.dimension, []).append(dim.score)

    mean_scores = {}
    score_ranges = {}
    dimensions = []

    for dim, vals in dim_values.items():
        mean_val = sum(vals) / len(vals)
        mean_scores[dim] = mean_val
        score_ranges[dim] = (min(vals), max(vals))
        dimensions.append(DimensionScore(dimension=dim, score=mean_val))

    agg_score = Score(overall=agg_overall, passed=passed, failed=failed, dimensions=dimensions)
    return agg_score, mean_scores, score_ranges
