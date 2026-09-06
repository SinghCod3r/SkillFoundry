from __future__ import annotations

import os
import time
from typing import TypeVar

from pydantic import BaseModel

from skillfoundry.providers.base import (
    GenerateRequest,
    GenerateResponse,
    ModelCapability,
    ModelProvider,
    validate_and_parse,
)

T = TypeVar("T", bound=BaseModel)

try:
    import anthropic
    from anthropic import Anthropic
except ImportError:
    anthropic = None


class AnthropicProvider:
    """Anthropic implementation of ModelProvider."""

    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-20240620") -> None:
        if anthropic is None:
            raise ImportError("Anthropic SDK is not installed. Please run `pip install skillfoundry[anthropic]` or `pip install anthropic`.")

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key must be provided or set in ANTHROPIC_API_KEY environment variable.")

        self.model = model
        self.client = Anthropic(api_key=self.api_key)

    @property
    def name(self) -> str:
        return "anthropic"

    def supports(self, capability: ModelCapability) -> bool:
        return capability in (ModelCapability.GENERATE, ModelCapability.STRUCTURED_GENERATE)

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        """Generate text using Anthropic Claude."""
        start_time = time.time()
        try:
            response = self.client.messages.create(
                model=self.model,
                system=request.system_prompt,
                messages=[
                    {"role": "user", "content": request.user_prompt},
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            latency = (time.time() - start_time) * 1000

            content = response.content[0].text if response.content else ""
            token_usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }

            raw = response.model_dump() if hasattr(response, "model_dump") else {}

            return GenerateResponse(
                content=content,
                model=self.model,
                provider=self.name,
                token_usage=token_usage,
                latency_ms=latency,
                raw_response=raw,
            )
        except Exception as e:
            raise RuntimeError(f"Anthropic API Error: {e}") from e

    def structured_generate(self, request: GenerateRequest, schema: type[T]) -> T:
        """Generate structured output using text generation + JSON parsing fallback."""
        max_retries = 3
        req = request.model_copy()

        req.system_prompt += f"\n\nYou must output strictly valid JSON conforming to this schema:\n{schema.model_json_schema()}"

        for attempt in range(max_retries):
            try:
                resp = self.generate(req)
                return validate_and_parse(resp.content, schema)
            except ValueError as e:
                if attempt == max_retries - 1:
                    raise
                req.user_prompt += f"\n\nPrevious response failed to parse as JSON or validation failed. Error: {e}\nPlease correct the JSON output."

        raise ValueError("Failed to generate structured output after retries.")

# Check compatibility
