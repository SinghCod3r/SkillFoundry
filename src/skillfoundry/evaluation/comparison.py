from __future__ import annotations

from skillfoundry.models.evaluation import ComparisonResult, EvaluationResult, ImprovementWarning


def compare_results(baseline: EvaluationResult, with_skill: EvaluationResult) -> ComparisonResult:
    """Compares baseline evaluation with skill evaluation."""
    improvement_points = with_skill.score.overall - baseline.score.overall

    base_dims = {d.dimension: d.score for d in baseline.score.dimensions}
    skill_dims = {d.dimension: d.score for d in with_skill.score.dimensions}

    dimension_changes = {}
    warnings = []

    safety_regressed = False
    any_regressed = False

    for dim in skill_dims:
        if dim in base_dims:
            diff = skill_dims[dim] - base_dims[dim]
            dimension_changes[dim] = diff

            if diff < 0:
                any_regressed = True
                if dim == "safety":
                    safety_regressed = True
                    warnings.append(ImprovementWarning(dimension="safety", severity="critical", message="Safety score decreased."))
                else:
                    warnings.append(ImprovementWarning(dimension=dim, severity="warning", message=f"{dim} score decreased."))

    if safety_regressed:
        recommendation = "Reject: Safety regression detected. Review carefully before accepting."
    elif any_regressed:
        recommendation = "Review: Some dimensions regressed. Inspect individual scores."
    else:
        recommendation = "Accept: All dimensions improved."

    return ComparisonResult(
        improvement_points=improvement_points,
        dimension_changes=dimension_changes,
        warnings=warnings,
        recommendation=recommendation
    )
