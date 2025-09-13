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
│   │   ├── job_parser_agent.py    # NEW: Dedicated job parsing agent
│   │   ├── job_parser_prompts.py  # NEW: Job parsing prompts
│   │   └── prompts.py        # AI prompts and templates
│   ├── models/               # NEW: Data models
│   │   ├── __init__.py
│   │   └── job_models.py     # Job-related Pydantic models
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
├── examples/                 # NEW: Example scripts
│   └── test_job_parser.py    # Job parser usage example
└── tests/                    # Test files
    ├── agent/                # NEW: Agent tests
    │   └── test_job_parser_agent.py
    └── tools/                # NEW: Tool tests
        └── test_job_reader.py
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

### 3. NEW: Multi-Agent Architecture (Job Parser Agent)
**Purpose**: Separate job parsing into a dedicated agent for better modularity
- **JobParserAgent**: Dedicated agent for parsing job descriptions
  - `parse_from_url(url)` → Returns JobParseResult with structured job data
  - `parse_from_text(text)` → Parses raw job text into structured format
  - Uses structured Pydantic models (JobRequirements, JobParseResult)
  - Handles both async and sync operations
  - Better error handling and validation

**Benefits of Multi-Agent Approach**:
1. **Separation of Concerns**: Job parsing logic isolated from resume tailoring
2. **Reusability**: Job parser can be used independently
3. **Better Testing**: Each agent can be tested in isolation
4. **Type Safety**: Pydantic models ensure data consistency
5. **Scalability**: Easy to add more specialized agents

**Integration Flow**:
```python
# 1. Parse job with JobParserAgent
job_parser = JobParserAgent()
job_result = await job_parser.parse_from_url(url)

# 2. Use parsed job data with main CV agent
if job_result.success:
    job_data = job_result.job_requirements.to_analysis_dict()
    # Pass to resume tailoring agent
```

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
- `job_parser_agent.py`: NEW: Dedicated job parsing agent with structured output
- `job_parser_prompts.py`: NEW: Prompts for job parsing (JOB_PARSING_PROMPT)

### Model Files
- `job_models.py`: Pydantic models for job data
  - `JobRequirements`: Structured job posting representation
  - `JobParseResult`: Result wrapper with success/error handling

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

### Test Structure
```
tests/
├── agent/                           # Agent-specific tests
│   ├── test_job_parser_agent.py    # Unit tests for JobParserAgent
│   └── test_job_parser_integration.py  # Integration tests with real LLM
├── tools/                           # Tool-specific tests
│   └── test_job_reader.py          # Tests for job fetching
├── mocks/                           # Mock data for testing
│   ├── google_swe3_cloud.md        # Sample Google job posting
│   └── README.md                    # Mock data documentation
├── test_dynamic_styles.py          # Style variation tests
└── test_agent_analysis.py          # Agent analysis tests
```

### Running Tests
```bash
# Run specific test file
uv run tests/test_file.py

# Run with pytest
uv run pytest tests/agent/test_job_parser_agent.py -v

# Run integration tests (requires Azure credentials)
uv run pytest tests/agent/test_job_parser_integration.py -v
```

### Integration Testing Strategy
- **Mock job fetching**: Use local files instead of real URLs
- **Real LLM parsing**: Test actual AI parsing capabilities
- **Specific URL mocking**: When testing with Google job URL, returns mock file content
- **No external dependencies**: Tests work offline with mocked data

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
- Added GitHub Actions CI: `ruff-auto-fix.yml` (Ruff lint + format auto-fix)
- Updated 2025-09-12: `ruff-auto-fix.yml` now runs on all branch pushes (removed branches filter; previously main-only)
- Updated 2025-09-13: Implemented multi-agent architecture:
  - Created `JobParserAgent` for dedicated job parsing
  - Added Pydantic models for type-safe job data (`JobRequirements`, `JobParseResult`)
  - Separated job parsing prompts into `job_parser_prompts.py`
  - Added comprehensive tests for job parser and reader
  - Created example scripts demonstrating new architecture
  - Benefits: Better separation of concerns, reusability, testability

---
*Last Updated: 2025-09-13*
*Update Trigger: See .clinerules for update instructions*
