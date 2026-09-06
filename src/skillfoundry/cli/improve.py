"""Improve command — analyze failures and generate an improved skill."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from skillfoundry.cli.output import Output


@click.command(help="Improve a skill using evaluation failures.")
@click.argument("skill_path", type=click.Path(exists=True))
@click.option("--provider", type=str, default=None, help="LLM provider name.")
@click.option("--model", type=str, default=None, help="LLM model identifier.")
@click.option("--accept", is_flag=True, help="Auto-accept improvement if score improves and no safety regression.")
@click.pass_context
def improve(
    ctx: click.Context,
    skill_path: str,
    provider: str | None,
    model: str | None,
    accept: bool,
) -> None:
    """Improve a skill using evaluation failures as evidence."""
    from skillfoundry.config import load_config
    from skillfoundry.improvement import SkillImprover
    from skillfoundry.models.evaluation import EvaluationResult
    from skillfoundry.providers import get_provider

    output: Output = ctx.obj.output
    settings = ctx.obj.settings or load_config()

    if provider is not None:
        settings.model.provider = provider
    if model is not None:
        settings.model.model = model

    output.header()
    path = Path(skill_path).resolve()

    # Find evaluation results
    output.step(1, 4, "Loading evaluation results")
    reports_dir = Path("reports")
    skill_name = path.name
    result_file = reports_dir / f"{skill_name}.json"

    if not result_file.is_file():
        output.error(f"No evaluation results found at {result_file}")
        output.info("Run 'skillfoundry eval' first.")
        sys.exit(1)

    with open(result_file) as f:
        eval_data = json.load(f)
    eval_result = EvaluationResult.model_validate(eval_data.get("evaluation", eval_data))
    output.success(f"Loaded evaluation (score: {eval_result.aggregate_score.overall})")

    # Get provider
    output.step(2, 4, "Connecting to provider")
    try:
        model_provider = get_provider(settings.model)
    except ValueError as e:
        output.error(str(e))
        sys.exit(1)

    # Generate improvement
    output.step(3, 4, "Analyzing failures and generating improvement")
    improver = SkillImprover(model_provider, settings)
    improved_skill, diff_text = improver.improve(path, eval_result)
    output.success("Improved skill generated")

    # Show diff
    output.step(4, 4, "Changes")
    if diff_text:
        output.info(diff_text)
    else:
        output.info("No changes detected.")

    # Write improved version
    from skillfoundry.skills.writer import SkillWriter

    writer = SkillWriter()
    out_dir = path.parent
    new_path = writer.write(improved_skill, out_dir)
    output.newline()
    output.success(f"Improved skill written to: {new_path}")
    output.info(f"Next:\n  skillfoundry eval {new_path}")

    if ctx.obj.output.json_mode:
        output.json_output({
            "status": "improved",
            "original_path": str(path),
            "improved_path": str(new_path),
            "diff": diff_text,
        })
