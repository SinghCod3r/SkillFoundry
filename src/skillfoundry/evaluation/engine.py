from __future__ import annotations

import time
import uuid
from pathlib import Path

from skillfoundry.config import Settings
from skillfoundry.evaluation.agent import BaselineAgent, SkillEnabledAgent
from skillfoundry.evaluation.judge import JudgeFactory
from skillfoundry.evaluation.scoring import aggregate_runs, calculate_score
from skillfoundry.models.evaluation import (
    EvaluationResult,
    EvaluationRun,
    EvaluationTask,
)
from skillfoundry.providers.base import ModelProvider


class EvaluationEngine:
    def __init__(self, provider: ModelProvider, settings: Settings):
        self.provider = provider
        self.settings = settings

    def run_evaluation(
        self, skill_path: Path, tasks: list[EvaluationTask], with_skill: bool = False
    ) -> EvaluationRun:
        results = []
        skill_content = ""
        if with_skill:
            skill_md = skill_path / "SKILL.md"
            if skill_md.exists():
                skill_content = skill_md.read_text()

        run_id = str(uuid.uuid4())[:8]
        start_time = time.time()

        if with_skill:
            agent = SkillEnabledAgent(
                model_provider=self.provider,
                settings=self.settings,
                skill_content=skill_content
            )
        else:
            agent = BaselineAgent(
                model_provider=self.provider,
                settings=self.settings
            )

        for task in tasks:
            response_text = agent.execute(task)

            judge = JudgeFactory.create(task.evaluation_type, self.provider)
            res = judge.evaluate(task, response_text)
            results.append(res)

        latency = time.time() - start_time
        from skillfoundry.models.evaluation import ScoringWeights
        import dataclasses
        sw = ScoringWeights(**dataclasses.asdict(self.settings.scoring) if dataclasses.is_dataclass(self.settings.scoring) else self.settings.scoring.__dict__)
        score = calculate_score(results, sw)

        return EvaluationRun(
            run_id=run_id,
            score=score,
            task_results=results,
            latency=latency,
            timestamp=start_time,
            model="default-model",
            provider="default-provider"
        )

    def run_full_evaluation(
        self, skill_path: Path, tasks: list[EvaluationTask], num_runs: int = 1
    ) -> EvaluationResult:
        baseline_runs = []
        skill_runs = []

        for _ in range(num_runs):
            baseline_runs.append(self.run_evaluation(skill_path, tasks, with_skill=False))
            skill_runs.append(self.run_evaluation(skill_path, tasks, with_skill=True))

        base_agg_score, base_mean, base_range = aggregate_runs(baseline_runs)
        skill_agg_score, skill_mean, skill_range = aggregate_runs(skill_runs)

        return EvaluationResult(
            aggregate_score=skill_agg_score,
            baseline_score=base_agg_score,
            runs=skill_runs,
            baseline_runs=baseline_runs,
            mean_scores=skill_mean,
            score_range=skill_range
        )
