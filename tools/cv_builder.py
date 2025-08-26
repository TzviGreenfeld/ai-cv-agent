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

def get_mock_data() -> ResumeData:
    """Generate mock resume data"""
    resume = ResumeData()
    resume.candidate["name"] = "John Doe"
    resume.candidate["title"] = "Software Engineer"
    resume.summary = "Passionate software engineer with 5+ years of experience."
    resume.set_contact_info(
        phone="(123) 456-7890",
        email="john.doe@example.com",
        linkedin="linkedin.com/in/johndoe",
        github="github.com/johndoe"
    )
    resume.add_job(
        title="Senior Software Engineer",
        dates="01/2020 – Present",
        company="Tech Company",
        description="Lead a team of developers to build scalable web applications.",
        achievements=[
            "Implemented a microservices architecture.",
            "Reduced page load time by 30%."
        ]
    )
    resume.add_education(
        degree="Bachelor of Science in Computer Science",
        graduation_date="05/2018",
        university="University of Example",
        details=["GPA: 3.8/4.0"]
    )
    resume.add_skill_category(
        name="Programming Languages",
        items=["Python", "JavaScript", "Java"]
    )
    resume.add_skill_category(
        name="Frameworks",
        items=["React", "Django", "Spring Boot"]
    )
    resume.add_skill_category(
        name="Tools",
        items=["Git", "Docker", "AWS"]
    )
    return resume

def generate_cv_html(resume_data: Optional[ResumeData] = None, output_path: str = "templates/resume.html") -> str:
    """Generate HTML resume from template"""
    if resume_data is None:
        resume_data = get_mock_data()

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