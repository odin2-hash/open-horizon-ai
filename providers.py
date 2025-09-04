"""Model provider configuration for Open Horizon AI system."""

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from .settings import load_settings


def get_llm_model():
    """Get configured LLM model with proper environment loading."""
    settings = load_settings()
    
    provider = OpenAIProvider(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key
    )
    
    return OpenAIModel(settings.llm_model, provider=provider)