"""
Resume YAML Parser using Pydantic for robust validation and parsing.
Converts YAML data to the existing ResumeData class structure.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
import yaml
from pathlib import Path
from tools.cv_builder import ResumeData


class CandidateModel(BaseModel):
    """Model for candidate information"""
    name: str = "Unknown"
    title: str = "Professional"


class ExperienceModel(BaseModel):
    """Model for job experience entries"""
    title: str = "Position"
    dates: str = ""
    company: str = "Company"
    description: Optional[str] = None
    achievements: List[str] = Field(default_factory=list)


class EducationModel(BaseModel):
    """Model for education entries"""
    degree: str = "Degree"
    graduation_date: str = ""
    university: str = "University"
    details: List[str] = Field(default_factory=list)


class SkillCategoryModel(BaseModel):
    """Model for skill categories"""
    name: str = "General"
    skills: List[str] = Field(default_factory=list)


class ResumeYAMLModel(BaseModel):
    """Main model for the complete resume YAML structure"""
    candidate: CandidateModel = Field(default_factory=CandidateModel)
    summary: str = ""
    contact: List[str] = Field(default_factory=lambda: ["", "", "", ""])
    experience: List[ExperienceModel] = Field(default_factory=list)
    education: List[EducationModel] = Field(default_factory=list)
    skills: List[SkillCategoryModel] = Field(default_factory=list)
    
    @validator('contact', pre=True)
    def validate_contact(cls, v):
        """Ensure contact list has exactly 4 items"""
        if isinstance(v, list):
            # Pad with empty strings if too short
            v = v + [''] * (4 - len(v))
            # Truncate if too long
            return v[:4]
        elif isinstance(v, dict):
            # Convert dict format to list format
            return [
                v.get('phone', ''),
                v.get('email', ''),
                v.get('linkedin', ''),
                v.get('github', '')
            ]
        return ['', '', '', '']
    
    class Config:
        # Allow extra fields without raising errors
        extra = 'ignore'


def load_yaml_to_resume_data(yaml_path: str) -> ResumeData:
    """
    Load YAML file and convert to ResumeData instance.
    
    Args:
        yaml_path: Path to the YAML file
        
    Returns:
        ResumeData instance populated with the YAML data
        
    Raises:
        FileNotFoundError: If the YAML file doesn't exist
        yaml.YAMLError: If the YAML is malformed
        ValidationError: If the data doesn't match expected structure
    """
    # Check if file exists
    if not Path(yaml_path).exists():
        raise FileNotFoundError(f"YAML file not found: {yaml_path}")
    
    # Load YAML data
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            raw_data = yaml.safe_load(f)
            if raw_data is None:
                raw_data = {}
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file: {e}")
    
    # Parse with Pydantic model (handles validation and defaults)
    try:
        model = ResumeYAMLModel(**raw_data)
    except Exception as e:
        # Provide helpful error message
        raise ValueError(f"Error validating resume data: {e}")
    
    # Convert to ResumeData instance
    resume = ResumeData()
    
    # Set candidate info
    resume.candidate['name'] = model.candidate.name
    resume.candidate['title'] = model.candidate.title
    
    # Set summary
    resume.summary = model.summary
    
    # Set contact info (already validated to have 4 items)
    resume.contact = model.contact
    
    # Add experience entries
    for job in model.experience:
        resume.add_job(
            title=job.title,
            dates=job.dates,
            company=job.company,
            description=job.description,
            achievements=job.achievements
        )
    
    # Add education entries
    for edu in model.education:
        resume.add_education(
            degree=edu.degree,
            graduation_date=edu.graduation_date,
            university=edu.university,
            details=edu.details
        )
    
    # Add skill categories
    for skill_cat in model.skills:
        resume.add_skill_category(
            name=skill_cat.name,
            items=skill_cat.skills
        )
    
    return resume


def load_yaml_safe(yaml_path: str, default_on_error: bool = True) -> Optional[ResumeData]:
    """
    Safely load YAML with error handling.
    
    Args:
        yaml_path: Path to the YAML file
        default_on_error: If True, return empty ResumeData on error; if False, return None
        
    Returns:
        ResumeData instance or None if error and default_on_error is False
    """
    try:
        return load_yaml_to_resume_data(yaml_path)
    except Exception as e:
        print(f"Error loading resume from {yaml_path}: {e}")
        if default_on_error:
            return ResumeData()
        return None


# Example usage and testing
if __name__ == "__main__":
    # Test with the created YAML file
    try:
        resume = load_yaml_to_resume_data("../data/user_profile_resume_format.yaml")
        print("Successfully loaded resume:")
        print(f"Name: {resume.candidate['name']}")
        print(f"Title: {resume.candidate['title']}")
        print(f"Summary: {resume.summary[:50]}...")
        print(f"Number of jobs: {len(resume.experience)}")
        print(f"Number of education entries: {len(resume.education)}")
        print(f"Number of skill categories: {len(resume.skills)}")
    except Exception as e:
        print(f"Error: {e}")
