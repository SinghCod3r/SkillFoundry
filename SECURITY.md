# Security Policy

At SkillFoundry, security is our top priority. Because our framework analyzes untrusted codebases and orchestrates AI agents, we enforce rigorous security boundaries to protect the host environment and user data.

## 🎯 Threat Model

We consider the following threat vectors in our design:

1. **Malicious Repositories:** Codebases designed to trigger prompt injection, directory traversal, or buffer overflows during the analysis phase.
2. **Malicious LLM Outputs:** AI models generating command injections, arbitrary code execution payloads, or data exfiltration scripts.
3. **Malicious Agent Skills:** Skill definitions crafted to compromise the agent runtime.
4. **Supply Chain Attacks:** Compromised upstream dependencies.

## 🛡️ Security Boundaries & Protections

SkillFoundry implements defense-in-depth to mitigate the threats outlined above:

- **Strict Data Isolation:** Target repository content is treated exclusively as untrusted string data. It is never `eval()`'d, imported, or executed during the analysis phase.
- **No Auto-Execution:** SkillFoundry will **never** automatically execute LLM-generated bash commands or scripts in the host environment.
- **Secret Redaction Pipeline:** Before any repository data or context is sent to a model provider (OpenAI, Anthropic, Google), it passes through a regex-based and entropy-based secret redaction engine to prevent API key leakage.
- **Path Traversal Prevention:** All file system operations are strictly jailed to the target workspace directory using secure path resolution mechanisms.
- **SSRF Protection:** External network requests made during documentation analysis enforce strict timeouts and deny-list local/private IP ranges to prevent Server-Side Request Forgery.
- **Process-runner evaluation (V0.1):** The evaluation engine runs subprocesses with timeouts, output limits, and command checks. This is not a security sandbox and must not be treated as OS-level isolation.

## 🐛 Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub Issues.**

If you believe you have found a security vulnerability in SkillFoundry, please report it to us directly so we can remediate it safely.

1. **Email:** Send a detailed report to `security@skillfoundry.example.com`.
2. **GitHub Security Advisory:** Alternatively, use the private vulnerability reporting feature directly on our GitHub repository.

Please include the following information in your report:
- A description of the vulnerability and its impact.
- Steps to reproduce the issue (a proof-of-concept is highly appreciated).
- The version(s) of SkillFoundry affected.

We will acknowledge receipt of your vulnerability report within 48 hours and strive to provide a patch as quickly as possible.

## 📦 Supported Versions

Security updates are provided for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| `0.1.x` | :white_check_mark: |
| `< 0.1` | :x:                |

We strongly recommend always running the latest minor version of SkillFoundry to ensure you have the most up-to-date security patches.
