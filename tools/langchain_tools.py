"""
LangChain-compatible tools for CV/Resume generation using artifacts.
All tools are properly documented with type hints and @tool decorators.
"""

import yaml
import asyncio
from typing import Dict, Any, Optional
from langchain.tools import tool
from langchain.tools.base import ToolException
from langchain_core.tools import StructuredTool


# Import existing modules
from tools.job_reader import read_job_description as _read_job_description
from tools.user_profile import read_user_profile as _read_user_profile
from tools.resume_parser import convert_raw_resume_to_resume_data
from tools.html_cv_builder import ResumeData, generate_cv_html as _generate_cv_html
from tools.pdf_exporter import html_to_pdf as _html_to_pdf

# @tool
# async def fetch_job_description(url: str) -> str:
#     """
#     Fetch job description from a URL.
    
#     Args:
#         url: The URL of the job posting
        
#     Returns:
#         Markdown-formatted job description content
#     """
#     try:
#         result = await _read_job_description(url)
#         print(f"Fetched job description from {url}")
#         print(result)  # Print first 500 characters for verification
#         return result
#     except Exception as e:
#         raise ToolException(f"Failed to fetch job description: {str(e)}")
@tool
def fetch_job_description(url: str) -> str:
    """
    Fetch job description from a URL.
    
    Args:
        url: The URL of the job posting
        
    Returns:
        Markdown-formatted job description content
    """
    try:
        # Handle the async call synchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(_read_job_description(url))
            return result
        finally:
            loop.close()
    except Exception as e:
        raise ToolException(f"Failed to fetch job description: {str(e)}")
    
# @tool(response_format="content_and_artifact")
@tool
def load_user_profile(profile_path: Optional[str] = "data/user_profile_resume_format.yaml") -> Dict[str, Any]:
# def load_user_profile(profile_path: Optional[str] = "data/user_profile_resume_format.yaml") -> tuple[str, Dict[str, Any]]:
    """
    Load user's professional profile from YAML file.
    
    Args:
        profile_path: Optional Path to profile YAML (defaults to data/user_profile_resume_format.yaml)

    Returns:
        User profile data dictionary
    """
    try:
        profile_data = _read_user_profile(profile_path)
        # return "User profile loaded successfully", profile_data # TODO: is this artifact?
        return profile_data
    except Exception as e:
        raise ToolException(f"Failed to load user profile: {str(e)}")

@tool(response_format="content_and_artifact")
def parse_resume_yaml(yaml_content: str) -> tuple[str, ResumeData]:
    """
    Parse YAML content into ResumeData structure.
    
    Args:
        yaml_content: YAML-formatted resume string
        
    Returns:
        Tuple of (status message, ResumeData object as artifact)
    """
    try:
        resume_dict = yaml.safe_load(yaml_content)
        resume_data = convert_raw_resume_to_resume_data(resume_dict)
        return "Resume parsed successfully", resume_data
    except Exception as e:
        raise ToolException(f"Failed to parse resume YAML: {str(e)}")

@tool(response_format="content_and_artifact")
def build_html_resume(resume_data: Dict[str, Any]) -> tuple[str, str]:
    """
    Generate HTML from resume data.
    
    Args:
        resume_data: Resume data dictionary or ResumeData object
        
    Returns:
        Tuple of (status message, HTML content as artifact)
    """
    try:
        # Convert dict to ResumeData if needed
        if isinstance(resume_data, dict):
            resume_obj = convert_raw_resume_to_resume_data(resume_data)
        else:
            resume_obj = resume_data
            
        html_content = _generate_cv_html(resume_obj)
        return "HTML resume generated successfully", html_content
    except Exception as e:
        raise ToolException(f"Failed to generate HTML: {str(e)}")

@tool
def convert_html_to_pdf(html_content: str, output_path: str) -> str:
    """
    Convert HTML content to PDF file.
    
    Args:
        html_content: HTML content to convert
        output_path: Path where PDF should be saved (e.g., outputs/resume.pdf)
        
    Returns:
        Success message with output path
    """
    try:
        _html_to_pdf(html_content, output_path)
        return f"PDF saved successfully to: {output_path}"
    except Exception as e:
        raise ToolException(f"Failed to create PDF: {str(e)}")

@tool
def save_tailoring_report(
    job_url: str, 
    job_analysis: str,
    changes_made: str,
    output_path: str
) -> str:
    """
    Save a detailed report of resume tailoring changes.
    
    Args:
        job_url: URL of the job posting
        job_analysis: Analysis of job requirements
        changes_made: Description of changes made to resume
        output_path: Path to save the report (e.g., outputs/reports/tailoring_report.txt)
        
    Returns:
        Success message with report path
    """
    try:
        from pathlib import Path
        from datetime import datetime
        from mdutils import MdUtils

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)


        mdFile = MdUtils(file_name=path.stem, title='Resume Tailoring Report')

        mdFile.new_paragraph(f"**Job URL:** {job_url}")
        mdFile.new_paragraph(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        mdFile.new_header(level=2, title="Job Analysis")
        mdFile.new_paragraph(job_analysis)

        mdFile.new_header(level=2, title="Changes Made")
        mdFile.new_paragraph(changes_made)

        mdFile.create_md_file()

        return f"Tailoring report saved to: {output_path}"
    except Exception as e:
        raise ToolException(f"Failed to save report: {str(e)}")

# Export all tools for easy import
__all__ = [
    'fetch_job_description',
    'load_user_profile',
    'parse_resume_yaml',
    'build_html_resume',
    'convert_html_to_pdf',
    'save_tailoring_report'
]
