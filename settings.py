"""Settings configuration for Open Horizon AI system."""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from dotenv import load_dotenv
import logging


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # LLM Configuration
    llm_provider: str = Field(default="openai", description="LLM provider")
    llm_api_key: str = Field(..., description="API key for the LLM provider")
    llm_model: str = Field(default="gpt-4o-mini", description="Model name to use")
    llm_base_url: str = Field(
        default="https://api.openai.com/v1", 
        description="Base URL for the LLM API"
    )
    
    # Supabase Configuration
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_key: str = Field(..., description="Supabase anon key")
    supabase_service_key: str = Field(..., description="Supabase service role key")
    
    # External APIs
    erasmus_partner_api_key: str = Field(
        default="demo-key",
        description="API key for Erasmus+ partner database"
    )
    
    # Security
    secret_key: str = Field(..., description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(default=24, description="JWT expiration in hours")
    
    # Application Settings
    app_env: str = Field(default="development", description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    max_retries: int = Field(default=3, description="Max retries for API calls")
    timeout_seconds: int = Field(default=30, description="API timeout in seconds")
    
    # Database Settings
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_connections: int = Field(default=20, description="Max database connections")
    
    # CORS Settings
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow CORS credentials")
    
    @property
    def origins_list(self) -> list[str]:
        """Get allowed origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


def load_settings() -> Settings:
    """Load settings with proper error handling and environment loading."""
    # Load environment variables from .env file
    load_dotenv()
    
    try:
        settings = Settings()
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        return settings
    except Exception as e:
        error_msg = f"Failed to load settings: {e}"
        if "llm_api_key" in str(e).lower():
            error_msg += "\nMake sure to set LLM_API_KEY in your .env file"
        elif "supabase" in str(e).lower():
            error_msg += "\nMake sure to set SUPABASE_URL and SUPABASE_KEY in your .env file"
        raise ValueError(error_msg) from e