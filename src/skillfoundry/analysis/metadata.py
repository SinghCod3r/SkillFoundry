from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from skillfoundry.models.analysis import FileInfo, ProjectMetadata

logger = logging.getLogger(__name__)

def extract_metadata(root: Path, files: list[FileInfo]) -> ProjectMetadata:
    """Extract package metadata from manifest files."""
    metadata = ProjectMetadata(name="", version="", description="", dependencies=[], scripts={}, entry_points=[], license="")

    try:
        import tomllib
    except ImportError:
        tomllib = None

    for file_info in files:
        if file_info.path == "package.json":
            try:
                with (root / file_info.path).open() as f:
                    data = json.load(f)
                    metadata.name = metadata.name or data.get("name", "")
                    metadata.version = metadata.version or data.get("version", "")
                    metadata.description = metadata.description or data.get("description", "")
                    deps = list(data.get("dependencies", {}).keys()) + list(data.get("devDependencies", {}).keys())
                    metadata.dependencies.extend(deps)
                    metadata.scripts.update(data.get("scripts", {}))
                    metadata.license = metadata.license or data.get("license", "")
            except Exception as e:
                logger.warning(f"Error parsing package.json: {e}")

        elif file_info.path == "pyproject.toml" and tomllib:
            try:
                with (root / file_info.path).open("rb") as f:
                    data = tomllib.load(f)
                    project = data.get("project", {})
                    metadata.name = metadata.name or project.get("name", "")
                    metadata.version = metadata.version or project.get("version", "")
                    metadata.description = metadata.description or project.get("description", "")
                    metadata.dependencies.extend(project.get("dependencies", []))
                    metadata.scripts.update(project.get("scripts", {}))
            except Exception as e:
                logger.warning(f"Error parsing pyproject.toml: {e}")

        elif file_info.path == "setup.py":
            try:
                content = (root / file_info.path).read_text()
                name_match = re.search(r"name=['\"]([^'\"]+)['\"]", content)
                version_match = re.search(r"version=['\"]([^'\"]+)['\"]", content)
                desc_match = re.search(r"description=['\"]([^'\"]+)['\"]", content)
                if name_match: metadata.name = metadata.name or name_match.group(1)
                if version_match: metadata.version = metadata.version or version_match.group(1)
                if desc_match: metadata.description = metadata.description or desc_match.group(1)
            except Exception as e:
                logger.warning(f"Error parsing setup.py: {e}")

        elif file_info.path == "Cargo.toml" and tomllib:
            try:
                with (root / file_info.path).open("rb") as f:
                    data = tomllib.load(f)
                    pkg = data.get("package", {})
                    metadata.name = metadata.name or pkg.get("name", "")
                    metadata.version = metadata.version or pkg.get("version", "")
                    metadata.description = metadata.description or pkg.get("description", "")
            except Exception as e:
                logger.warning(f"Error parsing Cargo.toml: {e}")

        elif file_info.path == "go.mod":
            try:
                content = (root / file_info.path).read_text()
                module_match = re.search(r"^module\s+(.+)$", content, re.MULTILINE)
                if module_match:
                    metadata.name = metadata.name or module_match.group(1).strip()
            except Exception as e:
                logger.warning(f"Error parsing go.mod: {e}")

    return metadata
