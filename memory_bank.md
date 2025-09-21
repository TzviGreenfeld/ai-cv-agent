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
- **Orchestration**: LangGraph for workflow management
- **Language**: Python 3.x
- **Package Manager**: UV (modern Python package manager)
- **AI Model**: Azure OpenAI GPT deployment
- **PDF Generation**: HTML to PDF conversion via pdf_exporter
- **Web Scraping**: Async job description fetching
- **Observability**: LangSmith for tracing

### Project Structure
```
ai-cv-agent/
├── src/ai_cv_agent/          # Main package
│   ├── agent/                # Agent implementations
│   │   ├── cv_agent.py       # Base agent (currently empty)
│   │   ├── langchain_cv_agent.py  # Main LangChain agent
│   │   ├── job_parser_agent.py    # Dedicated job parsing agent
│   │   ├── job_parser_prompts.py  # Job parsing prompts
│   │   ├── resume_tailoring_agent.py  # Resume tailoring agent
│   │   ├── resume_tailoring_prompts.py # Tailoring prompts
│   │   └── prompts.py        # AI prompts and templates
│   ├── graph/                # LangGraph workflows (NEW)
│   │   ├── __init__.py
│   │   └── workflow_graph.py # Main LangGraph workflow implementation
│   ├── models/               # Data models
│   │   ├── __init__.py
│   │   ├── job_models.py     # Job-related Pydantic models
│   │   └── resume_models.py  # Resume data model
│   ├── utils/                # Utility modules (NEW structure)
│   │   ├── __init__.py
│   │   ├── html_builder.py   # HTML resume generation
│   │   ├── job_fetcher.py    # Job description fetcher
│   │   ├── logging_setup.py  # Logging configuration
│   │   ├── pdf_converter.py  # PDF conversion
│   │   ├── profile_manager.py # Profile management
│   │   └── resume_mapper.py  # YAML to ResumeData conversion
│   └── tools/                # LangChain tool modules
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
├── examples/                 # Example scripts
│   └── test_job_parser.py    # Job parser usage example
└── tests/                    # Test files
    ├── agent/                # Agent tests
    │   └── test_job_parser_integration.py
    ├── test_complete_workflow.py  # Complete workflow test
    └── test_graph_workflow.py     # LangGraph workflow test (NEW)
```

## Key Workflows

### 1. LangGraph Workflow (NEW - Primary Method)
**Orchestration**: State-based workflow using LangGraph

#### Workflow State
```python
class WorkflowState(TypedDict):
    job_url: str
    user_profile_path: str
    style_name: str
    original_resume: Optional[ResumeData]
    job_parse_result: Optional[JobParseResult]
    job_requirements: Optional[JobRequirements]
    tailored_resume: Optional[ResumeData]
    html_content: Optional[str]
    pdf_path: Optional[str]
    error: Optional[str]
```

#### Graph Nodes
1. **load_profile**: Load user profile YAML → ResumeData
2. **parse_job**: Fetch and parse job URL → JobRequirements
3. **tailor_resume**: AI-powered resume tailoring → ResumeData
4. **generate_html**: Create styled HTML → HTML string
5. **export_pdf**: Convert HTML to PDF → PDF path
6. **error_sink**: Handle errors gracefully
7. **success_sink**: Terminal success state

#### Usage
```python
from ai_cv_agent.graph import run_workflow

# Simple usage
pdf_path = await run_workflow("https://job-url.com/posting")

# With options
pdf_path = await run_workflow(
    job_url="https://job-url.com/posting",
    user_profile_path="data/custom_profile.yaml",
    style_name="modern"
)
```

#### Benefits
- **State Management**: Clear state tracking throughout workflow
- **Error Handling**: Automatic error routing and recovery
- **Observability**: Full LangSmith tracing support
- **Modularity**: Each node is independently testable
- **Conditional Routing**: Smart branching based on state

### 2. Complete Resume Tailoring Workflow (Legacy)
**Tool**: `create_tailored_resume_complete`
1. Fetch job description from URL
2. Load user profile YAML
3. Use AI to tailor resume content
4. Generate HTML from tailored data
5. Convert HTML to PDF
6. Create and save analysis report

### 3. Multi-Agent Architecture

**Complete Workflow with Specialized Agents**:

#### JobParserAgent
- **Purpose**: Parse job descriptions into structured data
- **Methods**: 
  - `parse_from_url(url)` → Returns JobParseResult
  - `parse_from_text(text)` → Parses raw text
- **Output**: JobRequirements model with structured job data

#### ResumeTailoringAgent (NEW)
- **Purpose**: Tailor resumes based on job requirements
- **Methods**:
  - `tailor_resume(original_resume, job_requirements)` → Returns tailored ResumeData
  - `tailor_resume_sync()` → Synchronous wrapper
- **Features**:
  - Uses structured JobRequirements input
  - Returns ResumeData for direct HTML/PDF generation
  - Separate prompts in `resume_tailoring_prompts.py`
  - Low temperature (0.3) for consistent output

#### Complete Workflow Integration
```python
# 1. Load user profile
user_profile_dict = read_user_profile("data/user_profile.yaml")
original_resume = convert_raw_resume_to_resume_data(user_profile_dict)

# 2. Parse job
job_parser = JobParserAgent()
job_result = await job_parser.parse_from_url(job_url)

# 3. Tailor resume
if job_result.success:
    tailoring_agent = ResumeTailoringAgent()
    tailored_resume = await tailoring_agent.tailor_resume(
        original_resume, 
        job_result.job_requirements
    )
    
# 4. Generate HTML
html = generate_cv_html(tailored_resume, style_name="modern")

# 5. Convert to PDF
html_to_pdf(html, "outputs/tailored_resume.pdf")
```

**Benefits**:
1. **Modularity**: Each agent has a single responsibility
2. **Type Safety**: Pydantic models throughout
3. **Testability**: Each component tested independently  
4. **Reusability**: Agents can be used in different workflows
5. **Maintainability**: Clear separation of concerns

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
- `job_parser_agent.py`: Dedicated job parsing agent with structured output
- `job_parser_prompts.py`: Prompts for job parsing (JOB_PARSING_PROMPT)
- `resume_tailoring_agent.py`: NEW: Resume tailoring agent with AI optimization
- `resume_tailoring_prompts.py`: NEW: Tailoring-specific prompts

### Model Files
- `job_models.py`: Pydantic models for job data
  - `JobRequirements`: Structured job posting representation
  - `JobParseResult`: Result wrapper with success/error handling
- `resume_models.py`: Resume data model (moved from html_cv_builder)
  - `ResumeData`: Core resume data structure with to_dict() method

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
# Run with LangGraph workflow (NEW)
python -m ai_cv_agent.main "https://job-url.com/posting"

# Run with custom profile
python -m ai_cv_agent.main "https://job-url.com/posting" --profile data/custom.yaml

# Run with different style
python -m ai_cv_agent.main "https://job-url.com/posting" --style modern

# Run main agent (legacy)
uv run run_agent.py

# Run specific test
uv run tests/test_dynamic_styles.py

# Run LangGraph workflow tests
uv run tests/test_graph_workflow.py

# Check code quality
uv run ruff check src/
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
- Updated 2025-09-12: `ruff-auto-fix.yml` now runs on all branch pushes
- Updated 2025-09-13: Implemented multi-agent architecture with JobParserAgent
- Updated 2025-09-15: Complete workflow refactoring:
  - Created `ResumeTailoringAgent` for dedicated resume optimization
  - Moved `ResumeData` model to `models/resume_models.py`
  - Separated tailoring prompts into `resume_tailoring_prompts.py`
  - Created complete workflow tests (`test_complete_workflow.py`)
  - Full pipeline: URL → JobParserAgent → ResumeTailoringAgent → HTML → PDF
  - Successfully tested end-to-end workflow with mock data
- Updated 2025-09-16: LangGraph workflow implementation:
  - Created `graph/workflow_graph.py` with state-based orchestration
  - Replaced imperative workflow in `main.py` with LangGraph runner
  - Added CLI argument support for job URL, profile path, and style
  - Removed manual logging in favor of LangSmith tracing
  - Added comprehensive tests in `test_graph_workflow.py`
  - Reorganized utils from tools directory for cleaner structure
  - Added `langgraph` dependency to project
  - Workflow now uses conditional routing for error handling

---
*Last Updated: 2025-09-16*
*Update Trigger: See .clinerules for update instructions*
