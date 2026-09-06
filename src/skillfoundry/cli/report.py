import json
from pathlib import Path

import click

from skillfoundry.models.report import ReportData
from skillfoundry.reporting.html_report import HTMLReporter

@click.command()
@click.argument('input_file', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), default=Path('report.html'), help='Output HTML file path.')
@click.pass_context
def report(ctx: click.Context, input_file: Path, output: Path) -> None:
    """Generate HTML report from eval results JSON."""
    out = ctx.obj.output
    out.info(f"Reading evaluation results from {input_file}...")
    try:
        data = input_file.read_text(encoding='utf-8')
        report_data = ReportData.model_validate_json(data)
    except Exception as e:
        out.error(f"Failed to parse input file: {e}")
        raise click.Abort()

    reporter = HTMLReporter()
    out.info(f"Generating HTML report to {output}...")
    try:
        reporter.save(report_data, output)
        out.success(f"Report generated successfully: {output}")
    except Exception as e:
        out.error(f"Failed to generate report: {e}")
        raise click.Abort()
