"""
Test script to demonstrate dynamic style loading in Jinja2 templates
"""

from pathlib import Path
from ..tools.html_cv_builder import ResumeData, generate_cv_html
from ..tools.pdf_exporter import html_to_pdf

def create_sample_resume_data():
    """Create sample resume data for testing"""
    resume = ResumeData()
    
    # Set candidate info
    resume.candidate["name"] = "John Doe"
    resume.candidate["title"] = "Senior Software Engineer"
    
    # Set summary
    resume.summary = """Experienced software engineer with 8+ years of expertise in full-stack development, 
    cloud architecture, and team leadership. Passionate about building scalable solutions and mentoring 
    junior developers."""
    
    # Set contact info
    resume.set_contact_info(
        phone="+1 (555) 123-4567",
        email="john.doe@email.com",
        linkedin="linkedin.com/in/johndoe",
        github="github.com/johndoe"
    )
    
    # Add experience
    resume.add_job(
        title="Senior Software Engineer",
        dates="2020 - Present",
        company="Tech Corp Inc.",
        description="Leading development of cloud-native applications",
        achievements=[
            "Architected and implemented microservices reducing system latency by 40%",
            "Led team of 5 engineers in delivering critical payment processing system",
            "Implemented CI/CD pipelines improving deployment frequency by 300%"
        ]
    )
    
    resume.add_job(
        title="Software Engineer",
        dates="2016 - 2020",
        company="StartupXYZ",
        description="Full-stack development for e-commerce platform",
        achievements=[
            "Developed RESTful APIs serving 1M+ daily requests",
            "Optimized database queries reducing page load time by 60%",
            "Mentored 3 junior developers on best practices"
        ]
    )
    
    # Add education
    resume.add_education(
        degree="B.S. Computer Science",
        graduation_date="2016",
        university="State University",
        details=["GPA: 3.8/4.0", "Dean's List", "Computer Science Club President"]
    )
    
    # Add skills
    resume.add_skill_category("Languages", ["Python", "JavaScript", "TypeScript", "Java", "Go"])
    resume.add_skill_category("Frameworks", ["React", "Django", "FastAPI", "Node.js", "Spring Boot"])
    resume.add_skill_category("Tools & Technologies", ["Docker", "Kubernetes", "AWS", "PostgreSQL", "Redis"])
    
    return resume

def test_dynamic_styles():
    """Test generating resumes with different styles"""
    output_paths = []
    # Create sample data
    resume_data = create_sample_resume_data()
    
    print("=" * 60)
    print("Testing Dynamic Style Loading for Jinja2 Templates")
    print("=" * 60)
    
    # Test 1: Generate with default style (embedded CSS)
    print("\n1. Generating resume with DEFAULT style (CSS embedded)...")
    try:
        html_default = generate_cv_html(
            resume_data=resume_data,
            style_name='default',
            embed_css=True,
            use_dynamic_template=True
        )
        output_path = Path("outputs/resume_default_embedded.html")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html_default, encoding='utf-8')
        print(f"   ✓ Saved to: {output_path}")
        output_paths.append(output_path)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Generate with modern style (embedded CSS)
    print("\n2. Generating resume with MODERN style (CSS embedded)...")
    try:
        html_modern = generate_cv_html(
            resume_data=resume_data,
            style_name='modern',
            embed_css=True,
            use_dynamic_template=True
        )
        output_path = Path("outputs/resume_modern_embedded.html")
        output_path.write_text(html_modern, encoding='utf-8')
        print(f"   ✓ Saved to: {output_path}")
        output_paths.append(output_path)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Generate with reversed style (embedded CSS)
    print("\n3. Generating resume with REVERSED layout style (CSS embedded)...")
    try:
        html_reversed = generate_cv_html(
            resume_data=resume_data,
            style_name='reversed',
            embed_css=True,
            use_dynamic_template=True
        )
        output_path = Path("outputs/resume_reversed_embedded.html")
        output_path.write_text(html_reversed, encoding='utf-8')
        print(f"   ✓ Saved to: {output_path}")
        print("   Note: Skills/Contact on left, Experience/Education on right")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Generate with external CSS link (not embedded)
    print("\n4. Generating resume with external CSS link...")
    try:
        html_external = generate_cv_html(
            resume_data=resume_data,
            style_name='default',
            embed_css=False,  # Use external CSS file
            use_dynamic_template=True
        )
        output_path = Path("outputs/resume_external_css.html")
        output_path.write_text(html_external, encoding='utf-8')
        print(f"   ✓ Saved to: {output_path}")
        print("   Note: This version requires CSS files to be served separately")
        output_paths.append(output_path)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 5: Compare with original template (backwards compatibility)
    print("\n5. Testing backwards compatibility with original template...")
    try:
        html_original = generate_cv_html(
            resume_data=resume_data,
            use_dynamic_template=False  # Use original template with hardcoded styles
        )
        output_path = Path("outputs/resume_original_template.html")
        output_path.write_text(html_original, encoding='utf-8')
        print(f"   ✓ Saved to: {output_path}")
        output_paths.append(output_path)
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("- Dynamic style loading allows switching between themes")
    print("- Available themes: default, modern, reversed")
    print("- CSS can be embedded (standalone HTML) or linked (requires CSS files)")
    print("- Original template still works for backwards compatibility")
    print("- Check the 'outputs' folder to see the generated HTML files")
    print("=" * 60)

    for path in output_paths:
        if path.exists():
            print(f"   ✓ Found: {path}")
        else:
            print(f"   ✗ Not found: {path}")
    return output_paths


def make_pdfs(output_paths, output_path):
    """Convert generated HTML files to PDFs"""
    for html_path in output_paths:
        if html_path.exists():
            print(f"\nConverting {html_path} to PDF...")
            try:
                pdf_output = html_path.with_suffix('.pdf')
                html_content = html_path.read_text(encoding='utf-8')
                html_to_pdf(html_content, str(pdf_output))
                print(f"   ✓ PDF saved to: {pdf_output}")
            except Exception as e:
                print(f"   ✗ Error converting to PDF: {e}")
        else:
            print(f"\n   ✗ HTML file not found, skipping PDF conversion: {html_path}")
    html_to_pdf(html_content, output_path)

if __name__ == "__main__":
    output_paths = test_dynamic_styles()
    make_pdfs(output_paths, Path("outputs/resume.pdf"))
