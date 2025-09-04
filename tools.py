"""Tools for Open Horizon AI agents."""

import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic_ai.tools import RunContext
from .dependencies import OpenHorizonDependencies
from .models import (
    ProjectConcept, Partner, ErasmusFocusArea, OrganizationType,
    ContactInfo, GeneratedContent, ComplianceDetails
)


async def brainstorm_project_ideas(
    ctx: RunContext[OpenHorizonDependencies],
    initial_concept: str,
    focus_preference: Optional[str] = None,
    organization_context: str = "Swedish NGO"
) -> Dict[str, Any]:
    """
    Generate and refine Erasmus+ project ideas with focus areas, target audiences, and innovation angles.
    
    Args:
        initial_concept: User's initial project idea or description
        focus_preference: Preferred Erasmus+ focus area (Digital, Green, Inclusion, etc.)
        organization_context: Organization type for contextual suggestions
        
    Returns:
        Dictionary with project concepts, feasibility scores, and next steps
    """
    try:
        # Mock project concept generation based on input
        concepts = []
        
        # Generate 2-3 project concepts based on initial_concept
        if "digital" in initial_concept.lower() or focus_preference == "Digital Transformation":
            concepts.append({
                "title": f"Digital Skills for {organization_context}: {initial_concept}",
                "focus_area": ErasmusFocusArea.DIGITAL_TRANSFORMATION,
                "target_audience": "Young adults 18-30, unemployed or with low digital skills",
                "innovation_angle": "AI-powered personalized learning paths with peer mentoring",
                "feasibility_score": 8,
                "rationale": "Strong EU priority, clear target group, proven methodologies available"
            })
        
        if "green" in initial_concept.lower() or "environment" in initial_concept.lower():
            concepts.append({
                "title": f"Green Transition Champions: {initial_concept}",
                "focus_area": ErasmusFocusArea.GREEN_TRANSITION,
                "target_audience": "Youth organizations and environmental activists",
                "innovation_angle": "Gamified environmental action with cross-border challenges",
                "feasibility_score": 9,
                "rationale": "High EU priority, engaging methodology, measurable outcomes"
            })
        
        if "inclusion" in initial_concept.lower() or "diversity" in initial_concept.lower():
            concepts.append({
                "title": f"Inclusive Europe: {initial_concept}",
                "focus_area": ErasmusFocusArea.INCLUSION_DIVERSITY,
                "target_audience": "Marginalized youth and support organizations",
                "innovation_angle": "Peer-to-peer support networks with digital storytelling",
                "feasibility_score": 7,
                "rationale": "Critical EU priority, requires sensitive approach, strong impact potential"
            })
        
        # Default concept if no specific focus detected
        if not concepts:
            concepts.append({
                "title": f"European Youth Network: {initial_concept}",
                "focus_area": ErasmusFocusArea.PARTICIPATION,
                "target_audience": "Young people 16-25 interested in civic engagement",
                "innovation_angle": "Cross-border collaboration with local community projects",
                "feasibility_score": 6,
                "rationale": "Broad appeal, established methodologies, moderate complexity"
            })
        
        # Save concepts to Supabase if project_id is available
        if ctx.deps.project_id:
            try:
                # Update project with brainstorming results
                update_data = {
                    "status": "planning",
                    "brainstorm_concepts": json.dumps(concepts),
                    "updated_at": datetime.now().isoformat()
                }
                
                ctx.deps.supabase.table('projects').update(update_data).eq('id', ctx.deps.project_id).execute()
            except Exception as db_error:
                # Continue even if database update fails
                pass
        
        return {
            "success": True,
            "project_concepts": concepts,
            "next_steps": [
                "Select the most promising concept for further development",
                "Identify potential European partner organizations",
                "Define specific learning outcomes and impact metrics",
                "Estimate budget and timeline requirements"
            ],
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "project_concepts": [],
            "next_steps": [],
            "error": f"Brainstorming failed: {str(e)}"
        }


async def discover_erasmus_partners(
    ctx: RunContext[OpenHorizonDependencies],
    project_focus: str,
    required_countries: Optional[List[str]] = None,
    expertise_areas: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Search for and assess potential Erasmus+ project partners based on project requirements.
    
    Args:
        project_focus: The project's main focus area or theme
        required_countries: Specific countries needed for partnerships
        expertise_areas: Required expertise or organizational capabilities
        
    Returns:
        Dictionary with potential partners, compatibility scores, and search metadata
    """
    try:
        # Mock partner data - in production, this would call the Erasmus+ Partner Database API
        mock_partners = [
            {
                "name": "Digital Youth Foundation",
                "country": "Germany",
                "organization_type": OrganizationType.NGO,
                "expertise_areas": ["Digital Skills", "Youth Work", "Innovation"],
                "contact_info": {"email": "contact@digitalyouth.de", "website": "https://digitalyouth.de"},
                "erasmus_code": "DE-YOUTH-001",
                "compatibility_score": 9,
                "partnership_rationale": "Strong digital expertise and proven track record in youth projects"
            },
            {
                "name": "Green Action Network",
                "country": "Netherlands",
                "organization_type": OrganizationType.NGO,
                "expertise_areas": ["Environmental Education", "Sustainability", "Community Engagement"],
                "contact_info": {"email": "info@greenaction.nl", "website": "https://greenaction.nl"},
                "erasmus_code": "NL-GREEN-002",
                "compatibility_score": 8,
                "partnership_rationale": "Excellent environmental focus with European-wide networks"
            },
            {
                "name": "Inclusion Works",
                "country": "Spain",
                "organization_type": OrganizationType.PUBLIC,
                "expertise_areas": ["Social Inclusion", "Diversity Training", "Youth Support"],
                "contact_info": {"email": "hello@inclusionworks.es", "website": "https://inclusionworks.es"},
                "erasmus_code": "ES-INCL-003",
                "compatibility_score": 7,
                "partnership_rationale": "Specialized in inclusion work with vulnerable groups"
            },
            {
                "name": "Innovation Academy",
                "country": "Finland",
                "organization_type": OrganizationType.HEI,
                "expertise_areas": ["Innovation", "Entrepreneurship", "Technology"],
                "contact_info": {"email": "partnerships@innovacademy.fi", "website": "https://innovacademy.fi"},
                "erasmus_code": "FI-INNOV-004",
                "compatibility_score": 8,
                "partnership_rationale": "Academic excellence in innovation and strong research capabilities"
            }
        ]
        
        # Filter partners based on requirements
        filtered_partners = []
        for partner_data in mock_partners:
            partner = Partner(**partner_data)
            
            # Filter by country if specified
            if required_countries and partner.country not in required_countries:
                continue
                
            # Filter by expertise areas if specified
            if expertise_areas:
                expertise_match = any(
                    area.lower() in [exp.lower() for exp in partner.expertise_areas]
                    for area in expertise_areas
                )
                if not expertise_match:
                    continue
            
            # Adjust compatibility score based on project focus
            if project_focus.lower() in [area.lower() for area in partner.expertise_areas]:
                partner.compatibility_score = min(10, partner.compatibility_score + 1)
            
            filtered_partners.append(partner.model_dump())
        
        # Save partner search results if project_id is available
        if ctx.deps.project_id:
            try:
                search_data = {
                    "project_id": ctx.deps.project_id,
                    "search_query": project_focus,
                    "partners_found": json.dumps(filtered_partners),
                    "searched_at": datetime.now().isoformat()
                }
                
                ctx.deps.supabase.table('partner_searches').insert(search_data).execute()
            except Exception as db_error:
                # Continue even if database save fails
                pass
        
        countries_covered = list(set(partner["country"] for partner in filtered_partners))
        
        return {
            "success": True,
            "potential_partners": filtered_partners,
            "search_metadata": {
                "total_found": len(filtered_partners),
                "countries_covered": countries_covered,
                "search_focus": project_focus
            },
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "potential_partners": [],
            "search_metadata": {"total_found": 0, "countries_covered": []},
            "error": f"Partner search failed: {str(e)}"
        }


async def generate_application_section(
    ctx: RunContext[OpenHorizonDependencies],
    section_type: str,
    project_context: Dict[str, Any],
    word_limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate compliant Erasmus+ application text sections with automatic compliance checking.
    
    Args:
        section_type: Application section name (e.g., "Project Description", "Methodology", "Impact")
        project_context: Project details including title, focus area, partners, timeline
        word_limit: Maximum word count for the section
        
    Returns:
        Dictionary with generated content, compliance status, and alternative versions
    """
    try:
        project_title = project_context.get("title", "Unnamed Project")
        focus_area = project_context.get("focus_area", "General")
        target_audience = project_context.get("target_audience", "Young people")
        
        # Generate section content based on type
        content_templates = {
            "Project Description": f"""
{project_title} addresses the critical need for {focus_area.lower()} development among {target_audience.lower()} across Europe. 

Our project recognizes that traditional approaches to youth engagement often fail to capture the diverse needs and learning styles of today's generation. Through innovative methodologies and cross-border collaboration, we will create sustainable pathways for personal and professional development.

The project brings together partners from multiple European countries to share best practices, develop new approaches, and create lasting networks that extend beyond the project timeline. Our consortium combines grassroots experience with academic rigor, ensuring both practical relevance and evidence-based outcomes.

Key innovation elements include digital tools integration, peer-to-peer learning methodologies, and community-based action projects that create real-world impact while developing participants' competencies.
""".strip(),
            
            "Methodology": f"""
Our methodology is built on three pillars: participatory learning, digital innovation, and cross-cultural exchange.

**Participatory Learning**: We employ non-formal education techniques that place participants at the center of their learning journey. Through workshops, peer mentoring, and collaborative projects, participants develop both hard and soft skills while building confidence and intercultural competence.

**Digital Innovation**: Leveraging technology to enhance accessibility and engagement, we integrate digital tools that support personalized learning paths and enable virtual collaboration between participants from different countries.

**Cross-Cultural Exchange**: Physical and virtual mobility opportunities allow participants to experience different cultural approaches to {focus_area.lower()}, fostering European identity and global citizenship.

Quality assurance is ensured through regular evaluation cycles, participant feedback integration, and external expert review at key project milestones.
""".strip(),
            
            "Impact": f"""
{project_title} will create multi-level impact across individual, organizational, and systemic dimensions.

**Individual Impact**: Participants will develop enhanced competencies in {focus_area.lower()}, increased cultural awareness, and stronger European identity. We anticipate that 85% of participants will report increased confidence and 70% will pursue further education or employment opportunities directly related to project themes.

**Organizational Impact**: Partner organizations will benefit from strengthened capacity, new methodologies, and expanded European networks. The project will result in updated training curricula and sustainable partnership agreements for future collaboration.

**Systemic Impact**: Project outcomes will contribute to European policy discussions around {focus_area.lower()} and youth development. Dissemination activities will reach an estimated 10,000 stakeholders across partner countries, with toolkit resources made available to organizations throughout Europe.

Long-term sustainability is ensured through follow-up activities, alumni networks, and integration of project outcomes into partners' regular programming.
""".strip()
        }
        
        # Get appropriate content template
        content = content_templates.get(section_type, f"""
This section focuses on {section_type.lower()} aspects of {project_title}. The project addresses {focus_area.lower()} priorities through innovative approaches that engage {target_audience.lower()} in meaningful learning experiences.

Our approach combines proven methodologies with innovative elements, ensuring both effectiveness and European added value. Through collaboration with partners across multiple countries, we will create sustainable impact that extends beyond the project timeline.

Key elements include participant-centered design, quality assurance mechanisms, and comprehensive evaluation to ensure project objectives are met and lessons learned are shared with the broader European community.
""".strip())
        
        # Apply word limit if specified
        if word_limit:
            words = content.split()
            if len(words) > word_limit:
                content = " ".join(words[:word_limit]) + "..."
        
        # Calculate word count
        word_count = len(content.split())
        
        # Simple compliance checking
        compliance_issues = []
        strengths = []
        
        # Check for European dimension
        if "european" in content.lower() or "europe" in content.lower():
            strengths.append("Strong European dimension clearly articulated")
        else:
            compliance_issues.append("European dimension needs stronger emphasis")
        
        # Check for target group clarity
        if any(word in content.lower() for word in ["participants", "youth", "young people"]):
            strengths.append("Target group clearly defined")
        else:
            compliance_issues.append("Target group definition could be clearer")
        
        # Check for innovation elements
        if any(word in content.lower() for word in ["innovative", "innovation", "new approach"]):
            strengths.append("Innovation elements present")
        else:
            compliance_issues.append("Consider adding more innovation elements")
        
        compliance_status = len(compliance_issues) == 0
        
        generated_content = {
            "section_name": section_type,
            "content": content,
            "word_count": word_count,
            "compliance_status": compliance_status,
            "compliance_details": {
                "missing_elements": compliance_issues,
                "strength_areas": strengths,
                "improvement_suggestions": [
                    "Consider adding specific quantifiable outcomes",
                    "Include references to relevant EU policies or priorities",
                    "Ensure clear link between activities and expected results"
                ]
            }
        }
        
        # Create alternative versions
        alternative_versions = [
            {
                "content": content.replace("innovative", "cutting-edge").replace("traditional", "conventional"),
                "focus": "technical",
                "word_count": len(content.replace("innovative", "cutting-edge").split())
            },
            {
                "content": content + "\n\nThis project directly contributes to European social cohesion and democratic values.",
                "focus": "impact-focused", 
                "word_count": len((content + "\n\nThis project directly contributes to European social cohesion and democratic values.").split())
            }
        ]
        
        # Save to database if project_id is available
        if ctx.deps.project_id:
            try:
                section_data = {
                    "id": str(uuid.uuid4()),
                    "project_id": ctx.deps.project_id,
                    "section_name": section_type,
                    "content": content,
                    "word_count": word_count,
                    "compliance_status": compliance_status,
                    "suggestions": json.dumps(compliance_issues + generated_content["compliance_details"]["improvement_suggestions"]),
                    "created_at": datetime.now().isoformat()
                }
                
                ctx.deps.supabase.table('application_sections').insert(section_data).execute()
            except Exception as db_error:
                # Continue even if database save fails
                pass
        
        return {
            "success": True,
            "generated_content": generated_content,
            "alternative_versions": alternative_versions,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "generated_content": None,
            "alternative_versions": [],
            "error": f"Content generation failed: {str(e)}"
        }