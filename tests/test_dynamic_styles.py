import sys
from pathlib import Path

from click import style

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_cv_agent.tools.html_cv_builder import ResumeData, generate_cv_html
from ai_cv_agent.tools.pdf_exporter import html_to_pdf


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
        github="github.com/johndoe",
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
            "Implemented CI/CD pipelines improving deployment frequency by 300%",
        ],
    )

    resume.add_job(
        title="Software Engineer",
        dates="2016 - 2020",
        company="StartupXYZ",
        description="Full-stack development for e-commerce platform",
        achievements=[
            "Developed RESTful APIs serving 1M+ daily requests",
            "Optimized database queries reducing page load time by 60%",
            "Mentored 3 junior developers on best practices",
        ],
    )

    # Add education
    resume.add_education(
        degree="B.S. Computer Science",
        graduation_date="2016",
        university="State University",
        details=["GPA: 3.8/4.0", "Dean's List", "Computer Science Club President"],
    )

    # Add skills
    resume.add_skill_category(
        "Languages", ["Python", "JavaScript", "TypeScript", "Java", "Go"]
    )
    resume.add_skill_category(
        "Frameworks", ["React", "Django", "FastAPI", "Node.js", "Spring Boot"]
    )
    resume.add_skill_category(
        "Tools & Technologies", ["Docker", "Kubernetes", "AWS", "PostgreSQL", "Redis"]
    )

    return resume


def test_external_styles(resume_data):
    #  Generate with external CSS link (not embedded)
    print("\n5. Generating resume with external CSS link...")
    try:
        html_external = generate_cv_html(
            resume_data=resume_data,
            style_name="default",
            embed_css=False,  # Use external CSS file
            use_dynamic_template=True,
        )
        output_path = Path("outputs/resume_external_css.html")
        output_path.write_text(html_external, encoding="utf-8")
        print(f"   ✓ Saved to: {output_path}")
        print("   Note: This version requires CSS files to be served separately")
        return output_path
    except Exception as e:
        print(f"   ✗ Error: {e}")


def test_backward_compatibility(resume_data):
    # Test 6: Compare with original template (backwards compatibility)
    print("\n6. Testing backwards compatibility with original template...")
    try:
        html_original = generate_cv_html(
            resume_data=resume_data,
            use_dynamic_template=False,  # Use original template with hardcoded styles
        )
        output_path = Path("outputs/resume_original_template.html")
        output_path.write_text(html_original, encoding="utf-8")
        print(f"   ✓ Saved to: {output_path}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    return output_path


def get_styles():
    path = Path("templates/styles")
    # remove the "-styles" suffix
    return [f.stem.replace("-styles", "") for f in path.glob("*.css")]


def test_embed_css(css_name, resume_data):
    """Test embedding CSS styles in the generated HTML"""
    print(f"Testing CSS embedding for: {css_name}")
    try:
        html = generate_cv_html(
            resume_data=resume_data, style_name=css_name, embed_css=True
        )
        output_path = Path(f"outputs/resume_{css_name}_embedded.html")
        output_path.write_text(html, encoding="utf-8")
        print(f"   ✓ Saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"   ✗ Error: {e}")


def make_pdfs(output_paths):
    """Convert generated HTML files to PDFs"""
    for html_path in output_paths:
        if html_path.exists():
            print(f"\nConverting {html_path} to PDF...")
            try:
                pdf_output = html_path.with_suffix(".pdf")
                html_content = html_path.read_text(encoding="utf-8")
                html_to_pdf(html_content, str(pdf_output))
                print(f"   ✓ PDF saved to: {pdf_output}")
            except Exception as e:
                print(f"   ✗ Error converting to PDF: {e}")
        else:
            print(f"\n   ✗ HTML file not found, skipping PDF conversion: {html_path}")


if __name__ == "__main__":
    styles = get_styles()
    resume_data = create_sample_resume_data()
    output_paths = []
    for style in styles:
        output_path = test_embed_css(style, resume_data)
        if output_path:
            output_paths.append(output_path)
    test_backward_compatibility(resume_data)
    test_external_styles(resume_data)

    make_pdfs(output_paths)
