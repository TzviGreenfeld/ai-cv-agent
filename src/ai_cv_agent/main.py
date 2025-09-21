"""Main module for AI CV Agent using LangGraph workflow"""

import asyncio
import argparse
from pathlib import Path

from ai_cv_agent.graph import run_workflow

async def main(job_url: str, user_profile_path: str = "data/user_profile_resume_format.yaml", style_name: str = "default"):
    """Run the CV tailoring workflow"""
    try:
        print(f"🚀 Starting AI CV Agent workflow...")
        print(f"📋 Job URL: {job_url}")
        print(f"👤 Profile: {user_profile_path}")
        print(f"🎨 Style: {style_name}")
        print()
        
        # Run the workflow
        pdf_path = await run_workflow(job_url, user_profile_path, style_name)
        
        print(f"\n✅ Success! Resume generated at: {pdf_path}")
        return pdf_path
        
    except RuntimeError as e:
        print(f"\n❌ Workflow failed: {e}")
        raise
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        raise

def run():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI CV Agent - Tailor your resume to job postings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default profile
  python -m ai_cv_agent.main "https://example.com/job-posting"
  
  # Use custom profile
  python -m ai_cv_agent.main "https://example.com/job-posting" --profile data/custom_profile.yaml
  
  # Use different style
  python -m ai_cv_agent.main "https://example.com/job-posting" --style modern
        """
    )
    
    parser.add_argument("job_url", help="URL of the job posting to tailor resume for")
    parser.add_argument(
        "--profile", 
        "-p",
        default="data/user_profile_resume_format.yaml",
        help="Path to user profile YAML (default: data/user_profile_resume_format.yaml)"
    )
    parser.add_argument(
        "--style",
        "-s",
        default="default",
        choices=["default", "modern", "classic", "reversed"],
        help="CSS style for the resume (default: default)"
    )
    
    args = parser.parse_args()
    
    # Run the async main function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            main(args.job_url, args.profile, args.style)
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    finally:
        loop.close()

if __name__ == "__main__":
    run()
