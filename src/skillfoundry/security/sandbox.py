"""Execution sandbox abstraction."""
from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

BLOCKED_COMMANDS = ['rm -rf /', 'sudo', 'chmod 777', 'mkfs', 'dd']

@dataclass
class SandboxConfig:
    timeout: int = 60
    max_output_bytes: int = 1024 * 1024  # 1MB
    network_enabled: bool = False
    working_dir: Path | None = None
    allowed_paths: list[Path] = field(default_factory=list)

@dataclass
class SandboxResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    duration_ms: float

def validate_command(command: list[str]) -> list[str]:
    """Check command against blocklist, raise ValueError if dangerous."""
    cmd_str = " ".join(command)
    for blocked in BLOCKED_COMMANDS:
        if blocked in cmd_str:
            raise ValueError(f"Command blocked due to security policy: {blocked}")
    return command

def create_temp_workspace() -> Path:
    """Create isolated temp directory for execution."""
    return Path(tempfile.mkdtemp(prefix="skillfoundry_sandbox_"))

def cleanup_workspace(path: Path) -> None:
    """Safely remove temp workspace."""
    if path.exists() and path.is_dir():
        shutil.rmtree(path, ignore_errors=True)

def run_sandboxed(command: list[str], config: SandboxConfig) -> SandboxResult:
    """Run a command as subprocess with timeout, output capture, and resource limits."""
    validate_command(command)

    start_time = time.time()
    stdout_b = b""
    stderr_b = b""
    exit_code = -1
    timed_out = False

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=config.working_dir if config.working_dir else None,
        )

        try:
            stdout_b, stderr_b = process.communicate(timeout=config.timeout)
            exit_code = process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            stdout_b, stderr_b = process.communicate()
            timed_out = True
            exit_code = -1

    except Exception as e:
        stderr_b = str(e).encode()
        exit_code = -1

    duration_ms = (time.time() - start_time) * 1000

    if len(stdout_b) > config.max_output_bytes:
        stdout_b = stdout_b[:config.max_output_bytes] + b"\n[TRUNCATED]"
    if len(stderr_b) > config.max_output_bytes:
        stderr_b = stderr_b[:config.max_output_bytes] + b"\n[TRUNCATED]"

    return SandboxResult(
        stdout=stdout_b.decode(errors="replace"),
        stderr=stderr_b.decode(errors="replace"),
        exit_code=exit_code,
        timed_out=timed_out,
        duration_ms=duration_ms
    )
