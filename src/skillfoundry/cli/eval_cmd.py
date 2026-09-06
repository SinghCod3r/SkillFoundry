"""Eval command — run baseline vs. skill evaluation."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from skillfoundry.cli.output import Output


@click.command("eval", help="Evaluate a skill: run baseline and with-skill comparison.")
@click.argument("skill_path", type=click.Path(exists=True))
@click.option("--runs", type=int, default=None, help="Number of evaluation runs (default: 1).")
@click.option("--provider", type=str, default=None, help="LLM provider name.")
@click.option("--model", type=str, default=None, help="LLM model identifier.")
@click.option("--output-dir", type=click.Path(), default=None, help="Directory for evaluation results.")
@click.pass_context
def eval_cmd(
    ctx: click.Context,
    skill_path: str,
    runs: int | None,
    provider: str | None,
    model: str | None,
    output_dir: str | None,
) -> None:
    """Evaluate a skill with baseline comparison."""
    from skillfoundry.config import load_config
    from skillfoundry.evaluation import EvaluationEngine, TaskGenerator
    from skillfoundry.evaluation.comparison import compare_results
    from skillfoundry.evaluation.scoring import aggregate_runs
    from skillfoundry.providers import get_provider
    from skillfoundry.reporting import JSONReporter, HTMLReporter
    from skillfoundry.models.report import ReportData, ReportMetadata
    from skillfoundry.skills.validator import SkillValidator, parse_frontmatter

    output: Output = ctx.obj.output
    settings = ctx.obj.settings or load_config()

    if runs is not None:
        settings.evaluation.runs = runs
    if provider is not None:
        settings.model.provider = provider
    if model is not None:
        settings.model.model = model

    output.header()
    path = Path(skill_path).resolve()

    # Validate skill first
    output.step(1, 5, "Validating skill")
    validator = SkillValidator()
    val_result = validator.validate(path)
    if not val_result.valid:
        output.error("Skill validation failed")
        for err in val_result.errors:
            output.error(err)
        sys.exit(2)
    output.success("Skill valid")

    # Get provider
    output.step(2, 5, "Connecting to provider")
    try:
        model_provider = get_provider(settings.model)
    except ValueError as e:
        output.error(str(e))
        sys.exit(1)
    output.success(f"Using {model_provider.name}")

    # Load or generate tasks
    output.step(3, 5, "Loading evaluation tasks")
    tasks_dir = path / "evals"
    task_gen = TaskGenerator(model_provider, settings)

    if tasks_dir.is_dir():
        tasks = task_gen.load_tasks(tasks_dir)
        output.success(f"Loaded {len(tasks)} tasks")
    else:
        output.info("No eval tasks found. Generating tasks requires project analysis.")
        output.error("Run 'skillfoundry build' first to generate evaluation tasks.")
        sys.exit(1)

    # Run evaluation
    output.step(4, 5, f"Running evaluation ({settings.evaluation.runs} run(s))")
    engine = EvaluationEngine(model_provider, settings)
    eval_result = engine.run_full_evaluation(path, tasks, settings.evaluation.runs)
    output.success(f"Baseline score: {eval_result.aggregate_score.overall}")

    # Generate report
    output.step(5, 5, "Generating report")
    report_dir = Path(output_dir) if output_dir else Path("reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    # Read skill name
    skill_md = path / "SKILL.md"
    skill_name = path.name
    if skill_md.is_file():
        fm, _ = parse_frontmatter(skill_md.read_text())
        skill_name = fm.get("name", path.name)

    report = ReportData(
        skill_name=skill_name,
        source_path=str(path),
        evaluation=eval_result,
        generated_files=[str(p.relative_to(path)) for p in path.rglob("*") if p.is_file()],
    )

    json_reporter = JSONReporter()
    json_path = json_reporter.save(report, report_dir / f"{skill_name}.json")
    output.success(f"JSON report: {json_path}")

    html_reporter = HTMLReporter()
    html_path = html_reporter.save(report, report_dir / f"{skill_name}.html")
    output.success(f"HTML report: {html_path}")

    # Summary
    output.newline()
    output.result("Overall Score", str(eval_result.aggregate_score.overall))
    output.result("Tasks", f"{eval_result.aggregate_score.passed}/{eval_result.aggregate_score.task_count} passed")

    if ctx.obj.output.json_mode:
        output.json_output(eval_result.model_dump(mode="json"))
