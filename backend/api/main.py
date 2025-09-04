"""
Open Horizon AI - FastAPI Backend

This backend integrates Archon's crawling and knowledge management capabilities
with Open Horizon AI's specialized Erasmus+ project management agents.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uvicorn
import asyncio
from contextlib import asynccontextmanager

# Import Open Horizon AI agents
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from agent import BrainstormingAgent, PlanningAgent, ApplicationAgent
from models import ProjectConcept, ProjectPlan, ApplicationSection
from services.crawling.erasmus_knowledge_service import ErasmusKnowledgeService


# Pydantic models for API
class BrainstormRequest(BaseModel):
    focus_area: str
    target_audience: str
    innovation_keywords: List[str] = []
    existing_concepts: List[Dict[str, Any]] = []


class BrainstormResponse(BaseModel):
    concepts: List[Dict[str, Any]]
    inspiration_sources: List[str]
    next_steps: List[str]


class PlanningRequest(BaseModel):
    concept_id: str
    duration_months: int
    budget_range_eur: tuple
    partner_requirements: List[str] = []


class PlanningResponse(BaseModel):
    project_plan: Dict[str, Any]
    timeline: List[Dict[str, Any]]
    budget_breakdown: Dict[str, float]
    partner_suggestions: List[Dict[str, Any]]


class ApplicationRequest(BaseModel):
    project_id: str
    section_name: str
    requirements: Dict[str, Any]
    existing_content: str = ""


class ApplicationResponse(BaseModel):
    content: str
    word_count: int
    compliance_check: Dict[str, Any]
    suggestions: List[str]


class KnowledgeSearchRequest(BaseModel):
    query: str
    source_types: List[str] = []
    max_results: int = 10


class KnowledgeSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_found: int
    search_time_ms: float


# Global agent instances
brainstorming_agent = None
planning_agent = None
application_agent = None
knowledge_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources."""
    global brainstorming_agent, planning_agent, application_agent, knowledge_service
    
    print("🚀 Starting Open Horizon AI Backend...")
    
    try:
        # Initialize agents
        brainstorming_agent = BrainstormingAgent()
        planning_agent = PlanningAgent()
        application_agent = ApplicationAgent()
        
        # Initialize knowledge service
        knowledge_service = ErasmusKnowledgeService()
        
        print("✅ All agents initialized successfully")
        
        # Initial knowledge base update in background
        asyncio.create_task(knowledge_service.update_knowledge_base())
        
        yield
        
    except Exception as e:
        print(f"❌ Failed to initialize agents: {e}")
        raise
    finally:
        print("🔄 Shutting down Open Horizon AI Backend...")


# Create FastAPI app
app = FastAPI(
    title="Open Horizon AI API",
    description="Erasmus+ Project Management with AI Agents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3030", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    agent_status = {
        "brainstorming_agent": brainstorming_agent is not None,
        "planning_agent": planning_agent is not None,
        "application_agent": application_agent is not None,
        "knowledge_service": knowledge_service is not None
    }
    
    all_ready = all(agent_status.values())
    
    return {
        "status": "healthy" if all_ready else "starting",
        "ready": all_ready,
        "agents": agent_status,
        "version": "1.0.0"
    }


# Brainstorming endpoints
@app.post("/api/brainstorm", response_model=BrainstormResponse)
async def brainstorm_ideas(request: BrainstormRequest):
    """Generate project concepts using the brainstorming agent."""
    if not brainstorming_agent:
        raise HTTPException(status_code=503, detail="Brainstorming agent not available")
    
    try:
        # Convert request to agent format
        context = {
            "focus_area": request.focus_area,
            "target_audience": request.target_audience,
            "innovation_keywords": request.innovation_keywords,
            "existing_concepts": request.existing_concepts
        }
        
        # Run brainstorming agent
        result = await brainstorming_agent.arun_agent(
            f"Generate innovative Erasmus+ project concepts for {request.focus_area} "
            f"targeting {request.target_audience}. "
            f"Innovation focus: {', '.join(request.innovation_keywords)}",
            context
        )
        
        return BrainstormResponse(
            concepts=result.get("concepts", []),
            inspiration_sources=result.get("inspiration_sources", []),
            next_steps=result.get("next_steps", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brainstorming failed: {str(e)}")


@app.get("/api/brainstorm/inspiration")
async def get_inspiration():
    """Get inspiration from successful Erasmus+ projects."""
    if not knowledge_service:
        raise HTTPException(status_code=503, detail="Knowledge service not available")
    
    try:
        # Search for best practices and successful projects
        inspiration = await knowledge_service.search_erasmus_knowledge(
            "successful projects best practices innovation",
            source_types=["best_practices", "project_database"]
        )
        
        return {
            "inspiration": inspiration.get("results", []),
            "total_found": inspiration.get("total_results", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get inspiration: {str(e)}")


# Planning endpoints
@app.post("/api/plan", response_model=PlanningResponse)
async def create_project_plan(request: PlanningRequest):
    """Create a detailed project plan using the planning agent."""
    if not planning_agent:
        raise HTTPException(status_code=503, detail="Planning agent not available")
    
    try:
        # Convert request to agent format
        context = {
            "concept_id": request.concept_id,
            "duration_months": request.duration_months,
            "budget_range": request.budget_range_eur,
            "partner_requirements": request.partner_requirements
        }
        
        # Run planning agent
        result = await planning_agent.arun_agent(
            f"Create a comprehensive {request.duration_months}-month Erasmus+ project plan "
            f"with budget range €{request.budget_range_eur[0]}-€{request.budget_range_eur[1]}",
            context
        )
        
        return PlanningResponse(
            project_plan=result.get("project_plan", {}),
            timeline=result.get("timeline", []),
            budget_breakdown=result.get("budget_breakdown", {}),
            partner_suggestions=result.get("partner_suggestions", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")


@app.get("/api/partners/search")
async def search_partners(
    expertise: str = "",
    countries: str = "",
    organization_type: str = ""
):
    """Search for potential project partners."""
    try:
        # This would integrate with the partner search functionality
        # For now, return sample data structure
        return {
            "partners": [
                {
                    "id": "1",
                    "name": "Sample Partner Organization",
                    "country": "Germany",
                    "expertise_areas": ["Digital Skills", "Youth Work"],
                    "organization_type": "NGO",
                    "compatibility_score": 8
                }
            ],
            "total_found": 1,
            "search_criteria": {
                "expertise": expertise,
                "countries": countries.split(",") if countries else [],
                "organization_type": organization_type
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Partner search failed: {str(e)}")


# Application writing endpoints
@app.post("/api/application/write", response_model=ApplicationResponse)
async def write_application_section(request: ApplicationRequest):
    """Write or improve an application section using the application agent."""
    if not application_agent:
        raise HTTPException(status_code=503, detail="Application agent not available")
    
    try:
        # Convert request to agent format
        context = {
            "project_id": request.project_id,
            "section_name": request.section_name,
            "requirements": request.requirements,
            "existing_content": request.existing_content
        }
        
        # Run application agent
        result = await application_agent.arun_agent(
            f"Write the '{request.section_name}' section for Erasmus+ project application",
            context
        )
        
        return ApplicationResponse(
            content=result.get("content", ""),
            word_count=result.get("word_count", 0),
            compliance_check=result.get("compliance_check", {}),
            suggestions=result.get("suggestions", [])
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Application writing failed: {str(e)}")


@app.get("/api/application/requirements/{section_name}")
async def get_section_requirements(section_name: str):
    """Get requirements and guidelines for a specific application section."""
    try:
        # Search knowledge base for section-specific requirements
        if knowledge_service:
            requirements = await knowledge_service.search_erasmus_knowledge(
                f"application {section_name} requirements guidelines",
                source_types=["programme_guide"]
            )
            
            return {
                "section": section_name,
                "requirements": requirements.get("results", []),
                "guidelines": f"Guidelines for {section_name} section"
            }
        else:
            # Fallback requirements
            return {
                "section": section_name,
                "requirements": [],
                "guidelines": f"Guidelines for {section_name} section (knowledge service unavailable)"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get requirements: {str(e)}")


# Knowledge base endpoints
@app.post("/api/knowledge/search", response_model=KnowledgeSearchResponse)
async def search_knowledge_base(request: KnowledgeSearchRequest):
    """Search the Erasmus+ knowledge base."""
    if not knowledge_service:
        raise HTTPException(status_code=503, detail="Knowledge service not available")
    
    try:
        import time
        start_time = time.time()
        
        # Search knowledge base
        results = await knowledge_service.search_erasmus_knowledge(
            request.query,
            request.source_types
        )
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return KnowledgeSearchResponse(
            results=results.get("results", [])[:request.max_results],
            total_found=results.get("total_results", 0),
            search_time_ms=search_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge search failed: {str(e)}")


@app.post("/api/knowledge/update")
async def update_knowledge_base(background_tasks: BackgroundTasks):
    """Trigger knowledge base update."""
    if not knowledge_service:
        raise HTTPException(status_code=503, detail="Knowledge service not available")
    
    # Run update in background
    background_tasks.add_task(knowledge_service.update_knowledge_base)
    
    return {
        "message": "Knowledge base update started",
        "status": "running"
    }


@app.get("/api/knowledge/sources")
async def get_knowledge_sources():
    """Get information about available knowledge sources."""
    if not knowledge_service:
        raise HTTPException(status_code=503, detail="Knowledge service not available")
    
    return {
        "sources": [
            {
                "name": source.description,
                "url": source.url,
                "type": source.source_type,
                "priority": source.priority,
                "tags": source.tags
            }
            for source in knowledge_service.erasmus_sources
        ]
    }


# Project management endpoints (integration with existing project system)
@app.get("/api/projects")
async def get_projects():
    """Get all projects."""
    # This would integrate with the existing project database
    return {"projects": [], "total": 0}


@app.post("/api/projects")
async def create_project(project_data: Dict[str, Any]):
    """Create a new project."""
    # This would integrate with the existing project creation logic
    return {"id": "new-project-id", "status": "created"}


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get specific project details."""
    # This would integrate with the existing project retrieval logic
    return {"id": project_id, "status": "found"}


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )