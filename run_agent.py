import argparse
import asyncio
import sys

from ai_cv_agent.main import main
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the main function

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
