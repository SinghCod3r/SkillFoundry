"""
Deterministic skill validation against Agent Skills spec.
"""
from __future__ import annotations

import logging
from pathlib import Path

import yaml

from skillfoundry.models.skill import (
    SKILL_DESCRIPTION_MAX_LENGTH,
    SKILL_NAME_MAX_LENGTH,
    SKILL_NAME_PATTERN,
    SkillMetadata,
    SkillValidationResult,
)

logger = logging.getLogger(__name__)

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """
    Split YAML frontmatter from markdown body.
    Handles '---' delimiters.
    """
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) >= 3:
        try:
            frontmatter = yaml.safe_load(parts[1]) or {}
            body = parts[2].lstrip()
            return frontmatter, body
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse frontmatter: {e}")
            return {}, content

    return {}, content

class SkillValidator:
    """Validates skills against the specification."""

    def validate(self, skill_dir: Path) -> SkillValidationResult:
        """Validate a skill directory on disk."""
        errors = []
        warnings = []

        if not skill_dir.is_dir():
            errors.append(f"Skill directory does not exist: {skill_dir}")
            return SkillValidationResult(valid=False, errors=errors, warnings=warnings)

        skill_md_path = skill_dir / "SKILL.md"
        if not skill_md_path.is_file():
            errors.append("SKILL.md not found in the root of the skill directory.")
            return SkillValidationResult(valid=False, errors=errors, warnings=warnings)

        try:
            content = skill_md_path.read_text(encoding="utf-8")

            # Check size (> 50KB)
            if len(content.encode("utf-8")) > 50 * 1024:
                warnings.append("SKILL.md is excessively large (>50KB). Consider using reference files.")

            frontmatter, body = parse_frontmatter(content)

            name = frontmatter.get("name")
            description = frontmatter.get("description")

            if not name:
                errors.append("Missing required 'name' field in frontmatter.")
            else:
                if not isinstance(name, str):
                    errors.append("'name' must be a string.")
                else:
                    if len(name) > SKILL_NAME_MAX_LENGTH:
                        errors.append(f"'name' exceeds max length of {SKILL_NAME_MAX_LENGTH}.")
                    if not SKILL_NAME_PATTERN.match(name):
                        errors.append("'name' contains invalid characters.")
                    if "--" in name:
                        errors.append("'name' cannot contain consecutive hyphens.")
                    if name != skill_dir.name:
                        errors.append(f"'name' ({name}) does not match directory name ({skill_dir.name}).")

            if not description:
                errors.append("Missing required 'description' field in frontmatter.")
            else:
                if not isinstance(description, str):
                    errors.append("'description' must be a string.")
                else:
                    if len(description) < 1 or len(description) > SKILL_DESCRIPTION_MAX_LENGTH:
                        errors.append(f"'description' length must be between 1 and {SKILL_DESCRIPTION_MAX_LENGTH}.")

            # Optional fields
            if "license" in frontmatter and not isinstance(frontmatter["license"], str):
                errors.append("'license' must be a string.")
            if "compatibility" in frontmatter:
                if not isinstance(frontmatter["compatibility"], str):
                    errors.append("'compatibility' must be a string.")
                elif len(frontmatter["compatibility"]) > 500:
                    errors.append("'compatibility' exceeds max length of 500 characters.")
            if "metadata" in frontmatter and not isinstance(frontmatter["metadata"], dict):
                errors.append("'metadata' must be a dictionary.")
            if "allowed-tools" in frontmatter and not isinstance(frontmatter["allowed-tools"], str):
                errors.append("'allowed-tools' must be a string.")

            # Check references
            references_dir = skill_dir / "references"
            if references_dir.is_dir():
                for ref_file in references_dir.iterdir():
                    pass # Just verifying directory iteration

            import re
            links = re.findall(r'\\]\\(([^)]+)\\)', body)
            for link in links:
                if link.startswith("references/"):
                    ref_path = skill_dir / link
                    if not ref_path.is_file():
                        errors.append(f"Referenced file not found: {link}")

        except Exception as e:
            errors.append(f"Error processing SKILL.md: {e}")

        return SkillValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)

    def validate_metadata(self, metadata: SkillMetadata) -> SkillValidationResult:
        """Validate just the metadata object."""
        errors = []
        warnings = []

        if not metadata.name:
            errors.append("Missing 'name'.")
        elif len(metadata.name) > SKILL_NAME_MAX_LENGTH:
            errors.append(f"'name' exceeds max length of {SKILL_NAME_MAX_LENGTH}.")
        elif not SKILL_NAME_PATTERN.match(metadata.name):
            errors.append("'name' contains invalid characters.")
        elif "--" in metadata.name:
            errors.append("'name' cannot contain consecutive hyphens.")

        if not metadata.description:
            errors.append("Missing 'description'.")
        elif len(metadata.description) < 1 or len(metadata.description) > SKILL_DESCRIPTION_MAX_LENGTH:
            errors.append(f"'description' length must be between 1 and {SKILL_DESCRIPTION_MAX_LENGTH}.")

        return SkillValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
