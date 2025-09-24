"""LangGraph-based workflow for AI CV Agent"""

from typing import TypedDict, Optional, Callable
from datetime import datetime
from pathlib import Path
import logging
from functools import wraps

from langgraph.graph import StateGraph, END

from ai_cv_agent.agent.job_parser_agent import JobParserAgent
from ai_cv_agent.agent.resume_tailoring_agent import ResumeTailoringAgent
from ai_cv_agent.models.job_models import JobRequirements, JobParseResult
from ai_cv_agent.models.resume_models import ResumeData
from ai_cv_agent.utils.profile_manager import read_user_profile
from ai_cv_agent.utils.resume_mapper import convert_raw_resume_to_resume_data
from ai_cv_agent.utils.html_builder import generate_cv_html
from ai_cv_agent.utils.pdf_converter import html_to_pdf_async

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowState(TypedDict, total=False):
    """State definition for the CV workflow"""

    # Input parameters
    job_url: str
    user_profile_path: str
    style_name: str

    # Intermediate data
    original_resume: Optional[ResumeData]
    job_parse_result: Optional[JobParseResult]
    job_requirements: Optional[JobRequirements]
    tailored_resume: Optional[ResumeData]
    html_content: Optional[str]

    # Output
    pdf_path: Optional[str]

    # Error tracking
    error: Optional[str]
    error_step: Optional[str]
    error_details: Optional[str]


def with_error_handling(node_name: str) -> Callable:
    """Decorator to add consistent error handling to workflow nodes.
    
    Args:
        node_name: Name of the node for error tracking
        
    Returns:
        Decorated function with error handling
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(state: WorkflowState) -> dict:
            # Check if there's already an error from a previous step
            if state.get("error"):
                logger.info(f"Skipping node {node_name} due to previous error: {state['error']}")
                return {}  # Return empty dict to not modify state
            
            try:
                # Log node execution
                logger.info(f"Executing node: {node_name}")
                
                # Execute the node function
                result = await func(state)
                
                # Check if the node itself returned an error
                if result.get("error"):
                    logger.error(f"Node {node_name} returned error: {result['error']}")
                    result["error_step"] = node_name
                
                return result
                
            except Exception as e:
                # Log the error with full context
                logger.exception(f"Error in node {node_name}")
                
                # Return error state
                return {
                    "error": f"Failed in {node_name}: {str(e)}",
                    "error_step": node_name,
                    "error_details": str(e),
                }
        
        return wrapper
    return decorator


# Node functions with error handling
@with_error_handling("load_profile")
async def load_profile(state: WorkflowState) -> dict:
    """Load user profile and convert to ResumeData"""
    user_profile_dict = read_user_profile(state["user_profile_path"])
    original_resume = convert_raw_resume_to_resume_data(user_profile_dict)
    return {"original_resume": original_resume}


@with_error_handling("parse_job")
async def parse_job(state: WorkflowState) -> dict:
    """Parse job from URL"""
    job_parser = JobParserAgent()
    job_result = await job_parser.parse_from_url(state["job_url"])

    if not job_result.success:
        return {
            "error": f"Failed to parse job: {job_result.error_message}",
            "error_details": job_result.error_message,
        }

    return {
        "job_parse_result": job_result,
        "job_requirements": job_result.job_requirements,
    }


@with_error_handling("tailor_resume")
async def tailor_resume(state: WorkflowState) -> dict:
    """Tailor resume to job requirements"""
    tailoring_agent = ResumeTailoringAgent(temperature=0.3)
    tailored_resume = await tailoring_agent.tailor_resume(
        state["original_resume"], state["job_requirements"]
    )
    return {"tailored_resume": tailored_resume}


@with_error_handling("generate_html")
async def generate_html(state: WorkflowState) -> dict:
    """Generate HTML from tailored resume"""
    html_content = generate_cv_html(
        resume_data=state["tailored_resume"],
        style_name=state.get("style_name", "default"),
        embed_css=True,
        use_dynamic_template=True,
    )
    return {"html_content": html_content}


@with_error_handling("export_pdf")
async def export_pdf(state: WorkflowState) -> dict:
    """Export HTML to PDF"""
    # Generate filename from company and role
    company_clean = (
        state["job_requirements"].company.replace(" ", "_").replace("/", "_")
    )
    role_clean = state["job_requirements"].role.replace(" ", "_").replace("/", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    # Ensure output directory exists
    output_dir = (
        Path(__file__).parent.parent.parent.parent / "outputs" / "tailored_resumes"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate PDF
    pdf_path = output_dir / f"{company_clean}_{role_clean}_{timestamp}.pdf"
    await html_to_pdf_async(state["html_content"], str(pdf_path))

    return {"pdf_path": str(pdf_path)}


def build_workflow_graph() -> StateGraph:
    """Build the CV workflow graph with simplified linear flow.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize graph with state definition
    graph = StateGraph(WorkflowState)

    # Add nodes - all with error handling decorator
    graph.add_node("load_profile", load_profile)
    graph.add_node("parse_job", parse_job)
    graph.add_node("tailor_resume", tailor_resume)
    graph.add_node("generate_html", generate_html)
    graph.add_node("export_pdf", export_pdf)

    # Set entry point
    graph.set_entry_point("load_profile")

    # Simple linear flow - no conditional edges needed
    graph.add_edge("load_profile", "parse_job")
    graph.add_edge("parse_job", "tailor_resume")
    graph.add_edge("tailor_resume", "generate_html")
    graph.add_edge("generate_html", "export_pdf")
    graph.add_edge("export_pdf", END)

    return graph


async def run_workflow(
    job_url: str,
    user_profile_path: str = "data/user_profile_resume_format.yaml",
    style_name: str = "default",
) -> str:
    """Run the complete CV workflow using LangGraph.
    
    This function orchestrates the entire resume tailoring process:
    1. Loads user profile
    2. Parses job description from URL
    3. Tailors resume to match job requirements
    4. Generates styled HTML
    5. Exports to PDF
    
    Args:
        job_url: URL of the job posting
        user_profile_path: Path to user profile YAML
        style_name: CSS style name for HTML generation
        
    Returns:
        Path to generated PDF
        
    Raises:
        RuntimeError: If workflow fails at any step
    """
    # Build and compile the graph
    graph = build_workflow_graph()
    app = graph.compile()

    # Initialize state
    initial_state = {
        "job_url": job_url,
        "user_profile_path": user_profile_path,
        "style_name": style_name,
    }

    try:
        # Run the workflow
        logger.info(f"Starting workflow for job URL: {job_url}")
        final_state = await app.ainvoke(initial_state)

        # Check if any step set an error
        if final_state.get("error"):
            error_step = final_state.get("error_step", "unknown")
            error_details = final_state.get("error_details", "No details available")
            
            logger.error(
                f"Workflow failed at step '{error_step}': {final_state['error']}\n"
                f"Details: {error_details}"
            )
            
            raise RuntimeError(final_state["error"])

        # Ensure we have a PDF path
        if not final_state.get("pdf_path"):
            raise RuntimeError("Workflow completed but no PDF was generated")

        logger.info(f"Workflow completed successfully: {final_state['pdf_path']}")
        return final_state["pdf_path"]

    except Exception:
        # Log with full context
        logger.exception("Workflow failed with exception")
        raise
