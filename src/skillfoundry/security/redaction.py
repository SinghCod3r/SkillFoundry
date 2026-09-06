"""Secret detection and redaction."""
from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

SECRET_FILE_PATTERNS = [
    ".env", ".env.*", "*.pem", "*.key", "*credentials*", "*secrets*",
    "*.p12", "*.pfx", "id_rsa*", "id_ed25519*"
]

@dataclass
class SecretPattern:
    name: str
    pattern: re.Pattern[str]
    replacement: str

SECRET_CONTENT_PATTERNS: list[SecretPattern] = [
    SecretPattern(
        name="API Key (sk-)",
        pattern=re.compile(r"sk-[a-zA-Z0-9]{20,}"),
        replacement="[REDACTED]"
    ),
    SecretPattern(
        name="AWS Access Key",
        pattern=re.compile(r"AKIA[0-9A-Z]{16}"),
        replacement="[REDACTED]"
    ),
    SecretPattern(
        name="GitHub Personal Access Token",
        pattern=re.compile(r"ghp_[a-zA-Z0-9]{36}"),
        replacement="[REDACTED]"
    ),
    SecretPattern(
        name="GitHub Server-to-Server Token",
        pattern=re.compile(r"ghs_[a-zA-Z0-9]{36}"),
        replacement="[REDACTED]"
    ),
    SecretPattern(
        name="Slack Token (Bot)",
        pattern=re.compile(r"xoxb-[a-zA-Z0-9\-]+"),
        replacement="[REDACTED]"
    ),
    SecretPattern(
        name="Slack Token (User)",
        pattern=re.compile(r"xoxp-[a-zA-Z0-9\-]+"),
        replacement="[REDACTED]"
    ),
    SecretPattern(
        name="PostgreSQL Connection String",
        pattern=re.compile(r"postgresql://[^:]+:[^@]+@"),
        replacement="postgresql://[REDACTED]:[REDACTED]@"
    ),
    SecretPattern(
        name="MySQL Connection String",
        pattern=re.compile(r"mysql://[^:]+:[^@]+@"),
        replacement="mysql://[REDACTED]:[REDACTED]@"
    ),
    SecretPattern(
        name="MongoDB Connection String",
        pattern=re.compile(r"mongodb://[^:]+:[^@]+@"),
        replacement="mongodb://[REDACTED]:[REDACTED]@"
    ),
]

ENV_PATTERN = re.compile(
    r"^(?P<key>(?:KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL|AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY)[^=]*)=(?P<value>.*)$",
    re.MULTILINE | re.IGNORECASE
)

def is_secret_file(path: str | Path) -> bool:
    """Check if a file path matches secret patterns."""
    p = Path(path)
    for pattern in SECRET_FILE_PATTERNS:
        if p.match(pattern):
            return True
    return False

def has_high_entropy(value: str, threshold: float = 4.0) -> bool:
    """Shannon entropy check for detecting random tokens."""
    if not value:
        return False
    prob = [float(value.count(c)) / len(value) for c in set(value)]
    entropy = -sum(p * math.log2(p) for p in prob)
    return entropy > threshold

def redact_env_values(content: str) -> str:
    """Specifically handle KEY=value patterns in .env-style files."""
    def replacer(match: re.Match[str]) -> str:
        key = match.group("key")
        value = match.group("value").strip()
        if not value or (value.startswith("[") and value.endswith("]")):
            return match.group(0)

        if has_high_entropy(value) or len(value) > 8:
            logger.warning(f"Redacting sensitive environment variable: {key}")
            return f"{key}=[REDACTED]"
        return match.group(0)

    return ENV_PATTERN.sub(replacer, content)

def redact_secrets(content: str) -> str:
    """Replace detected secrets with [REDACTED]."""
    redacted = content
    for sp in SECRET_CONTENT_PATTERNS:
        if sp.pattern.search(redacted):
            logger.warning(f"Redacting secret matching pattern: {sp.name}")
            redacted = sp.pattern.sub(sp.replacement, redacted)

    redacted = redact_env_values(redacted)
    return redacted
