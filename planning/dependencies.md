# Open Horizon AI - Dependency Configuration

## Architecture Overview

Open Horizon AI uses a dual-architecture approach:
- **Frontend**: React/TypeScript web interface (Archon fork)
- **Backend**: FastAPI + Pydantic AI agents
- **Database**: Supabase for data persistence
- **AI Integration**: OpenAI-powered multi-agent system

## Environment Configuration

### Essential Environment Variables

```bash
# LLM Configuration (REQUIRED)
LLM_PROVIDER=openai
LLM_API_KEY=your-openai-api-key-here
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1

# Database Configuration (REQUIRED)
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key

# External APIs (REQUIRED)
ERASMUS_PARTNER_DB_API_KEY=your-erasmus-partner-api-key

# Application Security (REQUIRED)
SECRET_KEY=your-jwt-secret-key-for-sessions
APP_ENV=development

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT_SECONDS=30
```

### Configuration Structure

```
dependencies/
├── __init__.py
├── settings.py       # Environment configuration with Supabase
├── providers.py      # OpenAI model provider setup
├── dependencies.py   # Agent dependencies with database models
├── agent.py         # Main agent initialization
├── database.py      # Supabase client configuration
├── .env.example     # Environment template
└── requirements.txt # Python dependencies
```

## Core Dependencies

### Agent Dependencies Class

The agent will use these dependencies injected through RunContext:

```python
@dataclass
class OpenHorizonDependencies:
    """
    Dependencies for Open Horizon AI agent system.
    Includes Supabase client and external API credentials.
    """
    
    # Database and Storage
    supabase_client: Optional[Any] = None
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
```

### Core Data Models

The agent will work with these Pydantic models:

```python
# Project Management Models
class Project(BaseModel):
    id: str
    title: str
    focus_area: str
    target_audience: str
    innovation_angle: str
    status: str
    created_at: datetime
    partners: List['Partner'] = []

class Partner(BaseModel):
    id: str
    name: str
    country: str
    organization_type: str
    expertise_areas: List[str]
    erasmus_code: str
    contact_email: Optional[str] = None

class ApplicationSection(BaseModel):
    section_name: str
    content: str
    word_count: int
    compliance_status: bool
    suggestions: List[str] = []
```

## Service Integrations

### Supabase Database Client

```python
# Lazy initialization pattern for Supabase
@property
def supabase_client(self):
    """Lazy initialization of Supabase client."""
    if self._supabase_client is None:
        from supabase import create_client, Client
        self._supabase_client = create_client(
            self.supabase_url,
            self.supabase_key
        )
    return self._supabase_client
```

### External API Clients

```python
# HTTP client for Erasmus+ Partner Database
@property
def partner_api_client(self):
    """HTTP client for partner discovery."""
    if self._partner_api_client is None:
        import httpx
        self._partner_api_client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            headers={"Authorization": f"Bearer {self.erasmus_partner_api_key}"}
        )
    return self._partner_api_client
```

## Python Dependencies

### Core Requirements

```
# Pydantic AI Framework
pydantic-ai>=0.1.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# OpenAI Integration
openai>=1.0.0

# Database and Storage
supabase>=2.0.0
asyncpg>=0.28.0

# Web Framework (for API endpoints)
fastapi>=0.104.0
uvicorn[standard]>=0.24.0

# HTTP and Async
httpx>=0.25.0
aiofiles>=23.0.0

# Environment Management
python-dotenv>=1.0.0

# Security
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Development Tools
pytest>=7.4.0
pytest-asyncio>=0.21.0
black>=23.0.0
ruff>=0.1.0
```

### Optional Development Dependencies

```
# Testing and Validation
pytest-mock>=3.12.0
httpx-mock>=0.10.0

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.4.0

# Monitoring
loguru>=0.7.0
sentry-sdk>=1.38.0
```

## Database Schema Requirements

### Supabase Tables

The system requires these database tables:

```sql
-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    focus_area TEXT NOT NULL,
    target_audience TEXT,
    innovation_angle TEXT,
    status TEXT DEFAULT 'brainstorming',
    created_at TIMESTAMP DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id)
);

-- Partners table  
CREATE TABLE partners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    organization_type TEXT,
    expertise_areas TEXT[],
    erasmus_code TEXT UNIQUE,
    contact_email TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Project Partners junction table
CREATE TABLE project_partners (
    project_id UUID REFERENCES projects(id),
    partner_id UUID REFERENCES partners(id),
    role TEXT,
    PRIMARY KEY (project_id, partner_id)
);

-- Application Sections table
CREATE TABLE application_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    section_name TEXT NOT NULL,
    content TEXT,
    word_count INTEGER,
    compliance_status BOOLEAN DEFAULT false,
    suggestions TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Security Configuration

### API Key Validation

```python
@field_validator("llm_api_key", "supabase_key", "erasmus_partner_api_key")
@classmethod
def validate_api_keys(cls, v):
    """Ensure API keys are not empty."""
    if not v or v.strip() == "":
        raise ValueError("API key cannot be empty")
    return v
```

### Database Security

```python
@field_validator("supabase_url")
@classmethod
def validate_supabase_url(cls, v):
    """Validate Supabase URL format."""
    if not v.startswith("https://"):
        raise ValueError("Supabase URL must use HTTPS")
    return v
```

## Agent Initialization Pattern

### Simple Agent Setup

```python
# Load settings with Supabase configuration
settings = load_settings()

# Initialize agent with OpenAI model
agent = Agent(
    get_llm_model(),  # OpenAI GPT-4o-mini
    deps_type=OpenHorizonDependencies,
    system_prompt=SYSTEM_PROMPT,
    retries=settings.max_retries
)

# Convenience function for agent execution
async def run_erasmus_agent(
    prompt: str,
    project_id: Optional[str] = None,
    **overrides
) -> str:
    """Run agent with Supabase database access."""
    deps = OpenHorizonDependencies.from_settings(
        settings,
        project_id=project_id,
        **overrides
    )
    
    try:
        result = await agent.run(prompt, deps=deps)
        return result.data
    finally:
        await deps.cleanup()
```

## FastAPI Integration

### Endpoint Configuration

```python
# Agent endpoints for React frontend
@app.post("/api/brainstorm")
async def brainstorm_project(request: BrainstormRequest):
    """Project brainstorming endpoint."""
    return await run_erasmus_agent(
        f"Help brainstorm: {request.idea}",
        session_id=request.session_id
    )

@app.post("/api/partners/search")  
async def search_partners(request: PartnerSearchRequest):
    """Partner discovery endpoint."""
    return await run_erasmus_agent(
        f"Find partners for: {request.project_details}",
        project_id=request.project_id
    )
```

## Environment File Template

### .env.example

```bash
# LLM Configuration (REQUIRED)
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-openai-api-key-here
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1

# Supabase Configuration (REQUIRED)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key

# External APIs (REQUIRED)
ERASMUS_PARTNER_DB_API_KEY=your-erasmus-partner-db-api-key

# Application Security (REQUIRED)
SECRET_KEY=your-secure-random-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Application Settings
APP_ENV=development
DEBUG=false
LOG_LEVEL=INFO
MAX_RETRIES=3
TIMEOUT_SECONDS=30

# Database Settings
DATABASE_POOL_SIZE=10
DATABASE_MAX_CONNECTIONS=20

# CORS Settings (for React frontend)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
CORS_ALLOW_CREDENTIALS=true
```

## Resource Management

### Cleanup Pattern

```python
async def cleanup(self):
    """Cleanup all external connections."""
    if self._supabase_client:
        # Supabase client cleanup if needed
        pass
    if self._partner_api_client:
        await self._partner_api_client.aclose()
    if self._db_pool:
        await self._db_pool.close()
```

### Connection Pooling

```python
# Database connection pool for heavy workloads
@property
def db_pool(self):
    """Database connection pool for direct SQL if needed."""
    if self._db_pool is None and self.database_url:
        import asyncpg
        # Initialize connection pool
        pass
    return self._db_pool
```

## Quality Checklist

- ✅ OpenAI GPT-4o-mini model configuration
- ✅ Supabase database client setup
- ✅ Essential environment variables defined
- ✅ External API integration (Erasmus+ partner DB)
- ✅ Security validation for API keys and URLs
- ✅ FastAPI integration pattern
- ✅ React frontend compatibility
- ✅ Database schema requirements
- ✅ Resource cleanup handling
- ✅ Development and production configurations

## Integration Notes

This configuration enables:
- **Multi-agent orchestration** for brainstorming, planning, and writing
- **Real-time database** updates through Supabase
- **Partner discovery** via external Erasmus+ API
- **Compliance checking** for application content
- **Session management** for multi-user collaboration
- **Document generation** for submission-ready applications

The dependency structure supports the complete workflow from project brainstorming through partner discovery to final application generation, with proper data persistence and external service integration.