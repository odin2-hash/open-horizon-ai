# Tools for Open Horizon AI - Pydantic AI agent tools specification

## Overview

This document specifies 3 essential tools for the Open Horizon AI agent, focusing on the core Erasmus+ project workflow: brainstorming ideas → discovering partners → writing applications.

## Tool 1: Project Brainstorming Tool

### Function: `brainstorm_project_ideas`

**Purpose**: Generate and refine Erasmus+ project ideas with focus areas, target audiences, and innovation angles.

**Parameters**:
- `initial_concept` (str): User's initial project idea or description
- `focus_preference` (str, optional): Preferred Erasmus+ focus area (Digital, Green, Inclusion, etc.)
- `organization_context` (str, default="Swedish NGO"): Organization type for contextual suggestions

**Returns**:
```python
{
    "success": bool,
    "project_concepts": [
        {
            "title": str,
            "focus_area": str,
            "target_audience": str,
            "innovation_angle": str,
            "feasibility_score": int,  # 1-10
            "rationale": str
        }
    ],
    "next_steps": List[str],
    "error": Optional[str]
}
```

**Implementation Strategy**:
- Uses OpenAI to analyze initial concept and generate structured suggestions
- Validates against Erasmus+ program priorities and eligibility criteria
- Provides feasibility scoring based on typical project success factors
- Error handling for API failures returns empty suggestions with error message

## Tool 2: Partner Discovery Tool

### Function: `discover_erasmus_partners`

**Purpose**: Search for and assess potential Erasmus+ project partners based on project requirements and expertise needs.

**Parameters**:
- `project_focus` (str): The project's main focus area or theme
- `required_countries` (List[str], optional): Specific countries needed for partnerships
- `expertise_areas` (List[str]): Required expertise or organizational capabilities

**Returns**:
```python
{
    "success": bool,
    "potential_partners": [
        {
            "name": str,
            "country": str,
            "organization_type": str,
            "expertise_match": List[str],
            "contact_info": {
                "email": str,
                "website": str
            },
            "erasmus_code": str,
            "compatibility_score": int,  # 1-10
            "partnership_rationale": str
        }
    ],
    "search_metadata": {
        "total_found": int,
        "countries_covered": List[str]
    },
    "error": Optional[str]
}
```

**Implementation Strategy**:
- Integrates with Erasmus+ Partner Database API for official partner search
- Falls back to mock data generation if API unavailable (MVP approach)
- Scores partners based on expertise alignment and geographic diversity
- Error handling provides alternative search strategies if primary API fails

## Tool 3: Application Content Generator

### Function: `generate_application_section`

**Purpose**: Generate compliant Erasmus+ application text sections with automatic compliance checking and optimization.

**Parameters**:
- `section_type` (str): Application section name (e.g., "Project Description", "Methodology", "Impact")
- `project_context` (Dict): Project details including title, focus area, partners, timeline
- `word_limit` (int, optional): Maximum word count for the section

**Returns**:
```python
{
    "success": bool,
    "generated_content": {
        "section_name": str,
        "content": str,
        "word_count": int,
        "compliance_status": bool,
        "compliance_details": {
            "missing_elements": List[str],
            "strength_areas": List[str],
            "improvement_suggestions": List[str]
        }
    },
    "alternative_versions": [
        {
            "content": str,
            "focus": str,  # "technical", "impact-focused", "concise"
            "word_count": int
        }
    ],
    "error": Optional[str]
}
```

**Implementation Strategy**:
- Uses structured prompts with Erasmus+ application requirements and best practices
- Validates generated content against official program criteria and common requirements
- Provides multiple content variations for user selection
- Includes automatic compliance checking with specific feedback
- Error handling returns basic template content if generation fails

## Error Handling Approach

**Common Error Patterns**:
- **API Failures**: Return mock/template data with error notification
- **Invalid Parameters**: Validate inputs and provide specific error messages
- **Rate Limiting**: Implement basic retry logic with exponential backoff
- **Network Issues**: Graceful degradation with cached or default responses

**Error Response Format**:
All tools return consistent error structure:
```python
{
    "success": false,
    "error": "Specific error description",
    "error_type": "API_FAILURE|VALIDATION_ERROR|NETWORK_ERROR",
    "fallback_data": Optional[Any],  # Alternative data if available
    "suggested_action": str  # User guidance
}
```

## Integration Notes

**Supabase Integration**:
- All tools should save intermediate results to Supabase for persistence
- Use project_id to maintain data relationships across workflow steps
- Cache partner search results to reduce API calls

**Context Dependencies**:
Tools require access to:
- OpenAI API key for content generation
- Supabase credentials for data persistence
- Erasmus+ Partner Database API key (when available)
- Current project context and user session

**Performance Considerations**:
- Implement async/await patterns for all external API calls
- Use connection pooling for database operations
- Cache frequently accessed partner data
- Limit concurrent API requests to avoid rate limiting

## Testing Strategy

**Mock Data Requirements**:
- Sample Erasmus+ project concepts for brainstorming validation
- Mock partner database with diverse European organizations
- Template application sections for compliance testing

**Validation Tests**:
- Verify tool parameter validation works correctly
- Test error handling for various failure scenarios
- Ensure generated content meets Erasmus+ standards
- Validate partner search results contain required fields

## Tool Dependencies

**Required Python Packages**:
- `httpx` for async HTTP requests
- `supabase-py` for database integration
- `pydantic` for data validation
- `tenacity` for retry logic
- `asyncio` for concurrency management

**External APIs**:
- OpenAI API for content generation
- Erasmus+ Partner Database API (with fallback mock data)
- Supabase API for data persistence

---

**Note**: This specification focuses on MVP functionality. Advanced features like real-time collaboration, multi-language support, and complex partner matching algorithms can be added in future iterations.

**Generated**: 2025-09-04  
**Archon Project ID**: 4613e073-d90a-45ad-9957-b88413c68a04