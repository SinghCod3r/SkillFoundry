"""Build command — analyze project and generate a skill."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import click

from skillfoundry.cli.output import Output


@click.command(help="Analyze a project and generate an Agent Skill.")
@click.argument("source", type=str)
@click.option("--output-dir", type=click.Path(), default=None, help="Output directory for generated skill.")
@click.option("--max-files", type=int, default=None, help="Maximum number of files to analyze.")
@click.option("--max-file-size", type=int, default=None, help="Maximum file size in bytes.")
@click.option("--provider", type=str, default=None, help="LLM provider name (openai, anthropic, google).")
@click.option("--model", type=str, default=None, help="LLM model identifier.")
@click.option("--no-cache", is_flag=True, help="Disable caching.")
@click.pass_context
def build(
    ctx: click.Context,
    source: str,
    output_dir: str | None,
    max_files: int | None,
    max_file_size: int | None,
    provider: str | None,
    model: str | None,
    no_cache: bool,
) -> None:
    """Analyze a project and generate an Agent Skill."""
    from skillfoundry.analysis import ProjectAnalyzer
    from skillfoundry.config import load_config
    from skillfoundry.github.url import is_github_url
    from skillfoundry.providers import get_provider
    from skillfoundry.skills import SkillGenerator, SkillValidator, SkillWriter

    output: Output = ctx.obj.output
    settings = ctx.obj.settings

    if settings is None:
        settings = load_config()

    # Apply CLI overrides
    overrides: dict = {}
    if max_files is not None:
        overrides["max_files"] = max_files
    if max_file_size is not None:
        overrides["max_file_size"] = max_file_size
    if provider is not None:
        overrides["provider"] = provider
    if model is not None:
        overrides["model"] = model
    if no_cache:
        overrides["no_cache"] = True
    if output_dir is not None:
        overrides["output_dir"] = output_dir

    if overrides:
        from skillfoundry.config.loader import _apply_cli_overrides

        settings = _apply_cli_overrides(settings, overrides)

    output.header()
    clone_dir = None

    try:
        # Step 1: Validate input
        output.step(1, 5, "Validating input")
        source_path: Path

        if is_github_url(source):
            output.success("GitHub URL detected")
            output.step(2, 5, "Cloning repository")
            from skillfoundry.github.clone import clone_repository

            clone_dir = tempfile.mkdtemp(prefix="skillfoundry-")
            source_path = clone_repository(source, Path(clone_dir))
            output.success("Repository cloned")
        else:
            source_path = Path(source).resolve()
            if not source_path.is_dir():
                output.error(f"Source path does not exist or is not a directory: {source}")
                output.info("Provide a local directory path or a GitHub URL.")
                sys.exit(1)
            output.success("Local directory detected")
            output.step(2, 5, "Preparing analysis")

        # Step 2: Analyze project
        output.step(3, 5, "Analyzing project")
        analyzer = ProjectAnalyzer(settings)
        analysis = analyzer.analyze(source_path)
        output.success(f"{analysis.analyzed_files:,} relevant files")
        if analysis.capabilities:
            output.success(f"{len(analysis.capabilities)} capabilities found")
        for warning in analysis.warnings:
            output.warning(warning)

        # Step 3: Generate skill
        output.step(4, 5, "Generating skill")
        try:
            model_provider = get_provider(settings.model)
        except ValueError as e:
            output.error(str(e))
            output.info("Set a provider via --provider flag, skillfoundry.toml, or environment variable.")
            output.info("Example: export OPENAI_API_KEY=sk-...")
            sys.exit(1)

        generator = SkillGenerator(model_provider, settings)
        skill = generator.generate(analysis)
        output.success("SKILL.md")
        if skill.references:
            output.success(f"{len(skill.references)} references")
        if skill.examples:
            output.success(f"{len(skill.examples)} examples")

        # Step 4: Validate + Write
        output.step(5, 5, "Validating and writing")
        writer = SkillWriter()
        out_dir = Path(settings.output_dir)
        skill_path = writer.write(skill, out_dir)

        validator = SkillValidator()
        result = validator.validate(skill_path)
        if result.valid:
            output.success("Skill valid")
        else:
            for err in result.errors:
                output.warning(f"Validation: {err}")

        output.newline()
        output.info(f"Created:\n  {skill_path}/")
        output.newline()
        output.info(f"Next:\n  skillfoundry eval {skill_path}")

        if ctx.obj.output.json_mode:
            output.json_output({
                "status": "success",
                "skill_name": skill.metadata.name,
                "skill_path": str(skill_path),
                "files_analyzed": analysis.analyzed_files,
                "capabilities": len(analysis.capabilities),
                "references": len(skill.references),
                "valid": result.valid,
                "errors": result.errors,
                "warnings": result.warnings,
            })

    finally:
        if clone_dir is not None:
            from skillfoundry.github.clone import cleanup_clone

            cleanup_clone(Path(clone_dir))
