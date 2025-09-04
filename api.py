"""FastAPI application for Open Horizon AI system."""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from typing import Optional

from .models import (
    BrainstormRequest, BrainstormResponse,
    PartnerSearchRequest, PartnerSearchResponse,
    ApplicationContentRequest, ApplicationContentResponse
)
from .agent import (
    run_brainstorming_session,
    run_partner_search, 
    run_application_writing,
    run_open_horizon_agent
)
from .settings import load_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize security
security = HTTPBearer()
settings = load_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting Open Horizon AI API")
    yield
    logger.info("Shutting down Open Horizon AI API")

# Initialize FastAPI app
app = FastAPI(
    title="Open Horizon AI",
    description="Erasmus+ Project Management System with AI Assistance",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from JWT token."""
    # In a real implementation, you'd validate the JWT token here
    # For now, return a mock user ID
    return "user_123"


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Open Horizon AI - Erasmus+ Project Management System",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "agents": "operational",
            "database": "operational"  # Would check Supabase connection
        }
    }


@app.post("/api/brainstorm", response_model=BrainstormResponse)
async def brainstorm_project(
    request: BrainstormRequest,
    current_user: str = Depends(get_current_user)
):
    """Generate Erasmus+ project ideas through AI brainstorming."""
    try:
        logger.info(f"Brainstorming request from user {current_user}: {request.initial_concept}")
        
        response = await run_brainstorming_session(
            request=request,
            user_id=current_user
        )
        
        logger.info(f"Brainstorming completed for user {current_user}")
        return response
        
    except Exception as e:
        logger.error(f"Brainstorming failed for user {current_user}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Brainstorming session failed: {str(e)}"
        )


@app.post("/api/partners/search", response_model=PartnerSearchResponse)
async def search_partners(
    request: PartnerSearchRequest,
    current_user: str = Depends(get_current_user)
):
    """Search for potential Erasmus+ project partners."""
    try:
        logger.info(f"Partner search request from user {current_user}: {request.project_focus}")
        
        response = await run_partner_search(
            request=request,
            user_id=current_user
        )
        
        logger.info(f"Partner search completed for user {current_user}")
        return response
        
    except Exception as e:
        logger.error(f"Partner search failed for user {current_user}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Partner search failed: {str(e)}"
        )


@app.post("/api/application/content", response_model=ApplicationContentResponse)
async def generate_application_content(
    request: ApplicationContentRequest,
    current_user: str = Depends(get_current_user)
):
    """Generate application content for a specific section."""
    try:
        logger.info(f"Content generation request from user {current_user}: {request.section_type}")
        
        response = await run_application_writing(
            request=request,
            user_id=current_user
        )
        
        logger.info(f"Content generation completed for user {current_user}")
        return response
        
    except Exception as e:
        logger.error(f"Content generation failed for user {current_user}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {str(e)}"
        )


@app.post("/api/chat")
async def chat_with_agent(
    message: str,
    agent_type: Optional[str] = "brainstorming",
    project_id: Optional[str] = None,
    session_id: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """General chat interface with the AI agents."""
    try:
        logger.info(f"Chat request from user {current_user} to {agent_type} agent")
        
        response = await run_open_horizon_agent(
            prompt=message,
            agent_type=agent_type,
            user_id=current_user,
            project_id=project_id,
            session_id=session_id
        )
        
        return {
            "success": True,
            "response": response,
            "agent_type": agent_type,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Chat failed for user {current_user}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat session failed: {str(e)}"
        )


# Project management endpoints (would integrate with Supabase)
@app.get("/api/projects")
async def list_projects(current_user: str = Depends(get_current_user)):
    """List user's projects."""
    # Mock response - would query Supabase in real implementation
    return {
        "success": True,
        "projects": [
            {
                "id": "proj_1",
                "title": "Digital Skills for Youth",
                "status": "brainstorming",
                "focus_area": "Digital Transformation",
                "created_at": "2024-01-15T10:00:00Z"
            }
        ]
    }


@app.post("/api/projects")
async def create_project(
    title: str,
    current_user: str = Depends(get_current_user)
):
    """Create a new project."""
    # Mock response - would create in Supabase in real implementation
    project_id = f"proj_{hash(title + current_user) % 10000}"
    
    return {
        "success": True,
        "project": {
            "id": project_id,
            "title": title,
            "status": "brainstorming",
            "created_at": "2024-01-15T10:00:00Z",
            "user_id": current_user
        }
    }


@app.get("/api/projects/{project_id}")
async def get_project(
    project_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get project details."""
    # Mock response - would query Supabase in real implementation
    return {
        "success": True,
        "project": {
            "id": project_id,
            "title": "Sample Project",
            "status": "planning", 
            "focus_area": "Digital Transformation",
            "partners": [],
            "sections": []
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )