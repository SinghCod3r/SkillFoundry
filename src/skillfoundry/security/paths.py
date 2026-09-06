"""Path validation and traversal prevention."""
from __future__ import annotations

from pathlib import Path


def validate_path(path: str | Path, workspace: str | Path) -> Path:
    """Resolve and verify a path is within workspace. Raise ValueError on traversal attempt."""
    resolved_path = Path(path).resolve()
    resolved_workspace = Path(workspace).resolve()

    try:
        resolved_path.relative_to(resolved_workspace)
    except ValueError:
        raise ValueError(f"Path traversal detected: {path} is outside workspace {workspace}")

    return resolved_path

def safe_join(base: str | Path, *parts: str) -> Path:
    """Safely join path components, checking for traversal."""
    resolved_base = Path(base).resolve()
    joined = resolved_base.joinpath(*parts)
    return validate_path(joined, resolved_base)

def is_path_safe(path: str | Path, workspace: str | Path) -> bool:
    """Check if a path is safely within the workspace."""
    try:
        validate_path(path, workspace)
        return True
    except ValueError:
        return False

def resolve_symlink_safely(path: str | Path, workspace: str | Path) -> Path | None:
    """Follow symlinks but ensure target is within workspace, return None if not safe."""
    p = Path(path)
    if not p.is_symlink():
        return p if is_path_safe(p, workspace) else None

    resolved = p.resolve()
    if is_path_safe(resolved, workspace):
        return resolved
    return None
