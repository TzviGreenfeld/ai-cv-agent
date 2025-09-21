"""Example script demonstrating LangGraph workflow usage"""

import asyncio
from pathlib import Path

from ai_cv_agent.graph import run_workflow


async def main():
    """Run the LangGraph workflow with a sample job URL"""

    # Example job URL (you can replace with any job posting)
    job_url = "https://moovit.com/careers/co/rd/CF.B5A/junior-java-developer/"

    # Optional: specify custom profile and style
    # profile_path = "data/custom_profile.yaml"
    # style = "modern"

    try:
        print("🚀 Starting LangGraph workflow...")
        print(f"📋 Processing job: {job_url}")
        print("⏳ This may take a few moments...\n")

        # Run the workflow with default settings
        pdf_path = await run_workflow(job_url)

        # Or with custom settings:
        # pdf_path = await run_workflow(
        #     job_url=job_url,
        #     user_profile_path=profile_path,
        #     style_name=style
        # )

        print(f"\n✅ Success! Resume generated at:")
        print(f"   {pdf_path}")
        print(f"\n📂 You can find it in: {Path(pdf_path).parent}")

    except RuntimeError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
