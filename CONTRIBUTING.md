# Contributing to SkillFoundry

First off, thank you for considering contributing to SkillFoundry! We are building the definitive framework for AI Agent Skills, and community contributions are essential to making it robust, scalable, and secure.

This document provides guidelines and instructions for contributing.

## 📝 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any unacceptable behavior to the maintainers.

## 🛠️ Development Environment Setup

We use modern Python tooling to ensure code quality and a smooth developer experience.

### Prerequisites

- Python 3.11 or higher
- Git

### Installation

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/SinghCod3r/SkillFoundry.git
   cd SkillFoundry
   ```

2. **Install in editable mode with development dependencies:**
   We recommend using a virtual environment (e.g., `venv` or `conda`).
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev,all-providers]"
   ```

3. **Set up pre-commit hooks:**
   We use `pre-commit` to ensure code formatting and linting rules are applied before every commit.
   ```bash
   pre-commit install
   ```

## 📏 Code Standards

SkillFoundry maintains high standards for code quality to ensure reliability in production environments:

- **Formatting & Linting:** We use `ruff` for all linting and formatting. 
  - Format: `ruff format src/ tests/`
  - Lint: `ruff check src/ tests/`
- **Type Checking:** Strict type hints are mandatory. We use `pyright`. Run `pyright` to verify types.
- **Imports:** Always use `from __future__ import annotations` at the top of Python files.

## 🧪 Testing

All new features and bug fixes must include comprehensive tests.

- **Framework:** We use `pytest`.
- **Running Tests:**
  ```bash
  pytest
  ```
- **Coverage:** Aim for at least 90% test coverage for new modules. Run `pytest --cov=src` to check coverage.
- **Security Tests:** If you are touching security-sensitive code (like path resolution or command execution), include specific tests to verify boundary enforcement (e.g., path traversal prevention).

## 🏗️ Architecture Overview

To help you navigate the codebase, here is a high-level overview of the core modules in `src/skillfoundry/`:

- `cli/`: Command-line interface definitions and configuration loading.
- `analysis/`: Parsers and static analyzers for target codebases.
- `providers/`: Abstraction layers for interacting with external LLM APIs.
- `skills/`: Logic for generating, formatting, and validating Agent Skills.
- `evaluation/`: The core benchmarking engine that orchestrates baseline vs. enhanced runs.
- `reporting/`: Generators for JSON, HTML, and terminal-based evaluation reports.

## 🔄 Pull Request Process

1. **Find an Issue:** Look for issues tagged `good first issue` or `help wanted`. If you want to build a new feature, please open an issue to discuss it first.
2. **Branch Out:** Create a descriptive branch from `main` (e.g., `feature/add-azure-provider` or `bugfix/fix-path-resolution`).
3. **Write Code & Tests:** Implement your changes and ensure all tests pass.
4. **Commit:** Write clear, concise commit messages. Your commits will be checked by pre-commit hooks.
5. **Submit PR:** Open a Pull Request against the `main` branch. Fill out the PR template thoroughly.
6. **Review:** A maintainer will review your code. Address any feedback promptly. Once approved, your PR will be merged!

Thank you for helping make SkillFoundry better!

## 🚀 Your First Contribution

This quick path takes you from cloning SkillFoundry to opening your first pull request.

### 1. Clone the repository

Fork the repository on GitHub, then clone your fork:

```bash
git clone https://github.com/YOUR-USERNAME/SkillFoundry.git
cd SkillFoundry
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install the development dependencies

```bash
pip install -e ".[dev,all-providers]"
```

### 4. Run the tests

```bash
pytest
```

### 5. Run linting and type checking

```bash
ruff check src/ tests/
pyright
```

### 6. Run SkillFoundry without a paid LLM API

You can work on documentation, tests, validation, and other parts of the codebase that do not call an external LLM provider. Running the test suite and development checks above does not require a paid LLM API.

### 7. Understand the source tree

The main code lives in `src/skillfoundry/`, while automated tests live in `tests/`. See the Architecture Overview above for a breakdown of the core modules.

### 8. Find a good first issue

Look for open issues labelled `good first issue` or `help wanted`. Read the issue and existing discussion before starting work.

### 9. Create a branch

Create a descriptive branch from `main`:

```bash
git checkout -b docs/your-change
```

### 10. Commit and open your pull request

After making and testing your changes:

```bash
git add .
git commit -m "docs: describe your change"
git push origin docs/your-change
```
Open your fork on GitHub and create a pull request against SkillFoundry's `main` branch. Explain what you changed and link the issue it addresses.

