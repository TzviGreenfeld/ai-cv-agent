# tool_tester.py
"""
Simple tool tester.
Edit the TOOL_NAME and PARAMS below to run any tool directly.
"""

# --- Import your tools ---
# from tools.job_reader import read_job_description
from tools.user_profile import read_user_profile
from tools.cv_builder import generate_cv_html
from tools.pdf_exporter import html_file_to_pdf

# --- Pick which tool to run ---
PARAMS = {
    # Example params:
    # "url": "https://example.com/job"
    # "file_path": "data/user_profile.yaml"
    # "template_path": "templates/base_template.html", "content": {"name": "Tzvi"}
    # "html": "<h1>Hello</h1>", "output_path": "outputs/test.pdf"
    "html_file_path": "templates/resume_template.html"
}

# --- Tool mapping ---
TOOLS = {
    # "read_job_description": read_job_description,
    "read_user_profile": read_user_profile,
    "generate_cv_html": generate_cv_html,
    "html_file_to_pdf": html_file_to_pdf
}

TOOL_NAME = "html_file_to_pdf"   # e.g. "read_job_description", "generate_cv_html"
def run_tool():
    if TOOL_NAME not in TOOLS:
        raise ValueError(f"Unknown tool: {TOOL_NAME}. Choose from {list(TOOLS.keys())}")
    
    tool_func = TOOLS[TOOL_NAME]
    result = tool_func(**PARAMS) if PARAMS else tool_func()
    
    print(type(result))
    print(f"\n✅ Result from {TOOL_NAME}:")
    print(result)

if __name__ == "__main__":
    run_tool()
