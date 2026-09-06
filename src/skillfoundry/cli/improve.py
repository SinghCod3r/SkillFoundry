"""Improve command — analyze failures, generate and evaluate an improved skill."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

import click

from skillfoundry.cli.output import Output


@click.command(help="Improve a skill using evaluation failures.")
@click.argument("skill_path", type=click.Path(exists=True))
@click.option("--provider", type=str, default=None, help="LLM provider name.")
@click.option("--model", type=str, default=None, help="LLM model identifier.")
@click.option("--accept", is_flag=True, help="Auto-accept improvement if score improves and no safety regression.")
@click.option("--allow-safety-regression", is_flag=True, help="Explicitly allow a safety regression.")
@click.pass_context
def improve(
    ctx: click.Context,
    skill_path: str,
    provider: str | None,
    model: str | None,
    accept: bool,
    allow_safety_regression: bool,
) -> None:
    """Improve a skill using evaluation failures as evidence."""
    from skillfoundry.config import load_config
    from skillfoundry.evaluation import EvaluationEngine, TaskGenerator
    from skillfoundry.evaluation.comparison import compare_results
    from skillfoundry.improvement import SkillImprover
    from skillfoundry.providers import get_provider
    from skillfoundry.skills.writer import SkillWriter

    output: Output = ctx.obj.output
    settings = ctx.obj.settings or load_config()

    if provider is not None:
        settings.model.provider = provider
    if model is not None:
        settings.model.model = model

    output.header()
    path = Path(skill_path).resolve()
    skill_name = path.name

    # Get provider
    output.step(1, 6, "Connecting to provider")
    try:
        model_provider = get_provider(settings.model)
    except ValueError as e:
        output.error(str(e))
        sys.exit(1)

    # Evaluate old skill
    output.step(2, 6, "Evaluating old skill (baseline)")
    tasks_dir = path / "evals"
    task_gen = TaskGenerator(model_provider, settings)
    if tasks_dir.is_dir():
        tasks = task_gen.load_tasks(tasks_dir)
    else:
        output.error("No eval tasks found. Run 'skillfoundry build' first.")
        sys.exit(1)

    engine = EvaluationEngine(model_provider, settings)
    # Using run_full_evaluation to evaluate the current skill at `path`
    old_eval_result = engine.run_full_evaluation(path, tasks, settings.evaluation.runs)
    output.success(f"Old skill evaluated. Score: {old_eval_result.aggregate_score.overall}")

    # Generate improvement
    output.step(3, 6, "Analyzing failures and generating improvement")
    improver = SkillImprover(model_provider, settings)
    improved_skill, diff_text = improver.improve(path, old_eval_result)
    output.success("Improved skill generated")

    if diff_text:
        output.info("Changes:")
        output.info(diff_text)
    else:
        output.info("No changes detected.")

    # Write improved version to a temporary directory for evaluation
    output.step(4, 6, "Evaluating new skill")
    writer = SkillWriter()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        new_skill_path = writer.write(improved_skill, temp_dir_path)

        # Copy evals so TaskGenerator/EvaluationEngine has everything if needed
        # Or just pass tasks directly as we already have them loaded
        new_eval_result = engine.run_full_evaluation(new_skill_path, tasks, settings.evaluation.runs)

    output.success(f"New skill evaluated. Score: {new_eval_result.aggregate_score.overall}")

    # Compare results
    output.step(5, 6, "Comparing results")

    comparison = compare_results(
        old_eval_result,
        new_eval_result,
        allow_safety_regression=allow_safety_regression,
    )

    old_score = old_eval_result.aggregate_score.overall
    new_score = new_eval_result.aggregate_score.overall

    old_safety = 0.0
    for dim in old_eval_result.aggregate_score.dimensions:
        if dim.name == "safety":
            old_safety = dim.score
            break

    new_safety = 0.0
    for dim in new_eval_result.aggregate_score.dimensions:
        if dim.name == "safety":
            new_safety = dim.score
            break

    output.info(f"Overall Score: {old_score} -> {new_score}")
    output.info(f"Safety Score: {old_safety} -> {new_safety}")

    # Decision logic
    output.step(6, 6, "Decision")
    rejected = False
    reject_reason = ""

    if any(w.severity == "critical" for w in comparison.warnings) and not allow_safety_regression:
        rejected = True
        reject_reason = "Safety regressed. Use --allow-safety-regression to override explicitly."
    elif new_score <= old_score:
        rejected = True
        reject_reason = "Overall score did not improve."

    if rejected:
        output.error(f"Improvement rejected: {reject_reason}")
        output.info("Preserving the old skill.")

        if ctx.obj.output.json_mode:
            output.json_output({
                "status": "rejected",
                "reason": reject_reason,
                "old_score": old_score,
                "new_score": new_score,
            })
        sys.exit(1)
    else:
        output.success("Improvement accepted!")

        # Overwrite with new skill
        # We write to a temporary location, then move to overwrite
        with tempfile.TemporaryDirectory() as overwrite_tmp:
            tmp_write_path = writer.write(improved_skill, Path(overwrite_tmp))

            # Remove old SKILL.md
            (path / "SKILL.md").unlink(missing_ok=True)
            # Copy new SKILL.md
            shutil.copy2(tmp_write_path / "SKILL.md", path / "SKILL.md")

        output.success(f"Improved skill written to: {path}")

        if ctx.obj.output.json_mode:
            output.json_output({
                "status": "accepted",
                "old_score": old_score,
                "new_score": new_score,
                "diff": diff_text,
            })
