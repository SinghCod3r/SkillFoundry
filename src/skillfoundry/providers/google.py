from __future__ import annotations

import os
import time
from typing import TypeVar

from pydantic import BaseModel

from skillfoundry.providers.base import (
    GenerateRequest,
    GenerateResponse,
    ModelCapability,
)

T = TypeVar("T", bound=BaseModel)

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None


class GoogleProvider:
    """Google Gemini implementation of ModelProvider using google-genai."""

    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash") -> None:
        if genai is None:
            raise ImportError("Google GenAI SDK is not installed. Please run `pip install google-genai`.")

        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Google API key must be provided or set in GOOGLE_API_KEY environment variable.")

        self.client = genai.Client(api_key=self.api_key)
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
            config = types.GenerateContentConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
                system_instruction=request.system_prompt if request.system_prompt else None,
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=request.user_prompt,
                config=config,
            )
            latency = (time.time() - start_time) * 1000

            content = response.text or ""

            input_tokens = 0
            output_tokens = 0
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)

            raw_response = {}
            if hasattr(response, "model_dump"):
                raw_response = response.model_dump()
            elif hasattr(response, "to_dict"):
                raw_response = response.to_dict()

            return GenerateResponse(
                content=content,
                model=self.model_name,
                provider=self.name,
                token_usage={"input_tokens": input_tokens, "output_tokens": output_tokens},
                latency_ms=latency,
                raw_response=raw_response,
            )
        except Exception as e:
            raise RuntimeError(f"Google GenAI Error: {e}") from e

    def structured_generate(self, request: GenerateRequest, schema: type[T]) -> T:
        """Generate structured output using GenAI response_schema."""
        try:
            config = types.GenerateContentConfig(
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
                system_instruction=request.system_prompt if request.system_prompt else None,
                response_mime_type="application/json",
                response_schema=schema,
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=request.user_prompt,
                config=config,
            )
            content = response.text
            if not content:
                raise ValueError("Received empty content from model.")

            return schema.model_validate_json(content)
        except Exception as e:
            raise RuntimeError(f"Google GenAI Structured Output Error: {e}") from e
