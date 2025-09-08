# AI CV Agent - Memory Bank

## Project Overview
AI-powered CV/Resume tailoring system that intelligently adapts resumes to specific job descriptions using LangChain and Azure OpenAI.

### Core Purpose
- Fetch job descriptions from URLs
- Load user profiles from YAML files
- Use AI to tailor resumes to match job requirements
- Generate ATS-optimized HTML/PDF outputs
- Create detailed reports of changes made

## Architecture

### Technology Stack
- **Framework**: LangChain with Azure OpenAI
- **Language**: Python 3.x
- **Package Manager**: UV (modern Python package manager)
- **AI Model**: Azure OpenAI GPT deployment
- **PDF Generation**: HTML to PDF conversion via pdf_exporter
- **Web Scraping**: Async job description fetching

### Project Structure
```
ai-cv-agent/
├── src/ai_cv_agent/          # Main package
│   ├── agent/                # Agent implementations
│   │   ├── cv_agent.py       # Base agent (currently empty)
│   │   ├── langchain_cv_agent.py  # Main LangChain agent
│   │   └── prompts.py        # AI prompts and templates
│   └── tools/                # Tool modules
│       ├── html_cv_builder.py     # HTML resume generation
│       ├── job_reader.py          # Job description fetcher
│       ├── langchain_tools.py     # LangChain tool wrappers
│       ├── pdf_exporter.py        # PDF conversion
│       ├── resume_parser.py       # YAML to ResumeData conversion
│       └── user_profile.py        # Profile management
├── templates/                # HTML templates and styles
│   ├── base_template.html    # Standard template
│   ├── base_template_dynamic.html  # Dynamic template
│   └── styles/               # CSS style variations
├── data/                     # User profiles and templates
├── outputs/                  # Generated resumes and reports
└── tests/                    # Test files
```

## Key Workflows

### 1. Complete Resume Tailoring Workflow
**Tool**: `create_tailored_resume_complete`
1. Fetch job description from URL
2. Load user profile YAML
3. Use AI to tailor resume content
4. Generate HTML from tailored data
5. Convert HTML to PDF
6. Create and save analysis report

### 2. Step-by-Step Workflow (Individual Tools)
1. `fetch_job_description(url)` → Returns job text
2. `load_user_profile(path)` → Returns profile dict
3. `tailor_resume_with_llm(job_desc, profile)` → Returns tailored dict
4. `analyze_job_with_llm(job_desc)` → Returns job analysis
5. `build_html_resume(resume_data)` → Returns HTML content
6. `convert_html_to_pdf(html, path)` → Saves PDF
7. `create_detailed_tailoring_analysis(...)` → Returns report
8. `save_tailoring_report(...)` → Saves report

## Data Formats

### User Profile YAML Structure
```yaml
name: "Full Name"
title: "Professional Title"
contact:
  email: "email@example.com"
  phone: "+1234567890"
  location: "City, Country"
  linkedin: "linkedin.com/in/profile"
summary: "Professional summary..."
experience:
  - title: "Job Title"
    company: "Company Name"
    duration: "Start - End"
    description: "Role description"
    achievements:
      - "Achievement 1"
      - "Achievement 2"
skills:
  technical: ["Skill1", "Skill2"]
  soft: ["Skill1", "Skill2"]
education:
  - degree: "Degree Name"
    institution: "University"
    year: "Year"
```

### ResumeData Object Structure
- Converted from YAML using `convert_raw_resume_to_resume_data()`
- Used by HTML builder and PDF exporter
- Contains all resume sections as structured data

## Important Files and Their Purposes

### Core Agent Files
- `langchain_cv_agent.py`: Main agent class with tool orchestration
- `prompts.py`: Contains SYSTEM_PROMPT, TAILORING_PROMPT, JOB_ANALYSIS_PROMPT
- `langchain_tools.py`: Tool wrappers with artifact support

### Tool Files
- `job_reader.py`: Async web scraping for job descriptions
- `user_profile.py`: YAML profile loading
- `resume_parser.py`: YAML to ResumeData conversion
- `html_cv_builder.py`: HTML generation with template support
- `pdf_exporter.py`: HTML to PDF conversion

### Configuration
- `.env`: Azure OpenAI credentials (AZURE_AI_ENDPOINT, AZURE_AI_API_KEY, etc.)
- `pyproject.toml`: Project dependencies and configuration
- `uv.lock`: Locked dependencies

## Environment Variables Required
```
AZURE_AI_ENDPOINT=<endpoint>
AZURE_AI_API_KEY=<api-key>
AZURE_AI_API_VERSION=<version>
AZURE_OPENAI_DEPLOYMENT_NAME=<deployment>
```

## Known Issues and TODOs
From `docs/TODO.md`:
- yaml creation process needs improvement
- File handling improvements (context object)
- Fix hallucination issues
- Fix paths in html_cv_builder
- Add Ruff linter

## Common Patterns

### Tool Response Format
Tools with `response_format="content_and_artifact"` return tuples:
```python
return "Status message", artifact_data
```

### Error Handling
All tools wrap exceptions in ToolException:
```python
try:
    # tool logic
except Exception as e:
    raise ToolException(f"Failed to X: {str(e)}")
```

### Async Handling
Job fetching uses asyncio:
```python
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    result = loop.run_until_complete(async_function())
finally:
    loop.close()
```

## Testing
- Test files in `tests/` directory
- `test_dynamic_styles.py`: Tests style variations
- `test_agent_analysis.py`: Tests agent analysis capabilities
- Run with: `uv run tests/test_file.py`

## Output Structure
```
outputs/
├── *.pdf              # Generated PDF resumes
├── *.html             # Generated HTML resumes
└── reports/           # Tailoring analysis reports
    └── *_report.md    # Markdown reports
```

## Style Templates
Available CV styles in `templates/styles/`:
- `default-styles.css`: Standard professional
- `classic-styles.css`: Traditional format
- `modern-styles.css`: Contemporary design
- `reversed-styles.css`: Alternative layout

## Development Commands
```bash
# Run main agent
uv run run_agent.py

# Run specific test
uv run tests/test_dynamic_styles.py

```

## Critical Considerations
1. **Artifact Passing**: Tools return tuples; extract second element for data
2. **Path Resolution**: All paths relative to project root
3. **Async Operations**: Job fetching requires proper event loop handling
4. **Template Selection**: Dynamic template supports style switching
5. **ATS Optimization**: Keywords from job descriptions must be naturally incorporated

## Integration Points
- Azure OpenAI for LLM operations
- LangChain for agent orchestration
- Puppeteer/Playwright for potential browser automation
- PDF libraries for document generation

## Recent Changes and Updates
- Migrated to proper `src/` layout structure
- Added artifact support to tools
- Implemented complete workflow tool
- Enhanced prompt engineering for better tailoring

---
*Last Updated: January 2025*
*Update Trigger: See .clinerules for update instructions*
