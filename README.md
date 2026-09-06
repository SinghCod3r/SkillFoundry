# SkillFoundry

Build AI Agent Skills that actually work.

Generate a skill from a project, benchmark it against real tasks, and improve it using evidence.

## Quick Start

```bash
pip install skillfoundry

skillfoundry build ./my-project
```

```text
Analyzing project...
Found 150 files, 4 APIs, 2 CLI commands
Generating skill...
Skill generated successfully: my-project-skill
```

## What It Does

SkillFoundry takes a project (local directory or GitHub URL) and:
1. Analyzes the codebase, documentation, and API surface
2. Generates an Agent Skill following the [Agent Skills specification](https://agentskills.io/specification)
3. Creates evaluation tasks to benchmark the skill
4. Runs baseline vs. with-skill comparisons
5. Improves the skill using evaluation failures

## Installation

```bash
pip install skillfoundry

# With a specific provider
pip install "skillfoundry[openai]"
pip install "skillfoundry[anthropic]"
pip install "skillfoundry[google]"

# All providers
pip install "skillfoundry[all-providers]"
```

## Commands

| Command | Description |
|---|---|
| `skillfoundry build <source>` | Analyze project and generate skill |
| `skillfoundry validate <skill>` | Validate skill against spec (offline) |
| `skillfoundry eval <skill>` | Evaluate skill with baseline comparison |
| `skillfoundry improve <skill>` | Improve skill using evaluation failures |
| `skillfoundry compare <a> <b>` | Compare two evaluation results |

Global flags: `--json`, `--quiet`, `--verbose`, `--help`, `--version`

## Configuration

Create `skillfoundry.toml` in your project root:
```toml
[project]
name = "my-skill"

[analysis]
max_files = 5000
max_file_size = 1000000

[evaluation]
runs = 3
timeout = 60

[model]
provider = "openai"
```

Provider credentials are set via environment variables:
```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GOOGLE_API_KEY=...
```

## How Evaluation Works

SkillFoundry generates a diverse set of tasks that an AI agent might need to perform with the analyzed project. It runs a baseline evaluation where an agent attempts these tasks without the generated skill. It then runs the same tasks where the agent has access to the generated skill. The results are compared using a weighted scoring model: correctness (30%), task success (25%), safety (20%), instruction following (15%), and efficiency (10%). SkillFoundry then reports the improvement achieved by using the skill.

## Security Model

- Repository content is treated as untrusted data, never as instructions
- Secrets are detected and redacted before model submission
- Generated commands are never auto-executed
- Path traversal and SSRF protections are enforced
- Evaluation runs in isolated environments

## Supported Providers

| Provider | Package | Models |
|---|---|---|
| OpenAI | `skillfoundry[openai]` | gpt-4o, gpt-4o-mini |
| Anthropic | `skillfoundry[anthropic]` | claude-sonnet-4-20250514 |
| Google | `skillfoundry[google]` | gemini-2.0-flash |

Auto-detection: if no provider is configured, SkillFoundry checks for API key environment variables in order.

## Limitations

- V0.1: evaluation quality depends on the configured model
- LLM judge scores are labeled as "model-judged", not ground truth
- Large repositories may need `--max-files` tuning
- Generated skills should always be human-reviewed

## Development

```bash
git clone https://github.com/skillfoundry/skillfoundry.git
cd skillfoundry
pip install -e ".[dev,all-providers]"
pytest
ruff check src/ tests/
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Apache-2.0. See [LICENSE](LICENSE).
