from __future__ import annotations

from skillfoundry.models.analysis import ProjectAnalysis, FileCategory

try:
    from skillfoundry.security.redaction import redact_secrets
except ImportError:
    def redact_secrets(text: str) -> str:
        return text

def select_context(analysis: ProjectAnalysis, max_chars: int = 100000) -> str:
    """Select project context and build prompt string."""
    parts = []
    current_length = 0
    
    def add_part(title: str, content: str):
        nonlocal current_length
        if not content:
            return
        section = f"\n=== {title} ===\n{content}\n"
        if current_length + len(section) <= max_chars:
            parts.append(section)
            current_length += len(section)
        elif current_length < max_chars:
            remaining = max_chars - current_length
            parts.append(section[:remaining])
            current_length = max_chars
            
    add_part("README", analysis.documentation_summary)
    
    metadata_str = f"Name: {analysis.metadata.name}\nVersion: {analysis.metadata.version}\nDescription: {analysis.metadata.description}"
    add_part("Metadata", metadata_str)
    
    add_part("Directory Structure", analysis.directory_tree)
    
    for example in analysis.examples:
        add_part(f"Example: {example.title}", example.content)
        
    for f in analysis.files:
        if f.category in (FileCategory.TEST, FileCategory.SOURCE):
            add_part(f"File {f.path} ({f.category.value})", f"Path: {f.path}\nLanguage: {f.language}")
            
    return redact_secrets("".join(parts))
