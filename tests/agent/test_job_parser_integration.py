"""Integration tests for JobParserAgent with real LLM but mocked job fetching"""

import pytest
from unittest.mock import patch
from pathlib import Path
from ai_cv_agent.agent.job_parser_agent import JobParserAgent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# The specific URL we're testing with
GOOGLE_JOB_URL = "https://www.google.com/about/careers/applications/jobs/results/74939955737961158-software-engineer-iii-google-cloud"


class TestJobParserIntegration:
    """Integration tests with real LLM but mocked job fetching"""

    @pytest.fixture
    def mock_job_content(self):
        """Load mock job description from file"""
        mock_file = Path(__file__).parent.parent / "mocks" / "google_swe3_cloud.md"
        return mock_file.read_text()

    @pytest.fixture
    def has_azure_credentials(self):
        """Check if Azure OpenAI credentials are available"""
        return all(
            [
                os.getenv("AZURE_AI_ENDPOINT"),
                os.getenv("AZURE_AI_API_KEY"),
                os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            ]
        )

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not all(
            [
                os.getenv("AZURE_AI_ENDPOINT"),
                os.getenv("AZURE_AI_API_KEY"),
                os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            ]
        ),
        reason="Azure OpenAI credentials not found in environment",
    )
    async def test_parse_google_swe3_job(self, mock_job_content):
        """Test parsing a real Google SWE III job with actual LLM"""

        # Mock the fetch function where it's used (in the agent module)
        with patch(
            "ai_cv_agent.agent.job_parser_agent.read_job_description"
        ) as mock_fetch:
            # Create an async mock that returns the content only for our specific URL
            async def mock_async_fetch(url):
                if url == GOOGLE_JOB_URL:
                    return mock_job_content
                else:
                    raise ValueError(f"URL not mocked: {url}")

            mock_fetch.side_effect = mock_async_fetch

            # Use real JobParserAgent with real LLM
            parser = JobParserAgent()
            url = GOOGLE_JOB_URL

            result = await parser.parse_from_url(url)

            # Validate the parsing worked
            assert result.success, f"Parsing failed: {result.error_message}"

            job = result.job_requirements

            # Basic validation
            assert job.role is not None
            assert job.company is not None
            assert job.raw_description == mock_job_content

            # Validate role extraction - LLM should identify this correctly
            assert "Software Engineer" in job.role or "SWE" in job.role, (
                f"Role extracted: {job.role}"
            )
            assert "III" in job.role or "3" in job.role or "Senior" in job.role, (
                f"Level not identified in role: {job.role}"
            )

            # Validate company extraction
            assert "Google" in str(job.company), f"Company extracted: {job.company}"

            # Check location was mentioned (even if not extracted as a field)
            assert any(
                "Bengaluru" in str(item) or "Hyderabad" in str(item)
                for item in [
                    job.raw_description,
                    job.nice_to_have,
                    job.key_requirements,
                ]
            )

            # Validate key requirements were extracted
            assert len(job.key_requirements) > 0, "No key requirements extracted"
            assert any(
                "Bachelor" in req or "degree" in req for req in job.key_requirements
            ), f"Degree requirement not found in: {job.key_requirements}"
            assert any(
                "2 years" in req or "experience" in req for req in job.key_requirements
            ), f"Experience requirement not found in: {job.key_requirements}"

            # Check technical skills
            assert len(job.technical_skills) > 0, "No technical skills extracted"
            expected_skills_keywords = [
                "software development",
                "programming",
                "data structures",
                "algorithms",
                "distributed computing",
                "system design",
                "cloud",
                "google cloud",
            ]
            found_skills_text = " ".join(
                skill.lower() for skill in job.technical_skills
            )
            assert any(
                keyword in found_skills_text for keyword in expected_skills_keywords
            ), f"Expected technical skills not found. Extracted: {job.technical_skills}"

            # Check responsibilities extraction
            assert len(job.main_responsibilities) > 0, "No responsibilities extracted"
            responsibility_keywords = [
                "code",
                "design",
                "review",
                "develop",
                "test",
                "debug",
            ]
            found_responsibilities_text = " ".join(
                resp.lower() for resp in job.main_responsibilities
            )
            assert any(
                keyword in found_responsibilities_text
                for keyword in responsibility_keywords
            ), (
                f"Expected responsibilities not found. Extracted: {job.main_responsibilities}"
            )

            # Verify ATS keywords
            assert len(job.keywords_for_ats) > 0, "No ATS keywords extracted"
            # Should include both technical and role-specific keywords
            ats_keywords_lower = [kw.lower() for kw in job.keywords_for_ats]
            assert any(
                "cloud" in kw or "google cloud" in kw for kw in ats_keywords_lower
            ), f"Cloud keywords not found in ATS keywords: {job.keywords_for_ats}"

            # Check nice-to-have extraction
            assert any(
                "Master" in nth or "PhD" in nth or "accessible" in nth
                for nth in job.nice_to_have
            ), f"Nice-to-have qualifications not properly extracted: {job.nice_to_have}"

            # Validate the model methods work correctly
            assert job.has_minimum_data() is True
            all_keywords = job.get_all_keywords()
            assert len(all_keywords) > 5, f"Too few total keywords: {len(all_keywords)}"

            # Test conversion to dict format
            analysis_dict = job.to_analysis_dict()
            assert "role" in analysis_dict
            assert "company" in analysis_dict
            assert analysis_dict["role"] == job.role
            assert len(analysis_dict["technical_skills"]) == len(job.technical_skills)

            print("\n✅ Successfully parsed Google SWE III job:")
            print(f"  Role: {job.role}")
            print(f"  Company: {job.company}")
            print(
                f"  Technical Skills ({len(job.technical_skills)}): {', '.join(job.technical_skills[:5])}..."
            )
            print(
                f"  ATS Keywords ({len(job.keywords_for_ats)}): {', '.join(job.keywords_for_ats[:5])}..."
            )
            print(f"  Responsibilities: {len(job.main_responsibilities)}")
            print(f"  Total unique keywords: {len(all_keywords)}")

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not all(
            [
                os.getenv("AZURE_AI_ENDPOINT"),
                os.getenv("AZURE_AI_API_KEY"),
                os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            ]
        ),
        reason="Azure OpenAI credentials not found in environment",
    )
    async def test_parse_from_text_integration(self, mock_job_content):
        """Test parsing from text directly with real LLM"""

        parser = JobParserAgent()
        result = await parser.parse_from_text(mock_job_content)

        assert result.success, f"Parsing failed: {result.error_message}"
        job = result.job_requirements

        # Should extract the same information as URL parsing
        assert "Software Engineer" in job.role
        assert "Google" in str(job.company)
        assert len(job.technical_skills) > 0
        assert len(job.keywords_for_ats) > 0

    def test_sync_parse_integration(self, mock_job_content, has_azure_credentials):
        """Test synchronous parsing with real LLM"""

        if not has_azure_credentials:
            pytest.skip("Azure OpenAI credentials not found")

        # For sync test, we need to mock the async function properly
        with patch(
            "ai_cv_agent.agent.job_parser_agent.read_job_description"
        ) as mock_fetch:
            # Create an async mock that returns the content only for our specific URL
            async def mock_async_fetch(url):
                if url == GOOGLE_JOB_URL:
                    return mock_job_content
                else:
                    raise ValueError(f"URL not mocked: {url}")

            mock_fetch.side_effect = mock_async_fetch

            parser = JobParserAgent()
            url = GOOGLE_JOB_URL

            result = parser.parse_from_url_sync(url)

            assert result.success, f"Parsing failed: {result.error_message}"
            assert "Software Engineer" in result.job_requirements.role


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "-s"])
