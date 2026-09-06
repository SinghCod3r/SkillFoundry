from __future__ import annotations

import os
from pathlib import Path

from skillfoundry.models.analysis import FileInfo, FileCategory, CodeExample

def _build_tree(root: Path, current_path: Path, max_depth: int, current_depth: int = 0, max_entries: int = 200, count: list[int] = None) -> str:
    if count is None:
        count = [0]
    if current_depth > max_depth or count[0] >= max_entries:
        return ""
        
    tree_str = ""
    try:
        entries = sorted(os.listdir(current_path))
    except Exception:
        return ""
        
    for entry in entries:
        if count[0] >= max_entries:
            break
        entry_path = current_path / entry
        indent = "  " * current_depth
        tree_str += f"{indent}- {entry}\n"
        count[0] += 1
        
        if entry_path.is_dir():
            tree_str += _build_tree(root, entry_path, max_depth, current_depth + 1, max_entries, count)
            
    return tree_str

def analyze_structure(root: Path, files: list[FileInfo]) -> tuple[str, list[CodeExample]]:
    """Analyze directory tree and code examples."""
    tree = _build_tree(root, root, max_depth=3, max_entries=200)
    examples = []
    
    for f in files:
        if f.category == FileCategory.EXAMPLE:
            try:
                content = (root / f.path).read_text(errors="ignore")
                examples.append(CodeExample(
                    language=f.language,
                    title=f.path,
                    content=content[:2000]
                ))
            except Exception:
                pass
                
    return tree, examples
