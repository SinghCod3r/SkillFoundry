from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.table import Table

from skillfoundry import __version__

class Output:
    """Terminal output helpers using Rich."""
    
    def __init__(self, quiet: bool = False, json_mode: bool = False) -> None:
        self.quiet = quiet
        self.json_mode = json_mode
        self.console = Console(quiet=self.quiet and not self.json_mode)

    def header(self) -> None:
        """Print SkillFoundry banner with version."""
        if self.json_mode or self.quiet:
            return
        self.console.print(f"SkillFoundry v{__version__}")

    def step(self, number: int, total: int, description: str) -> None:
        """Print progress step."""
        if self.json_mode or self.quiet:
            return
        self.console.print(f"[{number}/{total}] {description}")

    def success(self, message: str) -> None:
        """Print success message."""
        if self.json_mode or self.quiet:
            return
        self.console.print(f"[green]✓ {message}[/green]")

    def warning(self, message: str) -> None:
        """Print warning message."""
        if self.json_mode:
            return
        self.console.print(f"[yellow]⚠ {message}[/yellow]")

    def error(self, message: str) -> None:
        """Print error message."""
        if self.json_mode:
            return
        self.console.print(f"[red]✗ {message}[/red]")

    def info(self, message: str) -> None:
        """Print plain message."""
        if self.json_mode or self.quiet:
            return
        self.console.print(message)

    def result(self, label: str, value: str) -> None:
        """Print label: value."""
        if self.json_mode or self.quiet:
            return
        self.console.print(f"{label}: {value}")

    def newline(self) -> None:
        """Print empty line."""
        if self.json_mode or self.quiet:
            return
        self.console.print()

    def json_output(self, data: dict[str, Any]) -> None:
        """Print formatted JSON to stdout."""
        if self.json_mode:
            self.console.print_json(json.dumps(data))

    def table(self, headers: list[str], rows: list[list[str]]) -> None:
        """Print a Rich table."""
        if self.json_mode or self.quiet:
            return
        table = Table()
        for header in headers:
            table.add_column(header)
        for row in rows:
            table.add_row(*row)
        self.console.print(table)
