# Contributing to SkillFoundry

First off, thank you for considering contributing to SkillFoundry! We welcome issues, bug reports, feature requests, and pull requests.

## Prerequisites

- Python 3.11+
- git

## Development Setup

1. Fork and clone the repository
2. Install the package in editable mode with development dependencies:
   ```bash
   pip install -e ".[dev,all-providers]"
   ```
3. Run tests to ensure everything is set up correctly:
   ```bash
   pytest
   ```

## Code Style

SkillFoundry strictly enforces code quality and style standards:
- **Linting & Formatting:** We use `ruff`. Run `ruff check src/ tests/` and `ruff format src/ tests/`.
- **Type Hints:** We use `pyright` for static type checking. All Python files must use type hints and `from __future__ import annotations`.
- Please ensure you configure `pre-commit` hooks for automatic checking before commits.

## Testing

All new features and bug fixes should include tests.
- We use `pytest` as our testing framework.
- Make use of appropriate fixtures when writing tests.
- Include security tests where applicable (e.g., verifying secret redaction or path traversal prevention).

## Pull Request Process

1. Create a descriptive branch for your work.
2. Commit your changes.
3. Push to your fork and submit a PR against the `main` branch.
4. Ensure your PR description explains what changes you are making and why.
5. All CI checks (tests, lints, type checks) must pass before a PR can be merged.

## Architecture Overview

SkillFoundry is organized into these core modules:
- `cli/`: Handles command-line arguments and configuration loading.
- `analysis/`: Analyzes the target codebase or documentation.
- `providers/`: Interface with external LLM APIs (OpenAI, Anthropic, Google).
- `skills/`: Generating and validating Agent Skills.
- `evaluation/`: Orchestrates the evaluation runs and baseline comparisons.
- `reporting/`: Generates human-readable output (JSON, HTML).

## Where to Start

If you're looking for ways to contribute, check our issue tracker for:
- "good first issue" tags.
- Missing test coverage.
- Enhancements to the prompt templates or evaluation workflows.
