"""Load configuration from skillfoundry.toml, env vars, and CLI flags."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from skillfoundry.config.settings import (
    AnalysisSettings,
    EvaluationSettings,
    ModelSettings,
    ScoringSettings,
    Settings,
)

CONFIG_FILENAME = "skillfoundry.toml"


def find_config_file(start_dir: Path | None = None) -> Path | None:
    """Search for skillfoundry.toml starting from start_dir, walking up to root."""
    if start_dir is None:
        start_dir = Path.cwd()
    current = start_dir.resolve()
    while True:
        config_path = current / CONFIG_FILENAME
        if config_path.is_file():
            return config_path
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def load_config(
    config_path: Path | None = None,
    cli_overrides: dict | None = None,
) -> Settings:
    """Load configuration with precedence: CLI flags > env vars > TOML > defaults."""
    settings = Settings()

    # Load from TOML
    if config_path is None:
        config_path = find_config_file()
    if config_path is not None and config_path.is_file():
        settings = _merge_toml(settings, config_path)

    # Apply env vars (secrets only — never store creds in config)
    settings = _apply_env_vars(settings)

    # Apply CLI overrides
    if cli_overrides:
        settings = _apply_cli_overrides(settings, cli_overrides)

    return settings


def _merge_toml(settings: Settings, config_path: Path) -> Settings:
    """Merge TOML configuration into settings."""
    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    if "name" in project:
        settings.project_name = project["name"]
    if "output_dir" in project:
        settings.output_dir = project["output_dir"]

    analysis = data.get("analysis", {})
    if "max_files" in analysis:
        settings.analysis.max_files = int(analysis["max_files"])
    if "max_file_size" in analysis:
        settings.analysis.max_file_size = int(analysis["max_file_size"])
    if "max_total_bytes" in analysis:
        settings.analysis.max_total_bytes = int(analysis["max_total_bytes"])
    if "exclude_patterns" in analysis:
        settings.analysis.exclude_patterns.extend(analysis["exclude_patterns"])

    evaluation = data.get("evaluation", {})
    if "runs" in evaluation:
        settings.evaluation.runs = int(evaluation["runs"])
    if "timeout" in evaluation:
        settings.evaluation.timeout = int(evaluation["timeout"])
    if "temperature" in evaluation:
        settings.evaluation.temperature = float(evaluation["temperature"])

    scoring = data.get("scoring", {})
    for key in ("correctness", "task_success", "instruction_following", "safety", "efficiency"):
        if key in scoring:
            setattr(settings.scoring, key, float(scoring[key]))

    model = data.get("model", {})
    if "provider" in model:
        settings.model.provider = model["provider"]
    if "model" in model:
        settings.model.model = model["model"]
    if "api_base" in model:
        settings.model.api_base = model["api_base"]

    return settings


def _apply_env_vars(settings: Settings) -> Settings:
    """Apply environment variable overrides. Only for provider selection, never credentials."""
    provider = os.environ.get("SKILLFOUNDRY_PROVIDER")
    if provider:
        settings.model.provider = provider

    model = os.environ.get("SKILLFOUNDRY_MODEL")
    if model:
        settings.model.model = model

    return settings


def _apply_cli_overrides(settings: Settings, overrides: dict) -> Settings:
    """Apply CLI flag overrides (highest precedence)."""
    if "verbose" in overrides:
        settings.verbose = overrides["verbose"]
    if "quiet" in overrides:
        settings.quiet = overrides["quiet"]
    if "json" in overrides:
        settings.json_output = overrides["json"]
    if "no_cache" in overrides:
        settings.no_cache = overrides["no_cache"]
    if "max_files" in overrides and overrides["max_files"] is not None:
        settings.analysis.max_files = overrides["max_files"]
    if "max_file_size" in overrides and overrides["max_file_size"] is not None:
        settings.analysis.max_file_size = overrides["max_file_size"]
    if "runs" in overrides and overrides["runs"] is not None:
        settings.evaluation.runs = overrides["runs"]
    if "output_dir" in overrides and overrides["output_dir"] is not None:
        settings.output_dir = overrides["output_dir"]
    if "provider" in overrides and overrides["provider"] is not None:
        settings.model.provider = overrides["provider"]
    if "model" in overrides and overrides["model"] is not None:
        settings.model.model = overrides["model"]
    return settings
