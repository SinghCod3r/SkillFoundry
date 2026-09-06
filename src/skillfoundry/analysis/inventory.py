from __future__ import annotations

import fnmatch
import logging
import os
from pathlib import Path

from skillfoundry.config.settings import AnalysisSettings
from skillfoundry.models.analysis import FileCategory, FileInfo

try:
    from skillfoundry.security.redaction import is_secret_file
except ImportError:
    def is_secret_file(path: Path) -> bool:
        return False

logger = logging.getLogger(__name__)

def is_binary(file_path: Path) -> bool:
    try:
        with file_path.open("rb") as f:
            chunk = f.read(8192)
            if b"\x00" in chunk:
                return True
    except Exception:
        pass
    return False

def discover_files(root: Path, settings: AnalysisSettings) -> list[FileInfo]:
    """Discover and filter files in the project root."""
    discovered = []
    total_bytes = 0
    file_count = 0

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)

        # Apply excludes to directories to prevent descending
        dirnames[:] = [d for d in dirnames if not any(fnmatch.fnmatch(str(rel_dir / d), pat) for pat in settings.exclude_patterns)]

        for filename in filenames:
            file_path = Path(dirpath) / filename
            rel_path = file_path.relative_to(root)

            if any(fnmatch.fnmatch(str(rel_path), pat) for pat in settings.exclude_patterns):
                continue

            if file_count >= settings.max_files:
                logger.warning(f"Max files limit reached ({settings.max_files}). Stopping discovery.")
                break

            if not file_path.is_file():
                continue

            try:
                size = file_path.stat().st_size
            except Exception:
                continue

            if size > settings.max_file_size:
                logger.warning(f"Skipping {rel_path}: file size {size} exceeds max_file_size {settings.max_file_size}")
                continue

            if total_bytes + size > settings.max_total_bytes:
                logger.warning("Max total bytes limit reached. Stopping discovery.")
                break

            if is_binary(file_path):
                continue

            is_generated = filename in {"package-lock.json", "yarn.lock", "Pipfile.lock", "poetry.lock", "Gemfile.lock", "go.sum"} or filename.endswith(".min.js")
            is_secret = is_secret_file(file_path)

            category = FileCategory.OTHER
            score = 0.2

            if filename.startswith("README") or rel_path.parts[0] == "docs" or filename.endswith((".md", ".rst")) or (filename.endswith(".txt") and "doc" in str(rel_path)):
                category = FileCategory.DOCUMENTATION
                score = 1.0
            elif filename in {"package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "Gemfile", "setup.py", "setup.cfg"}:
                category = FileCategory.MANIFEST
                score = 0.95
            elif filename.endswith((".graphql", ".proto")) or filename.startswith(("openapi", "swagger")):
                category = FileCategory.SCHEMA
                score = 0.9
            elif "example" in str(rel_path) or "demo" in str(rel_path):
                category = FileCategory.EXAMPLE
                score = 0.85
            elif ".github/workflows" in str(rel_path) or ".gitlab-ci" in filename or ".circleci" in str(rel_path) or filename == "Jenkinsfile":
                category = FileCategory.CI
                score = 0.7
            elif filename.endswith((".toml", ".yaml", ".yml", ".json", ".ini", ".cfg")) and category == FileCategory.OTHER:
                category = FileCategory.CONFIGURATION
                score = 0.7
            elif filename in {"Makefile", "Dockerfile", "CMakeLists.txt", "Justfile"} or filename.startswith("docker-compose") or filename.endswith(".mk"):
                category = FileCategory.BUILD
                score = 0.65
            elif filename.endswith((".sh", ".bash", ".zsh", ".fish")) or "scripts" in str(rel_path):
                category = FileCategory.SCRIPT
                score = 0.6
            elif "test" in filename.lower() or "spec" in str(rel_path) or "test" in str(rel_path):
                category = FileCategory.TEST
                score = 0.5
            elif filename.endswith((".py", ".js", ".ts", ".go", ".rs", ".java", ".rb", ".php", ".c", ".cpp", ".h")):
                category = FileCategory.SOURCE
                score = 0.4

            language = file_path.suffix.lstrip(".")

            info = FileInfo(
                path=str(rel_path),
                size=size,
                category=category,
                language=language,
                is_generated=is_generated,
                is_secret=is_secret,
                relevance_score=score
            )
            discovered.append(info)
            total_bytes += size
            file_count += 1

        if file_count >= settings.max_files or total_bytes >= settings.max_total_bytes:
            break

    discovered.sort(key=lambda x: x.relevance_score, reverse=True)
    return discovered
