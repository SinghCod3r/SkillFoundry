"""Data models for project analysis."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class FileCategory(str, Enum):
    """Classification of a file by its role in the project."""

    DOCUMENTATION = "documentation"
    MANIFEST = "manifest"
    SOURCE = "source"
    TEST = "test"
    EXAMPLE = "example"
    CONFIGURATION = "configuration"
    BUILD = "build"
    CI = "ci"
    SCRIPT = "script"
    SCHEMA = "schema"
    ASSET = "asset"
    OTHER = "other"


class FileInfo(BaseModel):
    """Metadata about a single file in the project."""

    path: str
    relative_path: str
    size: int
    category: FileCategory = FileCategory.OTHER
    language: str | None = None
    is_binary: bool = False
    is_generated: bool = False
    is_secret: bool = False
    relevance_score: float = Field(ge=0.0, le=1.0, default=0.5)


class ProjectMetadata(BaseModel):
    """Extracted metadata from package manifests."""

    name: str = ""
    version: str = ""
    description: str = ""
    languages: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    dev_dependencies: list[str] = Field(default_factory=list)
    scripts: dict[str, str] = Field(default_factory=dict)
    entry_points: list[str] = Field(default_factory=list)
    repository_url: str = ""
    license: str = ""


class Capability(BaseModel):
    """A capability or feature of the project that could be useful for agents."""

    name: str
    description: str
    source_files: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class Workflow(BaseModel):
    """A multi-step workflow or process in the project."""

    name: str
    description: str
    steps: list[str] = Field(default_factory=list)
    source_files: list[str] = Field(default_factory=list)


class APIEndpoint(BaseModel):
    """A detected API endpoint or function."""

    name: str
    description: str = ""
    method: str = ""
    path: str = ""
    source_file: str = ""


class CLICommand(BaseModel):
    """A detected CLI command or subcommand."""

    name: str
    description: str = ""
    usage: str = ""
    source_file: str = ""


class CodeExample(BaseModel):
    """An example found in the project."""

    title: str
    description: str = ""
    file_path: str = ""
    content: str = ""
    language: str = ""


class ProjectAnalysis(BaseModel):
    """Complete analysis of a project — input to skill generation."""

    source_path: str
    project_metadata: ProjectMetadata = Field(default_factory=ProjectMetadata)
    files: list[FileInfo] = Field(default_factory=list)
    total_files: int = 0
    analyzed_files: int = 0
    skipped_files: int = 0
    capabilities: list[Capability] = Field(default_factory=list)
    workflows: list[Workflow] = Field(default_factory=list)
    api_endpoints: list[APIEndpoint] = Field(default_factory=list)
    cli_commands: list[CLICommand] = Field(default_factory=list)
    examples: list[CodeExample] = Field(default_factory=list)
    documentation_summary: str = ""
    readme_content: str = ""
    directory_tree: str = ""
    warnings: list[str] = Field(default_factory=list)
