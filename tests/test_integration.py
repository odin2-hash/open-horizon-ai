"""Integration tests for Open Horizon AI end-to-end Erasmus+ workflow."""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient

from ..api import app
from ..agent import (
    run_brainstorming_session, run_partner_search, run_application_writing
)
from ..models import (
    BrainstormRequest, PartnerSearchRequest, ApplicationContentRequest,
    ErasmusFocusArea, ProjectStatus
)
from ..dependencies import OpenHorizonDependencies


class TestErasmusPlusWorkflowIntegration:
    """Test complete Erasmus+ project development workflow."""

    @pytest.mark.asyncio
    async def test_complete_project_workflow(self, mock_dependencies, sample_project_concepts, sample_partners):
        """Test complete workflow from brainstorming to application writing."""
        project_id = "integration-test-project-123"
        user_id = "integration-test-user"
        
        # Update dependencies for this workflow
        mock_dependencies.project_id = project_id
        mock_dependencies.user_id = user_id
        
        # Step 1: Brainstorming Phase
        brainstorm_request = BrainstormRequest(
            initial_concept="digital skills for disadvantaged youth in Europe",
            focus_preference=ErasmusFocusArea.DIGITAL_TRANSFORMATION,
            organization_context="Swedish Social Services NGO",
            session_id="workflow-session-123"
        )
        
        with patch('open_horizon_ai.agent.brainstorm_project_ideas') as mock_brainstorm_tool:
            mock_brainstorm_tool.return_value = {
                "success": True,
                "project_concepts": sample_project_concepts,
                "next_steps": [
                    "Select most promising concept",
                    "Find European partners",
                    "Define learning outcomes"
                ],
                "error": None
            }
            
            brainstorm_response = await run_brainstorming_session(
                brainstorm_request,
                user_id=user_id,
                project_id=project_id
            )
            
            assert brainstorm_response.success is True
            assert len(brainstorm_response.next_steps) > 0
            mock_brainstorm_tool.assert_called_once()
        
        # Step 2: Partner Discovery Phase
        partner_request = PartnerSearchRequest(
            project_focus="digital skills development for disadvantaged youth",
            required_countries=["Germany", "Netherlands", "Spain"],
            expertise_areas=["Digital Skills", "Youth Work", "Social Inclusion"],
            project_id=project_id
        )
        
        with patch('open_horizon_ai.agent.discover_erasmus_partners') as mock_partner_tool:
            mock_partner_tool.return_value = {
                "success": True,
                "potential_partners": sample_partners,
                "search_metadata": {
                    "total_found": len(sample_partners),
                    "countries_covered": ["Germany", "Netherlands"],
                    "search_focus": "digital skills development"
                },
                "error": None
            }
            
            partner_response = await run_partner_search(
                partner_request,
                user_id=user_id
            )
            
            assert partner_response.success is True
            assert len(partner_response.search_metadata) > 0
            mock_partner_tool.assert_called_once()
        
        # Step 3: Application Writing Phase - Multiple Sections
        sections_to_generate = [
            "Project Description",
            "Methodology", 
            "Impact",
            "Sustainability Plan"
        ]
        
        project_context = {
            "title": "Digital Skills for European Disadvantaged Youth",
            "focus_area": "Digital Transformation",
            "target_audience": "Disadvantaged youth aged 16-25",
            "countries": ["Sweden", "Germany", "Netherlands", "Spain"],
            "duration_months": 24,
            "budget": 180000,
            "partners": len(sample_partners),
            "innovation_angle": "AI-powered personalized learning with peer mentoring"
        }
        
        generated_sections = []
        
        with patch('open_horizon_ai.agent.generate_application_section') as mock_content_tool:
            for section_type in sections_to_generate:
                mock_content_tool.return_value = {
                    "success": True,
                    "generated_content": {
                        "section_name": section_type,
                        "content": f"Generated content for {section_type} section...",
                        "word_count": 250,
                        "compliance_status": True,
                        "compliance_details": {
                            "missing_elements": [],
                            "strength_areas": ["European dimension", "Innovation"],
                            "improvement_suggestions": []
                        }
                    },
                    "alternative_versions": [
                        {
                            "content": f"Alternative content for {section_type}...",
                            "focus": "technical",
                            "word_count": 240
                        }
                    ],
                    "error": None
                }
                
                content_request = ApplicationContentRequest(
                    section_type=section_type,
                    project_context=project_context,
                    word_limit=300,
                    project_id=project_id
                )
                
                content_response = await run_application_writing(
                    content_request,
                    user_id=user_id
                )
                
                assert content_response.success is True
                assert content_response.generated_content is not None
                generated_sections.append(content_response)
        
        # Verify complete workflow results
        assert len(generated_sections) == len(sections_to_generate)
        
        # All sections should be compliant
        for section_response in generated_sections:
            content = section_response.generated_content
            if content:
                assert content["compliance_status"] is True
                assert len(content["compliance_details"]["strength_areas"]) > 0

    @pytest.mark.asyncio
    async def test_workflow_error_recovery(self, mock_dependencies):
        """Test workflow handles errors gracefully and continues."""
        project_id = "error-recovery-test-123"
        user_id = "error-test-user"
        
        mock_dependencies.project_id = project_id
        mock_dependencies.user_id = user_id
        
        # Step 1: Brainstorming succeeds
        brainstorm_request = BrainstormRequest(
            initial_concept="test project for error recovery",
            session_id="error-test-session"
        )
        
        with patch('open_horizon_ai.agent.brainstorm_project_ideas') as mock_brainstorm:
            mock_brainstorm.return_value = {
                "success": True,
                "project_concepts": [
                    {
                        "title": "Test Project",
                        "focus_area": ErasmusFocusArea.PARTICIPATION,
                        "target_audience": "Test group",
                        "innovation_angle": "Test innovation",
                        "feasibility_score": 7,
                        "rationale": "Test rationale"
                    }
                ],
                "next_steps": ["Continue to partner search"],
                "error": None
            }
            
            brainstorm_response = await run_brainstorming_session(
                brainstorm_request,
                user_id=user_id,
                project_id=project_id
            )
            
            assert brainstorm_response.success is True
        
        # Step 2: Partner search fails
        partner_request = PartnerSearchRequest(
            project_focus="test focus",
            project_id=project_id
        )
        
        with patch('open_horizon_ai.agent.discover_erasmus_partners') as mock_partner:
            mock_partner.return_value = {
                "success": False,
                "potential_partners": [],
                "search_metadata": {},
                "error": "Partner database temporarily unavailable"
            }
            
            partner_response = await run_partner_search(
                partner_request,
                user_id=user_id
            )
            
            assert partner_response.success is False
            assert partner_response.error is not None
        
        # Step 3: Application writing continues despite partner search failure
        content_request = ApplicationContentRequest(
            section_type="Project Description",
            project_context={
                "title": "Test Project",
                "focus_area": "Participation",
                "note": "Continuing without partner information"
            },
            project_id=project_id
        )
        
        with patch('open_horizon_ai.agent.generate_application_section') as mock_content:
            mock_content.return_value = {
                "success": True,
                "generated_content": {
                    "section_name": "Project Description",
                    "content": "Project description generated despite earlier errors...",
                    "word_count": 150,
                    "compliance_status": True,
                    "compliance_details": {
                        "missing_elements": ["Partner information"],
                        "strength_areas": ["European dimension"],
                        "improvement_suggestions": ["Add partner details when available"]
                    }
                },
                "alternative_versions": [],
                "error": None
            }
            
            content_response = await run_application_writing(
                content_request,
                user_id=user_id
            )
            
            # Should succeed despite earlier partner search failure
            assert content_response.success is True
            assert content_response.generated_content is not None

    @pytest.mark.asyncio
    async def test_parallel_workflow_processing(self, mock_dependencies, sample_partners):
        """Test processing multiple workflows in parallel."""
        base_project_id = "parallel-test-project"
        user_id = "parallel-test-user"
        
        # Create multiple workflow tasks
        workflow_tasks = []
        
        for i in range(3):
            project_id = f"{base_project_id}-{i}"
            session_id = f"parallel-session-{i}"
            
            # Create workflow task
            async def run_single_workflow(pid, sid):
                deps = OpenHorizonDependencies.from_settings(
                    project_id=pid,
                    user_id=user_id,
                    session_id=sid
                )
                
                # Mock database operations
                deps._supabase_client = Mock()
                deps._supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = {"data": []}
                
                brainstorm_request = BrainstormRequest(
                    initial_concept=f"test project {pid}",
                    session_id=sid
                )
                
                with patch('open_horizon_ai.agent.brainstorm_project_ideas') as mock_tool:
                    mock_tool.return_value = {
                        "success": True,
                        "project_concepts": [
                            {
                                "title": f"Project {pid}",
                                "focus_area": ErasmusFocusArea.DIGITAL_TRANSFORMATION,
                                "target_audience": "Test audience",
                                "innovation_angle": "Test innovation",
                                "feasibility_score": 8,
                                "rationale": "Test rationale"
                            }
                        ],
                        "next_steps": ["Continue workflow"],
                        "error": None
                    }
                    
                    response = await run_brainstorming_session(
                        brainstorm_request,
                        user_id=user_id,
                        project_id=pid
                    )
                    
                    return response
            
            task = run_single_workflow(project_id, session_id)
            workflow_tasks.append(task)
        
        # Execute all workflows in parallel
        results = await asyncio.gather(*workflow_tasks, return_exceptions=True)
        
        # Verify all workflows completed successfully
        assert len(results) == 3
        for result in results:
            assert not isinstance(result, Exception)
            assert result.success is True

    def test_api_workflow_integration(self, client, auth_headers):
        """Test complete workflow through API endpoints."""
        # Step 1: Create project
        create_response = client.post(
            "/api/projects",
            params={"title": "API Integration Test Project"},
            headers=auth_headers
        )
        
        assert create_response.status_code == 200
        project_data = create_response.json()
        project_id = project_data["project"]["id"]
        
        # Step 2: Brainstorm ideas
        with patch('open_horizon_ai.api.run_brainstorming_session') as mock_brainstorm:
            from ..models import BrainstormResponse
            mock_brainstorm.return_value = BrainstormResponse(
                success=True,
                project_concepts=[],
                next_steps=["Find partners"],
                error=None
            )
            
            brainstorm_response = client.post(
                "/api/brainstorm",
                json={
                    "initial_concept": "digital skills for youth",
                    "focus_preference": "Digital Transformation",
                    "organization_context": "Swedish NGO"
                },
                headers=auth_headers
            )
            
            assert brainstorm_response.status_code == 200
            brainstorm_data = brainstorm_response.json()
            assert brainstorm_data["success"] is True
        
        # Step 3: Search for partners
        with patch('open_horizon_ai.api.run_partner_search') as mock_search:
            from ..models import PartnerSearchResponse
            mock_search.return_value = PartnerSearchResponse(
                success=True,
                potential_partners=[],
                search_metadata={"total_found": 2},
                error=None
            )
            
            partner_response = client.post(
                "/api/partners/search",
                json={
                    "project_focus": "digital skills",
                    "required_countries": ["Germany", "Netherlands"],
                    "project_id": project_id
                },
                headers=auth_headers
            )
            
            assert partner_response.status_code == 200
            partner_data = partner_response.json()
            assert partner_data["success"] is True
        
        # Step 4: Generate application content
        with patch('open_horizon_ai.api.run_application_writing') as mock_writing:
            from ..models import ApplicationContentResponse
            mock_writing.return_value = ApplicationContentResponse(
                success=True,
                generated_content={
                    "section_name": "Project Description",
                    "content": "Generated project description...",
                    "word_count": 200,
                    "compliance_status": True,
                    "compliance_details": {
                        "missing_elements": [],
                        "strength_areas": ["European dimension"],
                        "improvement_suggestions": []
                    }
                },
                alternative_versions=[],
                error=None
            )
            
            content_response = client.post(
                "/api/application/content",
                json={
                    "section_type": "Project Description",
                    "project_context": {
                        "title": "API Integration Test Project",
                        "focus_area": "Digital Transformation"
                    },
                    "project_id": project_id
                },
                headers=auth_headers
            )
            
            assert content_response.status_code == 200
            content_data = content_response.json()
            assert content_data["success"] is True
        
        # Step 5: Verify project details
        project_response = client.get(
            f"/api/projects/{project_id}",
            headers=auth_headers
        )
        
        assert project_response.status_code == 200
        final_project = project_response.json()
        assert final_project["success"] is True


class TestDataPersistenceIntegration:
    """Test data persistence across workflow steps."""

    @pytest.mark.asyncio
    async def test_supabase_integration_workflow(self, mock_supabase_client):
        """Test workflow with Supabase database operations."""
        project_id = "supabase-integration-test"
        user_id = "supabase-test-user"
        
        # Mock Supabase client responses
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = {
            "data": [{"id": "new-record-id"}]
        }
        mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = {
            "data": [{"id": project_id}]
        }
        
        deps = OpenHorizonDependencies.from_settings(
            project_id=project_id,
            user_id=user_id
        )
        deps._supabase_client = mock_supabase_client
        
        # Test brainstorming with database save
        brainstorm_request = BrainstormRequest(
            initial_concept="database integration test project",
            session_id="supabase-session"
        )
        
        with patch('open_horizon_ai.agent.brainstorm_project_ideas') as mock_brainstorm:
            mock_brainstorm.return_value = {
                "success": True,
                "project_concepts": [
                    {
                        "title": "Database Test Project",
                        "focus_area": ErasmusFocusArea.INNOVATION,
                        "target_audience": "Test users",
                        "innovation_angle": "Database integration",
                        "feasibility_score": 9,
                        "rationale": "Test database operations"
                    }
                ],
                "next_steps": ["Test partner search with database"],
                "error": None
            }
            
            response = await run_brainstorming_session(
                brainstorm_request,
                user_id=user_id,
                project_id=project_id
            )
            
            assert response.success is True
            # Verify database operations were attempted
            mock_supabase_client.table.assert_called()

    @pytest.mark.asyncio
    async def test_workflow_state_management(self, mock_dependencies):
        """Test that workflow maintains state across steps."""
        project_id = "state-management-test"
        session_id = "state-session-123"
        
        mock_dependencies.project_id = project_id
        mock_dependencies.session_id = session_id
        
        # Track state through workflow steps
        workflow_state = {
            "project_concepts": [],
            "selected_partners": [],
            "generated_sections": []
        }
        
        # Step 1: Brainstorming - updates state
        with patch('open_horizon_ai.agent.brainstorm_project_ideas') as mock_brainstorm:
            concepts = [
                {
                    "title": "State Management Project",
                    "focus_area": ErasmusFocusArea.PARTICIPATION,
                    "target_audience": "European youth",
                    "innovation_angle": "State tracking",
                    "feasibility_score": 8,
                    "rationale": "Test state management"
                }
            ]
            
            mock_brainstorm.return_value = {
                "success": True,
                "project_concepts": concepts,
                "next_steps": ["Select concept and find partners"],
                "error": None
            }
            
            brainstorm_request = BrainstormRequest(
                initial_concept="state management test",
                session_id=session_id
            )
            
            response = await run_brainstorming_session(
                brainstorm_request,
                project_id=project_id
            )
            
            assert response.success is True
            workflow_state["project_concepts"] = concepts
        
        # Step 2: Partner search - uses state from previous step
        with patch('open_horizon_ai.agent.discover_erasmus_partners') as mock_partners:
            partners = [
                {
                    "id": "state-partner-1",
                    "name": "State Management Organization",
                    "country": "Sweden",
                    "organization_type": "NGO",
                    "expertise_areas": ["Project Management", "Youth Work"],
                    "contact_info": {"email": "state@org.se"},
                    "compatibility_score": 8,
                    "partnership_rationale": "Good state management practices"
                }
            ]
            
            mock_partners.return_value = {
                "success": True,
                "potential_partners": partners,
                "search_metadata": {"total_found": 1},
                "error": None
            }
            
            partner_request = PartnerSearchRequest(
                project_focus=workflow_state["project_concepts"][0]["title"],
                expertise_areas=["Project Management"],
                project_id=project_id
            )
            
            response = await run_partner_search(partner_request)
            
            assert response.success is True
            workflow_state["selected_partners"] = partners
        
        # Step 3: Application writing - uses accumulated state
        with patch('open_horizon_ai.agent.generate_application_section') as mock_content:
            mock_content.return_value = {
                "success": True,
                "generated_content": {
                    "section_name": "Project Description",
                    "content": f"Project: {workflow_state['project_concepts'][0]['title']} with partners: {len(workflow_state['selected_partners'])}",
                    "word_count": 100,
                    "compliance_status": True,
                    "compliance_details": {
                        "missing_elements": [],
                        "strength_areas": ["State consistency"],
                        "improvement_suggestions": []
                    }
                },
                "alternative_versions": [],
                "error": None
            }
            
            content_request = ApplicationContentRequest(
                section_type="Project Description",
                project_context={
                    "title": workflow_state["project_concepts"][0]["title"],
                    "focus_area": workflow_state["project_concepts"][0]["focus_area"],
                    "partners_count": len(workflow_state["selected_partners"])
                },
                project_id=project_id
            )
            
            response = await run_application_writing(content_request)
            
            assert response.success is True
            workflow_state["generated_sections"].append(response.generated_content)
        
        # Verify complete workflow state
        assert len(workflow_state["project_concepts"]) == 1
        assert len(workflow_state["selected_partners"]) == 1
        assert len(workflow_state["generated_sections"]) == 1
        
        # Verify state consistency across steps
        final_content = workflow_state["generated_sections"][0]
        if final_content:
            content_text = final_content.get("content", "")
            assert workflow_state["project_concepts"][0]["title"] in content_text


class TestPerformanceIntegration:
    """Test performance characteristics of the integrated system."""

    @pytest.mark.asyncio
    async def test_workflow_performance_timing(self, mock_dependencies):
        """Test workflow completes within reasonable time limits."""
        import time
        
        start_time = time.time()
        
        # Run simplified workflow with mocked tools
        with patch('open_horizon_ai.agent.brainstorm_project_ideas') as mock_brainstorm, \
             patch('open_horizon_ai.agent.discover_erasmus_partners') as mock_partners, \
             patch('open_horizon_ai.agent.generate_application_section') as mock_content:
            
            # Mock fast responses
            mock_brainstorm.return_value = {
                "success": True,
                "project_concepts": [{"title": "Speed Test", "focus_area": ErasmusFocusArea.INNOVATION, "target_audience": "Test", "innovation_angle": "Fast", "feasibility_score": 8, "rationale": "Speed"}],
                "next_steps": [],
                "error": None
            }
            
            mock_partners.return_value = {
                "success": True,
                "potential_partners": [],
                "search_metadata": {},
                "error": None
            }
            
            mock_content.return_value = {
                "success": True,
                "generated_content": {
                    "section_name": "Test",
                    "content": "Fast content",
                    "word_count": 2,
                    "compliance_status": True,
                    "compliance_details": {"missing_elements": [], "strength_areas": [], "improvement_suggestions": []}
                },
                "alternative_versions": [],
                "error": None
            }
            
            # Run workflow steps
            brainstorm_request = BrainstormRequest(initial_concept="speed test")
            await run_brainstorming_session(brainstorm_request, project_id="speed-test")
            
            partner_request = PartnerSearchRequest(project_focus="speed")
            await run_partner_search(partner_request)
            
            content_request = ApplicationContentRequest(section_type="Test", project_context={})
            await run_application_writing(content_request)
        
        end_time = time.time()
        workflow_duration = end_time - start_time
        
        # Workflow should complete quickly with mocked tools
        assert workflow_duration < 5.0  # Should complete in under 5 seconds

    @pytest.mark.asyncio
    async def test_concurrent_workflow_handling(self, mock_dependencies):
        """Test system handles concurrent workflows efficiently."""
        concurrent_workflows = 5
        
        async def run_concurrent_workflow(workflow_id):
            with patch('open_horizon_ai.agent.brainstorm_project_ideas') as mock_tool:
                mock_tool.return_value = {
                    "success": True,
                    "project_concepts": [{"title": f"Concurrent {workflow_id}", "focus_area": ErasmusFocusArea.PARTICIPATION, "target_audience": "Test", "innovation_angle": "Concurrent", "feasibility_score": 7, "rationale": "Concurrency test"}],
                    "next_steps": [],
                    "error": None
                }
                
                request = BrainstormRequest(initial_concept=f"concurrent test {workflow_id}")
                response = await run_brainstorming_session(request, project_id=f"concurrent-{workflow_id}")
                
                assert response.success is True
                return response
        
        # Run workflows concurrently
        import time
        start_time = time.time()
        
        tasks = [run_concurrent_workflow(i) for i in range(concurrent_workflows)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # All workflows should succeed
        assert len(results) == concurrent_workflows
        for result in results:
            assert not isinstance(result, Exception)
            assert result.success is True
        
        # Concurrent execution should be efficient
        # (Should not take 5x longer than sequential)
        assert total_duration < 10.0