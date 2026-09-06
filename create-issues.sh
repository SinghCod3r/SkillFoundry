#!/usr/bin/env bash
set -euo pipefail

REPO="SinghCod3r/SkillFoundry"

# Create useful project-specific labels if they don't exist.
gh label create "providers" \
  --repo "$REPO" \
  --color "5319E7" \
  --description "Provider integrations and model backends" 2>/dev/null || true

gh label create "evaluation" \
  --repo "$REPO" \
  --color "1D76DB" \
  --description "Evaluation, benchmarking, scoring and judges" 2>/dev/null || true

gh label create "improvement" \
  --repo "$REPO" \
  --color "A2EEEF" \
  --description "Skill improvement and regression handling" 2>/dev/null || true

gh label create "security" \
  --repo "$REPO" \
  --color "D93F0B" \
  --description "Security and untrusted-input handling" 2>/dev/null || true

gh label create "testing" \
  --repo "$REPO" \
  --color "BFD4F2" \
  --description "Tests and test infrastructure" 2>/dev/null || true

gh label create "reporting" \
  --repo "$REPO" \
  --color "C5DEF5" \
  --description "Reports, dashboards and benchmark output" 2>/dev/null || true

# 1
gh issue create --repo "$REPO" \
  --title "Fix repository URLs in README and package metadata" \
  --label "good first issue,documentation" \
  --body '## Problem

Some repository and development URLs still reference the old `skillfoundry/skillfoundry` location instead of `SinghCod3r/SkillFoundry`.

## Task

Update all repository, homepage, documentation, issue tracker and clone URLs to:

`https://github.com/SinghCod3r/SkillFoundry`

Check both `README.md` and `pyproject.toml`.

## Acceptance criteria

- No incorrect `skillfoundry/skillfoundry` repository URLs remain.
- README clone instructions work.
- Package metadata points to the correct repository.
- Existing tests continue to pass.

## Good first contribution

This is intentionally scoped as a documentation/metadata-only change.'

# 2
gh issue create --repo "$REPO" \
  --title "Add Ollama local-model provider for zero-cost development" \
  --label "help wanted,providers" \
  --body '## Goal

Add an optional Ollama provider so SkillFoundry can run against locally hosted models without requiring a paid cloud API.

## Proposed behavior

Support a configuration such as:

```toml
[model]
provider = "ollama"
model = "gemma3:4b"
base_url = "http://localhost:11434"
```

The provider should use the existing provider abstraction rather than adding model-specific logic throughout the application.

## Acceptance criteria

- Add an optional Ollama provider implementation.
- Register it through the existing provider registry.
- Support configurable model and base URL values.
- Add unit tests using a mocked local HTTP response.
- Document setup and usage without requiring cloud credentials.'
