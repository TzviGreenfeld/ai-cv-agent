import os
import sys
from typing import Optional
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import AzureChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Import refactored tools with artifacts support
from tools.langchain_tools import (
    fetch_job_description,
    load_user_profile,
    parse_resume_yaml,
    build_html_resume,
    convert_html_to_pdf,
    save_tailoring_report
)


# Import prompts
from agent.prompts import (
    SYSTEM_PROMPT,
    TAILORING_PROMPT,
    JOB_ANALYSIS_PROMPT,
    DETAILED_TAILORING_PROMPT
)

# Load environment variables
load_dotenv()

class LangChainCVAgent:
    """
    AI-powered CV Agent using LangChain for intelligent resume tailoring.
    
    This agent uses artifacts to pass data between tools, minimizing file I/O
    and only creating final output files (PDF and reports).
    """
    
    def __init__(self):
        """Initialize the agent with Azure OpenAI and tools"""
        # Initialize Azure OpenAI
        self.llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_AI_ENDPOINT"),
            api_key=os.getenv("AZURE_AI_API_KEY"),
            api_version=os.getenv("AZURE_AI_API_VERSION"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0.7
        )
        
        # Create LangChain tools
        self.tools = self._create_tools()
        
        # Create the agent
        self.agent_executor = self._create_agent()
    
    def _create_tools(self):
        """
        Create and configure all agent tools including LLM-enhanced tools.
        """
        
        @tool
        def create_tailored_resume_complete(job_url: str, profile_path: str = "data/user_profile_resume_format.yaml", output_name: str = "test_resume") -> str:
            """
            Complete workflow to create a tailored resume from job URL to PDF output.
            
            Args:
                job_url: URL of the job posting
                profile_path: Path to user profile YAML
                output_name: Base name for output files (without extension)
                
            Returns:
                Status message indicating success or failure
            """
            import yaml
            import json
            from pathlib import Path
            
            try:
                # Step 1: Fetch job description
                print(f"Fetching job description from {job_url}...")
                import asyncio
                from tools.job_reader import read_job_description as _read_job_description
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    job_description = loop.run_until_complete(_read_job_description(job_url))
                finally:
                    loop.close()
                
                # Step 2: Load user profile
                print(f"Loading user profile from {profile_path}...")
                from tools.user_profile import read_user_profile as _read_user_profile
                user_profile = _read_user_profile(profile_path)
                
                # Step 3: Tailor resume using LLM
                print("Tailoring resume to job requirements...")
                tailoring_prompt = TAILORING_PROMPT.format(
                    job_description=job_description,
                    user_profile=yaml.dump(user_profile, default_flow_style=False)
                )
                response = self.llm.invoke(tailoring_prompt)
                tailored_yaml = response.content
                
                # Clean YAML response
                if "```yaml" in tailored_yaml:
                    tailored_yaml = tailored_yaml.split("```yaml")[1].split("```")[0].strip()
                elif "```" in tailored_yaml:
                    tailored_yaml = tailored_yaml.split("```")[1].split("```")[0].strip()
                
                tailored_data = yaml.safe_load(tailored_yaml)
                
                # Step 4: Convert to ResumeData and generate HTML
                print("Generating HTML resume...")
                from tools.resume_parser import convert_raw_resume_to_resume_data
                from tools.html_cv_builder import generate_cv_html as _generate_cv_html
                
                resume_obj = convert_raw_resume_to_resume_data(tailored_data)
                html_content = _generate_cv_html(resume_obj)
                
                # Step 5: Save HTML and convert to PDF
                print("Converting to PDF...")
                from tools.pdf_exporter import html_to_pdf as _html_to_pdf
                
                # Ensure output directory exists
                Path("outputs").mkdir(exist_ok=True)
                                
                # Convert to PDF
                pdf_path = f"outputs/{output_name}.pdf"
                _html_to_pdf(html_content, pdf_path)
                
                # Step 6: Generate and save analysis report
                print("Generating tailoring analysis report...")
                analysis_prompt = JOB_ANALYSIS_PROMPT.format(job_description=job_description)
                analysis_response = self.llm.invoke(analysis_prompt)
                
                comparison_prompt = f"""
                Compare the original and tailored resumes and describe what changes were made.
                
                Original Profile Summary: {user_profile.get('summary', '')}
                Tailored Profile Summary: {tailored_data.get('summary', '')}
                
                Job Analysis: {analysis_response.content}
                
                Provide a detailed report of changes made and why they align with the job requirements.
                """
                
                report_response = self.llm.invoke(comparison_prompt)
                
                # Save report
                Path("outputs/reports").mkdir(parents=True, exist_ok=True)
                report_path = f"outputs/reports/{output_name}_report.md"
                with open(report_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Resume Tailoring Report\n\n")
                    f.write(f"**Job URL:** {job_url}\n\n")
                    f.write(f"## Changes Made\n\n")
                    f.write(report_response.content)
                
                return f"""
Successfully created tailored resume!
- PDF saved to: {pdf_path}
- Report saved to: {report_path}
"""
                
            except Exception as e:
                return f"Error creating tailored resume: {str(e)}"
        
        @tool(response_format="content_and_artifact")
        def analyze_job_with_llm(job_description: str) -> tuple[str, dict]:
            """
            Analyze job posting to extract key requirements and keywords.
            
            Args:
                job_description: The job description text
                
            Returns:
                Tuple of (analysis summary, structured analysis dict as artifact)
            """
            import json
            
            try:
                analysis_prompt = JOB_ANALYSIS_PROMPT.format(
                    job_description=job_description
                )
                
                response = self.llm.invoke(analysis_prompt)
                analysis = response.content
                
                # Clean and parse JSON
                if "```json" in analysis:
                    analysis = analysis.split("```json")[1].split("```")[0].strip()
                elif "```" in analysis:
                    analysis = analysis.split("```")[1].split("```")[0].strip()
                
                try:
                    analysis_dict = json.loads(analysis)
                    return "Job analysis completed", analysis_dict
                except json.JSONDecodeError:
                    # Return as dict with raw analysis
                    return "Job analysis completed (non-structured)", {"raw_analysis": analysis}
                    
            except Exception as e:
                return f"Analysis failed: {str(e)}", {}
        
        @tool(response_format="content_and_artifact")
        def tailor_resume_with_llm(job_description: str, user_profile: dict) -> tuple[str, dict]:
            """
            Use AI to tailor resume content for specific job requirements.
            
            Args:
                job_description: The job description text
                user_profile: User's profile data dictionary
                
            Returns:
                Tuple of (tailoring summary, tailored resume dict as artifact)
            """
            import yaml
            
            try:
                tailoring_prompt = TAILORING_PROMPT.format(
                    job_description=job_description,
                    user_profile=yaml.dump(user_profile, default_flow_style=False)
                )
                
                response = self.llm.invoke(tailoring_prompt)
                tailored_yaml = response.content
                
                # Clean YAML response - remove markdown code fences if present
                if "```yaml" in tailored_yaml:
                    tailored_yaml = tailored_yaml.split("```yaml")[1].split("```")[0].strip()
                elif "```" in tailored_yaml:
                    tailored_yaml = tailored_yaml.split("```")[1].split("```")[0].strip()
                
                # Parse the tailored YAML back to dict
                tailored_data = yaml.safe_load(tailored_yaml)
                
                return "Resume successfully tailored to job requirements", tailored_data
                
            except Exception as e:
                return f"Tailoring failed: {str(e)}", user_profile
        
        @tool(response_format="content_and_artifact")
        def create_detailed_tailoring_analysis(
            job_analysis: Optional[dict] = None, 
            original_profile: Optional[dict] = None,
            tailored_profile: Optional[dict] = None
        ) -> tuple[str, str]:
            """
            Generate detailed report of changes made during tailoring.
            
            Args:
                job_analysis: Structured job analysis (optional)
                original_profile: Original user profile (optional)
                tailored_profile: Tailored resume data (optional)
                
            Returns:
                Tuple of (summary, detailed changes report as artifact)
            """
            import yaml
            
            try:
                # Check if we have required data
                if not tailored_profile:
                    return "Error: Missing tailored profile data", "Cannot generate report without tailored resume data"
                
                if not original_profile:
                    return "Error: Missing original profile data", "Cannot generate report without original profile data"
                
                # Generate a comparison prompt
                comparison_prompt = f"""
                Compare the original and tailored resumes and describe what changes were made.
                
                Original Profile:
                {yaml.dump(original_profile, default_flow_style=False)}
                
                Tailored Profile:
                {yaml.dump(tailored_profile, default_flow_style=False)}
                
                Job Analysis:
                {str(job_analysis)}
                Provide a detailed report of changes made and why they align with the job requirements.
                use the save_tailoring_report tool to save the report.
                """
                
                response = self.llm.invoke(comparison_prompt)
                changes_report = response.content
                
                return "Tailoring analysis completed", changes_report
                
            except Exception as e:
                return f"Analysis failed: {str(e)}", "Could not generate changes report"
        
        # Return all tools (simplified tools + LLM-enhanced tools)
        return [
            # Complete workflow tool
            create_tailored_resume_complete,
            # Basic artifact-based tools
            fetch_job_description,
            load_user_profile,
            parse_resume_yaml,
            build_html_resume,
            convert_html_to_pdf,
            save_tailoring_report,
            # LLM-powered tools
            analyze_job_with_llm,
            tailor_resume_with_llm,
            create_detailed_tailoring_analysis
        ]

    def _create_agent(self):
        """Create the LangChain agent with enhanced prompt"""
        # Enhanced prompt for CV tailoring with better data handling instructions
        enhanced_system_prompt = SYSTEM_PROMPT + """

RECOMMENDED: Use the create_tailored_resume_complete tool for a complete workflow!
This tool handles the entire process from job URL to PDF output in one step.

If you need to use individual tools, follow this CRITICAL WORKFLOW:

1. Fetch the job description using fetch_job_description(url)
   - Store the job description text for later use

2. Load user profile using load_user_profile(profile_path)
   - Store the original profile dict for later use  

3. Use tailor_resume_with_llm(job_description, user_profile) to create a tailored resume
   - Pass the job description string and user profile dict from steps 1 and 2
   - This returns a tuple: (message, tailored_resume_dict)
   - STORE THE TAILORED RESUME DICT - you will need it for later steps

4. Use analyze_job_with_llm(job_description) to analyze the job
   - Pass the job description from step 1
   - This returns a tuple: (message, job_analysis_dict)
   - STORE THE JOB ANALYSIS DICT

5. Build HTML using build_html_resume(resume_data)
   - Pass the tailored_resume_dict from step 3
   - This returns a tuple: (message, html_content)
   - STORE THE HTML CONTENT

6. Convert to PDF using convert_html_to_pdf(html_content, output_path)
   - Pass the html_content from step 5
   - Use output path like "outputs/test_resume.pdf"

7. Create analysis using create_detailed_tailoring_analysis(job_analysis, original_profile, tailored_profile)
   - Pass job_analysis_dict from step 4, original profile from step 2, and tailored_resume_dict from step 3
   - This returns a tuple: (message, detailed_report)
   - STORE THE DETAILED REPORT

8. Save the report using save_tailoring_report()
   - Pass appropriate parameters including the detailed_report from step 7

IMPORTANT: 
- Tools marked with response_format="content_and_artifact" return a TUPLE of (message, artifact)
- You MUST extract and use the artifact (second element) for subsequent tool calls
- DO NOT pass None or empty dicts to tools expecting data from previous steps
- ALWAYS pass the complete data structures between tools
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", enhanced_system_prompt),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        
        # Create executor
        return AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True,
            return_intermediate_steps=True  # Enable to see artifact passing
        )
    
    def run(self, query: str) -> str:
        """
        Run the agent with a user query.
        
        Args:
            query: The user's request or question
            
        Returns:
            The agent's response after executing necessary tools
        """
        try:
            result = self.agent_executor.invoke({"input": query})
            return result["output"]
        except Exception as e:
            return f"Error executing agent: {str(e)}"



if __name__ == "__main__":
    agent = LangChainCVAgent()

    

    response = agent.run("""Create a complete tailored resume for a the position.
    Use the job URL: https://www.google.com/about/careers/applications/jobs/results/115044372650566342-software-engineer-ii-ios-google-notifications?location=Tel%20Aviv%2C%20Israel&q=%22Software%20Engineer%22
    my profile is at data/user_profile_resume_format.yaml
    create a resume tailored to the job description based on my profile, and save it as pdf. also create a detailed report of changes made.
    Name the output: 'test_resume'""")
