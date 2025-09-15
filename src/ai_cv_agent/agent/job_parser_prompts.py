"""Prompts for Job Parser Agent"""

# Re-export the job analysis prompt for use in job parser
JOB_PARSER_PROMPT = """Analyze this job posting and provide a structured analysis:

Job Description:
{job_description}

Provide your analysis in this exact JSON format:
{{
    "company": "Company Name",
    "role": "Job Title",
    "key_requirements": ["requirement1", "requirement2", ...],
    "technical_skills": ["skill1", "skill2", ...],
    "soft_skills": ["skill1", "skill2", ...],
    "keywords_for_ats": ["keyword1", "keyword2", ...],
    "main_responsibilities": ["resp1", "resp2", ...],
    "nice_to_have": ["nice1", "nice2", ...]
}}

Return ONLY the JSON object, no additional text or formatting."""


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
