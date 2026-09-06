"""SkillFoundry settings with sensible defaults."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AnalysisSettings:
    """Settings for repository analysis."""

    max_files: int = 5000
    max_file_size: int = 1_000_000  # 1 MB
    max_total_bytes: int = 50_000_000  # 50 MB
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            ".git/",
            "node_modules/",
            "vendor/",
            "dist/",
            "build/",
            "coverage/",
            ".cache/",
            ".venv/",
            "venv/",
            "__pycache__/",
            "target/",
            ".next/",
            ".nuxt/",
            ".tox/",
            ".eggs/",
            "*.egg-info/",
        ]
    )


@dataclass
class EvaluationSettings:
    """Settings for evaluation runs."""

    runs: int = 1
    timeout: int = 60  # seconds per task
    max_concurrent: int = 4
    temperature: float = 0.0
    network_enabled: bool = False


@dataclass
class ScoringSettings:
    """Configurable scoring weights."""

    correctness: float = 0.30
    task_success: float = 0.25
    instruction_following: float = 0.15
    safety: float = 0.20
    efficiency: float = 0.10


@dataclass
class ModelSettings:
    """Model provider settings."""

    provider: str = ""
    model: str = ""
    api_base: str = ""
    max_retries: int = 3
    timeout: int = 120


@dataclass
class Settings:
    """Top-level SkillFoundry configuration."""

    project_name: str = ""
    output_dir: str = "dist"
    cache_dir: str = ".skillfoundry-cache"
    analysis: AnalysisSettings = field(default_factory=AnalysisSettings)
    evaluation: EvaluationSettings = field(default_factory=EvaluationSettings)
    scoring: ScoringSettings = field(default_factory=ScoringSettings)
    model: ModelSettings = field(default_factory=ModelSettings)
    verbose: bool = False
    quiet: bool = False
    json_output: bool = False
    no_cache: bool = False
