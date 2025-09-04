"""Test Open Horizon AI tool functionality."""

import pytest
import json
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from pydantic_ai.tools import RunContext

from ..tools import (
    brainstorm_project_ideas,
    discover_erasmus_partners,
    generate_application_section
)
from ..models import ErasmusFocusArea, OrganizationType
from ..dependencies import OpenHorizonDependencies


class TestBrainstormProjectIdeas:
    """Test the brainstorm_project_ideas tool."""

    @pytest.mark.asyncio
    async def test_brainstorm_digital_skills_project(self, mock_dependencies):
        """Test brainstorming for digital skills project."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        result = await brainstorm_project_ideas(
            ctx,
            initial_concept="teach young people programming skills",
            focus_preference="Digital Transformation",
            organization_context="Swedish NGO"
        )
        
        assert result["success"] is True
        assert len(result["project_concepts"]) > 0
        assert len(result["next_steps"]) > 0
        assert result["error"] is None
        
        # Verify first concept structure
        concept = result["project_concepts"][0]
        assert "title" in concept
        assert "focus_area" in concept
        assert "target_audience" in concept
        assert "innovation_angle" in concept
        assert "feasibility_score" in concept
        assert "rationale" in concept
        assert isinstance(concept["feasibility_score"], int)
        assert 1 <= concept["feasibility_score"] <= 10

    @pytest.mark.asyncio
    async def test_brainstorm_green_transition_project(self, mock_dependencies):
        """Test brainstorming for green transition project."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        result = await brainstorm_project_ideas(
            ctx,
            initial_concept="environmental sustainability for youth",
            focus_preference="Green Transition",
            organization_context="Environmental NGO"
        )
        
        assert result["success"] is True
        concepts = result["project_concepts"]
        assert len(concepts) > 0
        
        # Should generate green transition focused concept
        green_concepts = [c for c in concepts if c["focus_area"] == ErasmusFocusArea.GREEN_TRANSITION]
        assert len(green_concepts) > 0

    @pytest.mark.asyncio
    async def test_brainstorm_inclusion_diversity_project(self, mock_dependencies):
        """Test brainstorming for inclusion and diversity project."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        result = await brainstorm_project_ideas(
            ctx,
            initial_concept="help marginalized youth find opportunities",
            focus_preference="Inclusion and Diversity",
            organization_context="Social Services NGO"
        )
        
        assert result["success"] is True
        concepts = result["project_concepts"]
        assert len(concepts) > 0
        
        # Should focus on inclusion
        inclusion_concepts = [c for c in concepts if c["focus_area"] == ErasmusFocusArea.INCLUSION_DIVERSITY]
        assert len(inclusion_concepts) > 0

    @pytest.mark.asyncio
    async def test_brainstorm_default_concept_generation(self, mock_dependencies):
        """Test brainstorming with generic concept generates default project."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        result = await brainstorm_project_ideas(
            ctx,
            initial_concept="help young people in Europe",
            focus_preference=None,
            organization_context="General NGO"
        )
        
        assert result["success"] is True
        concepts = result["project_concepts"]
        assert len(concepts) > 0
        
        # Should generate at least one concept
        concept = concepts[0]
        assert concept["focus_area"] in [area.value for area in ErasmusFocusArea]

    @pytest.mark.asyncio
    async def test_brainstorm_with_supabase_integration(self, mock_dependencies):
        """Test brainstorming with Supabase database integration."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        # Mock Supabase update operation
        mock_dependencies._supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = {
            "data": [{"id": "test-project-789"}]
        }
        
        result = await brainstorm_project_ideas(
            ctx,
            initial_concept="digital literacy for seniors",
            focus_preference="Digital Transformation",
            organization_context="Senior Care Organization"
        )
        
        assert result["success"] is True
        
        # Verify Supabase was called if project_id exists
        if mock_dependencies.project_id:
            mock_dependencies._supabase_client.table.assert_called_with('projects')

    @pytest.mark.asyncio
    async def test_brainstorm_error_handling(self, mock_dependencies):
        """Test brainstorming tool error handling."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        # Force an exception by corrupting dependencies
        mock_dependencies.supabase = Mock()
        mock_dependencies.supabase.table.side_effect = Exception("Database error")
        
        result = await brainstorm_project_ideas(
            ctx,
            initial_concept="test project",
            focus_preference=None,
            organization_context="Test Org"
        )
        
        # Should still succeed despite database error
        assert result["success"] is True
        assert len(result["project_concepts"]) > 0

    @pytest.mark.asyncio
    async def test_brainstorm_multiple_concepts_generation(self, mock_dependencies):
        """Test that multiple concepts are generated when appropriate."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        result = await brainstorm_project_ideas(
            ctx,
            initial_concept="digital green inclusive project for youth",  # Multiple keywords
            focus_preference=None,
            organization_context="Multi-focus NGO"
        )
        
        assert result["success"] is True
        concepts = result["project_concepts"]
        
        # Should generate multiple concepts for multi-keyword input
        # At least one should be generated
        assert len(concepts) >= 1


class TestDiscoverErasmusPartners:
    """Test the discover_erasmus_partners tool."""

    @pytest.mark.asyncio
    async def test_partner_discovery_basic(self, mock_dependencies):
        """Test basic partner discovery functionality."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        result = await discover_erasmus_partners(
            ctx,
            project_focus="digital skills development",
            required_countries=None,
            expertise_areas=None
        )
        
        assert result["success"] is True
        assert "potential_partners" in result
        assert "search_metadata" in result
        assert result["error"] is None
        assert len(result["potential_partners"]) > 0
        
        # Verify metadata structure
        metadata = result["search_metadata"]
        assert "total_found" in metadata
        assert "countries_covered" in metadata
        assert "search_focus" in metadata

    @pytest.mark.asyncio
    async def test_partner_discovery_with_country_filter(self, mock_dependencies):
        """Test partner discovery with country requirements."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        result = await discover_erasmus_partners(
            ctx,
            project_focus="digital skills",
            required_countries=["Germany", "Netherlands"],
            expertise_areas=None
        )
        
        assert result["success"] is True
        partners = result["potential_partners"]
        
        # All partners should be from required countries
        countries = [p["country"] for p in partners]
        for country in countries:
            assert country in ["Germany", "Netherlands"]

    @pytest.mark.asyncio
    async def test_partner_discovery_with_expertise_filter(self, mock_dependencies):
        """Test partner discovery with expertise requirements."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        result = await discover_erasmus_partners(
            ctx,
            project_focus="environmental education",
            required_countries=None,
            expertise_areas=["Environmental Education", "Sustainability"]
        )
        
        assert result["success"] is True
        partners = result["potential_partners"]
        
        # Partners should have matching expertise
        for partner in partners:
            expertise = partner["expertise_areas"]
            has_match = any(
                area.lower() in [exp.lower() for exp in expertise]
                for area in ["Environmental Education", "Sustainability"]
            )
            assert has_match

    @pytest.mark.asyncio
    async def test_partner_discovery_compatibility_scoring(self, mock_dependencies):
        """Test partner compatibility scoring."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        result = await discover_erasmus_partners(
            ctx,
            project_focus="Digital Skills",  # Exact match with mock data
            required_countries=None,
            expertise_areas=None
        )
        
        assert result["success"] is True
        partners = result["potential_partners"]
        
        # Verify compatibility scores
        for partner in partners:
            assert "compatibility_score" in partner
            score = partner["compatibility_score"]
            assert isinstance(score, int)
            assert 1 <= score <= 10
            
            # Partners with matching focus should have higher scores
            if "Digital Skills" in partner["expertise_areas"]:
                assert score >= 8  # Should be boosted

    @pytest.mark.asyncio
    async def test_partner_discovery_data_structure(self, mock_dependencies):
        """Test partner data structure compliance."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        result = await discover_erasmus_partners(
            ctx,
            project_focus="innovation",
            required_countries=None,
            expertise_areas=None
        )
        
        assert result["success"] is True
        partners = result["potential_partners"]
        
        for partner in partners:
            # Verify all required fields are present
            assert "name" in partner
            assert "country" in partner
            assert "organization_type" in partner
            assert "expertise_areas" in partner
            assert "contact_info" in partner
            assert "erasmus_code" in partner
            assert "compatibility_score" in partner
            assert "partnership_rationale" in partner
            
            # Verify data types
            assert isinstance(partner["name"], str)
            assert isinstance(partner["country"], str)
            assert isinstance(partner["expertise_areas"], list)
            assert isinstance(partner["contact_info"], dict)
            
            # Verify organization type is valid
            org_type = partner["organization_type"]
            assert org_type in [t.value for t in OrganizationType]

    @pytest.mark.asyncio
    async def test_partner_discovery_with_supabase(self, mock_dependencies):
        """Test partner discovery with Supabase logging."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        # Mock Supabase insert operation
        mock_dependencies._supabase_client.table.return_value.insert.return_value.execute.return_value = {
            "data": [{"id": "search-123"}]
        }
        
        result = await discover_erasmus_partners(
            ctx,
            project_focus="youth work",
            required_countries=["Spain"],
            expertise_areas=["Youth Support"]
        )
        
        assert result["success"] is True
        
        # Verify Supabase was called if project_id exists
        if mock_dependencies.project_id:
            mock_dependencies._supabase_client.table.assert_called_with('partner_searches')

    @pytest.mark.asyncio
    async def test_partner_discovery_error_handling(self, mock_dependencies):
        """Test partner discovery error handling."""
        # Test with corrupted dependencies
        original_project_id = mock_dependencies.project_id
        mock_dependencies.project_id = "invalid-id"
        
        # Mock database error
        mock_dependencies._supabase_client.table.side_effect = Exception("Database error")
        
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        result = await discover_erasmus_partners(
            ctx,
            project_focus="test focus",
            required_countries=None,
            expertise_areas=None
        )
        
        # Should handle database errors gracefully
        assert result["success"] is True  # Tool should still work
        
        # Restore original project_id
        mock_dependencies.project_id = original_project_id

    @pytest.mark.asyncio
    async def test_partner_discovery_empty_results(self, mock_dependencies):
        """Test partner discovery with no matching results."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        result = await discover_erasmus_partners(
            ctx,
            project_focus="very specific niche topic",
            required_countries=["NonexistentCountry"],
            expertise_areas=["VerySpecificExpertise"]
        )
        
        assert result["success"] is True
        assert result["potential_partners"] == []
        assert result["search_metadata"]["total_found"] == 0
        assert result["search_metadata"]["countries_covered"] == []


class TestGenerateApplicationSection:
    """Test the generate_application_section tool."""

    @pytest.mark.asyncio
    async def test_generate_project_description(self, mock_dependencies):
        """Test generating Project Description section."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        project_context = {
            "title": "Digital Skills for European Youth",
            "focus_area": "Digital Transformation",
            "target_audience": "Young adults 18-30",
            "countries": ["Sweden", "Germany", "Netherlands"]
        }
        
        result = await generate_application_section(
            ctx,
            section_type="Project Description",
            project_context=project_context,
            word_limit=500
        )
        
        assert result["success"] is True
        assert "generated_content" in result
        assert result["error"] is None
        
        content = result["generated_content"]
        assert content["section_name"] == "Project Description"
        assert len(content["content"]) > 0
        assert content["word_count"] > 0
        assert content["word_count"] <= 500  # Respects word limit
        assert isinstance(content["compliance_status"], bool)
        assert "compliance_details" in content

    @pytest.mark.asyncio
    async def test_generate_methodology_section(self, mock_dependencies):
        """Test generating Methodology section."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        project_context = {
            "title": "Green Skills Development",
            "focus_area": "Green Transition",
            "target_audience": "Environmental activists"
        }
        
        result = await generate_application_section(
            ctx,
            section_type="Methodology",
            project_context=project_context,
            word_limit=300
        )
        
        assert result["success"] is True
        content = result["generated_content"]
        
        # Methodology should contain specific elements
        assert "methodology" in content["content"].lower() or "approach" in content["content"].lower()
        assert content["word_count"] <= 300
        
        # Should mention participatory learning, digital innovation, etc.
        content_lower = content["content"].lower()
        assert any(word in content_lower for word in ["participatory", "digital", "cross-cultural", "learning"])

    @pytest.mark.asyncio
    async def test_generate_impact_section(self, mock_dependencies):
        """Test generating Impact section."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        project_context = {
            "title": "Inclusive Europe Project",
            "focus_area": "Inclusion and Diversity",
            "target_audience": "Marginalized youth"
        }
        
        result = await generate_application_section(
            ctx,
            section_type="Impact",
            project_context=project_context,
            word_limit=400
        )
        
        assert result["success"] is True
        content = result["generated_content"]
        
        # Impact section should mention different levels of impact
        content_lower = content["content"].lower()
        assert "impact" in content_lower
        assert any(word in content_lower for word in ["individual", "organizational", "systemic"])

    @pytest.mark.asyncio
    async def test_generate_custom_section(self, mock_dependencies):
        """Test generating custom/unknown section."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        project_context = {
            "title": "Innovation Hub",
            "focus_area": "Innovation",
            "target_audience": "Young entrepreneurs"
        }
        
        result = await generate_application_section(
            ctx,
            section_type="Sustainability Plan",
            project_context=project_context,
            word_limit=200
        )
        
        assert result["success"] is True
        content = result["generated_content"]
        
        # Should generate generic but relevant content
        assert len(content["content"]) > 0
        assert content["word_count"] <= 200
        assert "Sustainability Plan" in content["section_name"]

    @pytest.mark.asyncio
    async def test_compliance_checking_european_dimension(self, mock_dependencies):
        """Test compliance checking for European dimension."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        project_context = {
            "title": "Local Skills Training",  # No European reference
            "focus_area": "General",
            "target_audience": "Local youth"
        }
        
        result = await generate_application_section(
            ctx,
            section_type="Project Description",
            project_context=project_context
        )
        
        assert result["success"] is True
        content = result["generated_content"]
        compliance = content["compliance_details"]
        
        # Should flag missing European dimension if not present
        if not any("european" in content["content"].lower() or "europe" in content["content"].lower()):
            assert "european dimension" in " ".join(compliance["missing_elements"]).lower()

    @pytest.mark.asyncio
    async def test_compliance_checking_target_group(self, mock_dependencies):
        """Test compliance checking for target group definition."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        project_context = {
            "title": "Skills Development Project",
            "focus_area": "Digital Transformation",
            "target_audience": "Young people"
        }
        
        result = await generate_application_section(
            ctx,
            section_type="Project Description",
            project_context=project_context
        )
        
        assert result["success"] is True
        content = result["generated_content"]
        compliance = content["compliance_details"]
        
        # Should recognize target group is defined
        if any(word in content["content"].lower() for word in ["participants", "youth", "young people"]):
            assert "target group clearly defined" in " ".join(compliance["strength_areas"]).lower()

    @pytest.mark.asyncio
    async def test_word_limit_enforcement(self, mock_dependencies):
        """Test word limit enforcement."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        project_context = {
            "title": "Comprehensive Project",
            "focus_area": "Innovation"
        }
        
        result = await generate_application_section(
            ctx,
            section_type="Project Description",
            project_context=project_context,
            word_limit=50  # Very restrictive limit
        )
        
        assert result["success"] is True
        content = result["generated_content"]
        
        # Should enforce word limit
        assert content["word_count"] <= 52  # Allow small margin for "..." addition
        if content["word_count"] > 50:
            assert content["content"].endswith("...")

    @pytest.mark.asyncio
    async def test_alternative_versions_generation(self, mock_dependencies):
        """Test generation of alternative content versions."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        project_context = {
            "title": "Innovation Project",
            "focus_area": "Innovation"
        }
        
        result = await generate_application_section(
            ctx,
            section_type="Project Description",
            project_context=project_context
        )
        
        assert result["success"] is True
        assert "alternative_versions" in result
        alternatives = result["alternative_versions"]
        
        assert len(alternatives) > 0
        for alt in alternatives:
            assert "content" in alt
            assert "focus" in alt
            assert "word_count" in alt
            assert len(alt["content"]) > 0

    @pytest.mark.asyncio
    async def test_supabase_integration(self, mock_dependencies):
        """Test Supabase integration for saving generated content."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        # Mock Supabase insert
        mock_dependencies._supabase_client.table.return_value.insert.return_value.execute.return_value = {
            "data": [{"id": "section-123"}]
        }
        
        project_context = {"title": "Test Project"}
        
        result = await generate_application_section(
            ctx,
            section_type="Test Section",
            project_context=project_context
        )
        
        assert result["success"] is True
        
        # Verify Supabase was called if project_id exists
        if mock_dependencies.project_id:
            mock_dependencies._supabase_client.table.assert_called_with('application_sections')

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_dependencies):
        """Test error handling in content generation."""
        # Test with minimal/invalid project context
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        result = await generate_application_section(
            ctx,
            section_type="Test Section",
            project_context={},  # Empty context
            word_limit=10
        )
        
        # Should handle gracefully
        assert result["success"] is True
        assert result["generated_content"] is not None

    @pytest.mark.asyncio
    async def test_compliance_improvement_suggestions(self, mock_dependencies):
        """Test that compliance checking provides improvement suggestions."""
        ctx = RunContext(deps=mock_dependencies, retry=0)
        
        project_context = {
            "title": "Basic Project",
            "focus_area": "General"
        }
        
        result = await generate_application_section(
            ctx,
            section_type="Project Description",
            project_context=project_context
        )
        
        assert result["success"] is True
        content = result["generated_content"]
        compliance = content["compliance_details"]
        
        # Should always provide improvement suggestions
        assert "improvement_suggestions" in compliance
        assert len(compliance["improvement_suggestions"]) > 0
        
        # Suggestions should be relevant
        suggestions_text = " ".join(compliance["improvement_suggestions"]).lower()
        assert any(word in suggestions_text for word in ["outcome", "policy", "result", "quantifiable"])