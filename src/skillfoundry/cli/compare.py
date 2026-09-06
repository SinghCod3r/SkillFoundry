"""Compare command — compare two evaluation results."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from skillfoundry.cli.output import Output


@click.command(help="Compare two evaluation result files.")
@click.argument("baseline_path", type=click.Path(exists=True))
@click.argument("skill_path", type=click.Path(exists=True))
@click.pass_context
def compare(ctx: click.Context, baseline_path: str, skill_path: str) -> None:
    """Compare baseline and skill evaluation results."""
    from skillfoundry.evaluation.comparison import compare_results
    from skillfoundry.models.evaluation import EvaluationResult

    output: Output = ctx.obj.output
    output.header()

    # Load results
    output.step(1, 2, "Loading evaluation results")
    try:
        with open(baseline_path) as f:
            baseline_data = json.load(f)
        baseline = EvaluationResult.model_validate(
            baseline_data.get("evaluation", baseline_data)
        )
    except (json.JSONDecodeError, Exception) as e:
        output.error(f"Failed to load baseline: {e}")
        sys.exit(1)

    try:
        with open(skill_path) as f:
            skill_data = json.load(f)
        with_skill = EvaluationResult.model_validate(
            skill_data.get("evaluation", skill_data)
        )
    except (json.JSONDecodeError, Exception) as e:
        output.error(f"Failed to load skill result: {e}")
        sys.exit(1)

    output.success("Results loaded")

    # Compare
    output.step(2, 2, "Comparing results")
    comparison = compare_results(baseline, with_skill)

    output.newline()
    output.result("Baseline", str(baseline.aggregate_score.overall))
    output.result("With Skill", str(with_skill.aggregate_score.overall))
    output.result("Improvement", f"{comparison.improvement_points:+d} points")
    output.newline()

    # Dimension breakdown
    if comparison.dimension_changes:
        headers = ["Dimension", "Change"]
        rows = []
        for dim, change in comparison.dimension_changes.items():
            sign = "+" if change >= 0 else ""
            rows.append([dim, f"{sign}{change:.0%}"])
        output.table(headers, rows)

    # Warnings
    for warning in comparison.warnings:
        if warning.severity == "critical":
            output.error(f"SAFETY: {warning.message}")
        else:
            output.warning(warning.message)

    if comparison.recommendation:
        output.newline()
        output.info(f"Recommendation: {comparison.recommendation}")

    if ctx.obj.output.json_mode:
        output.json_output(comparison.model_dump(mode="json"))
