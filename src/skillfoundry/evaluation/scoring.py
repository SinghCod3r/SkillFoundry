from __future__ import annotations

import statistics

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
        return Score(overall=0.0, passed=0, failed=0, dimensions=[])

    if not weights.validate_sum():
        weights.normalize()

    dim_totals: dict[str, float] = {}
    dim_counts: dict[str, int] = {}

    passed = 0
    failed = 0

    weights_dict = {
        "correctness": weights.correctness,
        "task_success": weights.task_success,
        "instruction_following": weights.instruction_following,
        "safety": weights.safety,
        "efficiency": weights.efficiency,
    }

    all_overall_scores = []

    for res in results:
        if res.passed:
            passed += 1
        else:
            failed += 1

        task_weighted_sum = 0.0
        task_weight_total = 0.0

        for dim_name, score_val in res.scores.items():
            # Bound check
            score_val = max(0.0, min(1.0, score_val))

            dim_totals[dim_name] = dim_totals.get(dim_name, 0.0) + score_val
            dim_counts[dim_name] = dim_counts.get(dim_name, 0) + 1

            w = weights_dict.get(dim_name, 0.0)
            if w <= 0:
                continue
            task_weighted_sum += score_val * w
            task_weight_total += w

        if task_weight_total > 0:
            all_overall_scores.append(task_weighted_sum / task_weight_total)

    dimensions = []

    for dim_name, total in dim_totals.items():
        avg = total / dim_counts[dim_name]
        weight = weights_dict.get(dim_name, 0.0)
        dimensions.append(DimensionScore(name=dim_name, score=avg, weight=weight))

    mean_val = 0.0
    min_val = 0.0
    max_val = 0.0
    var_val = 0.0

    if all_overall_scores:
        mean_val = statistics.mean(all_overall_scores)
        min_val = min(all_overall_scores)
        max_val = max(all_overall_scores)
        if len(all_overall_scores) > 1:
            var_val = statistics.variance(all_overall_scores)

    overall = mean_val * 100.0

    return Score(
        overall=overall,
        passed=passed,
        failed=failed,
        dimensions=dimensions,
        task_count=len(results),
        mean=mean_val,
        min=min_val,
        max=max_val,
        variance=var_val,
        num_runs=1,
        single_run_warning=True
    )


def aggregate_runs(runs: list[EvaluationRun]) -> tuple[Score, dict[str, float], dict[str, tuple[float, float]]]:
    """Aggregates multiple evaluation runs."""
    if not runs:
        raise ValueError("No runs provided.")

    overall_scores = [run.score.overall for run in runs]
    agg_overall = sum(overall_scores) / len(overall_scores)

    passed = sum(run.score.passed for run in runs)
    failed = sum(run.score.failed for run in runs)
    task_count = sum(run.score.task_count for run in runs)

    dim_values: dict[str, list[float]] = {}
    for run in runs:
        for dim in run.score.dimensions:
            dim_values.setdefault(dim.name, []).append(dim.score)

    mean_scores = {}
    score_ranges = {}
    dimensions = []

    for dim, vals in dim_values.items():
        mean_val = sum(vals) / len(vals)
        mean_scores[dim] = mean_val
        score_ranges[dim] = (min(vals), max(vals))
        weights = [
            run_dim.weight
            for run in runs
            for run_dim in run.score.dimensions
            if run_dim.name == dim
        ]
        dimensions.append(
            DimensionScore(
                name=dim,
                score=mean_val,
                weight=statistics.mean(weights) if weights else 0.0,
            )
        )

    mean_val = 0.0
    min_val = 0.0
    max_val = 0.0
    var_val = 0.0

    overall_scores_normalized = [s / 100.0 for s in overall_scores]
    if overall_scores_normalized:
        mean_val = statistics.mean(overall_scores_normalized)
        min_val = min(overall_scores_normalized)
        max_val = max(overall_scores_normalized)
        if len(overall_scores_normalized) > 1:
            var_val = statistics.variance(overall_scores_normalized)

    agg_score = Score(
        overall=agg_overall,
        passed=passed,
        failed=failed,
        dimensions=dimensions,
        task_count=task_count,
        mean=mean_val,
        min=min_val,
        max=max_val,
        variance=var_val,
        num_runs=len(runs),
        single_run_warning=(len(runs) == 1)
    )
    return agg_score, mean_scores, score_ranges
