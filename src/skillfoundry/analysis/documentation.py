from __future__ import annotations

import logging
from pathlib import Path

from skillfoundry.models.analysis import FileInfo, FileCategory

try:
    from skillfoundry.security.redaction import redact_secrets
except ImportError:
    def redact_secrets(text: str) -> str:
        return text

logger = logging.getLogger(__name__)

def extract_documentation(root: Path, files: list[FileInfo]) -> tuple[str, str]:
    """Extract documentation content, with size limits and redaction."""
    readme_content = ""
    docs_summary = []
    
    readme_files = [f for f in files if f.path.lower().startswith("readme")]
    readme_file = next((f for f in readme_files if f.path.lower().endswith(".md")), None)
    if not readme_file and readme_files:
        readme_file = readme_files[0]
        
    if readme_file:
        try:
            content = (root / readme_file.path).read_text(errors="ignore")
            readme_content = content[:50000]
        except Exception as e:
            logger.warning(f"Failed to read README: {e}")
            
    for f in files:
        if f.category == FileCategory.DOCUMENTATION and f.path != getattr(readme_file, "path", ""):
            try:
                content = (root / f.path).read_text(errors="ignore")
                docs_summary.append(f"--- {f.path} ---\n{content[:5000]}")
            except Exception:
                pass
                
    return redact_secrets(readme_content), redact_secrets("\n".join(docs_summary))
