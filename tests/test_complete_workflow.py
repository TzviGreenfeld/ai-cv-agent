"""
Complete Workflow Test for AI CV Agent

This test demonstrates the full pipeline:
1. User inputs a job URL
2. Job parser creates JobParseResult from URL (LLM)
3. Resume tailoring agent creates new YAML based on job requirements (LLM)
4. YAML is mapped to ResumeData (no LLM)
5. ResumeData is converted to HTML, then PDF, then saved (no LLM)
"""

import sys
import yaml
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ai_cv_agent.agent.job_parser_agent import JobParserAgent
from ai_cv_agent.agent.resume_tailoring_agent import ResumeTailoringAgent
from ai_cv_agent.tools.user_profile import read_user_profile
from ai_cv_agent.tools.resume_parser import convert_raw_resume_to_resume_data
from ai_cv_agent.tools.html_cv_builder import generate_cv_html
from ai_cv_agent.tools.pdf_exporter import html_to_pdf_async


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
    print("=" * 60)
    print("AI CV AGENT - COMPLETE WORKFLOW")
    print("=" * 60)

    # Step 1: Load user profile
    print("\n[Step 1] Loading user profile...")
    try:
        user_profile_dict = read_user_profile(user_profile_path)
        original_resume = convert_raw_resume_to_resume_data(user_profile_dict)
        print(f"✓ Loaded profile for: {original_resume.candidate['name']}")
        print(f"  Current title: {original_resume.candidate['title']}")
    except Exception as e:
        print(f"✗ Failed to load user profile: {e}")
        return None

    # Step 2: Parse job from URL
    print("\n[Step 2] Parsing job from URL...")
    print(f"  URL: {job_url}")
    try:
        job_parser = JobParserAgent()
        job_result = await job_parser.parse_from_url(job_url)

        if not job_result.success:
            print(f"✗ Failed to parse job: {job_result.error_message}")
            return None

        print("✓ Successfully parsed job:")
        print(f"  Company: {job_result.job_requirements.company}")
        print(f"  Role: {job_result.job_requirements.role}")
        print(
            f"  Key requirements: {len(job_result.job_requirements.key_requirements)} items"
        )
        print(
            f"  Technical skills: {len(job_result.job_requirements.technical_skills)} items"
        )
    except Exception as e:
        print(f"✗ Failed to parse job: {e}")
        return None

    # Step 3: Tailor resume using AI
    print("\n[Step 3] Tailoring resume to job requirements...")
    try:
        tailoring_agent = ResumeTailoringAgent(temperature=0.3)
        tailored_resume = await tailoring_agent.tailor_resume(
            original_resume, job_result.job_requirements
        )
        print("✓ Successfully tailored resume")
        print(f"  New title: {tailored_resume.candidate['title']}")
        print(f"  Summary preview: {tailored_resume.summary[:100]}...")
    except Exception as e:
        print(f"✗ Failed to tailor resume: {e}")
        return None

    # Step 4: Generate HTML
    print("\n[Step 4] Generating HTML...")
    try:
        html_content = generate_cv_html(
            resume_data=tailored_resume,
            style_name="classic",
            embed_css=True,
            use_dynamic_template=True,
        )
        print(f"✓ Generated HTML ({len(html_content)} characters)")
    except Exception as e:
        print(f"✗ Failed to generate HTML: {e}")
        return None

    # Step 5: Convert to PDF and save
    print("\n[Step 5] Converting to PDF and saving...")
    try:
        # Create output filename with company and role
        company_clean = job_result.job_requirements.company.replace(" ", "_").replace(
            "/", "_"
        )
        role_clean = job_result.job_requirements.role.replace(" ", "_").replace(
            "/", "_"
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")

        output_dir = Path("outputs/tailored_resumes")
        output_dir.mkdir(parents=True, exist_ok=True)

        pdf_path = output_dir / f"{company_clean}_{role_clean}_{timestamp}.pdf"

        await html_to_pdf_async(html_content, str(pdf_path))
        print(f"✓ Saved PDF: {pdf_path}")

        # Also save the tailored YAML for reference
        yaml_path = output_dir / f"{company_clean}_{role_clean}_{timestamp}.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(tailored_resume.to_dict(), f, default_flow_style=False)
        print(f"✓ Saved YAML: {yaml_path}")

        # Save a report with the changes
        report_path = (
            output_dir / f"{company_clean}_{role_clean}_{timestamp}_report.txt"
        )
        with open(report_path, "w") as f:
            f.write("CV TAILORING REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Job URL: {job_url}\n")
            f.write(f"Company: {job_result.job_requirements.company}\n")
            f.write(f"Role: {job_result.job_requirements.role}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("KEY REQUIREMENTS ADDRESSED:\n")
            for req in job_result.job_requirements.key_requirements[:5]:
                f.write(f"  • {req}\n")
            f.write("\nTECHNICAL SKILLS EMPHASIZED:\n")
            for skill in job_result.job_requirements.technical_skills[:10]:
                f.write(f"  • {skill}\n")
            f.write("\nATS KEYWORDS INCORPORATED:\n")
            for keyword in job_result.job_requirements.keywords_for_ats[:10]:
                f.write(f"  • {keyword}\n")
        print(f"✓ Saved report: {report_path}")

        return str(pdf_path)

    except Exception as e:
        print(f"✗ Failed to save outputs: {e}")
        return None


def main():
    """Main function to run the workflow with example job URLs."""

    # Example job URLs (you can change these)
    test_jobs = [
        # Add your test job URL here
        "https://www.google.com/about/careers/applications/jobs/results/115044372650566342-software-engineer-ii-ios-google-notifications",
    ]

    print("Welcome to AI CV Agent - Complete Workflow Test")
    print("-" * 60)

    # Check if user wants to input a custom URL
    custom_url = input("\nEnter a job URL (or press Enter to use test URL): ").strip()

    if custom_url:
        job_url = custom_url
    else:
        job_url = test_jobs[0]
        print(f"Using test URL: {job_url}")

    # Run the workflow
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        result = loop.run_until_complete(run_complete_workflow(job_url))

        if result:
            print("\n" + "=" * 60)
            print("SUCCESS! Workflow completed successfully.")
            print(f"Output saved to: {result}")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("FAILED: Workflow did not complete successfully.")
            print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
