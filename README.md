# 🛠️ SkillFoundry

<p align="center">
  <em>The definitive framework for converting codebases into production-ready AI Agent Skills.</em>
</p>

<p align="center">
  <a href="https://github.com/SinghCod3r/SkillFoundry/actions"><img src="https://img.shields.io/github/actions/workflow/status/SinghCod3r/SkillFoundry/ci.yml?branch=main" alt="CI Status"></a>
  <a href="https://pypi.org/project/skillfoundry/"><img src="https://img.shields.io/pypi/v/skillfoundry.svg" alt="PyPI Version"></a>
  <a href="https://pypi.org/project/skillfoundry/"><img src="https://img.shields.io/pypi/pyversions/skillfoundry.svg" alt="Python Versions"></a>
  <a href="https://github.com/SinghCod3r/SkillFoundry/blob/main/LICENSE"><img src="https://img.shields.io/github/license/SinghCod3r/SkillFoundry.svg" alt="License"></a>
</p>

---

**SkillFoundry** bridges the gap between raw repositories and effective AI agents. It automatically analyzes your codebase, generates an optimized [Agent Skill](https://agentskills.io/specification), and—crucially—evaluates its performance against real-world tasks using rigorous benchmarks.

By treating AI skills as software artifacts that require testing, validation, and continuous improvement, SkillFoundry ensures your agents operate reliably and effectively.

## ✨ Key Features

- **🧠 Automated Skill Generation:** Convert any local directory or GitHub repository into a standardized Agent Skill.
- **📊 Rigorous Evaluation Engine:** Automatically generate evaluation tasks to benchmark your skill against baseline agent performance.
- **📈 Data-Driven Improvement:** Utilize evaluation failures to autonomously refine and improve the generated skill.
- **🛡️ Security Controls:** Built-in secret redaction, SSRF protection, and a constrained process runner. The runner is not a security sandbox.
- **🔌 Multi-Provider Support:** Seamless integration with leading LLM providers (OpenAI, Anthropic, Google).

## 🚀 Quick Start

### Install From PyPI

Use this path when you only want to use SkillFoundry:

```bash
python3 -m pip install "skillfoundry[openai]"
export OPENAI_API_KEY="your-api-key"
skillfoundry --help
```

Replace `openai` with `anthropic`, `google`, or `all-providers` when needed.

### Clone And Use The Repository

Use this copy-paste setup when you want to run the current source checkout:

```bash
git clone https://github.com/SinghCod3r/SkillFoundry.git
cd SkillFoundry
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[openai]"
export OPENAI_API_KEY="your-api-key"
```

Build and evaluate a skill from a local project:

```bash
skillfoundry build /path/to/your-project --output-dir ./dist
skillfoundry validate ./dist/your-project
skillfoundry eval ./dist/your-project --runs 1
```

Use `skillfoundry build --help` and `skillfoundry eval --help` for all options.

### Developer Setup

Install the checkout with development tools and an LLM provider:

```bash
python -m pip install -e ".[dev,openai]"
pytest
ruff check .
pyright
```

For a different provider, replace `openai` in the install command and set its API key environment variable.

## 📖 How It Works

SkillFoundry implements a closed-loop system for skill development:

1. **Analysis:** Deep parsing of the target codebase (files, APIs, CLI commands, documentation).
2. **Generation:** Constructing an Agent Skill definition optimized for LLM consumption.
3. **Benchmarking:** Running a baseline agent (without the skill) vs. an enhanced agent (with the skill) across generated tasks.
4. **Scoring:** Utilizing applicable weighted dimensions (Correctness 30%, Success 25%, Safety 20%, Instruction Following 15%, Efficiency 10%). Deterministic judges report only the dimensions they measure; missing dimensions do not silently receive scores.
5. **Iteration:** Automatically fixing skill definitions based on evaluation failures.

## 💻 Command Reference

| Command | Description |
| :--- | :--- |
| `skillfoundry build <source>` | Analyze a project and generate an Agent Skill |
| `skillfoundry validate <skill>` | Validate a skill against the AgentSkills specification |
| `skillfoundry eval <skill>` | Evaluate a skill with a baseline comparison |
| `skillfoundry improve <skill>`| Improve a skill using feedback from evaluation failures |
| `skillfoundry compare <a> <b>`| Compare two evaluation result sets |

*Append `--help` to any command for detailed usage.*

## ⚙️ Configuration

Control SkillFoundry's behavior using a `skillfoundry.toml` file in your project root:

```toml
[project]
name = "my-custom-skill"

[analysis]
max_files = 5000
max_file_size = 1000000  # in bytes

[evaluation]
runs = 3
timeout = 60  # seconds

[model]
provider = "openai" # Options: openai, anthropic, google
```

## 🤝 Contributing

We welcome contributions from the community! Whether it's adding a new model provider, improving the evaluation engine, or fixing a bug.

Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to set up your development environment and submit pull requests.

## 🛡️ Security

Security is a primary concern when executing code and handling LLM prompts. Read our [SECURITY.md](SECURITY.md) to understand our threat model and how to responsibly report vulnerabilities.

## 📄 License

SkillFoundry is open-source software licensed under the [Apache 2.0 License](LICENSE).
