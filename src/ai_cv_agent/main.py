import asyncio
import logging
from pathlib import Path
from datetime import datetime

from ai_cv_agent.agent.job_parser_agent import JobParserAgent
from ai_cv_agent.agent.resume_tailoring_agent import ResumeTailoringAgent
from ai_cv_agent.utils.profile_manager import read_user_profile
from ai_cv_agent.utils.resume_mapper import convert_raw_resume_to_resume_data
from ai_cv_agent.utils.html_builder import generate_cv_html
from ai_cv_agent.utils.pdf_converter import html_to_pdf_async
from ai_cv_agent.utils.logging_setup import configure_logging, banner, step, success, fail

async def run_complete_workflow(
    job_url: str, user_profile_path: str = "data/user_profile_resume_format.yaml"
):
    banner("AI CV AGENT - COMPLETE WORKFLOW")

    # Step 1: Load user profile
    step(1, "Loading user profile")
    try:
        user_profile_dict = read_user_profile(user_profile_path)
        original_resume = convert_raw_resume_to_resume_data(user_profile_dict)
        success(f"Loaded profile: {original_resume.candidate['name']}  (Title: {original_resume.candidate['title']})")
    except Exception as e:
        fail(f"Failed to load user profile: {e}")
        return None

    # Step 2: Parse job
    step(2, "Parsing job from URL")
    logging.info(f"URL: {job_url}")
    try:
        job_parser = JobParserAgent()
        job_result = await job_parser.parse_from_url(job_url)

        if not job_result.success:
            fail(f"Failed to parse job: {job_result.error_message}")
            return None

        success("Parsed job")
        logging.info(f"Company          : {job_result.job_requirements.company}")
        logging.info(f"Role             : {job_result.job_requirements.role}")
        logging.info(f"Key requirements : {len(job_result.job_requirements.key_requirements)}")
        logging.info(f"Technical skills : {len(job_result.job_requirements.technical_skills)}")
    except Exception as e:
        fail(f"Failed to parse job: {e}")
        return None

    # Step 3: Tailor resume
    step(3, "Tailoring resume")
    try:
        tailoring_agent = ResumeTailoringAgent(temperature=0.3)
        tailored_resume = await tailoring_agent.tailor_resume(
            original_resume, job_result.job_requirements
        )
        success("Tailored resume")
        logging.info(f"Updated title    : {tailored_resume.candidate['title']}")
        logging.info(f"Summary preview  : {tailored_resume.summary[:100]}...")
    except Exception as e:
        fail(f"Failed to tailor resume: {e}")
        return None

    # Step 4: Generate HTML
    step(4, "Generating HTML")
    try:
        html_content = generate_cv_html(
            resume_data=tailored_resume,
            style_name="default",
            embed_css=True,
            use_dynamic_template=True,
        )
        success(f"Generated HTML ({len(html_content)} chars)")
    except Exception as e:
        fail(f"Failed to generate HTML: {e}")
        return None

    # Step 5: PDF export
    step(5, "Exporting PDF")
    try:
        company_clean = job_result.job_requirements.company.replace(" ", "_").replace("/", "_")
        role_clean = job_result.job_requirements.role.replace(" ", "_").replace("/", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        output_dir = Path(__file__).parent.parent.parent / "outputs" / "tailored_resumes"
        output_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = output_dir / f"{company_clean}_{role_clean}_{timestamp}.pdf"
        await html_to_pdf_async(html_content, str(pdf_path))
        success(f"Saved PDF → {pdf_path}")
        banner("WORKFLOW COMPLETED")
        return str(pdf_path)
    except Exception as e:
        fail(f"Failed to save outputs: {e}")
        return None

def main():
    configure_logging()
    test_jobs = [
        "https://www.google.com/about/careers/applications/jobs/results/115044372650566342-software-engineer-ii-ios-google-notifications",
    ]
    logging.info("AI CV Agent - Interactive Runner")
    custom_url = input("Enter a job URL (or press Enter for test): ").strip()
    job_url = custom_url or test_jobs[0]
    if not custom_url:
        logging.debug(f"Using default test URL: {job_url}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(run_complete_workflow(job_url))
        if not result:
            fail("Workflow did not complete successfully")
    except KeyboardInterrupt:
        logging.warning("Interrupted by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        loop.close()

if __name__ == "__main__":
    main()