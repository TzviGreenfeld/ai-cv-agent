"""Prompts for Job Parser Agent"""

from .prompts import JOB_ANALYSIS_PROMPT

# Re-export the job analysis prompt for use in job parser
JOB_PARSER_PROMPT = JOB_ANALYSIS_PROMPT

# Additional prompt for cleaning/extracting job text if needed
JOB_TEXT_EXTRACTION_PROMPT = """Extract the main job description text from the following content. 
Remove any navigation elements, ads, or unrelated content.
Focus only on the job title, company, requirements, and responsibilities.

Content:
{content}

Return only the cleaned job description text."""

# System prompt for the job parser agent
JOB_PARSER_SYSTEM_PROMPT = """You are an expert job posting analyzer. 
Your role is to extract structured information from job descriptions.

Key guidelines:
1. Extract all relevant information accurately
2. Categorize skills and requirements appropriately
3. Identify ATS keywords that candidates should include
4. If information is not found, leave the field empty
5. Always provide the output in the exact JSON format requested

Focus on being precise and comprehensive in your analysis."""
