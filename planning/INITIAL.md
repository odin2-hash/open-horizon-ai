# Open Horizon AI - Simple Requirements

## What This Agent Does
A Pydantic AI system for Swedish NGO "Open Horizon" that streamlines Erasmus+ project management through an intelligent web interface, focusing on brainstorming ideas, planning project structure with partners, and writing compelling applications.

## Core Features (MVP)
1. **Project Brainstorming Assistant**: Interactive brainstorming for Erasmus+ project ideas with focus area suggestions, target audience identification, and innovation angle development
2. **Partner & Planning Orchestrator**: Intelligent partner discovery and project structure planning with timeline generation and role assignments
3. **Application Writer**: Automated generation of Erasmus+ application text sections with compliance checking and narrative optimization

## Technical Setup

### Architecture
- **Frontend**: React/TypeScript web interface (forked from Archon architecture)
- **Backend**: FastAPI orchestrator with Pydantic AI agents
- **Database**: Supabase for project data, partners, and application drafts
- **AI Integration**: Multi-agent system with specialized sub-agents

### Model
- **Provider**: openai
- **Model**: gpt-4o-mini
- **Why**: Cost-effective for complex document generation with sufficient context window for Erasmus+ applications

### Required Tools
1. **erasmus_partner_search**: Search and validate potential project partners from EU database
2. **project_structure_generator**: Generate project timelines, work packages, and deliverables
3. **compliance_checker**: Validate application content against Erasmus+ requirements
4. **application_composer**: Compose and optimize application text sections

### External Services
- **Supabase**: Database for projects, partners, applications, and user management
- **Erasmus+ Partner Database API**: For partner discovery and validation
- **OpenAI API**: For AI agent functionality

## Core Pydantic Models

### Project Models
```python
class Project(BaseModel):
    id: str
    title: str
    focus_area: str  # Digital transformation, Green transition, Inclusion, etc.
    target_audience: str
    innovation_angle: str
    status: ProjectStatus
    created_at: datetime
    partners: List[Partner] = []

class Partner(BaseModel):
    id: str
    name: str
    country: str
    organization_type: str
    expertise_areas: List[str]
    contact_info: ContactInfo
    erasmus_code: str

class ApplicationSection(BaseModel):
    section_name: str
    content: str
    word_count: int
    compliance_status: bool
    suggestions: List[str] = []
```

### Interface Architecture
Following Archon fork approach:
- React frontend with project dashboard, brainstorming interface, partner search, and application editor
- FastAPI backend with specialized agent endpoints for each workflow step
- Real-time collaboration features for multi-user project development

## Environment Variables
```bash
OPENAI_API_KEY=your-openai-api-key
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-anon-key
ERASMUS_PARTNER_DB_API_KEY=your-erasmus-api-key
SECRET_KEY=your-jwt-secret-key
```

## Success Criteria
- [ ] Users can brainstorm Erasmus+ project ideas with AI guidance
- [ ] System discovers and suggests relevant project partners
- [ ] Generates structured project plans with timelines and work packages
- [ ] Produces compliant Erasmus+ application text sections
- [ ] Web interface provides seamless workflow from idea to submission-ready application

## Assumptions Made
- Using OpenAI for cost-effective document generation over other providers
- Supabase provides sufficient real-time features for collaboration
- Erasmus+ partner database API is accessible (will mock if needed for MVP)
- React frontend similar to Archon interface for familiar UX
- Single organization focus (Open Horizon) for initial deployment
- English-first interface with Swedish localization capability later

## MVP Workflow
1. **Brainstorming Phase**: User describes project idea → AI suggests focus areas, target audiences, innovation angles
2. **Planning Phase**: AI discovers potential partners → generates project structure with timelines and deliverables
3. **Writing Phase**: AI composes application sections → validates compliance → provides optimization suggestions

---
Generated: 2025-09-04
Note: This is an MVP focusing on the core workflow. Multi-agent orchestration, advanced collaboration features, and multi-language support can be added after the basic system works.