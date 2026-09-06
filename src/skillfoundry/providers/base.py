from __future__ import annotations

import json
import re
from enum import Enum
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ModelCapability(Enum):
    GENERATE = "generate"
    STRUCTURED_GENERATE = "structured_generate"
    EMBED = "embed"


class GenerateRequest(BaseModel):
    system_prompt: str
    user_prompt: str
    temperature: float = 0.0
    max_tokens: int = 4096
    response_format: type[BaseModel] | None = None


class GenerateResponse(BaseModel):
    content: str
    model: str
    provider: str
    token_usage: dict[str, int]
    latency_ms: float
    raw_response: Any = None


def parse_json_from_text(text: str) -> dict:
    """Extract JSON from model output that may contain markdown fences or extra text."""
    # Try direct parsing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try finding markdown JSON blocks
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding the first { to the last }
    start_idx = text.find("{")
    end_idx = text.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
        try:
            return json.loads(text[start_idx : end_idx + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not parse JSON from the provided text.")


def validate_and_parse(text: str, schema: type[T], max_retries: int = 3) -> T:
    """Parse and validate model output against a schema."""
    try:
        parsed_data = parse_json_from_text(text)
        return schema.model_validate(parsed_data)
    except (ValueError, ValidationError) as e:
        raise ValueError(f"Validation or parsing failed: {e}") from e


class ModelProvider(Protocol):
    """Protocol for model providers."""

    @property
    def name(self) -> str:
        """Name of the provider."""
        ...

    def supports(self, capability: ModelCapability) -> bool:
        """Check if provider supports a specific capability."""
        ...

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        """Generate text from a prompt."""
        ...

    def structured_generate(self, request: GenerateRequest, schema: type[T]) -> T:
        """Generate structured output conforming to a Pydantic schema.
        
        Default implementation uses text generation and JSON parsing with retries.
        """
        max_retries = 3
        req = request.model_copy()

        req.system_prompt += f"\n\nYou must output strictly valid JSON conforming to this schema:\n{schema.model_json_schema()}"

        for attempt in range(max_retries):
            try:
                response = self.generate(req)
                return validate_and_parse(response.content, schema)
            except ValueError as e:
                if attempt == max_retries - 1:
                    raise
                req.user_prompt += f"\n\nPrevious response failed to parse as JSON or validation failed. Error: {e}\nPlease correct the JSON output."

        raise ValueError("Failed to generate structured output after retries.")
