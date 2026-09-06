from __future__ import annotations

import json
from pathlib import Path

from skillfoundry.models.report import ReportData


class JSONReporter:
    """Reporter for generating JSON reports."""

    def generate(self, report: ReportData) -> str:
        """Serialize report to formatted JSON string."""
        return json.dumps(report.model_dump(mode='json'), indent=2)

    def save(self, report: ReportData, output_path: Path) -> Path:
        """Write JSON report to file."""
        json_content = self.generate(report)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_content, encoding='utf-8')
        return output_path
