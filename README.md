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
- **🛡️ Enterprise-Grade Security:** Built-in secret redaction, SSRF protection, and sandboxed evaluation execution.
- **🔌 Multi-Provider Support:** Seamless integration with leading LLM providers (OpenAI, Anthropic, Google).

## 🚀 Quick Start

### Installation

Install SkillFoundry using `pip`. We recommend installing it with your preferred LLM provider:

```bash
# Install with OpenAI support
pip install "skillfoundry[openai]"

# Or install all providers
pip install "skillfoundry[all-providers]"
```

### Build Your First Skill

1. **Set your API credentials:**
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

2. **Run the build command** against a local project:
   ```bash
   skillfoundry build ./my-project
   ```

3. **Evaluate the generated skill:**
   ```bash
   skillfoundry eval ./my-project-skill
   ```

## 📖 How It Works

SkillFoundry implements a closed-loop system for skill development:

1. **Analysis:** Deep parsing of the target codebase (files, APIs, CLI commands, documentation).
2. **Generation:** Constructing an Agent Skill definition optimized for LLM consumption.
3. **Benchmarking:** Running a baseline agent (without the skill) vs. an enhanced agent (with the skill) across generated tasks.
4. **Scoring:** Utilizing a weighted model (Correctness 30%, Success 25%, Safety 20%, Instruction Following 15%, Efficiency 10%) to prove the skill's utility.
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
