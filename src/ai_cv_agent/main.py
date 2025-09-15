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

logging.basicConfig(level=logging.INFO)

async def run_complete_workflow(
    job_url: str, user_profile_path: str = "data/user_profile_resume_format.yaml"
):
    """
    Run the complete CV tailoring workflow.

    Args:
        job_url: URL of the job posting
        user_profile_path: Path to user's resume YAML file

    Returns:
        Path to the generated PDF file
    """
    logging.info("=" * 60)
    logging.info("AI CV AGENT - COMPLETE WORKFLOW")
    logging.info("=" * 60)

    # Step 1: Load user profile
    logging.info("\n[Step 1] Loading user profile...")
    try:
        user_profile_dict = read_user_profile(user_profile_path)
        original_resume = convert_raw_resume_to_resume_data(user_profile_dict)
        logging.info(f"Loaded profile for: {original_resume.candidate['name']}")
        logging.info(f"Current title: {original_resume.candidate['title']}")
    except Exception as e:
        logging.error(f"✗ Failed to load user profile: {e}")
        return None

    # Step 2: Parse job from URL
    logging.info("\n[Step 2] Parsing job from URL...")
    logging.info(f"  URL: {job_url}")
    try:
        job_parser = JobParserAgent()
        job_result = await job_parser.parse_from_url(job_url)

        if not job_result.success:
            logging.error(f"✗ Failed to parse job: {job_result.error_message}")
            return None

        logging.info("✓ Successfully parsed job:")
        logging.info(f"  Company: {job_result.job_requirements.company}")
        logging.info(f"  Role: {job_result.job_requirements.role}")
        logging.info(
            f"  Key requirements: {len(job_result.job_requirements.key_requirements)} items"
        )
        logging.info(
            f"  Technical skills: {len(job_result.job_requirements.technical_skills)} items"
        )
    except Exception as e:
        logging.error(f"✗ Failed to parse job: {e}")
        return None

    # Step 3: Tailor resume using AI
    logging.info("\n[Step 3] Tailoring resume to job requirements...")
    try:
        tailoring_agent = ResumeTailoringAgent(temperature=0.3)
        tailored_resume = await tailoring_agent.tailor_resume(
            original_resume, job_result.job_requirements
        )
        logging.info("✓ Successfully tailored resume")
        logging.info(f"  New title: {tailored_resume.candidate['title']}")
        logging.info(f"  Summary preview: {tailored_resume.summary[:100]}...")
    except Exception as e:
        logging.error(f"✗ Failed to tailor resume: {e}")
        return None

    # Step 4: Generate HTML
    logging.info("\n[Step 4] Generating HTML...")
    try:
        html_content = generate_cv_html(
            resume_data=tailored_resume,
            style_name="default",
            embed_css=True,
            use_dynamic_template=True,
        )
        logging.info(f"✓ Generated HTML ({len(html_content)} characters)")
    except Exception as e:
        logging.error(f"✗ Failed to generate HTML: {e}")
        return None

    # Step 5: Convert to PDF and save
    logging.info("\n[Step 5] Converting to PDF and saving...")
    try:
        # Create output filename with company and role
        company_clean = job_result.job_requirements.company.replace(" ", "_").replace(
            "/", "_"
        )
        role_clean = job_result.job_requirements.role.replace(" ", "_").replace(
            "/", "_"
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        # output_dir = Path("outputs/tailored_resumes")
        output_dir = Path(__file__).parent.parent.parent / "outputs" / "tailored_resumes"
        output_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = output_dir / f"{company_clean}_{role_clean}_{timestamp}.pdf"

        await html_to_pdf_async(html_content, str(pdf_path))
        logging.info(f"✓ Saved PDF: {pdf_path}")

        return str(pdf_path)

    except Exception as e:
        logging.error(f"✗ Failed to save outputs: {e}")
        return None


def main():
    test_jobs = [
        "https://www.google.com/about/careers/applications/jobs/results/115044372650566342-software-engineer-ii-ios-google-notifications",
    ]

    logging.info("AI CV Agent - Complete Workflow")
    logging.info("-" * 60)

    # Check if user wants to input a custom URL
    custom_url = input("\nEnter a job URL (or press Enter to use test URL): ").strip()

    if custom_url:
        job_url = custom_url
    else:
        job_url = test_jobs[0]
        logging.info(f"Using test URL: {job_url}")

    # Run the workflow
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(run_complete_workflow(job_url))

        if result:
            logging.info("\n" + "=" * 60)
            logging.info("completed successfully.")
            logging.info(f"Output saved to: {result}")
            logging.info("=" * 60)
        else:
            logging.info("\n" + "=" * 60)
            logging.error("FAILED: Workflow did not complete successfully.")
            logging.info("=" * 60)

    except KeyboardInterrupt:
        logging.info("\n\nWorkflow interrupted by user.")
    except Exception as e:
        logging.info(f"\n\nUnexpected error: {e}")
    finally:
        loop.close()




if __name__ == "__main__":
    main()
