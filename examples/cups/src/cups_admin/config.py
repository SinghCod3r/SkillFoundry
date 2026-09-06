from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ServerConfig:
    host: str = "localhost"
    port: int = 631
    use_ssl: bool = True

@dataclass
class DefaultsConfig:
    printer: str = ""
    format: str = "table"

@dataclass
class Config:
    server: ServerConfig = field(default_factory=ServerConfig)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)

class ConfigManager:
    """Manages the application configuration."""

    def __init__(self, config_path: str = "~/.cups-admin/config.json") -> None:
        self.config_path = Path(os.path.expanduser(config_path))
        self.config = Config()

    def load(self) -> None:
        """Load configuration from file."""
        if not self.config_path.exists():
            return

        with open(self.config_path) as f:
            data = json.load(f)

        if 'server' in data:
            self.config.server = ServerConfig(**data['server'])
        if 'defaults' in data:
            self.config.defaults = DefaultsConfig(**data['defaults'])

    def save(self) -> None:
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "server": {
                "host": self.config.server.host,
                "port": self.config.server.port,
                "use_ssl": self.config.server.use_ssl
            },
            "defaults": {
                "printer": self.config.defaults.printer,
                "format": self.config.defaults.format
            }
        }
        with open(self.config_path, 'w') as f:
            json.dump(data, f, indent=2)
