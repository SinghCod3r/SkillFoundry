from __future__ import annotations

import time
import uuid
from pathlib import Path

from skillfoundry.models.evaluation import EvaluationTask, EvaluationRun, EvaluationResult, TaskResult, ScoringWeights
from skillfoundry.providers.base import ModelProvider, GenerateRequest
from skillfoundry.config import Settings
from skillfoundry.evaluation.judge import JudgeFactory
from skillfoundry.evaluation.scoring import calculate_score, aggregate_runs


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
        
        for task in tasks:
            prompt = task.prompt
            if with_skill and skill_content:
                prompt = f"Background Skill Information:\n{skill_content}\n\nTask:\n{prompt}"
                
            req = GenerateRequest(
                prompt=prompt,
                temperature=self.settings.evaluation.temperature
            )
            response = self.provider.generate(req)
            
            judge = JudgeFactory.create(task.evaluation_type, self.provider)
            res = judge.evaluate(task, response)
            results.append(res)
            
        latency = time.time() - start_time
        score = calculate_score(results, ScoringWeights(weights=self.settings.scoring.weights))
        
        return EvaluationRun(
            run_id=run_id,
            score=score,
            results=results,
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
            
        base_agg_score, _, _ = aggregate_runs(baseline_runs)
        skill_agg_score, _, _ = aggregate_runs(skill_runs)
        
        return EvaluationResult(
            score=skill_agg_score,
            baseline_score=base_agg_score,
            runs=skill_runs,
            baseline_runs=baseline_runs
        )
