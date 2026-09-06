# Security Policy

## Threat Model

SkillFoundry operates in diverse environments where the analyzed data and outputs are untrusted. We consider the following threat vectors:

- **Malicious repository author:** Attempting prompt injection or including malicious files to exploit the analysis engine.
- **Malicious skill author:** Creating dangerous skill content designed to cause harm when loaded.
- **Malicious model output:** The LLM generating command injections or exfiltration attempts.
- **Malicious evaluation task:** Sandbox escape attempts during evaluation.
- **Malicious dependency:** Supply chain attacks via compromised packages.
- **Malicious PR:** Exploitation via GitHub Actions.

## Security Boundaries

SkillFoundry implements strict security boundaries to protect the host environment:

- **Untrusted Data:** Repository content is treated strictly as untrusted data and never evaluated as raw instructions.
- **Model Output Validation:** All LLM outputs are carefully parsed and validated before further processing.
- **No Auto-Execution:** Generated commands are **never** executed automatically. They require explicit confirmation or run within sandboxes.
- **Secret Redaction:** Potential secrets and API keys are detected and redacted before being submitted to model providers.
- **SSRF Protection:** External URLs fetched during analysis or evaluation have SSRF protections enforced.
- **Path Traversal Prevention:** Secure path resolution prevents access outside of the target workspace.
- **Isolated Evaluation:** Evaluations must run in isolated or containerized environments to prevent host compromise.

## Reporting a Vulnerability

**DO NOT** report security vulnerabilities through public GitHub Issues.

If you discover a security vulnerability within SkillFoundry, please send an email to `security@skillfoundry.example.com` or use the private vulnerability reporting feature on GitHub. We will respond promptly.

## Supported Versions

Only the latest `0.1.x` and `main` branches are actively supported with security updates.
