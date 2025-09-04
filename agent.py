"""Main Open Horizon AI agent implementation."""

import asyncio
from typing import Optional, Dict, Any
from pydantic_ai import Agent
from pydantic_ai.tools import RunContext

from .models import (
    BrainstormRequest, BrainstormResponse,
    PartnerSearchRequest, PartnerSearchResponse, 
    ApplicationContentRequest, ApplicationContentResponse
)
from .dependencies import OpenHorizonDependencies
from .providers import get_llm_model
from .prompts import (
    BRAINSTORMING_PROMPT,
    PLANNING_ORCHESTRATOR_PROMPT, 
    APPLICATION_WRITER_PROMPT,
    get_session_context
)
from .tools import (
    brainstorm_project_ideas,
    discover_erasmus_partners,
    generate_application_section
)


# Initialize the three specialized agents
brainstorming_agent = Agent(
    get_llm_model(),
    deps_type=OpenHorizonDependencies,
    system_prompt=BRAINSTORMING_PROMPT
)

planning_agent = Agent(
    get_llm_model(),
    deps_type=OpenHorizonDependencies,
    system_prompt=PLANNING_ORCHESTRATOR_PROMPT
)

application_agent = Agent(
    get_llm_model(),
    deps_type=OpenHorizonDependencies,
    system_prompt=APPLICATION_WRITER_PROMPT
)


# Register tools with appropriate agents
@brainstorming_agent.tool
async def brainstorm_tool(
    ctx: RunContext[OpenHorizonDependencies],
    initial_concept: str,
    focus_preference: Optional[str] = None,
    organization_context: str = "Swedish NGO"
) -> Dict[str, Any]:
    """Generate Erasmus+ project ideas based on initial concept."""
    return await brainstorm_project_ideas(ctx, initial_concept, focus_preference, organization_context)


@planning_agent.tool
async def partner_discovery_tool(
    ctx: RunContext[OpenHorizonDependencies],
    project_focus: str,
    required_countries: Optional[list[str]] = None,
    expertise_areas: Optional[list[str]] = None
) -> Dict[str, Any]:
    """Discover potential Erasmus+ partners for the project."""
    return await discover_erasmus_partners(ctx, project_focus, required_countries, expertise_areas)


@application_agent.tool
async def content_generation_tool(
    ctx: RunContext[OpenHorizonDependencies],
    section_type: str,
    project_context: Dict[str, Any],
    word_limit: Optional[int] = None
) -> Dict[str, Any]:
    """Generate application section content with compliance checking."""
    return await generate_application_section(ctx, section_type, project_context, word_limit)


# Add session context to all agents
for agent in [brainstorming_agent, planning_agent, application_agent]:
    agent.system_prompt(get_session_context)


# Main orchestrator functions
async def run_brainstorming_session(
    request: BrainstormRequest,
    user_id: Optional[str] = None,
    project_id: Optional[str] = None
) -> BrainstormResponse:
    """Run a brainstorming session for Erasmus+ project ideas."""
    deps = OpenHorizonDependencies.from_settings(
        session_id=request.session_id,
        user_id=user_id,
        project_id=project_id
    )
    
    try:
        prompt = f"""
Help me brainstorm Erasmus+ project ideas based on this initial concept: "{request.initial_concept}"

Organization context: {request.organization_context}
"""
        if request.focus_preference:
            prompt += f"Preferred focus area: {request.focus_preference.value}\n"
        
        prompt += """
Please use the brainstorm_tool to generate structured project concepts with feasibility scores and next steps.
"""
        
        async with brainstorming_agent:
            result = await brainstorming_agent.run(prompt, deps=deps)
            
        # Parse the tool result from the agent's response
        # In a real implementation, you'd extract the tool result from the agent's run
        tool_result = await brainstorm_project_ideas(
            RunContext(deps=deps, retry=0),
            request.initial_concept,
            request.focus_preference.value if request.focus_preference else None,
            request.organization_context
        )
        
        return BrainstormResponse(
            success=tool_result["success"],
            project_concepts=[],  # Would parse from tool_result["project_concepts"]
            next_steps=tool_result.get("next_steps", []),
            error=tool_result.get("error")
        )
        
    except Exception as e:
        return BrainstormResponse(
            success=False,
            error=f"Brainstorming session failed: {str(e)}"
        )
    finally:
        await deps.cleanup()


async def run_partner_search(
    request: PartnerSearchRequest,
    user_id: Optional[str] = None
) -> PartnerSearchResponse:
    """Run a partner search for the project."""
    deps = OpenHorizonDependencies.from_settings(
        user_id=user_id,
        project_id=request.project_id
    )
    
    try:
        prompt = f"""
Help me find Erasmus+ partners for this project:

Project focus: {request.project_focus}
"""
        if request.required_countries:
            prompt += f"Required countries: {', '.join(request.required_countries)}\n"
        if request.expertise_areas:
            prompt += f"Required expertise: {', '.join(request.expertise_areas)}\n"

        prompt += """
Please use the partner_discovery_tool to find suitable partners with compatibility scores and rationale.
"""

        async with planning_agent:
            result = await planning_agent.run(prompt, deps=deps)
        
        # Get tool result
        tool_result = await discover_erasmus_partners(
            RunContext(deps=deps, retry=0),
            request.project_focus,
            request.required_countries,
            request.expertise_areas
        )
        
        return PartnerSearchResponse(
            success=tool_result["success"],
            potential_partners=[],  # Would parse from tool_result
            search_metadata=tool_result.get("search_metadata", {}),
            error=tool_result.get("error")
        )
        
    except Exception as e:
        return PartnerSearchResponse(
            success=False,
            error=f"Partner search failed: {str(e)}"
        )
    finally:
        await deps.cleanup()


async def run_application_writing(
    request: ApplicationContentRequest,
    user_id: Optional[str] = None
) -> ApplicationContentResponse:
    """Generate application content for a specific section."""
    deps = OpenHorizonDependencies.from_settings(
        user_id=user_id,
        project_id=request.project_id
    )
    
    try:
        prompt = f"""
Help me write the "{request.section_type}" section for my Erasmus+ application.

Project context:
"""
        for key, value in request.project_context.items():
            prompt += f"- {key}: {value}\n"
        
        if request.word_limit:
            prompt += f"\nWord limit: {request.word_limit} words"
        
        prompt += """

Please use the content_generation_tool to create compelling, compliant application text with compliance checking.
"""

        async with application_agent:
            result = await application_agent.run(prompt, deps=deps)
        
        # Get tool result
        tool_result = await generate_application_section(
            RunContext(deps=deps, retry=0),
            request.section_type,
            request.project_context,
            request.word_limit
        )
        
        return ApplicationContentResponse(
            success=tool_result["success"],
            generated_content=None,  # Would parse from tool_result
            alternative_versions=tool_result.get("alternative_versions", []),
            error=tool_result.get("error")
        )
        
    except Exception as e:
        return ApplicationContentResponse(
            success=False,
            error=f"Application writing failed: {str(e)}"
        )
    finally:
        await deps.cleanup()


# Convenience function for general queries
async def run_open_horizon_agent(
    prompt: str,
    agent_type: str = "brainstorming",
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> str:
    """
    Run the appropriate Open Horizon AI agent based on the query type.
    
    Args:
        prompt: User's query or request
        agent_type: Type of agent to use ("brainstorming", "planning", "application")
        user_id: Optional user identifier
        project_id: Optional project identifier  
        session_id: Optional session identifier
        
    Returns:
        Agent response as string
    """
    deps = OpenHorizonDependencies.from_settings(
        user_id=user_id,
        project_id=project_id,
        session_id=session_id
    )
    
    # Select appropriate agent
    agent_map = {
        "brainstorming": brainstorming_agent,
        "planning": planning_agent,
        "application": application_agent
    }
    
    selected_agent = agent_map.get(agent_type, brainstorming_agent)
    
    try:
        async with selected_agent:
            result = await selected_agent.run(prompt, deps=deps)
            return result.data
    except Exception as e:
        return f"Agent execution failed: {str(e)}"
    finally:
        await deps.cleanup()


if __name__ == "__main__":
    # Example usage
    async def main():
        response = await run_open_horizon_agent(
            "I want to create a project about digital skills for young people",
            agent_type="brainstorming"
        )
        print(response)
    
    asyncio.run(main())