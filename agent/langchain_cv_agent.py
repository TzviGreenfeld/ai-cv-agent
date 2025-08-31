
import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from langchain_openai import AzureChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Import our existing tools
from tools.job_reader import read_job_description
from tools.cv_builder import ResumeData, generate_cv_html
from tools.pdf_exporter import html_file_to_pdf
from tools.user_profile import read_user_profile
from utils.resume_parser import load_yaml_to_resume_data

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
    """Simple CV Agent using LangChain with existing tools"""
    
    def __init__(self):
        """Initialize the agent with Azure OpenAI"""
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
        """Wrap existing tools for LangChain"""
        
        @tool
        def read_job(url: str) -> str:
            """Fetch and extract job description from a URL"""
            return read_job_description(url)
        
        @tool
        def get_user_profile() -> str:
            """Get the user's profile information"""
            profile = read_user_profile()
            return str(profile)
        
        @tool
        def create_tailored_resume_yaml(job_description: str, output_path: str = "outputs/tailored_resume.yaml") -> str:
            """Create a tailored resume YAML file based on job description and user profile"""
            import yaml
            
            # Get the user's base profile
            user_profile = read_user_profile()
            
            # Use LLM to create tailored version
            tailoring_prompt = TAILORING_PROMPT.format(
                job_description=job_description,
                user_profile=yaml.dump(user_profile, default_flow_style=False)
            )

            response = self.llm.invoke(tailoring_prompt)
            tailored_yaml = response.content
            
            # Save the tailored YAML
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(tailored_yaml)
            
            return f"Tailored resume YAML created at: {output_path}"
        
        @tool
        def build_resume_from_yaml(yaml_path: str, output_path: str = "outputs/resume.html") -> str:
            """Build an HTML resume from a YAML file"""
            resume_data = load_yaml_to_resume_data(yaml_path)
            generate_cv_html(resume_data, output_path)
            return f"Resume HTML created at: {output_path}"
        
        @tool
        def export_to_pdf(html_path: str, pdf_path: str = None) -> str:
            """Convert HTML resume to PDF"""
            if not pdf_path:
                pdf_path = html_path.replace('.html', '.pdf')
            html_file_to_pdf(html_path, pdf_path)
            return f"PDF created at: {pdf_path}"

        @tool
        def analyze_job_posting(job_url: str) -> str:
            """Analyze a job posting and extract key requirements, skills, and keywords"""
            import json
            
            job_description = read_job_description(job_url)
            
            analysis_prompt = JOB_ANALYSIS_PROMPT.format(
                job_description=job_description
            )

            response = self.llm.invoke(analysis_prompt)
            job_analysis = response.content
            
            # Clean JSON if wrapped in code blocks
            if "```json" in job_analysis:
                job_analysis = job_analysis.split("```json")[1].split("```")[0].strip()
            elif "```" in job_analysis:
                job_analysis = job_analysis.split("```")[1].split("```")[0].strip()
            
            # Validate it's proper JSON
            try:
                json.loads(job_analysis)
            except json.JSONDecodeError:
                # If not valid JSON, return as structured text
                return response.content
            
            return job_analysis
        
        @tool # just for debugging
        def create_complete_tailored_resume_with_analysis(job_url: str, output_name: str = "tailored_resume") -> str:
            """Complete workflow with detailed analysis: read job, analyze changes, create tailored resume, and export all formats"""
            import yaml
            import json
            from datetime import datetime
            
            # Create output directory if it doesn't exist
            os.makedirs("outputs", exist_ok=True)
            
            # Step 1: Use the analyze_job_posting tool to get structured analysis
            job_analysis = analyze_job_posting(job_url)
            
            
            # Save job analysis
            analysis_path = f"outputs/debug/{output_name}_job_analysis.json"
            with open(analysis_path, 'w', encoding='utf-8') as f:
                f.write(job_analysis)
            
            # Step 2: Get user profile
            user_profile = read_user_profile()
            
            # Step 3: Create tailored resume with change tracking
            tailoring_prompt = DETAILED_TAILORING_PROMPT.format(
                job_analysis=job_analysis,
                user_profile=yaml.dump(user_profile, default_flow_style=False)
            )

            response = self.llm.invoke(tailoring_prompt)
            full_response = response.content
            
            # Extract YAML and changes
            yaml_start = full_response.find("[RESUME_YAML]") + len("[RESUME_YAML]")
            yaml_end = full_response.find("[/RESUME_YAML]")
            tailored_yaml = full_response[yaml_start:yaml_end].strip()
            
            changes_start = full_response.find("[CHANGES_MADE]") + len("[CHANGES_MADE]")
            changes_end = full_response.find("[/CHANGES_MADE]")
            changes_made = full_response[changes_start:changes_end].strip() if changes_start > len("[CHANGES_MADE]") - 1 else "No detailed changes provided"
            
            # Save tailored YAML
            yaml_path = f"outputs/{output_name}.yaml"
            with open(yaml_path, 'w', encoding='utf-8') as f:
                f.write(tailored_yaml)
            
            # Save changes report
            changes_path = f"outputs/debug/{output_name}_changes_report.txt"
            with open(changes_path, 'w', encoding='utf-8') as f:
                f.write("RESUME TAILORING REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Job URL: {job_url}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("JOB ANALYSIS:\n")
                f.write("-" * 30 + "\n")
                try:
                    job_data = json.loads(job_analysis)
                    f.write(f"Company: {job_data.get('company', 'N/A')}\n")
                    f.write(f"Role: {job_data.get('role', 'N/A')}\n")
                    f.write(f"Key Requirements: {', '.join(job_data.get('key_requirements', []))}\n")
                    f.write(f"Important Keywords: {', '.join(job_data.get('keywords_for_ats', []))}\n")
                except:
                    f.write(job_analysis + "\n")
                f.write("\nCHANGES MADE TO RESUME:\n")
                f.write("-" * 30 + "\n")
                f.write(changes_made)
            
            # Step 4: Convert YAML to ResumeData and generate HTML
            resume_data = load_yaml_to_resume_data(yaml_path)
            html_path = f"outputs/{output_name}.html"
            generate_cv_html(resume_data, html_path)
            
            # Step 5: Convert HTML to PDF
            pdf_path = f"outputs/{output_name}.pdf"
            html_file_to_pdf(html_path, pdf_path)
            
            # Create summary
            summary = f"""✅ Complete! Created:
                    - Tailored YAML: {yaml_path}
                    - HTML Resume: {html_path}
                    - PDF Resume: {pdf_path}
                    - Job Analysis: {analysis_path}
                    - Changes Report: {changes_path}

                    📋 JOB ANALYSIS SUMMARY:
                    {job_analysis}

                    📝 KEY CHANGES MADE:
                    {changes_made[:500]}...

                    The resume has been optimized for the job posting with relevant keywords and tailored content.
                    Check the changes report for full details."""
            
            return summary

        return [read_job, get_user_profile, create_tailored_resume_yaml, build_resume_from_yaml, export_to_pdf, analyze_job_posting, create_complete_tailored_resume_with_analysis]


    def _create_agent(self):
        """Create the LangChain agent"""
        # Enhanced prompt for CV tailoring
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        
        # Create executor
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def run(self, query: str) -> str:
        """Run the agent with a query"""
        result = self.agent_executor.invoke({"input": query})
        return result["output"]

# Simple test
if __name__ == "__main__":
    print("Testing LangChain CV Agent...")
    print("="*50)
    
    agent = LangChainCVAgent()
    
    # # Test 1: Basic profile check
    # print("\nTest 1: Checking user profile")
    # response = agent.run("Show me my profile")
    # print(f"Response: {response[:300]}...")
    
    # Test 2: Complete workflow
    print("Creating a tailored resume")
    print("\n" + "="*50)
    response = agent.run("""Create a complete tailored resume for a the position.
    Use the job URL: https://www.activefence.com/careers/?comeet_pos=FD.B54&coref=1.10.r94_41D&t=1756629558672
    Name the output: 'test_resume'""")
    print(f"\nResponse: {response}")
    
    print("\n" + "="*50)
    print("complete! Check the 'outputs' directory for generated files.")
