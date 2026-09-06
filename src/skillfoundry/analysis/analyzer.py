"""Project analyzer — orchestrates the analysis pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

from skillfoundry.config import Settings
from skillfoundry.models.analysis import ProjectAnalysis

from .code_structure import analyze_structure
from .documentation import extract_documentation
from .inventory import discover_files
from .metadata import extract_metadata

logger = logging.getLogger(__name__)


class ProjectAnalyzer:
    """Analyzes a project directory to extract metadata, files, and structure."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.warnings: list[str] = []

    def analyze(self, source_path: Path) -> ProjectAnalysis:
        """Run the full analysis pipeline on a project directory."""
        if not source_path.exists() or not source_path.is_dir():
            msg = f"Invalid source path: {source_path}"
            raise ValueError(msg)

        logger.info("Starting analysis for %s", source_path)

        files = discover_files(source_path, self.settings.analysis)
        metadata = extract_metadata(source_path, files)
        readme_content, doc_summary = extract_documentation(source_path, files)
        tree, examples = analyze_structure(source_path, files)

        analyzed = len([f for f in files if not f.is_binary and not f.is_secret])
        skipped = len(files) - analyzed

        return ProjectAnalysis(
            source_path=str(source_path),
            project_metadata=metadata,
            files=files,
            total_files=len(files),
            analyzed_files=analyzed,
            skipped_files=skipped,
            examples=examples,
            readme_content=readme_content,
            documentation_summary=doc_summary,
            directory_tree=tree,
            warnings=self.warnings,
        )
