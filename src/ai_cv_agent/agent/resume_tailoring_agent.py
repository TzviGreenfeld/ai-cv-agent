"""Resume Tailoring Agent - Tailors resumes based on job requirements"""

import os
import yaml
import asyncio
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI

from ..models.job_models import JobRequirements
from ..models.resume_models import ResumeData
from ..tools.resume_parser import convert_raw_resume_to_resume_data
from .resume_tailoring_prompts import (
    RESUME_TAILORING_SYSTEM_PROMPT,
    RESUME_TAILORING_USER_PROMPT,
)

# Load environment variables
load_dotenv()


class ResumeTailoringAgent:
    """
    Agent that tailors a resume based on job requirements.

    Takes structured inputs and returns enhanced ResumeData.
    """

    def __init__(self, temperature: float = 0.3):
        """
        Initialize the Resume Tailoring Agent.

        Args:
            temperature: LLM temperature for tailoring (lower = more consistent)
        """
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_AI_ENDPOINT"),
            api_key=os.getenv("AZURE_AI_API_KEY"),
            api_version=os.getenv("AZURE_AI_API_VERSION"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=temperature,
        )

    async def tailor_resume(
        self, original_resume: ResumeData, job_requirements: JobRequirements
    ) -> ResumeData:
        """
        Tailor resume to match job requirements.

        Args:
            original_resume: Original ResumeData object
            job_requirements: Parsed job requirements

        Returns:
            New ResumeData object with tailored content
        """
        try:
            # Convert inputs to formats needed for prompt
            resume_dict = original_resume.to_dict()
            resume_yaml = yaml.dump(resume_dict, default_flow_style=False)
            job_analysis = job_requirements.to_analysis_dict()

            # Format the prompt with all data
            user_prompt = RESUME_TAILORING_USER_PROMPT.format(
                company=job_analysis.get("company", "N/A"),
                role=job_analysis.get("role", "N/A"),
                key_requirements=", ".join(job_analysis.get("key_requirements", [])),
                technical_skills=", ".join(job_analysis.get("technical_skills", [])),
                soft_skills=", ".join(job_analysis.get("soft_skills", [])),
                keywords_for_ats=", ".join(job_analysis.get("keywords_for_ats", [])),
                main_responsibilities=", ".join(
                    job_analysis.get("main_responsibilities", [])
                ),
                job_description=job_requirements.raw_description,
                user_profile=resume_yaml,
            )

            # Get LLM response
            messages = [
                {"role": "system", "content": RESUME_TAILORING_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ]

            response = await self.llm.ainvoke(messages)
            tailored_yaml = self._clean_yaml_response(response.content)

            # Parse and convert back to ResumeData
            tailored_dict = yaml.safe_load(tailored_yaml)
            tailored_resume = convert_raw_resume_to_resume_data(tailored_dict)

            return tailored_resume

        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse tailored YAML: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to tailor resume: {str(e)}")

    def tailor_resume_sync(
        self, original_resume: ResumeData, job_requirements: JobRequirements
    ) -> ResumeData:
        """
        Synchronous wrapper for tailor_resume.

        Args:
            original_resume: Original ResumeData object
            job_requirements: Parsed job requirements

        Returns:
            New ResumeData object with tailored content
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.tailor_resume(original_resume, job_requirements)
            )
        finally:
            loop.close()

    def _clean_yaml_response(self, response: str) -> str:
        """
        Clean YAML response from markdown code fences.

        Args:
            response: Raw LLM response

        Returns:
            Cleaned YAML string
        """
        if "```yaml" in response:
            return response.split("```yaml")[1].split("```")[0].strip()
        elif "```" in response:
            return response.split("```")[1].split("```")[0].strip()
        return response.strip()


# Example usage
if __name__ == "__main__":
    import asyncio
    from ..agent.job_parser_agent import JobParserAgent
    from ..tools.user_profile import read_user_profile

    async def test_tailoring():
        # Load original resume
        profile_dict = read_user_profile("data/user_profile_resume_format.yaml")
        original_resume = convert_raw_resume_to_resume_data(profile_dict)

        # Parse job
        job_parser = JobParserAgent()
        job_result = await job_parser.parse_from_url(
            "https://www.google.com/about/careers/applications/jobs/results/115044372650566342-software-engineer-ii-ios-google-notifications"
        )

        if job_result.success:
            # Tailor resume
            tailoring_agent = ResumeTailoringAgent()
            tailored_resume = await tailoring_agent.tailor_resume(
                original_resume, job_result.job_requirements
            )

            print("Successfully tailored resume!")
            print(f"Name: {tailored_resume.candidate['name']}")
            print(f"Title: {tailored_resume.candidate['title']}")
            print(f"Summary preview: {tailored_resume.summary[:100]}...")
        else:
            print(f"Job parsing failed: {job_result.error_message}")

    # Run the test
    asyncio.run(test_tailoring())
