from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel

from pfcompass.config import settings


class LLMResponse(BaseModel):
    content: str
    parsed_json: Optional[dict[str, Any]] = None
    model_name: str
    provider_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


class LLMProvider(ABC):
    """
    Abstract interface for LLM operations.
    Used for intent understanding and citizen-friendly explanations ONLY.
    Must NEVER make official EPFO eligibility decisions.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @abstractmethod
    async def generate_explanation(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2
    ) -> LLMResponse:
        ...

    @abstractmethod
    async def extract_structured_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: type[BaseModel]
    ) -> BaseModel:
        ...


class GroqProvider(LLMProvider):
    """Groq Provider implementation for MVP."""

    def __init__(self, api_key: str = "", model_name: str = ""):
        self._api_key = api_key or settings.GROQ_API_KEY
        self._model_name = model_name or settings.GROQ_MODEL

    @property
    def provider_name(self) -> str:
        return "groq"

    async def generate_explanation(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2
    ) -> LLMResponse:
        if not self._api_key:
            # Fallback stub if key not set in dev
            return LLMResponse(
                content="[Groq API Key not configured] Stubbed citizen-friendly explanation.",
                model_name=self._model_name,
                provider_name=self.provider_name
            )

        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=self._api_key)
            completion = await client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            choice = completion.choices[0].message
            usage = completion.usage
            return LLMResponse(
                content=choice.content or "",
                model_name=self._model_name,
                provider_name=self.provider_name,
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0
            )
        except Exception as e:
            return LLMResponse(
                content=f"Error generating explanation: {str(e)}",
                model_name=self._model_name,
                provider_name=self.provider_name
            )

    async def extract_structured_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: type[BaseModel]
    ) -> BaseModel:
        if not self._api_key:
            # Fallback dummy instance for schema if key not present
            return schema.model_construct()

        import json
        from groq import AsyncGroq
        client = AsyncGroq(api_key=self._api_key)
        json_sys_prompt = f"{system_prompt}\nReturn JSON strictly adhering to schema: {schema.model_json_schema()}"

        completion = await client.chat.completions.create(
            model=self._model_name,
            messages=[
                {"role": "system", "content": json_sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        content = completion.choices[0].message.content or "{}"
        parsed = json.loads(content)
        return schema.model_validate(parsed)


class OpenAIProvider(LLMProvider):
    """OpenAI Provider implementation (Future expansion)."""

    def __init__(self, api_key: str = "", model_name: str = ""):
        self._api_key = api_key or settings.OPENAI_API_KEY
        self._model_name = model_name or settings.OPENAI_MODEL

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate_explanation(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2
    ) -> LLMResponse:
        if not self._api_key:
            return LLMResponse(
                content="[OpenAI API Key not configured] Stubbed response.",
                model_name=self._model_name,
                provider_name=self.provider_name
            )
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self._api_key)
        completion = await client.chat.completions.create(
            model=self._model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        choice = completion.choices[0].message
        return LLMResponse(
            content=choice.content or "",
            model_name=self._model_name,
            provider_name=self.provider_name
        )

    async def extract_structured_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: type[BaseModel]
    ) -> BaseModel:
        if not self._api_key:
            return schema.model_construct()
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self._api_key)
        completion = await client.beta.chat.completions.parse(
            model=self._model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=schema
        )
        return completion.choices[0].message.parsed


def get_llm_provider() -> LLMProvider:
    """Factory function to retrieve active LLM provider based on config."""
    if settings.LLM_PROVIDER.lower() == "openai":
        return OpenAIProvider()
    return GroqProvider()
