"""
Skill name handling functionality.
"""
from __future__ import annotations

import logging

from pathlib import Path
from skillfoundry.models.analysis import ProjectAnalysis
from skillfoundry.models.skill import (
    SKILL_NAME_MAX_LENGTH,
    SKILL_NAME_PATTERN,
    normalize_skill_name,
)

logger = logging.getLogger(__name__)

def generate_skill_name(analysis: ProjectAnalysis) -> str:
    """
    Generate a skill name from project analysis.project_metadata.
    Uses project name if available, otherwise falls back to directory name.
    """
    raw_name = analysis.project_metadata.name if analysis.project_metadata and analysis.project_metadata.name else Path(analysis.source_path).name
    normalized_name = normalize_skill_name(raw_name)

    if raw_name != normalized_name:
        logger.info(f"Normalized skill name from '{raw_name}' to '{normalized_name}'")

    return normalized_name

def validate_skill_name(name: str) -> tuple[bool, list[str]]:
    """
    Validate a skill name according to Agent Skills spec requirements.
    
    Checks:
    - Matches SKILL_NAME_PATTERN
    - Length <= 64
    - No consecutive hyphens
    - No leading/trailing hyphens
    """
    errors: list[str] = []

    if not name:
        return False, ["Skill name cannot be empty"]

    if len(name) > SKILL_NAME_MAX_LENGTH:
        errors.append(f"Skill name exceeds max length of {SKILL_NAME_MAX_LENGTH}")

    if not SKILL_NAME_PATTERN.match(name):
        errors.append("Skill name contains invalid characters. Only lowercase alphanumeric and hyphens are allowed.")

    if "--" in name:
        errors.append("Skill name cannot contain consecutive hyphens.")

    if name.startswith("-") or name.endswith("-"):
        errors.append("Skill name cannot have leading or trailing hyphens.")

    return len(errors) == 0, errors
