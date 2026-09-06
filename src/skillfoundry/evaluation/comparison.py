from __future__ import annotations

from skillfoundry.models.evaluation import ComparisonResult, EvaluationResult, ImprovementWarning


def compare_results(
    baseline: EvaluationResult,
    with_skill: EvaluationResult,
    allow_safety_regression: bool = False,
) -> ComparisonResult:
    """Compare two results and flag safety regressions unless explicitly overridden."""
    improvement_points = with_skill.aggregate_score.overall - baseline.aggregate_score.overall

    base_dims = {d.name: d.score for d in baseline.aggregate_score.dimensions}
    skill_dims = {d.name: d.score for d in with_skill.aggregate_score.dimensions}

    dimension_changes = {}
    warnings = []

    safety_regressed = False
    any_regressed = False

    for dim in sorted(set(base_dims) | set(skill_dims)):
        if dim in base_dims and dim in skill_dims:
            diff = skill_dims[dim] - base_dims[dim]
            dimension_changes[dim] = diff

            if diff < 0:
                any_regressed = True
                if dim == "safety":
                    safety_regressed = True
                    warnings.append(ImprovementWarning(
                        dimension="safety",
                        old_score=base_dims[dim],
                        new_score=skill_dims[dim],
                        severity="critical",
                        message="Safety score decreased.",
                    ))
                else:
                    warnings.append(ImprovementWarning(
                        dimension=dim,
                        old_score=base_dims[dim],
                        new_score=skill_dims[dim],
                        severity="warning",
                        message=f"{dim} score decreased.",
                    ))

    if safety_regressed and not allow_safety_regression:
        recommendation = "Reject: Safety regression detected. Review carefully before accepting."
    elif any_regressed:
        recommendation = "Review: Some dimensions regressed. Inspect individual scores."
    else:
        recommendation = "Accept: All dimensions improved."

    return ComparisonResult(
        baseline=baseline,
        with_skill=with_skill,
        improvement_points=improvement_points,
        dimension_changes=dimension_changes,
        warnings=warnings,
        recommendation=recommendation
    )
