"""
LLM Service for OpenAI GPT-4 Vision integration.
Handles structured output parsing, error handling, and rate limiting.
"""

import asyncio
import base64
import logging
from io import BytesIO
from typing import Optional, Type, TypeVar

import openai
from openai import AsyncOpenAI
from PIL import Image
from pydantic import BaseModel, ValidationError

from app.core.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class LLMServiceError(Exception):
    """Base exception for LLM service errors."""

    pass


class RateLimitError(LLMServiceError):
    """Raised when hitting API rate limits."""

    pass


class ParseError(LLMServiceError):
    """Raised when failing to parse LLM response."""

    pass


class LLMService:
    """Service for interacting with LLM Vision API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM service.

        Args:
            api_key: OpenAI API key. will use settings.QWEN_API_KEY
        """
        self.api_key = getattr(settings, "QWEN_API_KEY", None)
        self.api_base = getattr(settings, "QWEN_BASE_URL", None)
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.api_base)
        self.max_retries = 3
        self.retry_delay = 1.0

    async def analyze_image_with_structured_output(
        self,
        image_data: bytes,
        prompt: str,
        response_model: Type[T],
        max_tokens: int = 2000,
        temperature: float = 0.1,
    ) -> T:
        """Analyze an image and return structured output.

        Args:
            image_data: Raw image bytes
            prompt: Text prompt for analysis
            response_model: Pydantic model for structured output
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            Parsed response as the specified model

        Raises:
            LLMServiceError: On API or parsing errors
            RateLimitError: On rate limit exceeded
            ParseError: On response parsing failure
        """
        # Validate and process image
        processed_image = await self._process_image(image_data)

        # Prepare the message with image
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{processed_image}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ]

        # Add schema information to the prompt
        schema_prompt = self._build_schema_prompt(response_model)
        messages[0]["content"][0]["text"] = f"{prompt}\n\n{schema_prompt}"

        # Make API call with retries
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model="qwen-vl-plus-2025-05-07",  # GPT-4 with vision capabilities
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )

                # Parse the response
                content = response.choices[0].message.content
                if not content:
                    raise ParseError("Empty response from LLM")

                # Parse JSON and validate with Pydantic
                try:
                    import json

                    parsed_data = json.loads(content)
                    return response_model(**parsed_data)
                except (json.JSONDecodeError, ValidationError) as e:
                    raise ParseError(f"Failed to parse response: {e}") from e

            except openai.RateLimitError as e:
                if attempt == self.max_retries - 1:
                    raise RateLimitError(
                        f"Rate limit exceeded after {self.max_retries} attempts"
                    ) from e
                await asyncio.sleep(self.retry_delay * (2**attempt))

            except openai.APIError as e:
                if attempt == self.max_retries - 1:
                    raise LLMServiceError(f"OpenAI API error: {e}") from e
                await asyncio.sleep(self.retry_delay)

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise LLMServiceError(f"Unexpected error: {e}") from e
                await asyncio.sleep(self.retry_delay)

    async def _process_image(self, image_data: bytes) -> str:
        """Process and encode image for API.

        Args:
            image_data: Raw image bytes

        Returns:
            Base64 encoded image string

        Raises:
            LLMServiceError: On image processing errors
        """
        try:
            # Open and validate image
            image = Image.open(BytesIO(image_data))

            # Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Resize if too large (max 2048x2048 for GPT-4 Vision)
            max_size = 2048
            if image.width > max_size or image.height > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            # Convert to JPEG and encode
            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=85, optimize=True)
            buffer.seek(0)

            return base64.b64encode(buffer.read()).decode("utf-8")

        except Exception as e:
            raise LLMServiceError(f"Failed to process image: {e}") from e

    def _build_schema_prompt(self, response_model: Type[BaseModel]) -> str:
        """Build schema prompt for structured output.

        Args:
            response_model: Pydantic model class

        Returns:
            Schema prompt string
        """
        schema = response_model.model_json_schema()

        prompt = f"""
Please respond with a valid JSON object that matches this exact schema:

{schema}

Important:
- Return ONLY valid JSON
- Include all required fields
- Use the exact field names specified
- Follow the data types specified in the schema
- Do not include any explanatory text outside the JSON
"""
        return prompt

    async def generate_text_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> str:
        """Generate a text response using GPT-4.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            Generated text response

        Raises:
            LLMServiceError: On API errors
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model="qwen-turbo",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                content = response.choices[0].message.content
                if not content:
                    raise LLMServiceError("Empty response from LLM")

                return content

            except openai.RateLimitError as e:
                if attempt == self.max_retries - 1:
                    raise RateLimitError(
                        f"Rate limit exceeded after {self.max_retries} attempts"
                    ) from e
                await asyncio.sleep(self.retry_delay * (2**attempt))

            except openai.APIError as e:
                if attempt == self.max_retries - 1:
                    raise LLMServiceError(f"OpenAI API error: {e}") from e
                await asyncio.sleep(self.retry_delay)

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise LLMServiceError(f"Unexpected error: {e}") from e
                await asyncio.sleep(self.retry_delay)


# Global LLM service instance
llm_service = LLMService()
