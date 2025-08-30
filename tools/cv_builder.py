import os
from jinja2 import Environment, FileSystemLoader
from typing import Dict, List, Any, Optional


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

def generate_cv_html(resume_data: Optional[ResumeData] = None, output_path: str = "templates/resume.html") -> str:
    """Generate HTML resume from template"""
    if resume_data is None:
        raise ValueError("resume_data must be provided")

    # Setup Jinja2 environment
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('base_template.html')
    
    # Debug: Print the data structure
    data = resume_data.to_dict()
    
    # Render template
    html_content = template.render(**data)
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nResume generated successfully: {output_path}")
    return html_content


if __name__ == "__main__":
    generate_cv_html()