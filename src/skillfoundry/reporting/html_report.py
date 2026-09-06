from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from skillfoundry.models.report import ReportData


class HTMLReporter:
    """Reporter for generating static HTML reports."""

    def __init__(self) -> None:
        templates_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate(self, report: ReportData) -> str:
        """Render HTML string from report data."""
        template = self.env.get_template("report.html")
        return template.render(report=report)

    def save(self, report: ReportData, output_path: Path) -> Path:
        """Write HTML report to file."""
        html_content = self.generate(report)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_content, encoding='utf-8')
        return output_path
