from __future__ import annotations

import difflib
from pathlib import Path

from skillfoundry.models.skill import GeneratedSkill


def generate_diff(old_content: str, new_content: str) -> str:
    """Generates a human-readable unified diff between two strings."""
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile="old",
        tofile="new"
    )
    return "".join(diff)


def generate_skill_diff(old_dir: Path, new_dir: Path) -> str:
    """Compares all files in both skill directories and returns a combined diff."""
    diffs = []
    
    old_files = {p.name: p for p in old_dir.rglob("*") if p.is_file()}
    new_files = {p.name: p for p in new_dir.rglob("*") if p.is_file()}
    
    all_names = set(old_files.keys()).union(new_files.keys())
    
    for name in sorted(all_names):
        old_p = old_files.get(name)
        new_p = new_files.get(name)
        
        old_content = old_p.read_text() if old_p else ""
        new_content = new_p.read_text() if new_p else ""
        
        if old_content != new_content:
            diffs.append(f"--- a/{name}\n+++ b/{name}\n")
            diffs.append(generate_diff(old_content, new_content))
            
    return "".join(diffs)


def summarize_changes(diff: str) -> list[str]:
    """Extracts a list of human-readable change descriptions from a diff."""
    changes = []
    for line in diff.splitlines():
        if line.startswith("+ ") and not line.startswith("+++"):
            changes.append(f"+ Added: {line[2:].strip()}")
        elif line.startswith("- ") and not line.startswith("---"):
            changes.append(f"- Removed: {line[2:].strip()}")
    return list(set(changes))
