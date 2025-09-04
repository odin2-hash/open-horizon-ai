"""Test configuration and fixtures for Open Horizon AI system."""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from typing import Any, Dict
from datetime import datetime
import json

from pydantic_ai.models.test import TestModel
from pydantic_ai.models.function import FunctionModel
from pydantic_ai.messages import ModelTextResponse

from ..models import (
    ProjectConcept, Partner, ErasmusFocusArea, OrganizationType,
    ContactInfo, BrainstormRequest, PartnerSearchRequest, 
    ApplicationContentRequest, OpenHorizonDependencies
)
from ..dependencies import OpenHorizonDependencies
from ..settings import Settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    return Settings(
        llm_api_key="test-openai-key",
        llm_provider="openai",
        llm_model="gpt-4o-mini",
        supabase_url="https://test.supabase.co",
        supabase_key="test-supabase-key",
        supabase_service_key="test-service-key",
        secret_key="test-secret-key",
        erasmus_partner_api_key="test-partner-key",
        app_env="testing",
        debug=True
    )


@pytest.fixture
def mock_dependencies(mock_settings):
    """Mock dependencies for agent testing."""
    deps = OpenHorizonDependencies.from_settings(
        mock_settings,
        session_id="test-session-123",
        user_id="test-user-456", 
        project_id="test-project-789"
    )
    
    # Mock the Supabase client
    deps._supabase_client = Mock()
    deps._supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = {"data": []}
    deps._supabase_client.table.return_value.insert.return_value.execute.return_value = {"data": []}
    deps._supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = {"data": []}
    
    return deps


@pytest.fixture
def test_model():
    """TestModel for predictable agent responses."""
    return TestModel()


@pytest.fixture
def brainstorm_test_model():
    """TestModel configured for brainstorming responses."""
    model = TestModel()
    model.agent_responses = [
        ModelTextResponse(content="I'll help you brainstorm Erasmus+ project ideas."),
        {
            "brainstorm_tool": {
                "initial_concept": "digital skills for youth",
                "focus_preference": "Digital Transformation",
                "organization_context": "Swedish NGO"
            }
        },
        ModelTextResponse(content="I've generated several project concepts focusing on digital skills development.")
    ]
    return model


@pytest.fixture 
def partner_search_test_model():
    """TestModel configured for partner search responses."""
    model = TestModel()
    model.agent_responses = [
        ModelTextResponse(content="I'll search for suitable Erasmus+ partners."),
        {
            "partner_discovery_tool": {
                "project_focus": "digital skills",
                "required_countries": ["Germany", "Netherlands"],
                "expertise_areas": ["Digital Skills", "Youth Work"]
            }
        },
        ModelTextResponse(content="I've found several potential partners with strong compatibility scores.")
    ]
    return model


@pytest.fixture
def application_test_model():
    """TestModel configured for application writing responses."""
    model = TestModel()
    model.agent_responses = [
        ModelTextResponse(content="I'll help you write compelling application content."),
        {
            "content_generation_tool": {
                "section_type": "Project Description",
                "project_context": {"title": "Digital Youth Skills", "focus_area": "Digital Transformation"},
                "word_limit": 500
            }
        },
        ModelTextResponse(content="I've generated compliant application text with compliance checking.")
    ]
    return model


@pytest.fixture
def custom_function_model():
    """FunctionModel for custom behavior testing."""
    call_count = 0
    
    async def custom_function(messages, tools):
        nonlocal call_count
        call_count += 1
        
        if call_count == 1:
            return ModelTextResponse(content="I understand your request.")
        elif call_count == 2:
            # Simulate tool call based on context
            last_message = messages[-1].content if messages else ""
            if "brainstorm" in last_message.lower():
                return {"brainstorm_tool": {"initial_concept": "test project", "focus_preference": None}}
            elif "partner" in last_message.lower():
                return {"partner_discovery_tool": {"project_focus": "test focus"}}
            elif "application" in last_message.lower():
                return {"content_generation_tool": {"section_type": "test section", "project_context": {}}}
        else:
            return ModelTextResponse(content="Task completed successfully.")
    
    return FunctionModel(custom_function)


@pytest.fixture
def sample_project_concepts():
    """Sample project concepts for testing."""
    return [
        {
            "title": "Digital Skills for Youth",
            "focus_area": ErasmusFocusArea.DIGITAL_TRANSFORMATION,
            "target_audience": "Young adults 18-30",
            "innovation_angle": "AI-powered learning paths",
            "feasibility_score": 8,
            "rationale": "Strong EU priority with clear methodology"
        },
        {
            "title": "Green Europe Initiative", 
            "focus_area": ErasmusFocusArea.GREEN_TRANSITION,
            "target_audience": "Environmental activists",
            "innovation_angle": "Gamified environmental challenges",
            "feasibility_score": 9,
            "rationale": "High impact potential with engaging approach"
        }
    ]


@pytest.fixture
def sample_partners():
    """Sample partner data for testing."""
    return [
        {
            "id": "partner-1",
            "name": "Digital Youth Foundation",
            "country": "Germany",
            "organization_type": OrganizationType.NGO,
            "expertise_areas": ["Digital Skills", "Youth Work"],
            "contact_info": {
                "email": "contact@digitalyouth.de",
                "website": "https://digitalyouth.de"
            },
            "erasmus_code": "DE-YOUTH-001",
            "compatibility_score": 9,
            "partnership_rationale": "Strong digital expertise"
        },
        {
            "id": "partner-2", 
            "name": "Green Action Network",
            "country": "Netherlands",
            "organization_type": OrganizationType.NGO,
            "expertise_areas": ["Environmental Education", "Sustainability"],
            "contact_info": {
                "email": "info@greenaction.nl",
                "website": "https://greenaction.nl"
            },
            "erasmus_code": "NL-GREEN-002",
            "compatibility_score": 8,
            "partnership_rationale": "European-wide networks"
        }
    ]


@pytest.fixture
def sample_brainstorm_request():
    """Sample brainstorm request for testing."""
    return BrainstormRequest(
        initial_concept="I want to help young people develop digital skills",
        focus_preference=ErasmusFocusArea.DIGITAL_TRANSFORMATION,
        organization_context="Swedish NGO",
        session_id="test-session-123"
    )


@pytest.fixture
def sample_partner_request():
    """Sample partner search request for testing."""
    return PartnerSearchRequest(
        project_focus="digital skills development",
        required_countries=["Germany", "Netherlands", "Spain"],
        expertise_areas=["Digital Skills", "Youth Work", "Innovation"],
        project_id="test-project-789"
    )


@pytest.fixture
def sample_application_request():
    """Sample application content request for testing."""
    return ApplicationContentRequest(
        section_type="Project Description",
        project_context={
            "title": "Digital Skills for European Youth",
            "focus_area": "Digital Transformation",
            "target_audience": "Young adults 18-30",
            "countries": ["Sweden", "Germany", "Netherlands"],
            "duration_months": 24,
            "budget": 150000
        },
        word_limit=500,
        project_id="test-project-789"
    )


@pytest.fixture
async def mock_httpx_client():
    """Mock httpx client for external API calls."""
    client = AsyncMock()
    
    # Mock partner API response
    partner_response = Mock()
    partner_response.json.return_value = {
        "success": True,
        "partners": [
            {
                "name": "Test Organization",
                "country": "Germany", 
                "type": "NGO",
                "expertise": ["Digital Skills", "Youth Work"]
            }
        ]
    }
    client.get.return_value = partner_response
    
    return client


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for database operations."""
    client = Mock()
    
    # Mock table operations
    table_mock = Mock()
    table_mock.insert.return_value.execute.return_value = {"data": [{"id": "test-id"}]}
    table_mock.update.return_value.eq.return_value.execute.return_value = {"data": [{"id": "test-id"}]}
    table_mock.select.return_value.eq.return_value.execute.return_value = {"data": []}
    client.table.return_value = table_mock
    
    return client


@pytest.mark.asyncio
@pytest.fixture
async def mock_agent_with_tools():
    """Mock agent with tools for integration testing."""
    from ..agent import brainstorming_agent
    
    # Override with test model
    test_agent = brainstorming_agent.override(model=TestModel())
    
    return test_agent


@pytest.fixture(scope="function", autouse=True)
def clean_environment():
    """Clean up after each test."""
    yield
    # Any cleanup logic here


# Utility fixtures for common test data
@pytest.fixture
def valid_project_data():
    """Valid project data for testing."""
    return {
        "id": "test-project-123",
        "title": "Test Digital Skills Project",
        "focus_area": ErasmusFocusArea.DIGITAL_TRANSFORMATION,
        "target_audience": "Young adults 18-30",
        "innovation_angle": "AI-powered learning",
        "duration_months": 24,
        "countries_involved": ["Sweden", "Germany", "Netherlands"]
    }


@pytest.fixture
def invalid_project_data():
    """Invalid project data for testing validation."""
    return {
        "title": "",  # Invalid: empty title
        "focus_area": "invalid_focus",  # Invalid: not in enum
        "duration_months": -5,  # Invalid: negative duration
    }


@pytest.fixture
def erasmus_compliance_requirements():
    """Erasmus+ compliance requirements for testing."""
    return {
        "required_elements": [
            "European dimension",
            "Innovation elements", 
            "Target group definition",
            "Learning outcomes",
            "Impact measurement",
            "Sustainability plan"
        ],
        "focus_areas": list(ErasmusFocusArea),
        "min_partners": 2,
        "max_duration_months": 36,
        "min_duration_months": 3
    }


# Mock patches for common external services
@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API responses."""
    with patch('openai.AsyncOpenAI') as mock:
        mock_client = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Mock AI response"
        mock_client.chat.completions.create.return_value = mock_response
        mock.return_value = mock_client
        yield mock


@pytest.fixture
def mock_supabase_operations():
    """Mock all Supabase operations."""
    with patch('supabase.create_client') as mock:
        mock_client = mock_supabase_client()
        mock.return_value = mock_client
        yield mock_client