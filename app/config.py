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
    # Railway and other platforms set PORT automatically
    # Pydantic will read PORT (uppercase) and map to port (lowercase) due to case_sensitive=False
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
# Initialize with validation - will raise clear error if required vars missing
try:
    settings = Settings()
    # Validate that required vars are actually set (not empty)
    if not settings.supabase_url or settings.supabase_url == "your_supabase_url_here":
        raise ValueError("SUPABASE_URL environment variable is required but not set")
    if not settings.supabase_key or settings.supabase_key == "your_supabase_anon_key_here":
        raise ValueError("SUPABASE_KEY environment variable is required but not set")
    if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
        raise ValueError("OPENAI_API_KEY environment variable is required but not set")
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Configuration error: {e}")
    logger.error("Please set all required environment variables:")
    logger.error("  - SUPABASE_URL")
    logger.error("  - SUPABASE_KEY")
    logger.error("  - OPENAI_API_KEY")
    raise

