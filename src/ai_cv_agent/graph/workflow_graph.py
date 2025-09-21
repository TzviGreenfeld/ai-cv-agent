"""LangGraph-based workflow for AI CV Agent"""

from typing import TypedDict, Optional
from datetime import datetime
from pathlib import Path

from langgraph.graph import StateGraph, END

from ai_cv_agent.agent.job_parser_agent import JobParserAgent
from ai_cv_agent.agent.resume_tailoring_agent import ResumeTailoringAgent
from ai_cv_agent.models.job_models import JobRequirements, JobParseResult
from ai_cv_agent.models.resume_models import ResumeData
from ai_cv_agent.utils.profile_manager import read_user_profile
from ai_cv_agent.utils.resume_mapper import convert_raw_resume_to_resume_data
from ai_cv_agent.utils.html_builder import generate_cv_html
from ai_cv_agent.utils.pdf_converter import html_to_pdf_async


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


# Node functions
async def load_profile(state: WorkflowState) -> dict:
    """Load user profile and convert to ResumeData"""
    try:
        user_profile_dict = read_user_profile(state["user_profile_path"])
        original_resume = convert_raw_resume_to_resume_data(user_profile_dict)
        return {"original_resume": original_resume}
    except Exception as e:
        return {"error": f"Failed to load user profile: {str(e)}"}


async def parse_job(state: WorkflowState) -> dict:
    """Parse job from URL"""
    try:
        job_parser = JobParserAgent()
        job_result = await job_parser.parse_from_url(state["job_url"])
        
        if not job_result.success:
            return {"error": f"Failed to parse job: {job_result.error_message}"}
        
        return {
            "job_parse_result": job_result,
            "job_requirements": job_result.job_requirements
        }
    except Exception as e:
        return {"error": f"Failed to parse job: {str(e)}"}


async def tailor_resume(state: WorkflowState) -> dict:
    """Tailor resume to job requirements"""
    try:
        tailoring_agent = ResumeTailoringAgent(temperature=0.3)
        tailored_resume = await tailoring_agent.tailor_resume(
            state["original_resume"],
            state["job_requirements"]
        )
        return {"tailored_resume": tailored_resume}
    except Exception as e:
        return {"error": f"Failed to tailor resume: {str(e)}"}


async def generate_html(state: WorkflowState) -> dict:
    """Generate HTML from tailored resume"""
    try:
        html_content = generate_cv_html(
            resume_data=state["tailored_resume"],
            style_name=state.get("style_name", "default"),
            embed_css=True,
            use_dynamic_template=True,
        )
        return {"html_content": html_content}
    except Exception as e:
        return {"error": f"Failed to generate HTML: {str(e)}"}


async def export_pdf(state: WorkflowState) -> dict:
    """Export HTML to PDF"""
    try:
        # Generate filename from company and role
        company_clean = state["job_requirements"].company.replace(" ", "_").replace("/", "_")
        role_clean = state["job_requirements"].role.replace(" ", "_").replace("/", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        # Ensure output directory exists
        output_dir = Path(__file__).parent.parent.parent.parent / "outputs" / "tailored_resumes"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate PDF
        pdf_path = output_dir / f"{company_clean}_{role_clean}_{timestamp}.pdf"
        await html_to_pdf_async(state["html_content"], str(pdf_path))
        
        return {"pdf_path": str(pdf_path)}
    except Exception as e:
        return {"error": f"Failed to export PDF: {str(e)}"}


async def error_sink(state: WorkflowState) -> dict:
    """Terminal node for error states"""
    return {}


async def success_sink(state: WorkflowState) -> dict:
    """Terminal node for success states"""
    return {}


# Routing functions
def route_after_load(state: WorkflowState) -> str:
    """Route after loading profile"""
    if state.get("error"):
        return "error_sink"
    return "parse_job"


def route_after_parse(state: WorkflowState) -> str:
    """Route after parsing job"""
    if state.get("error"):
        return "error_sink"
    return "tailor_resume"


def route_after_tailor(state: WorkflowState) -> str:
    """Route after tailoring resume"""
    if state.get("error"):
        return "error_sink"
    return "generate_html"


def route_after_html(state: WorkflowState) -> str:
    """Route after generating HTML"""
    if state.get("error"):
        return "error_sink"
    return "export_pdf"


def route_after_pdf(state: WorkflowState) -> str:
    """Route after exporting PDF"""
    if state.get("error"):
        return "error_sink"
    return "success_sink"


# Build the graph
def build_workflow_graph() -> StateGraph:
    """Build the CV workflow graph"""
    
    # Initialize graph with state definition
    graph = StateGraph(WorkflowState)
    
    # Add nodes
    graph.add_node("load_profile", load_profile)
    graph.add_node("parse_job", parse_job)
    graph.add_node("tailor_resume", tailor_resume)
    graph.add_node("generate_html", generate_html)
    graph.add_node("export_pdf", export_pdf)
    graph.add_node("error_sink", error_sink)
    graph.add_node("success_sink", success_sink)
    
    # Set entry point
    graph.set_entry_point("load_profile")
    
    # Add conditional edges
    graph.add_conditional_edges("load_profile", route_after_load)
    graph.add_conditional_edges("parse_job", route_after_parse)
    graph.add_conditional_edges("tailor_resume", route_after_tailor)
    graph.add_conditional_edges("generate_html", route_after_html)
    graph.add_conditional_edges("export_pdf", route_after_pdf)
    
    # Add terminal edges
    graph.add_edge("error_sink", END)
    graph.add_edge("success_sink", END)
    
    return graph


# Main workflow runner
async def run_workflow(
    job_url: str,
    user_profile_path: str = "data/user_profile_resume_format.yaml",
    style_name: str = "default"
) -> str:
    """
    Run the complete CV workflow using LangGraph.
    
    Args:
        job_url: URL of the job posting
        user_profile_path: Path to user profile YAML
        style_name: CSS style name for HTML generation
        
    Returns:
        Path to generated PDF
        
    Raises:
        RuntimeError: If workflow fails with an error
    """
    # Build and compile the graph
    graph = build_workflow_graph()
    app = graph.compile()
    
    # Initialize state
    initial_state = {
        "job_url": job_url,
        "user_profile_path": user_profile_path,
        "style_name": style_name
    }
    
    # Run the workflow
    final_state = await app.ainvoke(initial_state)
    
    # Check for errors
    if final_state.get("error"):
        raise RuntimeError(final_state["error"])
    
    # Return PDF path
    if not final_state.get("pdf_path"):
        raise RuntimeError("Workflow completed but no PDF was generated")
    
    return final_state["pdf_path"]
