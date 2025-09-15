# AI CV Agent - Complete Workflow Guide

## Overview

The AI CV Agent provides a complete pipeline for automatically tailoring resumes to job descriptions using AI. The system uses specialized agents for each step of the process.

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌──────────┐     ┌─────────┐
│   Job URL    │────▶│ JobParser    │────▶│ ResumeTailoring │────▶│   HTML   │────▶│   PDF   │
│              │     │    Agent     │     │     Agent       │     │ Generator│     │ Export  │
└──────────────┘     └──────────────┘     └─────────────────┘     └──────────┘     └─────────┘
                            │                       │
                            ▼                       ▼
                     JobRequirements         TailoredResume
                      (Pydantic)              (ResumeData)
```

## Complete Workflow Options

### Option 1: Using LangGraph (Advanced - Recommended for Complex Workflows)

LangGraph is ideal when you need:
- State management across multiple steps
- Conditional branching based on results
- Complex error handling and retries
- Parallel processing of multiple jobs

**When to use**: 
- Processing multiple job applications
- Need for human-in-the-loop approval steps
- Complex decision trees based on job type

### Option 2: Direct Agent Integration (Current Implementation)

Our current implementation uses direct agent composition, which is perfect for:
- Simple linear workflows
- Single job processing
- Quick prototyping
- Clear error tracking

**Current workflow steps:**

## Step-by-Step Implementation

### 1. Setup Environment

```bash
# Install dependencies
uv pip install -e .

# Create .env file with Azure OpenAI credentials
AZURE_AI_ENDPOINT=your-endpoint
AZURE_AI_API_KEY=your-api-key
AZURE_AI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
```

### 2. Update User Profile

Edit `data/user_profile_resume_format.yaml` with your information:

```yaml
candidate:
  name: "Your Name"
  title: "Your Current Title"

summary: "Your professional summary..."

contact:
  - "phone"
  - "email"
  - "linkedin"
  - "github"

experience:
  - title: "Job Title"
    dates: "Start - End"
    company: "Company"
    description: "Role description"
    achievements:
      - "Achievement 1"
      - "Achievement 2"

# ... continue with education and skills
```

### 3. Run the Complete Workflow

#### Using the Test Script

```python
# tests/test_complete_workflow.py
python tests/test_complete_workflow.py
# Enter job URL when prompted
```

#### Programmatic Usage

```python
import asyncio
from ai_cv_agent.agent.job_parser_agent import JobParserAgent
from ai_cv_agent.agent.resume_tailoring_agent import ResumeTailoringAgent
from ai_cv_agent.tools.user_profile import read_user_profile
from ai_cv_agent.tools.resume_parser import convert_raw_resume_to_resume_data
from ai_cv_agent.tools.html_cv_builder import generate_cv_html
from ai_cv_agent.tools.pdf_exporter import html_to_pdf

async def tailor_resume(job_url: str):
    # Step 1: Load user profile
    user_profile_dict = read_user_profile("data/user_profile_resume_format.yaml")
    original_resume = convert_raw_resume_to_resume_data(user_profile_dict)
    
    # Step 2: Parse job from URL
    job_parser = JobParserAgent()
    job_result = await job_parser.parse_from_url(job_url)
    
    if not job_result.success:
        print(f"Error: {job_result.error_message}")
        return
    
    # Step 3: Tailor resume with AI
    tailoring_agent = ResumeTailoringAgent(temperature=0.3)
    tailored_resume = await tailoring_agent.tailor_resume(
        original_resume,
        job_result.job_requirements
    )
    
    # Step 4: Generate HTML
    html_content = generate_cv_html(
        resume_data=tailored_resume,
        style_name="modern",  # or "classic", "default", "reversed"
        embed_css=True,
        use_dynamic_template=True
    )
    
    # Step 5: Convert to PDF
    output_path = f"outputs/{job_result.job_requirements.company}_resume.pdf"
    html_to_pdf(html_content, output_path)
    
    print(f"✓ Resume saved to: {output_path}")

# Run the async function
asyncio.run(tailor_resume("https://job-url-here.com"))
```

### 4. Synchronous Usage

For simpler scripts without async:

```python
from ai_cv_agent.agent.job_parser_agent import JobParserAgent
from ai_cv_agent.agent.resume_tailoring_agent import ResumeTailoringAgent

# Use sync methods
job_parser = JobParserAgent()
job_result = job_parser.parse_from_url_sync(job_url)

tailoring_agent = ResumeTailoringAgent()
tailored_resume = tailoring_agent.tailor_resume_sync(
    original_resume,
    job_result.job_requirements
)
```

## Individual Components

### JobParserAgent

Extracts structured data from job postings:

```python
from ai_cv_agent.agent.job_parser_agent import JobParserAgent

parser = JobParserAgent()

# From URL
result = await parser.parse_from_url("https://...")

# From text
result = await parser.parse_from_text("Job description text...")

# Access structured data
if result.success:
    job = result.job_requirements
    print(f"Company: {job.company}")
    print(f"Role: {job.role}")
    print(f"Key Requirements: {job.key_requirements}")
    print(f"Technical Skills: {job.technical_skills}")
```

### ResumeTailoringAgent

Optimizes resume content for specific jobs:

```python
from ai_cv_agent.agent.resume_tailoring_agent import ResumeTailoringAgent

agent = ResumeTailoringAgent(
    temperature=0.3,  # Lower = more consistent
    verbose=True      # Show progress
)

tailored = await agent.tailor_resume(
    original_resume,  # ResumeData object
    job_requirements  # JobRequirements object
)

# Result is a ResumeData object ready for HTML/PDF generation
print(tailored.candidate['title'])  # New optimized title
print(tailored.summary)  # Tailored summary
```

### HTML Generation

Multiple style options available:

```python
from ai_cv_agent.tools.html_cv_builder import generate_cv_html

html = generate_cv_html(
    resume_data=tailored_resume,
    style_name="modern",  # Options: default, modern, classic, reversed
    embed_css=True,       # Embed CSS in HTML
    use_dynamic_template=True  # Use flexible template
)
```

## Output Structure

The workflow generates multiple outputs:

```
outputs/
├── tailored_resumes/
│   ├── Company_Role_20250915_2000.pdf     # Final PDF
│   ├── Company_Role_20250915_2000.yaml    # Tailored YAML data
│   ├── Company_Role_20250915_2000.html    # HTML version
│   └── Company_Role_20250915_2000_report.txt  # Analysis report
```

## Testing

### Test with Mock Data

```bash
# Test the complete workflow with mock job data
uv run python tests/test_workflow_with_mock.py
```

### Test with Real URL

```bash
# Test with actual job posting
uv run python tests/test_complete_workflow.py
# Enter job URL when prompted
```

## Troubleshooting

### Common Issues

1. **Job URL parsing fails**
   - Some websites block automated access
   - Try using the text parsing method instead
   - Check if the URL is accessible in a browser

2. **PDF generation error about async**
   - This is a warning, not an error
   - PDFs are still generated correctly
   - Will be fixed in future updates

3. **Azure OpenAI errors**
   - Verify .env file has correct credentials
   - Check API quota and limits
   - Ensure deployment name is correct

### Debug Mode

Enable debug output by setting environment variable:

```bash
export DEBUG=true
```

This will save intermediate HTML files for inspection.

## Advanced Usage

### Batch Processing

Process multiple jobs at once:

```python
async def process_multiple_jobs(job_urls: list):
    results = []
    for url in job_urls:
        try:
            result = await tailor_resume(url)
            results.append(result)
        except Exception as e:
            print(f"Failed for {url}: {e}")
    return results
```

### Custom Styles

Add your own CSS style:

1. Create `templates/styles/custom-styles.css`
2. Use in generation:
   ```python
   html = generate_cv_html(
       resume_data=resume,
       style_name="custom"
   )
   ```

### Integration with LangGraph

For complex workflows with state management:

```python
from langgraph.graph import StateGraph, END

# Define workflow state
class WorkflowState(TypedDict):
    job_url: str
    job_requirements: Optional[JobRequirements]
    original_resume: ResumeData
    tailored_resume: Optional[ResumeData]
    pdf_path: Optional[str]

# Build graph
workflow = StateGraph(WorkflowState)

# Add nodes for each step
workflow.add_node("parse_job", parse_job_node)
workflow.add_node("tailor_resume", tailor_resume_node)
workflow.add_node("generate_pdf", generate_pdf_node)

# Define edges
workflow.add_edge("parse_job", "tailor_resume")
workflow.add_edge("tailor_resume", "generate_pdf")
workflow.add_edge("generate_pdf", END)

# Compile and run
app = workflow.compile()
result = app.invoke({"job_url": url, "original_resume": resume})
```

## Best Practices

1. **Keep user profile updated**: Maintain comprehensive data in YAML
2. **Review tailored output**: AI may occasionally need adjustments
3. **Test with target company**: Some companies have specific formats
4. **Use appropriate styles**: Modern for tech, classic for traditional industries
5. **Save originals**: Keep untailored versions for reference

## Next Steps

### Immediate Improvements
- Fix job URL parsing for more websites
- Add more HTML templates
- Implement caching for repeated jobs

### Future Enhancements
- LangGraph integration for complex workflows
- Multiple resume versions per job
- A/B testing different tailoring strategies
- Integration with job boards APIs
- Automated application submission

## Support

For issues or questions:
1. Check `memory_bank.md` for project details
2. Review test files for usage examples
3. Enable debug mode for detailed output
4. Check GitHub issues for known problems

---

*Last Updated: 2025-09-15*
