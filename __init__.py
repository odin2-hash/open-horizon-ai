"""Open Horizon AI - Erasmus+ Project Management System with AI Assistance."""

from .agent import (
    run_open_horizon_agent,
    run_brainstorming_session,
    run_partner_search,
    run_application_writing,
    brainstorming_agent,
    planning_agent,
    application_agent
)
from .models import (
    Project, Partner, ApplicationSection,
    BrainstormRequest, BrainstormResponse,
    PartnerSearchRequest, PartnerSearchResponse,
    ApplicationContentRequest, ApplicationContentResponse,
    ErasmusFocusArea, ProjectStatus, OrganizationType
)
from .dependencies import OpenHorizonDependencies
from .settings import load_settings
from .providers import get_llm_model

__version__ = "1.0.0"
__author__ = "Open Horizon AI Team"
__description__ = "Intelligent Erasmus+ project management system for Swedish NGO 'Open Horizon'"

__all__ = [
    # Main functions
    "run_open_horizon_agent",
    "run_brainstorming_session", 
    "run_partner_search",
    "run_application_writing",
    
    # Agents
    "brainstorming_agent",
    "planning_agent", 
    "application_agent",
    
    # Models
    "Project",
    "Partner", 
    "ApplicationSection",
    "BrainstormRequest",
    "BrainstormResponse",
    "PartnerSearchRequest",
    "PartnerSearchResponse", 
    "ApplicationContentRequest",
    "ApplicationContentResponse",
    "ErasmusFocusArea",
    "ProjectStatus",
    "OrganizationType",
    
    # Core components
    "OpenHorizonDependencies",
    "load_settings",
    "get_llm_model",
]