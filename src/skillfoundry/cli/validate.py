"""Validate command — offline skill validation against the Agent Skills spec."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from skillfoundry.cli.output import Output


@click.command(help="Validate a skill against the Agent Skills specification. Works offline.")
@click.argument("skill_path", type=click.Path(exists=True))
@click.pass_context
def validate(ctx: click.Context, skill_path: str) -> None:
    """Validate a skill directory against the Agent Skills specification."""
    from skillfoundry.skills.validator import SkillValidator

    output: Output = ctx.obj.output
    output.header()

    path = Path(skill_path).resolve()
    if not path.is_dir():
        output.error(f"Not a directory: {skill_path}")
        sys.exit(1)

    output.step(1, 1, "Validating skill")

    validator = SkillValidator()
    result = validator.validate(path)

    if result.valid:
        output.success("Skill is valid")
    else:
        output.error("Skill validation failed")

    for error in result.errors:
        output.error(error)
    for warning in result.warnings:
        output.warning(warning)

    if ctx.obj.output.json_mode:
        output.json_output({
            "valid": result.valid,
            "errors": result.errors,
            "warnings": result.warnings,
        })

    if not result.valid:
        sys.exit(2)
