from __future__ import annotations

import tempfile
from pathlib import Path

import yaml

from skillfoundry.config import Settings
from skillfoundry.improvement.differ import generate_skill_diff
from skillfoundry.models.evaluation import EvaluationResult
from skillfoundry.models.skill import GeneratedSkill, SkillMetadata
from skillfoundry.providers.base import GenerateRequest, ModelProvider


class SkillImprover:
    """Iteratively improves a generated skill based on evaluation results."""

    def __init__(self, provider: ModelProvider, settings: Settings):
        self.provider = provider
        self.settings = settings

    def parse_skill_md(self, content: str) -> tuple[SkillMetadata, str]:
        """Parses SKILL.md content into metadata and body."""
        content = content.strip()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_str = parts[1]
                body = parts[2].strip()
                data = yaml.safe_load(frontmatter_str) or {}
                try:
                    metadata = SkillMetadata(**data)
                    return metadata, body
                except Exception:
                    # fallback if validation fails
                    pass
        return SkillMetadata(name="improved-skill", description="Improved skill based on failures"), content

    def improve(self, skill_path: Path, eval_result: EvaluationResult) -> tuple[GeneratedSkill, str]:
        """Analyzes failures and generates an improved skill."""
        skill_md = skill_path / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8") if skill_md.exists() else ""

        # Extract and group failures
        grouped_failures = {}
        for run in eval_result.runs:
            for task in run.task_results:
                if not task.passed:
                    if task.errors:
                        group = "execution_errors"
                    elif task.scores:
                        group = min(task.scores.items(), key=lambda x: x[1])[0]
                    else:
                        group = "general"
                    grouped_failures.setdefault(group, []).append(task)

        # Summarize failures
        summary_lines = []
        for group, tasks in grouped_failures.items():
            summary_lines.append(f"### Dimension/Error Type: {group}")
            for t in tasks:
                summary_lines.append(f"- Task {t.task_id}:")
                if t.judge_reasoning:
                    summary_lines.append(f"  Reasoning: {t.judge_reasoning}")
                if t.errors:
                    summary_lines.append(f"  Errors: {', '.join(t.errors)}")
            summary_lines.append("")

        failure_summary = "\n".join(summary_lines) if summary_lines else "No specific failures found."

        system_prompt = (
            "You are an expert AI improving an Agent Skill based on evaluation failures.\n"
            "Provide the full updated SKILL.md contents, starting with the YAML frontmatter and followed by the markdown body.\n"
            "Ensure the YAML frontmatter includes 'name' and 'description'."
        )

        user_prompt = (
            f"Current SKILL.md:\n{content}\n\n"
            f"Improve this skill based on failures in the recent evaluation.\n\n"
            f"Evaluation Failures Evidence:\n{failure_summary}"
        )
        req = GenerateRequest(user_prompt=user_prompt, system_prompt=system_prompt)
        response_text = self.provider.generate(req)

        # Extract metadata and body
        metadata, body = self.parse_skill_md(response_text)
        improved_skill = GeneratedSkill(
            metadata=metadata,
            skill_md_body=body,
            references=[],
            examples=[],
            scripts=[]
        )

        # Create temporary directory to generate diff
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            temp_md = temp_path / "SKILL.md"
            temp_md.write_text(response_text, encoding="utf-8")
            diff = generate_skill_diff(skill_path, temp_path)

        return improved_skill, diff
