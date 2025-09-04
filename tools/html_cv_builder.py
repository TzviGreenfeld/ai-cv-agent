import os
from jinja2 import Environment, FileSystemLoader
from typing import Dict, List, Any, Optional
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

SAVE_ARTIFACTS = os.getenv("DEBUG", "false").lower() == "true"

class ResumeData:
    """Data structure for resume information"""
    
    def __init__(self):
        self.candidate = {
            "name": "",
            "title": ""
        }
        self.summary = ""
        self.contact = []
        self.experience = []
        self.education = []
        self.skills = []
    
    def add_job(self, title: str, dates: str, company: str, 
                description: Optional[str] = None, achievements: Optional[List[str]] = None):
        """Add a job entry to experience"""
        job = {
            "title": title,
            "dates": dates,
            "company": company,
            "description": description,
            "achievements": achievements or []
        }
        self.experience.append(job)
    
    def add_education(self, degree: str, graduation_date: str, university: str, 
                     details: Optional[List[str]] = None):
        """Add an education entry"""
        edu = {
            "degree": degree,
            "graduation_date": graduation_date,
            "university": university,
            "details": details or []
        }
        self.education.append(edu)
    
    def add_skill_category(self, name: str, items: List[str]):
        """Add a skill category"""
        skill_cat = {
            "name": name,
            "skills": items
        }
        self.skills.append(skill_cat)
    
    def set_contact_info(self, phone: str, email: str, linkedin: str, github: str):
        """Set contact information"""
        self.contact = [phone, email, linkedin, github]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template rendering"""
        return {
            "candidate": self.candidate,
            "summary": self.summary,
            "contact": self.contact,
            "experience": self.experience,
            "education": self.education,
            "skills": self.skills
        }
    
def get_html_template():
    # Setup Jinja2 environment
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('base_template.html')
    return template

def save_html_to_file(html_content: str, output_path: str = "templates/resume.html"):
    """Save HTML content to a file"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_content, encoding='utf-8')
    print(f"\nHTML generated successfully: {output_path}")


def generate_cv_html(resume_data: ResumeData = None) -> str:
    """Generate HTML resume from template"""
    if resume_data is None:
        raise ValueError("resume_data must be provided")

    template = get_html_template()

    # Debug: Print the data structure
    data = resume_data.to_dict()
    
    # Render template
    html_content = template.render(**data)

    if SAVE_ARTIFACTS:
        save_html_to_file(html_content)

    return html_content


if __name__ == "__main__":
    generate_cv_html()