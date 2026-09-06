"""
Write generated skill to disk.
"""
from __future__ import annotations

import logging
from pathlib import Path

import yaml

from skillfoundry.models.skill import GeneratedSkill, SkillMetadata
from skillfoundry.security.paths import safe_join, validate_path

logger = logging.getLogger(__name__)

class SkillWriter:
    """Writes a GeneratedSkill to the filesystem."""

    def write(self, skill: GeneratedSkill, output_dir: Path, overwrite: bool = False) -> Path:
        """
        Write the skill to the output directory.
        Creates a subdirectory named after the skill.
        """
        validate_path(output_dir, output_dir)

        skill_dir = safe_join(output_dir, skill.metadata.name)
        if skill_dir.exists():
            if not overwrite:
                raise FileExistsError(f"Skill directory already exists: {skill_dir}")
        else:
            skill_dir.mkdir(parents=True)

        # SKILL.md
        skill_md_path = safe_join(skill_dir, "SKILL.md")
        frontmatter = self.format_frontmatter(skill.metadata)
        content = f"{frontmatter}\n\n{skill.skill_md_body}"
        skill_md_path.write_text(content, encoding="utf-8")

        # References
        if skill.references:
            refs_dir = safe_join(skill_dir, "references")
            refs_dir.mkdir(exist_ok=True)
            for ref in skill.references:
                ref_path = safe_join(refs_dir, ref.filename)
                ref_path.write_text(ref.content, encoding="utf-8")

        # Examples
        if hasattr(skill, "examples") and skill.examples:
            examples_dir = safe_join(skill_dir, "examples")
            examples_dir.mkdir(exist_ok=True)
            for ex in skill.examples:
                ex_path = safe_join(examples_dir, getattr(ex, "filename", "example.txt"))
                ex_path.write_text(getattr(ex, "content", ""), encoding="utf-8")

        # Scripts
        if hasattr(skill, "scripts") and skill.scripts:
            scripts_dir = safe_join(skill_dir, "scripts")
            scripts_dir.mkdir(exist_ok=True)
            for script in skill.scripts:
                script_path = safe_join(scripts_dir, getattr(script, "filename", "script.sh"))
                script_path.write_text(getattr(script, "content", ""), encoding="utf-8")
                # Intentionally not making it executable by default per requirements

        return skill_dir

    def format_frontmatter(self, metadata: SkillMetadata) -> str:
        """Render YAML frontmatter block."""
        data = {
            "name": metadata.name,
            "description": metadata.description,
        }
        if hasattr(metadata, "version") and metadata.version:
            data["version"] = metadata.version
        if hasattr(metadata, "license") and metadata.license:
            data["license"] = metadata.license
        if hasattr(metadata, "allowed_tools") and metadata.allowed_tools:
            data["allowed-tools"] = metadata.allowed_tools

        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
        return f"---\n{yaml_str}---"
