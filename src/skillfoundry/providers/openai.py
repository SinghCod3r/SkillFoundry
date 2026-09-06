from __future__ import annotations

import os
import time
from typing import Any, TypeVar

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
    import openai
    from openai import OpenAI
except ImportError:
    openai = None


class OpenAIProvider:
    """OpenAI implementation of ModelProvider."""
    
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o", api_base: str | None = None) -> None:
        if openai is None:
            raise ImportError("OpenAI SDK is not installed. Please run `pip install skillfoundry[openai]` or `pip install openai`.")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable.")
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key, base_url=api_base)

    @property
    def name(self) -> str:
        return "openai"

    def supports(self, capability: ModelCapability) -> bool:
        return capability in (ModelCapability.GENERATE, ModelCapability.STRUCTURED_GENERATE)

    def generate(self, request: GenerateRequest) -> GenerateResponse:
        """Generate text using OpenAI."""
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": request.user_prompt},
                ],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            latency = (time.time() - start_time) * 1000
            
            content = response.choices[0].message.content or ""
            usage = response.usage
            token_usage = {
                "input_tokens": usage.prompt_tokens if usage else 0,
                "output_tokens": usage.completion_tokens if usage else 0,
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
        except openai.APIError as e:
            raise RuntimeError(f"OpenAI API Error: {e}") from e
        except openai.RateLimitError as e:
            raise RuntimeError(f"OpenAI Rate Limit Error: {e}") from e
        except openai.APITimeoutError as e:
            raise RuntimeError(f"OpenAI Timeout Error: {e}") from e

    def structured_generate(self, request: GenerateRequest, schema: type[T]) -> T:
        """Generate structured output using OpenAI's native JSON support if possible."""
        try:
            # Using structured outputs native to OpenAI for supported models
            response = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": request.user_prompt},
                ],
                response_format=schema,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            if response.choices[0].message.parsed:
                return response.choices[0].message.parsed
        except Exception:
            pass # Fallback to base text + parse approach
            
        # Fallback approach
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
_: ModelProvider = OpenAIProvider()
