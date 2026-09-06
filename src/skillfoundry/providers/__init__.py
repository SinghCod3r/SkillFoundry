from __future__ import annotations

from skillfoundry.providers.base import ModelProvider, GenerateRequest, GenerateResponse, ModelCapability
from skillfoundry.providers.registry import ProviderRegistry, get_provider

__all__ = [
    "ModelProvider",
    "GenerateRequest",
    "GenerateResponse",
    "ModelCapability",
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
