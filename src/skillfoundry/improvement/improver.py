from __future__ import annotations

from pathlib import Path

from skillfoundry.config import Settings
from skillfoundry.improvement.differ import generate_skill_diff
from skillfoundry.models.evaluation import EvaluationResult
from skillfoundry.models.skill import GeneratedSkill
from skillfoundry.providers.base import GenerateRequest, ModelProvider


class SkillImprover:
    """Iteratively improves a generated skill based on evaluation results."""

    def __init__(self, provider: ModelProvider, settings: Settings):
        self.provider = provider
        self.settings = settings

    def improve(self, skill_path: Path, eval_result: EvaluationResult) -> tuple[GeneratedSkill, str]:
        """Analyzes failures and generates an improved skill."""
        skill_md = skill_path / "SKILL.md"
        content = skill_md.read_text() if skill_md.exists() else ""

        system_prompt = (
            "You are an expert AI improving a skill based on evaluation failures.\n"
            "Provide the updated SKILL.md contents."
        )

        user_prompt = f"Current SKILL.md:\n{content}\n\nImprove this skill based on failures in the recent evaluation."
        req = GenerateRequest(prompt=user_prompt, system_prompt=system_prompt)
        response = self.provider.generate(req)

        version = 2
        while (skill_path.parent / f"{skill_path.name}.v{version}").exists():
            version += 1

        new_dir = skill_path.parent / f"{skill_path.name}.v{version}"
        new_dir.mkdir(parents=True)
        (new_dir / "SKILL.md").write_text(response)

        diff = generate_skill_diff(skill_path, new_dir)

        improved_skill = GeneratedSkill(metadata=None, references=[])

        return improved_skill, diff
