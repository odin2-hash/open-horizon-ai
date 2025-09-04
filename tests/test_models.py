"""Test Pydantic models for Open Horizon AI system."""

import pytest
from datetime import datetime, timezone
from typing import List
from pydantic import ValidationError
import json

from ..models import (
    # Enums
    ProjectStatus, ErasmusFocusArea, OrganizationType,
    
    # Basic models
    ContactInfo, Partner, Project, ApplicationSection, ProjectConcept,
    
    # Request/Response models
    BrainstormRequest, BrainstormResponse,
    PartnerSearchRequest, PartnerSearchResponse,
    ApplicationContentRequest, ApplicationContentResponse,
    
    # Content models
    GeneratedContent, ComplianceDetails
)


class TestEnumModels:
    """Test enum model validation."""

    def test_project_status_enum(self):
        """Test ProjectStatus enum values."""
        # Valid values
        assert ProjectStatus.BRAINSTORMING == "brainstorming"
        assert ProjectStatus.PLANNING == "planning"
        assert ProjectStatus.PARTNERING == "partnering"
        assert ProjectStatus.WRITING == "writing"
        assert ProjectStatus.REVIEW == "review"
        assert ProjectStatus.SUBMITTED == "submitted"
        assert ProjectStatus.APPROVED == "approved"
        assert ProjectStatus.ACTIVE == "active"
        
        # Verify all expected statuses are available
        expected_statuses = [
            "brainstorming", "planning", "partnering", "writing", 
            "review", "submitted", "approved", "active"
        ]
        for status in expected_statuses:
            assert status in [s.value for s in ProjectStatus]

    def test_erasmus_focus_area_enum(self):
        """Test ErasmusFocusArea enum values."""
        # Valid values
        assert ErasmusFocusArea.DIGITAL_TRANSFORMATION == "Digital Transformation"
        assert ErasmusFocusArea.GREEN_TRANSITION == "Green Transition"
        assert ErasmusFocusArea.INCLUSION_DIVERSITY == "Inclusion and Diversity"
        assert ErasmusFocusArea.PARTICIPATION == "Participation"
        assert ErasmusFocusArea.EUROPEAN_VALUES == "European Values"
        assert ErasmusFocusArea.INNOVATION == "Innovation"
        
        # Verify comprehensive coverage of EU priorities
        focus_areas = [area.value for area in ErasmusFocusArea]
        assert len(focus_areas) == 6
        assert "Digital Transformation" in focus_areas
        assert "Green Transition" in focus_areas

    def test_organization_type_enum(self):
        """Test OrganizationType enum values."""
        # Valid values
        assert OrganizationType.NGO == "NGO"
        assert OrganizationType.PUBLIC == "Public Body"
        assert OrganizationType.SCHOOL == "School"
        assert OrganizationType.HEI == "Higher Education Institution"
        assert OrganizationType.COMPANY == "Company"
        assert OrganizationType.OTHER == "Other"
        
        # Verify all common Erasmus+ organization types
        org_types = [org.value for org in OrganizationType]
        assert "NGO" in org_types
        assert "Higher Education Institution" in org_types


class TestBasicModels:
    """Test basic model validation."""

    def test_contact_info_model(self):
        """Test ContactInfo model validation."""
        # Valid complete contact info
        contact = ContactInfo(
            email="test@example.com",
            website="https://example.com",
            phone="+46 123 456 789"
        )
        assert contact.email == "test@example.com"
        assert contact.website == "https://example.com"
        assert contact.phone == "+46 123 456 789"
        
        # Valid minimal contact info (all fields optional)
        minimal_contact = ContactInfo()
        assert minimal_contact.email is None
        assert minimal_contact.website is None
        assert minimal_contact.phone is None
        
        # Valid partial contact info
        partial_contact = ContactInfo(email="partial@example.com")
        assert partial_contact.email == "partial@example.com"
        assert partial_contact.website is None

    def test_contact_info_email_validation(self):
        """Test ContactInfo email validation."""
        # Valid email
        contact = ContactInfo(email="valid@example.com")
        assert contact.email == "valid@example.com"
        
        # Invalid email should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            ContactInfo(email="invalid-email")
        
        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"

    def test_partner_model_validation(self):
        """Test Partner model validation."""
        # Valid complete partner
        partner = Partner(
            id="partner-123",
            name="Test Organization",
            country="Sweden",
            organization_type=OrganizationType.NGO,
            expertise_areas=["Digital Skills", "Youth Work"],
            contact_info=ContactInfo(email="contact@test.org"),
            erasmus_code="SE-TEST-001",
            compatibility_score=8,
            partnership_rationale="Strong expertise match"
        )
        
        assert partner.id == "partner-123"
        assert partner.name == "Test Organization"
        assert partner.country == "Sweden"
        assert partner.organization_type == OrganizationType.NGO
        assert len(partner.expertise_areas) == 2
        assert partner.compatibility_score == 8
        
        # Test compatibility score validation
        with pytest.raises(ValidationError):
            Partner(
                id="test",
                name="Test",
                country="Test",
                organization_type=OrganizationType.NGO,
                compatibility_score=11  # Invalid: > 10
            )
        
        with pytest.raises(ValidationError):
            Partner(
                id="test",
                name="Test",
                country="Test",
                organization_type=OrganizationType.NGO,
                compatibility_score=0  # Invalid: < 1
            )

    def test_project_model_validation(self):
        """Test Project model validation."""
        # Valid complete project
        project = Project(
            id="proj-123",
            title="Digital Skills for Youth",
            focus_area=ErasmusFocusArea.DIGITAL_TRANSFORMATION,
            target_audience="Young adults 18-30",
            innovation_angle="AI-powered learning paths",
            status=ProjectStatus.PLANNING,
            duration_months=24,
            budget_estimate_eur=150000.0,
            countries_involved=["Sweden", "Germany", "Netherlands"],
            user_id="user-456"
        )
        
        assert project.id == "proj-123"
        assert project.title == "Digital Skills for Youth"
        assert project.focus_area == ErasmusFocusArea.DIGITAL_TRANSFORMATION
        assert project.status == ProjectStatus.PLANNING
        assert project.duration_months == 24
        assert project.budget_estimate_eur == 150000.0
        assert len(project.countries_involved) == 3
        
        # Test duration validation
        with pytest.raises(ValidationError):
            Project(
                id="test",
                title="Test Project",
                focus_area=ErasmusFocusArea.INNOVATION,
                target_audience="Test",
                innovation_angle="Test",
                duration_months=50  # Invalid: > 36
            )
        
        with pytest.raises(ValidationError):
            Project(
                id="test",
                title="Test Project",
                focus_area=ErasmusFocusArea.INNOVATION,
                target_audience="Test",
                innovation_angle="Test",
                duration_months=1  # Invalid: < 3
            )
        
        # Test budget validation
        with pytest.raises(ValidationError):
            Project(
                id="test",
                title="Test Project",
                focus_area=ErasmusFocusArea.INNOVATION,
                target_audience="Test",
                innovation_angle="Test",
                budget_estimate_eur=-1000  # Invalid: < 0
            )

    def test_project_concept_model(self):
        """Test ProjectConcept model validation."""
        concept = ProjectConcept(
            title="Innovative Youth Project",
            focus_area=ErasmusFocusArea.INNOVATION,
            target_audience="Young entrepreneurs 20-30",
            innovation_angle="Startup incubation with peer mentoring",
            feasibility_score=9,
            rationale="High market demand and proven methodology"
        )
        
        assert concept.title == "Innovative Youth Project"
        assert concept.focus_area == ErasmusFocusArea.INNOVATION
        assert concept.feasibility_score == 9
        
        # Test feasibility score validation
        with pytest.raises(ValidationError):
            ProjectConcept(
                title="Test",
                focus_area=ErasmusFocusArea.INNOVATION,
                target_audience="Test",
                innovation_angle="Test",
                feasibility_score=0,  # Invalid: < 1
                rationale="Test"
            )
        
        with pytest.raises(ValidationError):
            ProjectConcept(
                title="Test",
                focus_area=ErasmusFocusArea.INNOVATION,
                target_audience="Test",
                innovation_angle="Test",
                feasibility_score=11,  # Invalid: > 10
                rationale="Test"
            )

    def test_application_section_model(self):
        """Test ApplicationSection model validation."""
        section = ApplicationSection(
            id="section-123",
            project_id="proj-456",
            section_name="Project Description",
            content="This project addresses digital skills gaps in Europe...",
            word_count=150,
            compliance_status=True,
            suggestions=["Add specific outcomes", "Include timeline"]
        )
        
        assert section.id == "section-123"
        assert section.project_id == "proj-456"
        assert section.section_name == "Project Description"
        assert section.word_count == 150
        assert section.compliance_status is True
        assert len(section.suggestions) == 2
        assert isinstance(section.created_at, datetime)


class TestRequestResponseModels:
    """Test request and response model validation."""

    def test_brainstorm_request_model(self):
        """Test BrainstormRequest model validation."""
        # Valid complete request
        request = BrainstormRequest(
            initial_concept="digital skills for disadvantaged youth",
            focus_preference=ErasmusFocusArea.DIGITAL_TRANSFORMATION,
            organization_context="Swedish Social Services NGO",
            session_id="session-123"
        )
        
        assert request.initial_concept == "digital skills for disadvantaged youth"
        assert request.focus_preference == ErasmusFocusArea.DIGITAL_TRANSFORMATION
        assert request.organization_context == "Swedish Social Services NGO"
        assert request.session_id == "session-123"
        
        # Valid minimal request
        minimal_request = BrainstormRequest(
            initial_concept="help young people"
        )
        
        assert minimal_request.initial_concept == "help young people"
        assert minimal_request.focus_preference is None
        assert minimal_request.organization_context == "Swedish NGO"  # Default value
        assert minimal_request.session_id is None

    def test_brainstorm_response_model(self):
        """Test BrainstormResponse model validation."""
        # Valid successful response
        response = BrainstormResponse(
            success=True,
            project_concepts=[
                ProjectConcept(
                    title="Digital Skills Hub",
                    focus_area=ErasmusFocusArea.DIGITAL_TRANSFORMATION,
                    target_audience="Young adults",
                    innovation_angle="AI-powered learning",
                    feasibility_score=8,
                    rationale="Strong EU priority"
                )
            ],
            next_steps=["Define learning outcomes", "Find partners"],
            error=None
        )
        
        assert response.success is True
        assert len(response.project_concepts) == 1
        assert len(response.next_steps) == 2
        assert response.error is None
        
        # Valid error response
        error_response = BrainstormResponse(
            success=False,
            project_concepts=[],
            next_steps=[],
            error="Service temporarily unavailable"
        )
        
        assert error_response.success is False
        assert error_response.error == "Service temporarily unavailable"

    def test_partner_search_request_model(self):
        """Test PartnerSearchRequest model validation."""
        # Valid complete request
        request = PartnerSearchRequest(
            project_focus="digital skills development",
            required_countries=["Germany", "Netherlands", "Spain"],
            expertise_areas=["Digital Skills", "Youth Work", "Innovation"],
            project_id="proj-789"
        )
        
        assert request.project_focus == "digital skills development"
        assert len(request.required_countries) == 3
        assert len(request.expertise_areas) == 3
        assert request.project_id == "proj-789"
        
        # Valid minimal request
        minimal_request = PartnerSearchRequest(
            project_focus="general youth work"
        )
        
        assert minimal_request.project_focus == "general youth work"
        assert minimal_request.required_countries is None
        assert minimal_request.expertise_areas == []  # Default empty list
        assert minimal_request.project_id is None

    def test_partner_search_response_model(self):
        """Test PartnerSearchResponse model validation."""
        response = PartnerSearchResponse(
            success=True,
            potential_partners=[
                Partner(
                    id="partner-1",
                    name="Digital Youth Foundation", 
                    country="Germany",
                    organization_type=OrganizationType.NGO,
                    compatibility_score=9,
                    partnership_rationale="Strong expertise match"
                )
            ],
            search_metadata={
                "total_found": 1,
                "countries_covered": ["Germany"],
                "search_focus": "digital skills"
            },
            error=None
        )
        
        assert response.success is True
        assert len(response.potential_partners) == 1
        assert response.search_metadata["total_found"] == 1
        assert response.error is None

    def test_application_content_request_model(self):
        """Test ApplicationContentRequest model validation."""
        # Valid complete request
        request = ApplicationContentRequest(
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
            project_id="proj-123"
        )
        
        assert request.section_type == "Project Description"
        assert "title" in request.project_context
        assert request.word_limit == 500
        assert request.project_id == "proj-123"
        
        # Valid minimal request
        minimal_request = ApplicationContentRequest(
            section_type="Methodology",
            project_context={"title": "Basic Project"}
        )
        
        assert minimal_request.section_type == "Methodology"
        assert minimal_request.word_limit is None
        assert minimal_request.project_id is None

    def test_application_content_response_model(self):
        """Test ApplicationContentResponse model validation."""
        response = ApplicationContentResponse(
            success=True,
            generated_content=ApplicationSection(
                project_id="proj-123",
                section_name="Project Description",
                content="This innovative project addresses...",
                word_count=200,
                compliance_status=True,
                suggestions=[]
            ),
            alternative_versions=[
                {
                    "content": "Alternative version of the content...",
                    "focus": "technical",
                    "word_count": 180
                }
            ],
            error=None
        )
        
        assert response.success is True
        assert response.generated_content is not None
        assert response.generated_content.section_name == "Project Description"
        assert len(response.alternative_versions) == 1
        assert response.error is None


class TestContentModels:
    """Test content generation models."""

    def test_compliance_details_model(self):
        """Test ComplianceDetails model validation."""
        compliance = ComplianceDetails(
            missing_elements=["European dimension", "Impact measurement"],
            strength_areas=["Innovation", "Target group clarity"],
            improvement_suggestions=[
                "Add specific quantifiable outcomes",
                "Include references to EU policies",
                "Strengthen partnership rationale"
            ]
        )
        
        assert len(compliance.missing_elements) == 2
        assert len(compliance.strength_areas) == 2
        assert len(compliance.improvement_suggestions) == 3
        
        # Test with empty lists (valid)
        empty_compliance = ComplianceDetails()
        assert compliance.missing_elements == []
        assert compliance.strength_areas == []
        assert compliance.improvement_suggestions == []

    def test_generated_content_model(self):
        """Test GeneratedContent model validation."""
        content = GeneratedContent(
            section_name="Project Description",
            content="This innovative Erasmus+ project addresses digital skills gaps among young people across Europe...",
            word_count=150,
            compliance_status=True,
            compliance_details=ComplianceDetails(
                missing_elements=[],
                strength_areas=["European dimension", "Innovation"],
                improvement_suggestions=["Add specific timeline"]
            )
        )
        
        assert content.section_name == "Project Description"
        assert content.word_count == 150
        assert content.compliance_status is True
        assert len(content.compliance_details.strength_areas) == 2


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_project_json_serialization(self):
        """Test Project model JSON serialization."""
        project = Project(
            id="proj-123",
            title="Test Project",
            focus_area=ErasmusFocusArea.DIGITAL_TRANSFORMATION,
            target_audience="Young adults",
            innovation_angle="AI-powered learning",
            status=ProjectStatus.BRAINSTORMING,
            created_at=datetime.now(),
            partners=[
                Partner(
                    id="partner-1",
                    name="Test Partner",
                    country="Sweden",
                    organization_type=OrganizationType.NGO
                )
            ]
        )
        
        # Should serialize to JSON without errors
        json_data = project.model_dump()
        assert json_data["id"] == "proj-123"
        assert json_data["title"] == "Test Project"
        assert json_data["focus_area"] == "Digital Transformation"
        assert json_data["status"] == "brainstorming"
        assert len(json_data["partners"]) == 1
        
        # Should deserialize from JSON
        reconstructed = Project.model_validate(json_data)
        assert reconstructed.id == project.id
        assert reconstructed.title == project.title
        assert reconstructed.focus_area == project.focus_area

    def test_complex_model_serialization(self):
        """Test complex nested model serialization."""
        response = BrainstormResponse(
            success=True,
            project_concepts=[
                ProjectConcept(
                    title="Complex Project",
                    focus_area=ErasmusFocusArea.INCLUSION_DIVERSITY,
                    target_audience="Marginalized youth",
                    innovation_angle="Peer support networks",
                    feasibility_score=7,
                    rationale="High social impact potential"
                )
            ],
            next_steps=["Step 1", "Step 2"],
            error=None
        )
        
        # Serialize to JSON
        json_data = response.model_dump()
        assert json_data["success"] is True
        assert len(json_data["project_concepts"]) == 1
        assert json_data["project_concepts"][0]["title"] == "Complex Project"
        
        # Deserialize from JSON
        reconstructed = BrainstormResponse.model_validate(json_data)
        assert reconstructed.success == response.success
        assert len(reconstructed.project_concepts) == 1
        assert reconstructed.project_concepts[0].title == "Complex Project"


class TestModelValidationRules:
    """Test custom validation rules and constraints."""

    def test_project_title_validation(self):
        """Test project title validation."""
        # Valid title
        project = Project(
            id="test",
            title="Valid Project Title",
            focus_area=ErasmusFocusArea.INNOVATION,
            target_audience="Test audience",
            innovation_angle="Test innovation"
        )
        assert project.title == "Valid Project Title"
        
        # Empty title should raise validation error
        with pytest.raises(ValidationError):
            Project(
                id="test",
                title="",  # Empty title
                focus_area=ErasmusFocusArea.INNOVATION,
                target_audience="Test audience",
                innovation_angle="Test innovation"
            )

    def test_partner_expertise_areas_validation(self):
        """Test partner expertise areas validation."""
        # Valid expertise areas
        partner = Partner(
            id="test",
            name="Test Partner",
            country="Test Country",
            organization_type=OrganizationType.NGO,
            expertise_areas=["Digital Skills", "Youth Work", "Innovation"]
        )
        assert len(partner.expertise_areas) == 3
        
        # Empty expertise areas list should be valid
        partner_empty = Partner(
            id="test",
            name="Test Partner",
            country="Test Country",
            organization_type=OrganizationType.NGO,
            expertise_areas=[]
        )
        assert len(partner_empty.expertise_areas) == 0

    def test_application_section_word_count_consistency(self):
        """Test application section word count consistency."""
        content = "This is a test content with exactly ten words here."
        
        section = ApplicationSection(
            project_id="test",
            section_name="Test Section",
            content=content,
            word_count=10  # Should match actual word count
        )
        
        # Word count should be set correctly
        assert section.word_count == 10
        
        # Test with different word count
        section_different = ApplicationSection(
            project_id="test",
            section_name="Test Section",
            content=content,
            word_count=5  # Different from actual count
        )
        
        # Model should accept the provided word count
        # (Business logic for validation happens in tools/services)
        assert section_different.word_count == 5

    def test_enum_case_sensitivity(self):
        """Test enum values are case-sensitive."""
        # Valid enum value
        project = Project(
            id="test",
            title="Test",
            focus_area=ErasmusFocusArea.DIGITAL_TRANSFORMATION,
            target_audience="Test",
            innovation_angle="Test"
        )
        assert project.focus_area == ErasmusFocusArea.DIGITAL_TRANSFORMATION
        
        # Invalid case should raise validation error
        with pytest.raises(ValidationError):
            Project(
                id="test",
                title="Test",
                focus_area="digital transformation",  # Wrong case
                target_audience="Test",
                innovation_angle="Test"
            )


class TestModelDefaults:
    """Test model default values."""

    def test_project_defaults(self):
        """Test Project model default values."""
        project = Project(
            id="test",
            title="Test Project",
            focus_area=ErasmusFocusArea.INNOVATION,
            target_audience="Test audience",
            innovation_angle="Test innovation"
        )
        
        # Check defaults
        assert project.status == ProjectStatus.BRAINSTORMING
        assert project.partners == []
        assert project.countries_involved == []
        assert project.duration_months is None
        assert project.budget_estimate_eur is None
        assert project.user_id is None
        assert isinstance(project.created_at, datetime)

    def test_brainstorm_request_defaults(self):
        """Test BrainstormRequest default values."""
        request = BrainstormRequest(
            initial_concept="test concept"
        )
        
        assert request.focus_preference is None
        assert request.organization_context == "Swedish NGO"
        assert request.session_id is None

    def test_partner_search_request_defaults(self):
        """Test PartnerSearchRequest default values."""
        request = PartnerSearchRequest(
            project_focus="test focus"
        )
        
        assert request.required_countries is None
        assert request.expertise_areas == []
        assert request.project_id is None