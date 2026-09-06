from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from skillfoundry.security.urls import parse_github_url, validate_url


def clone_repository(url: str, target_dir: Path | None = None) -> Path:
    """Clones a GitHub repository safely using subprocess."""
    validate_url(url)

    if target_dir:
        target_dir = target_dir.resolve()
        if not target_dir.is_relative_to(Path.cwd()):
            raise ValueError(f"Target directory {target_dir} escapes the current working directory.")
    else:
        target_dir = Path(tempfile.mkdtemp(prefix="skillfoundry_clone_")).resolve()

    parsed = parse_github_url(url)
    branch = parsed.get("branch") if isinstance(parsed, dict) else None

    cmd = ["git", "clone", "--depth", "1"]
    if branch:
        cmd.extend(["--branch", branch])
    cmd.extend([url, str(target_dir)])

    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(f"Git clone timed out after 60 seconds for URL: {url}") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git clone failed: {e.stderr.decode('utf-8', errors='ignore')}") from e

    return target_dir


def cleanup_clone(clone_dir: Path) -> None:
    """Safely removes a cloned directory."""
    if clone_dir.exists() and clone_dir.is_dir():
        shutil.rmtree(clone_dir, ignore_errors=True)
