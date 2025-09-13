"""Job-related data models for AI CV Agent"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class JobRequirements(BaseModel):
    """
    Structured representation of a job posting.
    
    This model matches the output format of JOB_ANALYSIS_PROMPT
    and includes both required and optional fields.
    """
    
    # Required fields
    role: str = Field(..., description="Job title/position")
    raw_description: str = Field(..., description="Original job description text")
    
    # Optional fields (from JOB_ANALYSIS_PROMPT)
    company: Optional[str] = Field(None, description="Company name")
    key_requirements: List[str] = Field(default_factory=list, description="Key job requirements")
    technical_skills: List[str] = Field(default_factory=list, description="Required technical skills")
    soft_skills: List[str] = Field(default_factory=list, description="Required soft skills")
    keywords_for_ats: List[str] = Field(default_factory=list, description="Keywords for ATS optimization")
    main_responsibilities: List[str] = Field(default_factory=list, description="Main job responsibilities")
    nice_to_have: List[str] = Field(default_factory=list, description="Nice to have qualifications")
    
    # Metadata
    source_url: Optional[str] = Field(None, description="URL where job was fetched from")
    parsed_at: datetime = Field(default_factory=datetime.now, description="When the job was parsed")
    
    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
    
    def has_minimum_data(self) -> bool:
        """Check if the job has minimum required data."""
        return bool(self.role and self.raw_description)
    
    def get_all_keywords(self) -> List[str]:
        """Get all keywords combining ATS keywords and skills."""
        return list(set(
            self.keywords_for_ats + 
            self.technical_skills + 
            self.soft_skills
        ))
    
    def to_analysis_dict(self) -> dict:
        """
        Convert to dictionary format expected by existing prompts.
        Excludes raw_description and metadata fields.
        """
        return {
            "company": self.company,
            "role": self.role,
            "key_requirements": self.key_requirements,
            "technical_skills": self.technical_skills,
            "soft_skills": self.soft_skills,
            "keywords_for_ats": self.keywords_for_ats,
            "main_responsibilities": self.main_responsibilities,
            "nice_to_have": self.nice_to_have
        }


class JobParseResult(BaseModel):
    """Result of job parsing operation"""
    success: bool
    job_requirements: Optional[JobRequirements] = None
    error_message: Optional[str] = None
    
    @classmethod
    def success_result(cls, job_requirements: JobRequirements) -> "JobParseResult":
        """Create a successful parse result."""
        return cls(success=True, job_requirements=job_requirements)
    
    @classmethod
    def error_result(cls, error_message: str) -> "JobParseResult":
        """Create an error parse result."""
        return cls(success=False, error_message=error_message)
