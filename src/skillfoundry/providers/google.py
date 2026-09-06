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
    import google.generativeai as genai
except ImportError:
    genai = None


class GoogleProvider:
    """Google Gemini implementation of ModelProvider."""

    def __init__(self, api_key: str | None = None, model: str = "gemini-2.0-flash") -> None:
        if genai is None:
            raise ImportError("Google Generative AI SDK is not installed. Please run `pip install skillfoundry[google]` or `pip install google-generativeai`.")

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key must be provided or set in GOOGLE_API_KEY environment variable.")

        genai.configure(api_key=self.api_key)
        self.model_name = model

    @property
    def name(self) -> str:
        return "google"

    def supports(self, capability: ModelCapability) -> bool:
        return capability in (ModelCapability.GENERATE, ModelCapability.STRUCTURED_GENERATE)

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        """Generate text using Google Gemini."""
        start_time = time.time()
        try:
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=request.system_prompt if request.system_prompt else None
            )

            generation_config = genai.types.GenerationConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
            )

            response = model.generate_content(
                request.user_prompt,
                generation_config=generation_config
            )
            latency = (time.time() - start_time) * 1000

            content = response.text

            input_tokens = 0
            output_tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)

            return GenerateResponse(
                content=content,
                model=self.model_name,
                provider=self.name,
                token_usage={"input_tokens": input_tokens, "output_tokens": output_tokens},
                latency_ms=latency,
                raw_response=response.to_dict() if hasattr(response, "to_dict") else {},
            )
        except Exception as e:
            raise RuntimeError(f"Google Generative AI Error: {e}") from e

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
