"""Test Open Horizon AI FastAPI endpoints."""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, patch
import json

from ..api import app
from ..models import (
    BrainstormRequest, BrainstormResponse,
    PartnerSearchRequest, PartnerSearchResponse,
    ApplicationContentRequest, ApplicationContentResponse,
    ErasmusFocusArea
)


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {"Authorization": "Bearer test-token-123"}


class TestHealthEndpoints:
    """Test health check and basic endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns basic info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "status" in data
        assert "version" in data
        assert data["status"] == "healthy"
        assert "Open Horizon AI" in data["message"]

    def test_health_check_endpoint(self, client):
        """Test detailed health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "services" in data
        assert data["status"] == "healthy"
        
        services = data["services"]
        assert "api" in services
        assert "agents" in services
        assert "database" in services
        assert services["api"] == "operational"


class TestBrainstormEndpoint:
    """Test the brainstorm endpoint."""

    @patch('open_horizon_ai.api.run_brainstorming_session')
    def test_brainstorm_success(self, mock_brainstorm, client, auth_headers):
        """Test successful brainstorming request."""
        # Mock the brainstorming session
        mock_response = BrainstormResponse(
            success=True,
            project_concepts=[],
            next_steps=["Define learning outcomes", "Find partners"],
            error=None
        )
        mock_brainstorm.return_value = mock_response
        
        request_data = {
            "initial_concept": "teach young people programming skills",
            "focus_preference": "Digital Transformation",
            "organization_context": "Swedish NGO",
            "session_id": "test-session-123"
        }
        
        response = client.post(
            "/api/brainstorm",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["error"] is None
        assert len(data["next_steps"]) > 0
        
        # Verify the mock was called
        mock_brainstorm.assert_called_once()
        
        # Check the call arguments
        call_args = mock_brainstorm.call_args
        request_arg = call_args[1]['request']  # keyword argument
        assert request_arg.initial_concept == "teach young people programming skills"

    @patch('open_horizon_ai.api.run_brainstorming_session')
    def test_brainstorm_with_optional_fields(self, mock_brainstorm, client, auth_headers):
        """Test brainstorming with minimal required fields."""
        mock_response = BrainstormResponse(
            success=True,
            project_concepts=[],
            next_steps=[],
            error=None
        )
        mock_brainstorm.return_value = mock_response
        
        request_data = {
            "initial_concept": "help young people"
            # No focus_preference, using defaults
        }
        
        response = client.post(
            "/api/brainstorm",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch('open_horizon_ai.api.run_brainstorming_session')
    def test_brainstorm_error_handling(self, mock_brainstorm, client, auth_headers):
        """Test brainstorming error handling."""
        # Mock an exception
        mock_brainstorm.side_effect = Exception("Brainstorming service unavailable")
        
        request_data = {
            "initial_concept": "test project"
        }
        
        response = client.post(
            "/api/brainstorm",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Brainstorming session failed" in data["detail"]

    def test_brainstorm_authentication_required(self, client):
        """Test that brainstorm endpoint requires authentication."""
        request_data = {
            "initial_concept": "test project"
        }
        
        response = client.post("/api/brainstorm", json=request_data)
        
        # Should require authentication
        assert response.status_code == 403  # Forbidden without auth

    def test_brainstorm_invalid_request_data(self, client, auth_headers):
        """Test brainstorm with invalid request data."""
        request_data = {
            # Missing required 'initial_concept' field
            "focus_preference": "Invalid Focus Area"
        }
        
        response = client.post(
            "/api/brainstorm",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Unprocessable Entity
        data = response.json()
        assert "detail" in data


class TestPartnerSearchEndpoint:
    """Test the partner search endpoint."""

    @patch('open_horizon_ai.api.run_partner_search')
    def test_partner_search_success(self, mock_search, client, auth_headers):
        """Test successful partner search."""
        mock_response = PartnerSearchResponse(
            success=True,
            potential_partners=[
                {
                    "id": "partner-1",
                    "name": "Digital Youth Foundation",
                    "country": "Germany",
                    "organization_type": "NGO",
                    "expertise_areas": ["Digital Skills", "Youth Work"],
                    "contact_info": {"email": "contact@digitalyouth.de"},
                    "compatibility_score": 9,
                    "partnership_rationale": "Strong digital expertise"
                }
            ],
            search_metadata={"total_found": 1, "countries_covered": ["Germany"]},
            error=None
        )
        mock_search.return_value = mock_response
        
        request_data = {
            "project_focus": "digital skills development",
            "required_countries": ["Germany", "Netherlands"],
            "expertise_areas": ["Digital Skills", "Youth Work"],
            "project_id": "test-project-789"
        }
        
        response = client.post(
            "/api/partners/search",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["error"] is None
        assert len(data["potential_partners"]) > 0
        assert "search_metadata" in data
        
        # Verify partner data structure
        partner = data["potential_partners"][0]
        assert "name" in partner
        assert "country" in partner
        assert "compatibility_score" in partner

    @patch('open_horizon_ai.api.run_partner_search')
    def test_partner_search_minimal_request(self, mock_search, client, auth_headers):
        """Test partner search with minimal request data."""
        mock_response = PartnerSearchResponse(
            success=True,
            potential_partners=[],
            search_metadata={"total_found": 0},
            error=None
        )
        mock_search.return_value = mock_response
        
        request_data = {
            "project_focus": "general youth work"
            # Optional fields omitted
        }
        
        response = client.post(
            "/api/partners/search",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch('open_horizon_ai.api.run_partner_search')
    def test_partner_search_error_handling(self, mock_search, client, auth_headers):
        """Test partner search error handling."""
        mock_search.side_effect = Exception("Partner database unavailable")
        
        request_data = {
            "project_focus": "test focus"
        }
        
        response = client.post(
            "/api/partners/search",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Partner search failed" in data["detail"]

    def test_partner_search_invalid_data(self, client, auth_headers):
        """Test partner search with invalid data."""
        request_data = {
            # Missing required project_focus
            "required_countries": "not_a_list"  # Should be list
        }
        
        response = client.post(
            "/api/partners/search",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestApplicationContentEndpoint:
    """Test the application content generation endpoint."""

    @patch('open_horizon_ai.api.run_application_writing')
    def test_content_generation_success(self, mock_writing, client, auth_headers):
        """Test successful content generation."""
        mock_response = ApplicationContentResponse(
            success=True,
            generated_content={
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
            alternative_versions=[],
            error=None
        )
        mock_writing.return_value = mock_response
        
        request_data = {
            "section_type": "Project Description",
            "project_context": {
                "title": "Digital Skills for European Youth",
                "focus_area": "Digital Transformation",
                "target_audience": "Young adults 18-30"
            },
            "word_limit": 500,
            "project_id": "test-project-789"
        }
        
        response = client.post(
            "/api/application/content",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["error"] is None
        assert data["generated_content"] is not None
        
        content = data["generated_content"]
        assert content["section_name"] == "Project Description"
        assert content["word_count"] > 0
        assert isinstance(content["compliance_status"], bool)

    @patch('open_horizon_ai.api.run_application_writing')
    def test_content_generation_without_word_limit(self, mock_writing, client, auth_headers):
        """Test content generation without word limit."""
        mock_response = ApplicationContentResponse(
            success=True,
            generated_content={
                "section_name": "Methodology",
                "content": "Our methodology includes...",
                "word_count": 300,
                "compliance_status": True,
                "compliance_details": {
                    "missing_elements": [],
                    "strength_areas": [],
                    "improvement_suggestions": []
                }
            },
            alternative_versions=[],
            error=None
        )
        mock_writing.return_value = mock_response
        
        request_data = {
            "section_type": "Methodology",
            "project_context": {"title": "Test Project"}
            # No word_limit specified
        }
        
        response = client.post(
            "/api/application/content",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_content_generation_invalid_data(self, client, auth_headers):
        """Test content generation with invalid data."""
        request_data = {
            # Missing required section_type and project_context
            "word_limit": "not_a_number"
        }
        
        response = client.post(
            "/api/application/content",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestChatEndpoint:
    """Test the general chat endpoint."""

    @patch('open_horizon_ai.api.run_open_horizon_agent')
    def test_chat_success(self, mock_agent, client, auth_headers):
        """Test successful chat interaction."""
        mock_agent.return_value = "I can help you with Erasmus+ project development."
        
        response = client.post(
            "/api/chat",
            params={
                "message": "Help me create a project",
                "agent_type": "brainstorming",
                "project_id": "test-project",
                "session_id": "test-session"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "response" in data
        assert data["agent_type"] == "brainstorming"
        assert data["session_id"] == "test-session"
        
        mock_agent.assert_called_once()

    @patch('open_horizon_ai.api.run_open_horizon_agent')
    def test_chat_with_defaults(self, mock_agent, client, auth_headers):
        """Test chat with default parameters."""
        mock_agent.return_value = "Default response"
        
        response = client.post(
            "/api/chat",
            params={"message": "Hello"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["agent_type"] == "brainstorming"  # Default

    @patch('open_horizon_ai.api.run_open_horizon_agent')
    def test_chat_error_handling(self, mock_agent, client, auth_headers):
        """Test chat error handling."""
        mock_agent.side_effect = Exception("Agent unavailable")
        
        response = client.post(
            "/api/chat",
            params={"message": "Test message"},
            headers=auth_headers
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Chat session failed" in data["detail"]


class TestProjectManagementEndpoints:
    """Test project management endpoints."""

    def test_list_projects(self, client, auth_headers):
        """Test listing user projects."""
        response = client.get("/api/projects", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "projects" in data
        assert isinstance(data["projects"], list)

    def test_create_project(self, client, auth_headers):
        """Test creating a new project."""
        response = client.post(
            "/api/projects",
            params={"title": "Test Digital Skills Project"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "project" in data
        project = data["project"]
        assert project["title"] == "Test Digital Skills Project"
        assert project["status"] == "brainstorming"
        assert "id" in project

    def test_get_project(self, client, auth_headers):
        """Test getting project details."""
        project_id = "test-project-123"
        
        response = client.get(
            f"/api/projects/{project_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "project" in data
        project = data["project"]
        assert project["id"] == project_id


class TestCORSConfiguration:
    """Test CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are configured."""
        response = client.options("/")
        
        # FastAPI automatically handles OPTIONS for CORS
        assert response.status_code == 200


class TestRequestValidation:
    """Test request validation across endpoints."""

    def test_brainstorm_request_validation(self, client, auth_headers):
        """Test brainstorm request validation."""
        # Test with invalid focus_preference
        request_data = {
            "initial_concept": "test concept",
            "focus_preference": "InvalidFocusArea"
        }
        
        response = client.post(
            "/api/brainstorm",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        
        # Should contain validation error details
        errors = data["detail"]
        assert isinstance(errors, list)
        assert len(errors) > 0

    def test_partner_search_request_validation(self, client, auth_headers):
        """Test partner search request validation."""
        # Test with invalid required_countries (should be list)
        request_data = {
            "project_focus": "test focus",
            "required_countries": "Germany"  # Should be a list
        }
        
        response = client.post(
            "/api/partners/search",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422

    def test_application_content_request_validation(self, client, auth_headers):
        """Test application content request validation."""
        # Test with invalid word_limit (should be integer)
        request_data = {
            "section_type": "Project Description",
            "project_context": {},
            "word_limit": "not_a_number"
        }
        
        response = client.post(
            "/api/application/content",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422


class TestResponseModels:
    """Test response model compliance."""

    @patch('open_horizon_ai.api.run_brainstorming_session')
    def test_brainstorm_response_model(self, mock_brainstorm, client, auth_headers):
        """Test brainstorm response follows BrainstormResponse model."""
        mock_response = BrainstormResponse(
            success=True,
            project_concepts=[],
            next_steps=["Step 1", "Step 2"],
            error=None
        )
        mock_brainstorm.return_value = mock_response
        
        request_data = {"initial_concept": "test"}
        
        response = client.post(
            "/api/brainstorm",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure matches BrainstormResponse
        assert "success" in data
        assert "project_concepts" in data
        assert "next_steps" in data
        assert "error" in data
        
        assert isinstance(data["success"], bool)
        assert isinstance(data["project_concepts"], list)
        assert isinstance(data["next_steps"], list)

    @patch('open_horizon_ai.api.run_partner_search')
    def test_partner_search_response_model(self, mock_search, client, auth_headers):
        """Test partner search response follows PartnerSearchResponse model."""
        mock_response = PartnerSearchResponse(
            success=True,
            potential_partners=[],
            search_metadata={"total_found": 0},
            error=None
        )
        mock_search.return_value = mock_response
        
        request_data = {"project_focus": "test"}
        
        response = client.post(
            "/api/partners/search",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "success" in data
        assert "potential_partners" in data
        assert "search_metadata" in data
        assert "error" in data


@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test asynchronous endpoint behavior."""

    @pytest.mark.asyncio
    async def test_async_client_brainstorm(self, auth_headers):
        """Test brainstorming endpoint with async client."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('open_horizon_ai.api.run_brainstorming_session') as mock_brainstorm:
                mock_response = BrainstormResponse(
                    success=True,
                    project_concepts=[],
                    next_steps=[],
                    error=None
                )
                mock_brainstorm.return_value = mock_response
                
                request_data = {"initial_concept": "async test"}
                
                response = await ac.post(
                    "/api/brainstorm",
                    json=request_data,
                    headers=auth_headers
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True