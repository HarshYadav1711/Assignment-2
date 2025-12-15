"""
Application configuration using Pydantic settings.
Centralizes environment variable management with validation.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Supabase Configuration
    supabase_url: str
    supabase_key: str
    
    # OpenAI Configuration
    openai_api_key: str
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # LLM Configuration
    openai_model: str = "gpt-4o"  # Updated to current model. Alternatives: gpt-4-turbo, gpt-3.5-turbo, gpt-4
    # Can be overridden via OPENAI_MODEL environment variable
    max_tokens: int = 2000
    temperature: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

