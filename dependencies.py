"""Dependencies for Open Horizon AI agent system."""

from dataclasses import dataclass
from typing import Optional, Any
import httpx
from supabase import create_client, Client
from .settings import load_settings


@dataclass
class OpenHorizonDependencies:
    """
    Dependencies for Open Horizon AI agent system.
    Includes Supabase client and external API credentials.
    """
    
    # Database and Storage
    supabase_client: Optional[Client] = None
    database_url: Optional[str] = None
    
    # External APIs
    erasmus_partner_api_key: Optional[str] = None
    
    # Runtime Context
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    
    # Configuration
    max_retries: int = 3
    timeout: int = 30
    debug: bool = False
    
    # Private clients
    _supabase_client: Optional[Client] = None
    _partner_api_client: Optional[httpx.AsyncClient] = None
    
    @classmethod
    def from_settings(
        cls,
        settings = None,
        **overrides
    ) -> "OpenHorizonDependencies":
        """Create dependencies from settings."""
        if settings is None:
            settings = load_settings()
        
        return cls(
            database_url=settings.supabase_url,
            erasmus_partner_api_key=settings.erasmus_partner_api_key,
            max_retries=settings.max_retries,
            timeout=settings.timeout_seconds,
            debug=settings.debug,
            **overrides
        )
    
    @property
    def supabase(self) -> Client:
        """Lazy initialization of Supabase client."""
        if self._supabase_client is None:
            settings = load_settings()
            self._supabase_client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
        return self._supabase_client
    
    @property
    def partner_api_client(self) -> httpx.AsyncClient:
        """HTTP client for partner discovery."""
        if self._partner_api_client is None:
            self._partner_api_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers={"Authorization": f"Bearer {self.erasmus_partner_api_key}"}
            )
        return self._partner_api_client
    
    async def cleanup(self):
        """Cleanup all external connections."""
        if self._partner_api_client:
            await self._partner_api_client.aclose()
            self._partner_api_client = None