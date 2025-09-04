"""Pydantic models for Open Horizon AI system."""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from enum import Enum


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    BRAINSTORMING = "brainstorming"
    PLANNING = "planning"
    PARTNERING = "partnering"
    WRITING = "writing"
    REVIEW = "review"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    ACTIVE = "active"


class ErasmusFocusArea(str, Enum):
    """Erasmus+ focus areas."""
    DIGITAL_TRANSFORMATION = "Digital Transformation"
    GREEN_TRANSITION = "Green Transition"
    INCLUSION_DIVERSITY = "Inclusion and Diversity"
    PARTICIPATION = "Participation"
    EUROPEAN_VALUES = "European Values"
    INNOVATION = "Innovation"


class OrganizationType(str, Enum):
    """Organization type enumeration."""
    NGO = "NGO"
    PUBLIC = "Public Body"
    SCHOOL = "School"
    HEI = "Higher Education Institution"
    COMPANY = "Company"
    OTHER = "Other"


class ContactInfo(BaseModel):
    """Contact information model."""
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    phone: Optional[str] = None


class Partner(BaseModel):
    """Partner organization model."""
    id: str
    name: str
    country: str
    organization_type: OrganizationType
    expertise_areas: List[str] = []
    contact_info: ContactInfo = ContactInfo()
    erasmus_code: Optional[str] = None
    compatibility_score: Optional[int] = Field(None, ge=1, le=10)
    partnership_rationale: Optional[str] = None


class Project(BaseModel):
    """Project model for Erasmus+ applications."""
    id: str
    title: str
    focus_area: ErasmusFocusArea
    target_audience: str
    innovation_angle: str
    status: ProjectStatus = ProjectStatus.BRAINSTORMING
    created_at: datetime = Field(default_factory=datetime.now)
    partners: List[Partner] = []
    user_id: Optional[str] = None
    
    # Erasmus+ specific fields
    duration_months: Optional[int] = Field(None, ge=3, le=36)
    budget_estimate_eur: Optional[float] = Field(None, ge=0)
    countries_involved: List[str] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ApplicationSection(BaseModel):
    """Application section model."""
    id: Optional[str] = None
    project_id: str
    section_name: str
    content: str
    word_count: int = 0
    compliance_status: bool = False
    suggestions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate word count after initialization."""
        if self.content:
            self.word_count = len(self.content.split())


class ProjectConcept(BaseModel):
    """Project concept from brainstorming."""
    title: str
    focus_area: ErasmusFocusArea
    target_audience: str
    innovation_angle: str
    feasibility_score: int = Field(..., ge=1, le=10)
    rationale: str


class BrainstormRequest(BaseModel):
    """Request model for brainstorming endpoint."""
    initial_concept: str
    focus_preference: Optional[ErasmusFocusArea] = None
    organization_context: str = "Swedish NGO"
    session_id: Optional[str] = None


class BrainstormResponse(BaseModel):
    """Response model for brainstorming endpoint."""
    success: bool
    project_concepts: List[ProjectConcept] = []
    next_steps: List[str] = []
    error: Optional[str] = None


class PartnerSearchRequest(BaseModel):
    """Request model for partner search endpoint."""
    project_focus: str
    required_countries: Optional[List[str]] = None
    expertise_areas: List[str] = []
    project_id: Optional[str] = None


class PartnerSearchResponse(BaseModel):
    """Response model for partner search endpoint."""
    success: bool
    potential_partners: List[Partner] = []
    search_metadata: Dict[str, Any] = {}
    error: Optional[str] = None


class ApplicationContentRequest(BaseModel):
    """Request model for application content generation."""
    section_type: str
    project_context: Dict[str, Any]
    word_limit: Optional[int] = None
    project_id: Optional[str] = None


class ApplicationContentResponse(BaseModel):
    """Response model for application content generation."""
    success: bool
    generated_content: Optional[ApplicationSection] = None
    alternative_versions: List[Dict[str, Any]] = []
    error: Optional[str] = None


class ComplianceDetails(BaseModel):
    """Compliance check details."""
    missing_elements: List[str] = []
    strength_areas: List[str] = []
    improvement_suggestions: List[str] = []


class GeneratedContent(BaseModel):
    """Generated application content with compliance."""
    section_name: str
    content: str
    word_count: int
    compliance_status: bool
    compliance_details: ComplianceDetails = ComplianceDetails()