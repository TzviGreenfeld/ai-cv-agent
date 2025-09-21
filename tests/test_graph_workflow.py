"""Tests for LangGraph workflow"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from ai_cv_agent.graph.workflow_graph import run_workflow, build_workflow_graph
from ai_cv_agent.models.job_models import JobRequirements, JobParseResult
from ai_cv_agent.models.resume_models import ResumeData


@pytest.mark.asyncio
async def test_workflow_success():
    """Test successful workflow execution"""

    # Mock data
    mock_profile = {
        "candidate": {"name": "Test User", "title": "Software Engineer"},
        "contact": {"email": "test@example.com"},
        "summary": "Test summary",
        "work_experience": [],
        "education": [],
        "skills": {"technical": ["Python"], "soft": ["Communication"]},
    }

    mock_job_requirements = JobRequirements(
        role="Senior Python Developer",
        company="Test Corp",
        raw_description="Job description...",
        technical_skills=["Python", "Django"],
        key_requirements=["5 years experience"],
    )

    mock_resume_data = ResumeData()
    mock_resume_data.candidate = {
        "name": "Test User",
        "title": "Senior Python Developer",
    }
    mock_resume_data.contact = ["", "test@example.com", "", ""]
    mock_resume_data.summary = "Tailored summary"
    mock_resume_data.experience = []
    mock_resume_data.education = []
    mock_resume_data.skills = [
        {"name": "Technical", "skills": ["Python", "Django"]},
        {"name": "Soft", "skills": ["Leadership"]},
    ]

    # Apply mocks
    with (
        patch(
            "ai_cv_agent.graph.workflow_graph.read_user_profile"
        ) as mock_read_profile,
        patch(
            "ai_cv_agent.graph.workflow_graph.convert_raw_resume_to_resume_data"
        ) as mock_convert,
        patch("ai_cv_agent.graph.workflow_graph.JobParserAgent") as mock_parser_class,
        patch(
            "ai_cv_agent.graph.workflow_graph.ResumeTailoringAgent"
        ) as mock_tailoring_class,
        patch(
            "ai_cv_agent.graph.workflow_graph.generate_cv_html"
        ) as mock_generate_html,
        patch("ai_cv_agent.graph.workflow_graph.html_to_pdf_async") as mock_html_to_pdf,
    ):
        # Setup mocks
        mock_read_profile.return_value = mock_profile
        mock_convert.return_value = mock_resume_data

        # Mock job parser
        mock_parser = AsyncMock()
        mock_parser.parse_from_url = AsyncMock(
            return_value=JobParseResult.success_result(mock_job_requirements)
        )
        mock_parser_class.return_value = mock_parser

        # Mock tailoring agent
        mock_tailoring = AsyncMock()
        mock_tailoring.tailor_resume = AsyncMock(return_value=mock_resume_data)
        mock_tailoring_class.return_value = mock_tailoring

        # Mock HTML and PDF generation
        mock_generate_html.return_value = "<html>Test</html>"
        mock_html_to_pdf.return_value = None

        # Run workflow
        result = await run_workflow("https://test.com/job")

        # Assertions
        assert result.endswith(".pdf")
        assert "Test_Corp_Senior_Python_Developer" in result

        # Verify calls
        mock_read_profile.assert_called_once()
        mock_parser.parse_from_url.assert_called_once_with("https://test.com/job")
        mock_tailoring.tailor_resume.assert_called_once()
        mock_generate_html.assert_called_once()
        mock_html_to_pdf.assert_called_once()


@pytest.mark.asyncio
async def test_workflow_job_parse_failure():
    """Test workflow handling of job parse failure"""

    with (
        patch("ai_cv_agent.graph.workflow_graph.read_user_profile"),
        patch("ai_cv_agent.graph.workflow_graph.convert_raw_resume_to_resume_data"),
        patch("ai_cv_agent.graph.workflow_graph.JobParserAgent") as mock_parser_class,
    ):
        # Mock job parser failure
        mock_parser = AsyncMock()
        mock_parser.parse_from_url = AsyncMock(
            return_value=JobParseResult.error_result("Failed to fetch job")
        )
        mock_parser_class.return_value = mock_parser

        # Run workflow and expect error
        with pytest.raises(RuntimeError) as exc_info:
            await run_workflow("https://test.com/bad-job")

        assert "Failed to parse job" in str(exc_info.value)


@pytest.mark.asyncio
async def test_workflow_profile_load_failure():
    """Test workflow handling of profile load failure"""

    with patch(
        "ai_cv_agent.graph.workflow_graph.read_user_profile"
    ) as mock_read_profile:
        # Mock profile read failure
        mock_read_profile.side_effect = FileNotFoundError("Profile not found")

        # Run workflow and expect error
        with pytest.raises(RuntimeError) as exc_info:
            await run_workflow("https://test.com/job")

        assert "Failed to load user profile" in str(exc_info.value)


def test_graph_structure():
    """Test that the graph is built correctly"""

    graph = build_workflow_graph()
    compiled = graph.compile()

    # Check that all required nodes exist
    expected_nodes = {
        "load_profile",
        "parse_job",
        "tailor_resume",
        "generate_html",
        "export_pdf",
        "error_sink",
        "success_sink",
    }

    # Get the graph structure
    graph_def = compiled.get_graph()
    nodes = set(graph_def.nodes.keys())

    # Verify all expected nodes are present
    assert expected_nodes.issubset(nodes)


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_workflow_success())
    asyncio.run(test_workflow_job_parse_failure())
    asyncio.run(test_workflow_profile_load_failure())
    test_graph_structure()
    print("✅ All tests passed!")
