from __future__ import annotations

import json
from pathlib import Path

import yaml
from pydantic import BaseModel

from skillfoundry.config import Settings
from skillfoundry.models.analysis import ProjectAnalysis
from skillfoundry.models.evaluation import EvaluationTask
from skillfoundry.models.skill import GeneratedSkill
from skillfoundry.providers.base import GenerateRequest, ModelProvider


class TaskList(BaseModel):
    tasks: list[EvaluationTask]


class TaskGenerator:
    """Generates evaluation tasks using an LLM based on project analysis and skill capabilities."""

    def __init__(self, provider: ModelProvider, settings: Settings):
        self.provider = provider
        self.settings = settings

    def generate_tasks(
        self, analysis: ProjectAnalysis, skill: GeneratedSkill
    ) -> list[EvaluationTask]:
        """Generates 15-20 evaluation tasks to test the generated skill."""
        system_prompt = (
            "You are an expert AI evaluator creating tasks to test a new AI Agent Skill.\n"
            "Generate 15-20 tasks that test whether the skill's information helps an agent.\n"
            "Cover correctness, completeness, safety, and edge cases.\n"
            "Ensure tasks are detailed, challenging, and directly test the capabilities."
        )

        user_prompt = (
            f"Project Name: {analysis.project_metadata.name}\n"
            f"Skill Name: {skill.metadata.name}\n"
            f"Skill Claims: {[claim.description for claim in skill.metadata.claims]}\n"
        )

        req = GenerateRequest(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=self.settings.evaluation.temperature,
            schema=TaskList.model_json_schema()
        )
        response_text = self.provider.generate(req)

        try:
            data = json.loads(response_text)
            return TaskList.model_validate(data).tasks
        except Exception:
            raise ValueError("Failed to parse task generation output.")

    def load_tasks(self, tasks_dir: Path) -> list[EvaluationTask]:
        """Loads tasks from YAML files in the given directory."""
        tasks = []
        for file in tasks_dir.glob("*.yaml"):
            with open(file) as f:
                data = yaml.safe_load(f)
                if isinstance(data, list):
                    for task_data in data:
                        tasks.append(EvaluationTask.model_validate(task_data))
                else:
                    tasks.append(EvaluationTask.model_validate(data))
        return tasks

    def save_tasks(self, tasks: list[EvaluationTask], output_dir: Path) -> Path:
        """Saves tasks to YAML files in the output directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / "tasks.yaml"
        with open(file_path, "w") as f:
            yaml.dump([t.model_dump() for t in tasks], f)
        return file_path
