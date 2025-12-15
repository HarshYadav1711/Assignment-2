"""
Application configuration using Pydantic settings.
Centralizes environment variable management with validation.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


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
import logging
logger = logging.getLogger(__name__)

try:
    settings = Settings()
    # Validate that required vars are actually set (not empty)
    missing_vars = []
    if not settings.supabase_url or settings.supabase_url == "your_supabase_url_here":
        missing_vars.append("SUPABASE_URL")
    if not settings.supabase_key or settings.supabase_key == "your_supabase_anon_key_here":
        missing_vars.append("SUPABASE_KEY")
    if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
        missing_vars.append("OPENAI_API_KEY")
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error("=" * 60)
        logger.error("CONFIGURATION ERROR")
        logger.error("=" * 60)
        logger.error(error_msg)
        logger.error("")
        logger.error("Please set these environment variables in Railway:")
        for var in missing_vars:
            logger.error(f"  - {var}")
        logger.error("")
        logger.error("Go to: Railway Dashboard → Your Project → Variables")
        logger.error("=" * 60)
        raise ValueError(error_msg)
    
    logger.info("Configuration loaded successfully")
    logger.info(f"Port: {settings.port} (from PORT env var: {os.getenv('PORT', 'not set')})")
    
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    # Re-raise so the app doesn't start with invalid config
    raise

