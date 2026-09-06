from __future__ import annotations

from skillfoundry.providers.base import (
    GenerateRequest,
    GenerateResponse,
    ModelCapability,
    ModelProvider,
)
from skillfoundry.providers.registry import ProviderRegistry, get_provider

__all__ = [
    "GenerateRequest",
    "GenerateResponse",
    "ModelCapability",
    "ModelProvider",
    "ProviderRegistry",
    "get_provider",
]

# Auto-register standard providers
try:
    from skillfoundry.providers.openai import OpenAIProvider
    ProviderRegistry.register("openai", OpenAIProvider)
except ImportError:
    pass

try:
    from skillfoundry.providers.anthropic import AnthropicProvider
    ProviderRegistry.register("anthropic", AnthropicProvider)
except ImportError:
    pass

try:
    from skillfoundry.providers.google import GoogleProvider
    ProviderRegistry.register("google", GoogleProvider)
except ImportError:
    pass
