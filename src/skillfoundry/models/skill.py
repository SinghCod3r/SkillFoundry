"""Skill-related data models aligned with the Agent Skills specification."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator

# Agent Skills spec: 1-64 chars, lowercase alphanumeric + hyphens,
# no leading/trailing/consecutive hyphens, must match directory name.
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
SKILL_NAME_MAX_LENGTH = 64
SKILL_DESCRIPTION_MAX_LENGTH = 1024


class SkillMetadata(BaseModel):
    """YAML frontmatter for SKILL.md per the Agent Skills specification."""

    name: str = Field(..., min_length=1, max_length=SKILL_NAME_MAX_LENGTH)
    description: str = Field(..., min_length=1, max_length=SKILL_DESCRIPTION_MAX_LENGTH)
    license: str | None = None
    compatibility: str | None = Field(None, max_length=500)
    metadata: dict[str, str] | None = None
    allowed_tools: str | None = Field(None, alias="allowed-tools")

    model_config = {"populate_by_name": True}

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if "--" in v:
            msg = "Skill name must not contain consecutive hyphens"
            raise ValueError(msg)
        if not SKILL_NAME_PATTERN.match(v):
            msg = (
                "Skill name must be 1-64 lowercase alphanumeric characters and hyphens, "
                "must not start or end with a hyphen"
            )
            raise ValueError(msg)
        return v


class ReferenceFile(BaseModel):
    """A reference document to include in the skill's references/ directory."""

    filename: str
    content: str
    source_files: list[str] = Field(default_factory=list)


class GeneratedSkill(BaseModel):
    """A complete generated Agent Skill, ready to be written to disk."""

    metadata: SkillMetadata
    skill_md_body: str = Field(..., description="Markdown content after frontmatter")
    references: list[ReferenceFile] = Field(default_factory=list)
    examples: list[ReferenceFile] = Field(default_factory=list)
    scripts: list[ReferenceFile] = Field(default_factory=list)

    # Provenance tracking (internal, not written to SKILL.md)
    claims: list[SkillClaim] = Field(default_factory=list)


class SkillClaim(BaseModel):
    """Tracks provenance for a claim made in the generated skill."""

    claim: str
    source_file: str
    source_location: str = ""
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class SkillValidationResult(BaseModel):
    """Result of validating a skill against the Agent Skills specification."""

    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def normalize_skill_name(raw_name: str) -> str:
    """Convert an arbitrary project name to a valid skill name.

    Examples:
        "My Amazing Project!" -> "my-amazing-project"
        "PostgreSQL v16" -> "postgresql-v16"
        "hello_world" -> "hello-world"
    """
    # Lowercase
    name = raw_name.lower().strip()
    # Replace underscores and spaces with hyphens
    name = re.sub(r"[_\s]+", "-", name)
    # Remove characters that aren't lowercase alphanumeric or hyphens
    name = re.sub(r"[^a-z0-9-]", "", name)
    # Collapse consecutive hyphens
    name = re.sub(r"-{2,}", "-", name)
    # Strip leading/trailing hyphens
    name = name.strip("-")
    # Truncate to max length
    name = name[:SKILL_NAME_MAX_LENGTH].rstrip("-")
    # Fallback if empty
    if not name:
        name = "unnamed-skill"
    return name
