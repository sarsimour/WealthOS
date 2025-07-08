"""
LLM Service for OpenAI GPT-4 Vision integration.
Handles structured output parsing, error handling, and rate limiting.
"""

import asyncio
import base64
import logging
import os
import random
from io import BytesIO
from typing import Optional, Type, TypeVar

import openai
from openai import AsyncOpenAI
from PIL import Image
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.schemas.character import CharacterConfig, CharacterState, SMART_FRIEND_CONFIG

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

        # This should never be reached due to the exception handling above
        raise LLMServiceError("Unexpected end of retry loop")

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

        # This should never be reached due to the exception handling above
        raise LLMServiceError("Unexpected end of retry loop")


class CharacterAdvisorService:
    """Character-based investment advisor service with configurable personality."""

    def __init__(self, character_config: Optional[CharacterConfig] = None):
        """Initialize the character advisor service.

        Args:
            character_config: Character configuration (defaults to SMART_FRIEND_CONFIG)
        """
        self.config = character_config or SMART_FRIEND_CONFIG
        self.logger = logging.getLogger(__name__)

        # Initialize LLM client with character's model configuration
        self.api_key = os.getenv(self.config.api_key_env)
        self.base_url = os.getenv(self.config.base_url_env)

        if not self.api_key:
            raise ValueError(
                f"API key not found in environment variable: {self.config.api_key_env}"
            )

        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        self.max_retries = 3
        self.retry_delay = 1.0

    def _build_system_prompt(self, state: Optional[CharacterState] = None) -> str:
        """Build system prompt based on character configuration.

        Args:
            state: Current character state

        Returns:
            Complete system prompt
        """
        personality = self.config.personality

        # Base character description
        base_prompt = f"""
You are {personality.name}, a {personality.age}-year-old {personality.profession}.

{personality.background_story}

{personality.speaking_style}

Core values:
{chr(10).join(f"- {value}" for value in personality.core_values)}

Personality traits: {', '.join(trait.value for trait in personality.primary_traits)}
Tone modifiers: {', '.join(modifier.value for modifier in personality.tone_modifiers)}

Language style guidelines:
- Formality level: {personality.language_style.formality_level:.1f}/1.0 (0=casual, 1=formal)
- Technical jargon: {personality.language_style.technical_jargon:.1f}/1.0 (0=none, 1=heavy)
- Humor level: {personality.language_style.humor_level:.1f}/1.0 (0=serious, 1=funny)
- Directness: {personality.language_style.directness:.1f}/1.0 (0=diplomatic, 1=blunt)
- Empathy level: {personality.language_style.empathy_level:.1f}/1.0 (0=cold, 1=caring)
"""

        # Add state-specific instructions
        if state and state in self.config.state_prompts:
            base_prompt += f"\n\nCurrent situation: {self.config.state_prompts[state]}"

        # Add response style guidelines
        if personality.expertise_level.value == "popularized":
            base_prompt += "\n\nAlways explain complex financial concepts in simple terms that anyone can understand."

        return base_prompt

    def _get_response_template(self, template_type: str) -> str:
        """Get a random response template of the specified type.

        Args:
            template_type: Type of template (greeting, positive_feedback, etc.)

        Returns:
            Random template string
        """
        templates = getattr(
            self.config.personality.response_templates, template_type, []
        )
        if templates:
            return random.choice(templates)
        return ""

    async def generate_character_response(
        self,
        prompt: str,
        state: Optional[CharacterState] = None,
        context: Optional[dict] = None,
        use_template: Optional[str] = None,
    ) -> str:
        """Generate a character-based response.

        Args:
            prompt: User prompt or data to respond to
            state: Current character state
            context: Additional context for the response
            use_template: Template type to use for response intro

        Returns:
            Character-based response

        Raises:
            LLMServiceError: On API errors
        """
        # Build system prompt
        system_prompt = self._build_system_prompt(state)

        # Add template intro if specified
        if use_template:
            template_intro = self._get_response_template(use_template)
            if template_intro:
                prompt = f"{template_intro}\n\n{prompt}"

        # Add context if provided
        if context:
            context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
            prompt = f"Context:\n{context_str}\n\n{prompt}"

        # Generate response
        for attempt in range(self.max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.config.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                )

                content = response.choices[0].message.content
                if not content:
                    raise LLMServiceError("Empty response from character advisor")

                return content

            except openai.RateLimitError as e:
                if attempt == self.max_retries - 1:
                    raise RateLimitError(
                        f"Rate limit exceeded after {self.max_retries} attempts"
                    ) from e
                await asyncio.sleep(self.retry_delay * (2**attempt))

            except openai.APIError as e:
                if attempt == self.max_retries - 1:
                    raise LLMServiceError(f"API error: {e}") from e
                await asyncio.sleep(self.retry_delay)

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise LLMServiceError(f"Unexpected error: {e}") from e
                await asyncio.sleep(self.retry_delay)

        # This should never be reached due to the exception handling above
        raise LLMServiceError("Unexpected end of retry loop")

    async def analyze_portfolio_with_character(
        self,
        portfolio_data: dict,
        analysis_results: dict,
        state: CharacterState = CharacterState.EXPLAINING,
    ) -> str:
        """Analyze portfolio and provide character-based advice.

        Args:
            portfolio_data: Portfolio summary data
            analysis_results: Technical analysis results
            state: Character state for response

        Returns:
            Character-based portfolio analysis
        """
        # Format the analysis data for the character
        prompt = f"""
Please analyze this portfolio and provide advice in your characteristic style:

Portfolio Summary:
- Total Value: ¥{portfolio_data.get('total_value', 0):,.2f}
- Number of Holdings: {portfolio_data.get('total_holdings', 0)}
- Holdings: {portfolio_data.get('holdings_summary', 'Not available')}

Analysis Results:
- Risk Level: {analysis_results.get('risk_level', 'Unknown')}
- Volatility: {analysis_results.get('volatility', 0):.2%}
- Diversification Score: {analysis_results.get('diversification_score', 0):.2f}
- Factor Exposures: {analysis_results.get('factor_exposures', 'Not analyzed')}

Please provide:
1. Your honest assessment of this portfolio
2. Main strengths and weaknesses
3. Specific actionable recommendations
4. Risk warnings if any

Remember to keep it simple, direct, and in your characteristic style.
"""

        return await self.generate_character_response(
            prompt=prompt, state=state, use_template="explanation_intro"
        )

    def update_character_config(self, new_config: CharacterConfig) -> None:
        """Update the character configuration.

        Args:
            new_config: New character configuration
        """
        self.config = new_config

        # Reinitialize client if model configuration changed
        new_api_key = os.getenv(new_config.api_key_env)
        new_base_url = os.getenv(new_config.base_url_env)

        if new_api_key != self.api_key or new_base_url != self.base_url:
            self.api_key = new_api_key
            self.base_url = new_base_url

            if not self.api_key:
                raise ValueError(f"API key not found: {new_config.api_key_env}")

            self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    def get_character_info(self) -> dict:
        """Get current character information.

        Returns:
            Character information dictionary
        """
        return {
            "name": self.config.personality.name,
            "age": self.config.personality.age,
            "profession": self.config.personality.profession,
            "traits": [trait.value for trait in self.config.personality.primary_traits],
            "tone": [
                modifier.value for modifier in self.config.personality.tone_modifiers
            ],
            "expertise_level": self.config.personality.expertise_level.value,
            "response_style": self.config.personality.response_style.value,
        }


# Global service instances
llm_service = LLMService()
character_advisor = CharacterAdvisorService()
