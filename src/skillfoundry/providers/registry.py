from __future__ import annotations

import os
from typing import Any

from skillfoundry.config.settings import ModelSettings
from skillfoundry.providers.base import ModelProvider


class ProviderRegistry:
    """Registry for managing model providers."""
    
    _providers: dict[str, type[ModelProvider]] = {}

    @classmethod
    def register(cls, name: str, provider_class: type[ModelProvider]) -> None:
        """Register a new provider class."""
        cls._providers[name] = provider_class

    @classmethod
    def get(cls, name: str, **kwargs: Any) -> ModelProvider:
        """Get an instance of a registered provider."""
        if name not in cls._providers:
            raise ValueError(f"Provider '{name}' not found. Available providers: {cls.available()}")
        return cls._providers[name](**kwargs)

    @classmethod
    def available(cls) -> list[str]:
        """Get a list of registered provider names."""
        return list(cls._providers.keys())

    @classmethod
    def is_available(cls, name: str) -> bool:
        """Check if a provider is registered."""
        return name in cls._providers


def get_provider(settings: ModelSettings) -> ModelProvider:
    """Create a provider instance from settings."""
    provider_name = getattr(settings, "provider", None)
    
    # Auto-detect from environment if not specified
    if not provider_name:
        if os.getenv("OPENAI_API_KEY"):
            provider_name = "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            provider_name = "anthropic"
        elif os.getenv("GOOGLE_API_KEY"):
            provider_name = "google"
        else:
            raise ValueError("No provider specified and no API keys found in environment.")

    kwargs = {}
    if hasattr(settings, "model") and settings.model:
        kwargs["model"] = settings.model
    if hasattr(settings, "api_key") and settings.api_key:
        kwargs["api_key"] = settings.api_key
    if hasattr(settings, "api_base") and settings.api_base:
        kwargs["api_base"] = settings.api_base

    return ProviderRegistry.get(provider_name, **kwargs)
