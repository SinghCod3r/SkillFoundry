from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import git

from skillfoundry.security.urls import parse_github_url, validate_url


def clone_repository(url: str, target_dir: Path | None = None) -> Path:
    """Clones a GitHub repository safely."""
    validate_url(url)

    parsed = parse_github_url(url)
    branch = parsed.get("branch") if isinstance(parsed, dict) else None

    if not target_dir:
        target_dir = Path(tempfile.mkdtemp(prefix="skillfoundry_clone_"))

    kwargs = {"depth": 1}
    if branch:
        kwargs["branch"] = branch

    git.Repo.clone_from(url, target_dir, **kwargs)

    return target_dir


def cleanup_clone(clone_dir: Path) -> None:
    """Safely removes a cloned directory."""
    if clone_dir.exists() and clone_dir.is_dir():
        shutil.rmtree(clone_dir, ignore_errors=True)
