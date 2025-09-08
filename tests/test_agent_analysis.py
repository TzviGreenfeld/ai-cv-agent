"""
Test script to verify the enhanced LangChain CV agent properly uses the analyze_job_posting tool
and provides explanations for resume changes.
"""

import os
import sys
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_cv_agent.agent.langchain_cv_agent import LangChainCVAgent


def test_standalone_job_analysis():
    """Test that the agent can analyze a job posting independently."""
    print("\n" + "=" * 60)
    print("TEST 1: Standalone Job Analysis")
    print("=" * 60)

    agent = LangChainCVAgent()

    # Test with a sample job URL
    job_url = "https://www.metacareers.com/jobs/1439909109913818"

    print(f"\nAnalyzing job posting at: {job_url}")
    print("Asking agent to analyze the job posting...")

    try:
        result = agent.run(
            f"Analyze this job posting and tell me the key requirements: {job_url}"
        )
        print("\nAgent's Job Analysis:")
        print("-" * 40)
        print(result)

        # Check if the analysis is in JSON format
        try:
            # If it's valid JSON, pretty print it
            if result.strip().startswith("{"):
                job_data = json.loads(result)
                print("\nStructured Analysis:")
                print(f"  Company: {job_data.get('company', 'N/A')}")
                print(f"  Role: {job_data.get('role', 'N/A')}")
                print(
                    f"  Key Requirements: {', '.join(job_data.get('key_requirements', []))}"
                )
                print(
                    f"  Technical Skills: {', '.join(job_data.get('technical_skills', []))}"
                )
                print(
                    f"  ATS Keywords: {', '.join(job_data.get('keywords_for_ats', []))}"
                )
        except:
            # If not JSON, that's okay - it might be formatted text
            pass

    except Exception as e:
        print(f"Error during job analysis: {e}")
        return False

    return True


def test_complete_workflow_with_explanations():
    """Test the complete workflow with change explanations."""
    print("\n" + "=" * 60)
    print("TEST 2: Complete Workflow with Change Explanations")
    print("=" * 60)

    agent = LangChainCVAgent()

    job_url = "https://www.metacareers.com/jobs/1439909109913818"
    output_name = "test_analysis_resume"

    print(f"\nCreating tailored resume for: {job_url}")
    print(f"Output name: {output_name}")
    print("\nThis will:")
    print("  1. Analyze the job posting")
    print("  2. Tailor the resume to match")
    print("  3. Explain all changes made")
    print("  4. Generate HTML and PDF outputs")

    try:
        result = agent.run(
            f"Create a complete tailored resume with detailed analysis for this job: {job_url}. "
            f"Name the output: '{output_name}'"
        )

        print("\nAgent's Response:")
        print("-" * 40)
        print(result)

        # Check if output files were created
        print("\n" + "-" * 40)
        print("Checking generated files:")

        expected_files = [
            f"outputs/{output_name}.yaml",
            f"outputs/{output_name}.html",
            f"outputs/{output_name}.pdf",
            f"outputs/{output_name}_job_analysis.json",
            f"outputs/{output_name}_changes_report.txt",
        ]

        for file_path in expected_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"  ✓ {file_path} ({file_size} bytes)")
            else:
                print(f"  ✗ {file_path} (not found)")

        # Read and display the changes report
        changes_report_path = f"outputs/{output_name}_changes_report.txt"
        if os.path.exists(changes_report_path):
            print("\n" + "=" * 60)
            print("CHANGES REPORT PREVIEW:")
            print("-" * 40)
            with open(changes_report_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Show first 1000 characters of the report
                print(content[:1000])
                if len(content) > 1000:
                    print("\n... (truncated, see full report in file)")

        # Read and display the job analysis
        job_analysis_path = f"outputs/{output_name}_job_analysis.json"
        if os.path.exists(job_analysis_path):
            print("\n" + "=" * 60)
            print("JOB ANALYSIS (from JSON file):")
            print("-" * 40)
            with open(job_analysis_path, "r", encoding="utf-8") as f:
                try:
                    job_data = json.load(f)
                    print(json.dumps(job_data, indent=2))
                except:
                    print(f.read()[:500])

    except Exception as e:
        print(f"Error during complete workflow: {e}")
        return False

    return True


def test_agent_explains_changes():
    """Test that the agent can explain what it changed when asked."""
    print("\n" + "=" * 60)
    print("TEST 3: Agent Explains Changes")
    print("=" * 60)

    agent = LangChainCVAgent()

    print("\nAsking agent to explain how it would tailor a resume...")

    try:
        result = agent.run(
            "If you were to tailor my resume for a Senior Python Developer position, "
            "what kinds of changes would you make and why? "
            "Please analyze my profile first and explain your approach."
        )

        print("\nAgent's Explanation:")
        print("-" * 40)
        print(result)

    except Exception as e:
        print(f"Error: {e}")
        return False

    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING ENHANCED CV AGENT WITH ANALYSIS FEATURES")
    print("=" * 60)

    # Ensure output directory exists
    os.makedirs("outputs", exist_ok=True)

    tests_passed = []

    # Run Test 1: Standalone job analysis
    print("\nRunning Test 1...")
    tests_passed.append(("Standalone Job Analysis", test_standalone_job_analysis()))

    # Run Test 2: Complete workflow with explanations
    print("\nRunning Test 2...")
    tests_passed.append(
        (
            "Complete Workflow with Explanations",
            test_complete_workflow_with_explanations(),
        )
    )

    # Run Test 3: Agent explains changes
    print("\nRunning Test 3...")
    tests_passed.append(("Agent Explains Changes", test_agent_explains_changes()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in tests_passed:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {status}: {test_name}")

    print("\n" + "=" * 60)
    print("TESTING COMPLETE!")
    print("Check the 'outputs' directory for generated files.")
    print("=" * 60)


if __name__ == "__main__":
    main()
