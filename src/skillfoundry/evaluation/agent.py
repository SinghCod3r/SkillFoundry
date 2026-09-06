from __future__ import annotations

from typing import Protocol

from skillfoundry.config import Settings
from skillfoundry.models.evaluation import EvaluationTask
from skillfoundry.models.skill import GeneratedSkill
from skillfoundry.providers.base import GenerateRequest, ModelProvider


class AgentRunner(Protocol):
    """Protocol for an agent that executes evaluation tasks."""

    def execute(self, task: EvaluationTask) -> str:
        """Execute the task and return the resulting text output."""
        ...


class BaselineAgent:
    """Agent that solves tasks using just standard LLM prompt."""

    def __init__(self, model_provider: ModelProvider, settings: Settings):
        self.model_provider = model_provider
        self.settings = settings

    def execute(self, task: EvaluationTask) -> str:
        req = GenerateRequest(
            system_prompt="",
            user_prompt=task.prompt,
            temperature=self.settings.evaluation.temperature,
        )
        return self.model_provider.generate(req).content


class SkillEnabledAgent:
    """Agent that solves tasks using LLM equipped with the SKILL.md context."""

    def __init__(
        self,
        model_provider: ModelProvider,
        settings: Settings,
        skill: GeneratedSkill | None = None,
        skill_content: str = "",
    ):
        self.model_provider = model_provider
        self.settings = settings
        self.skill_content = skill_content
        if skill and skill.skill_md_body:
            self.skill_content = skill.skill_md_body

    def execute(self, task: EvaluationTask) -> str:
        prompt = task.prompt
        if self.skill_content:
            prompt = f"Background Skill Information:\n{self.skill_content}\n\nTask:\n{prompt}"

        req = GenerateRequest(
            system_prompt="",
            user_prompt=prompt,
            temperature=self.settings.evaluation.temperature,
        )
        return self.model_provider.generate(req).content
