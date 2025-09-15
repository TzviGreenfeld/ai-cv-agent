import os
import json
import asyncio
from typing import Optional
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from pydantic import ValidationError

from ..models.job_models import JobRequirements, JobParseResult
from ..utils.job_fetcher import read_job_description
from .job_parser_prompts import JOB_PARSER_PROMPT, JOB_PARSER_SYSTEM_PROMPT

# Load environment variables
load_dotenv()


class JobParserAgent:
    """
    Agent responsible for parsing job descriptions into structured data.

    This agent can:
    1. Fetch job descriptions from URLs
    2. Parse raw job text
    3. Extract structured information using LLM
    4. Return JobRequirements objects
    """

    def __init__(self, temperature: float = 0.1):
        """
        Initialize the Job Parser Agent.

        Args:
            temperature: LLM temperature for parsing (lower = more consistent)
        """
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_AI_ENDPOINT"),
            api_key=os.getenv("AZURE_AI_API_KEY"),
            api_version=os.getenv("AZURE_AI_API_VERSION"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=temperature,  # Low temperature for consistent parsing
        )

    async def parse_from_url(self, url: str) -> JobParseResult:
        """
        Parse a job from a URL.

        Args:
            url: The job posting URL

        Returns:
            JobParseResult with parsed job or error
        """
        try:
            # Fetch job description
            job_text = await read_job_description(url)

            if not job_text:
                return JobParseResult.error_result(
                    "Failed to fetch job description from URL"
                )

            # Parse the fetched text
            return await self.parse_from_text(job_text, source_url=url)

        except Exception as e:
            return JobParseResult.error_result(f"Error fetching job from URL: {str(e)}")

    async def parse_from_text(
        self, job_text: str, source_url: Optional[str] = None
    ) -> JobParseResult:
        """
        Parse structured data from raw job text.

        Args:
            job_text: The raw job description text
            source_url: Optional URL where the job was fetched from

        Returns:
            JobParseResult with parsed job or error
        """
        try:
            # Prepare the prompt
            analysis_prompt = JOB_PARSER_PROMPT.format(job_description=job_text)

            # Get LLM response
            messages = [
                {"role": "system", "content": JOB_PARSER_SYSTEM_PROMPT},
                {"role": "user", "content": analysis_prompt},
            ]

            response = await self.llm.ainvoke(messages)
            analysis_text = response.content

            # Extract JSON from response
            json_data = self._extract_json(analysis_text)

            # Add required fields
            json_data["raw_description"] = job_text
            if source_url:
                json_data["source_url"] = source_url

            # Parse into JobRequirements model
            job_requirements = JobRequirements(**json_data)

            # Validate minimum requirements
            if not job_requirements.has_minimum_data():
                return JobParseResult.error_result(
                    "Parsed job missing minimum required data (role and description)"
                )

            return JobParseResult.success_result(job_requirements)

        except ValidationError as e:
            return JobParseResult.error_result(
                f"Failed to validate parsed data: {str(e)}"
            )
        except json.JSONDecodeError as e:
            return JobParseResult.error_result(
                f"Failed to parse JSON from LLM response: {str(e)}"
            )
        except Exception as e:
            return JobParseResult.error_result(
                f"Unexpected error during parsing: {str(e)}"
            )

    def parse_from_url_sync(self, url: str) -> JobParseResult:
        """
        Synchronous wrapper for parse_from_url.

        Args:
            url: The job posting URL

        Returns:
            JobParseResult with parsed job or error
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.parse_from_url(url))
        finally:
            loop.close()

    def parse_from_text_sync(
        self, job_text: str, source_url: Optional[str] = None
    ) -> JobParseResult:
        """
        Synchronous wrapper for parse_from_text.

        Args:
            job_text: The raw job description text
            source_url: Optional URL where the job was fetched from

        Returns:
            JobParseResult with parsed job or error
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.parse_from_text(job_text, source_url))
        finally:
            loop.close()

    def _extract_json(self, text: str) -> dict:
        """
        Extract JSON from LLM response text.

        Args:
            text: The LLM response text

        Returns:
            Parsed JSON dictionary

        Raises:
            json.JSONDecodeError: If JSON parsing fails
        """
        # Try to find JSON in code blocks first
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0].strip()
        else:
            # Try to find JSON object directly
            start_idx = text.find("{")
            end_idx = text.rfind("}")
            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx : end_idx + 1]
            else:
                json_str = text.strip()

        return json.loads(json_str)


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_parser():
        parser = JobParserAgent()

        # Test with a URL
        result = await parser.parse_from_url(
            "https://www.google.com/about/careers/applications/jobs/results/115044372650566342-software-engineer-ii-ios-google-notifications"
        )

        if result.success:
            print("Successfully parsed job!")
            print(f"Role: {result.job_requirements.role}")
            print(f"Company: {result.job_requirements.company}")
            print(f"Skills: {result.job_requirements.technical_skills}")
        else:
            print(f"Error: {result.error_message}")

    # Run the test
    asyncio.run(test_parser())
