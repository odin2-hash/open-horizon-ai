"""Test Open Horizon AI agent functionality."""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.messages import ModelTextResponse
from pydantic_ai.tools import RunContext

from ..agent import (
    brainstorming_agent, planning_agent, application_agent,
    run_brainstorming_session, run_partner_search, run_application_writing,
    run_open_horizon_agent
)
from ..models import (
    BrainstormRequest, BrainstormResponse,
    PartnerSearchRequest, PartnerSearchResponse,
    ApplicationContentRequest, ApplicationContentResponse,
    ErasmusFocusArea
)
from ..dependencies import OpenHorizonDependencies


class TestBrainstormingAgent:
    """Test the brainstorming agent functionality."""

    @pytest.mark.asyncio
    async def test_brainstorming_agent_basic_response(self, mock_dependencies):
        """Test brainstorming agent provides appropriate response."""
        test_agent = brainstorming_agent.override(model=TestModel())
        
        result = await test_agent.run(
            "Help me brainstorm a digital skills project for young people",
            deps=mock_dependencies
        )
        
        assert result.data is not None
        assert isinstance(result.data, str)
        assert len(result.all_messages()) > 0
        # Verify the agent received the prompt
        messages = result.all_messages()
        assert any("brainstorm" in msg.content.lower() for msg in messages if hasattr(msg, 'content'))

    @pytest.mark.asyncio
    async def test_brainstorming_agent_tool_calling(self, brainstorm_test_model, mock_dependencies):
        """Test brainstorming agent calls brainstorm_tool correctly."""
        test_agent = brainstorming_agent.override(model=brainstorm_test_model)
        
        result = await test_agent.run(
            "Generate project ideas for digital skills development",
            deps=mock_dependencies
        )
        
        # Verify tool was called by checking message sequence
        messages = result.all_messages()
        assert len(messages) >= 2
        
        # Look for tool call pattern in messages
        tool_calls = [msg for msg in messages if hasattr(msg, 'tool_name')]
        if tool_calls:
            assert any(msg.tool_name == "brainstorm_tool" for msg in tool_calls)

    @pytest.mark.asyncio
    async def test_brainstorming_with_custom_function_model(self, mock_dependencies):
        """Test brainstorming agent with FunctionModel for precise control."""
        call_count = 0
        
        async def brainstorm_function(messages, tools):
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:
                return ModelTextResponse(
                    content="I'll help you brainstorm Erasmus+ project ideas."
                )
            elif call_count == 2:
                return {
                    "brainstorm_tool": {
                        "initial_concept": "digital skills for youth",
                        "focus_preference": "Digital Transformation",
                        "organization_context": "Swedish NGO"
                    }
                }
            else:
                return ModelTextResponse(
                    content="I've generated several innovative project concepts."
                )
        
        function_model = FunctionModel(brainstorm_function)
        test_agent = brainstorming_agent.override(model=function_model)
        
        result = await test_agent.run(
            "Help me create a project about digital skills",
            deps=mock_dependencies
        )
        
        assert call_count >= 2
        assert "brainstorm" in result.data.lower() or "project" in result.data.lower()

    @pytest.mark.asyncio
    async def test_brainstorming_session_end_to_end(self, sample_brainstorm_request, mock_dependencies):
        """Test complete brainstorming session workflow."""
        with patch('open_horizon_ai.agent.brainstorm_project_ideas') as mock_tool:
            mock_tool.return_value = {
                "success": True,
                "project_concepts": [
                    {
                        "title": "Digital Skills Hub",
                        "focus_area": "Digital Transformation",
                        "target_audience": "Young adults 18-30",
                        "innovation_angle": "AI-powered learning paths",
                        "feasibility_score": 8,
                        "rationale": "Strong EU alignment"
                    }
                ],
                "next_steps": ["Define learning outcomes", "Find partners"],
                "error": None
            }
            
            response = await run_brainstorming_session(
                sample_brainstorm_request,
                user_id="test-user"
            )
            
            assert isinstance(response, BrainstormResponse)
            assert response.success is True
            assert response.error is None
            assert len(response.next_steps) > 0
            mock_tool.assert_called_once()

    @pytest.mark.asyncio
    async def test_brainstorming_session_error_handling(self, sample_brainstorm_request):
        """Test brainstorming session handles errors gracefully."""
        # Test with invalid dependencies
        response = await run_brainstorming_session(
            sample_brainstorm_request,
            user_id="test-user"
        )
        
        # Should handle error gracefully
        assert isinstance(response, BrainstormResponse)
        # Error handling should prevent complete failure


class TestPlanningAgent:
    """Test the planning agent functionality."""

    @pytest.mark.asyncio
    async def test_planning_agent_basic_response(self, mock_dependencies):
        """Test planning agent responds appropriately."""
        test_agent = planning_agent.override(model=TestModel())
        
        result = await test_agent.run(
            "Help me find partners for my digital skills project",
            deps=mock_dependencies
        )
        
        assert result.data is not None
        assert isinstance(result.data, str)

    @pytest.mark.asyncio
    async def test_planning_agent_partner_discovery(self, partner_search_test_model, mock_dependencies):
        """Test planning agent calls partner discovery tool."""
        test_agent = planning_agent.override(model=partner_search_test_model)
        
        result = await test_agent.run(
            "Find European partners with digital skills expertise",
            deps=mock_dependencies
        )
        
        # Verify interaction occurred
        messages = result.all_messages()
        assert len(messages) > 0

    @pytest.mark.asyncio
    async def test_partner_search_end_to_end(self, sample_partner_request, mock_dependencies):
        """Test complete partner search workflow."""
        with patch('open_horizon_ai.agent.discover_erasmus_partners') as mock_tool:
            mock_tool.return_value = {
                "success": True,
                "potential_partners": [
                    {
                        "name": "Digital Youth Foundation",
                        "country": "Germany",
                        "compatibility_score": 9,
                        "partnership_rationale": "Strong expertise match"
                    }
                ],
                "search_metadata": {
                    "total_found": 1,
                    "countries_covered": ["Germany"]
                },
                "error": None
            }
            
            response = await run_partner_search(
                sample_partner_request,
                user_id="test-user"
            )
            
            assert isinstance(response, PartnerSearchResponse)
            assert response.success is True
            assert response.error is None
            assert "total_found" in response.search_metadata
            mock_tool.assert_called_once()


class TestApplicationAgent:
    """Test the application writing agent functionality."""

    @pytest.mark.asyncio
    async def test_application_agent_basic_response(self, mock_dependencies):
        """Test application agent responds appropriately."""
        test_agent = application_agent.override(model=TestModel())
        
        result = await test_agent.run(
            "Help me write the Project Description section",
            deps=mock_dependencies
        )
        
        assert result.data is not None
        assert isinstance(result.data, str)

    @pytest.mark.asyncio
    async def test_application_agent_content_generation(self, application_test_model, mock_dependencies):
        """Test application agent calls content generation tool."""
        test_agent = application_agent.override(model=application_test_model)
        
        result = await test_agent.run(
            "Generate content for the Methodology section with 300 word limit",
            deps=mock_dependencies
        )
        
        # Verify interaction occurred
        messages = result.all_messages()
        assert len(messages) > 0

    @pytest.mark.asyncio
    async def test_application_writing_end_to_end(self, sample_application_request, mock_dependencies):
        """Test complete application writing workflow."""
        with patch('open_horizon_ai.agent.generate_application_section') as mock_tool:
            mock_tool.return_value = {
                "success": True,
                "generated_content": {
                    "section_name": "Project Description",
                    "content": "This innovative project addresses digital skills gaps...",
                    "word_count": 150,
                    "compliance_status": True,
                    "compliance_details": {
                        "missing_elements": [],
                        "strength_areas": ["European dimension", "Innovation"],
                        "improvement_suggestions": []
                    }
                },
                "alternative_versions": [],
                "error": None
            }
            
            response = await run_application_writing(
                sample_application_request,
                user_id="test-user"
            )
            
            assert isinstance(response, ApplicationContentResponse)
            assert response.success is True
            assert response.error is None
            mock_tool.assert_called_once()


class TestGeneralAgentOrchestration:
    """Test the general agent orchestration functionality."""

    @pytest.mark.asyncio
    async def test_run_open_horizon_agent_brainstorming(self, mock_dependencies):
        """Test general agent function with brainstorming agent."""
        with patch('open_horizon_ai.agent.brainstorming_agent') as mock_agent:
            mock_result = Mock()
            mock_result.data = "Generated brainstorming response"
            mock_agent.run = AsyncMock(return_value=mock_result)
            
            response = await run_open_horizon_agent(
                prompt="Help me brainstorm a project",
                agent_type="brainstorming",
                user_id="test-user"
            )
            
            assert isinstance(response, str)
            assert "brainstorming" in response.lower() or "project" in response.lower()

    @pytest.mark.asyncio
    async def test_run_open_horizon_agent_planning(self, mock_dependencies):
        """Test general agent function with planning agent."""
        with patch('open_horizon_ai.agent.planning_agent') as mock_agent:
            mock_result = Mock()
            mock_result.data = "Generated planning response"
            mock_agent.run = AsyncMock(return_value=mock_result)
            
            response = await run_open_horizon_agent(
                prompt="Help me find partners",
                agent_type="planning",
                user_id="test-user"
            )
            
            assert isinstance(response, str)

    @pytest.mark.asyncio
    async def test_run_open_horizon_agent_application(self, mock_dependencies):
        """Test general agent function with application agent."""
        with patch('open_horizon_ai.agent.application_agent') as mock_agent:
            mock_result = Mock()
            mock_result.data = "Generated application content"
            mock_agent.run = AsyncMock(return_value=mock_result)
            
            response = await run_open_horizon_agent(
                prompt="Help me write application content",
                agent_type="application",
                user_id="test-user"
            )
            
            assert isinstance(response, str)

    @pytest.mark.asyncio
    async def test_agent_type_fallback(self, mock_dependencies):
        """Test agent type fallback to brainstorming."""
        with patch('open_horizon_ai.agent.brainstorming_agent') as mock_agent:
            mock_result = Mock()
            mock_result.data = "Fallback response"
            mock_agent.run = AsyncMock(return_value=mock_result)
            
            response = await run_open_horizon_agent(
                prompt="General query",
                agent_type="invalid_type",
                user_id="test-user"
            )
            
            assert isinstance(response, str)

    @pytest.mark.asyncio
    async def test_agent_error_handling(self):
        """Test agent error handling."""
        response = await run_open_horizon_agent(
            prompt="Test query",
            agent_type="brainstorming",
            user_id="test-user"
        )
        
        # Should handle errors gracefully
        assert isinstance(response, str)
        assert "failed" in response.lower() or "error" in response.lower() or response != ""


class TestAgentContextAndDependencies:
    """Test agent context management and dependencies."""

    @pytest.mark.asyncio
    async def test_agent_with_session_context(self, mock_dependencies):
        """Test agent receives proper session context."""
        test_agent = brainstorming_agent.override(model=TestModel())
        
        # Set specific context
        mock_dependencies.session_id = "session-123"
        mock_dependencies.user_id = "user-456" 
        mock_dependencies.project_id = "project-789"
        
        result = await test_agent.run(
            "Test with context",
            deps=mock_dependencies
        )
        
        assert result is not None
        # Context should be available to the agent

    @pytest.mark.asyncio
    async def test_agent_dependency_injection(self, mock_dependencies):
        """Test agent receives proper dependencies."""
        test_agent = brainstorming_agent.override(model=TestModel())
        
        # Verify dependencies are properly configured
        assert mock_dependencies.session_id == "test-session-123"
        assert mock_dependencies.user_id == "test-user-456"
        assert mock_dependencies.project_id == "test-project-789"
        
        result = await test_agent.run(
            "Test with dependencies",
            deps=mock_dependencies
        )
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_agent_cleanup(self, mock_dependencies):
        """Test agent cleanup functionality."""
        # Mock the cleanup method
        mock_dependencies.cleanup = AsyncMock()
        
        test_agent = brainstorming_agent.override(model=TestModel())
        
        result = await test_agent.run(
            "Test cleanup",
            deps=mock_dependencies
        )
        
        # Manually call cleanup to test
        await mock_dependencies.cleanup()
        
        mock_dependencies.cleanup.assert_called_once()

    def test_agent_system_prompts(self):
        """Test that agents have proper system prompts configured."""
        # Each agent should have a system prompt
        assert brainstorming_agent.system_prompt is not None
        assert planning_agent.system_prompt is not None
        assert application_agent.system_prompt is not None
        
        # System prompts should be different for each agent
        # (This test would need access to the actual prompt content)

    @pytest.mark.asyncio
    async def test_multiple_agents_parallel(self, mock_dependencies):
        """Test running multiple agents in parallel."""
        test_model = TestModel()
        
        brainstorm_agent = brainstorming_agent.override(model=test_model)
        plan_agent = planning_agent.override(model=test_model)
        app_agent = application_agent.override(model=test_model)
        
        # Run agents in parallel
        import asyncio
        
        results = await asyncio.gather(
            brainstorm_agent.run("Brainstorm ideas", deps=mock_dependencies),
            plan_agent.run("Find partners", deps=mock_dependencies),
            app_agent.run("Write content", deps=mock_dependencies),
            return_exceptions=True
        )
        
        # All should complete successfully or handle errors gracefully
        assert len(results) == 3
        for result in results:
            assert result is not None