"""
LLM Provider abstraction.

Supports: GroqProvider (active) | OpenAIProvider (future)
Provider is selected via LLM_PROVIDER env var.

IMPORTANT: All providers must:
1. Accept a system_prompt and user_prompt
2. Return a plain string response
3. Never be treated as source of truth for rules/eligibility
"""
from abc import ABC, abstractmethod
from typing import Optional
import asyncio

from pfcompass.config import settings


class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.3,
    ) -> str:
        """Generate a completion. Returns plain text response."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        ...


class GroqProvider(LLMProvider):
    """
    Groq LLM provider using llama-3.3-70b-versatile.
    Fast inference, suitable for real-time citizen explanations.
    """

    @property
    def provider_name(self) -> str:
        return "groq"

    @property
    def model_name(self) -> str:
        return settings.GROQ_MODEL

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.3,
    ) -> str:
        from groq import AsyncGroq

        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment")

        client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        response = await client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content or ""


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider — future implementation."""

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return settings.OPENAI_MODEL

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.3,
    ) -> str:
        raise NotImplementedError("OpenAI provider is planned for a future release.")


def get_llm_provider() -> LLMProvider:
    """
    Factory function — returns the active LLM provider based on LLM_PROVIDER setting.
    Defaults to Groq.
    """
    if settings.LLM_PROVIDER == "openai":
        return OpenAIProvider()
    return GroqProvider()


# Module-level singleton (lazy-initialized)
_provider: Optional[LLMProvider] = None


def llm() -> LLMProvider:
    global _provider
    if _provider is None:
        _provider = get_llm_provider()
    return _provider
