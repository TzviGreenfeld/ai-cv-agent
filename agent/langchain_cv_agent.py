import os
import sys
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
                
                # Parse the tailored YAML back to dict
                tailored_data = yaml.safe_load(tailored_yaml)
                
                return "Resume successfully tailored to job requirements", tailored_data
                
            except Exception as e:
                return f"Tailoring failed: {str(e)}", user_profile
        
        @tool(response_format="content_and_artifact")
        def create_detailed_tailoring_analysis(
            job_analysis: dict, 
            original_profile: dict,
            tailored_profile: dict
        ) -> tuple[str, str]:
            """
            Generate detailed report of changes made during tailoring.
            
            Args:
                job_analysis: Structured job analysis
                original_profile: Original user profile
                tailored_profile: Tailored resume data
                
            Returns:
                Tuple of (summary, detailed changes report as artifact)
            """
            import yaml
            
            try:
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
        # Enhanced prompt for CV tailoring
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
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

    # Test artifact flow
    print("\n📋 Testing artifact flow with simple query:")
    print("-" * 60)
    
    test_query = "Load my user profile and show me the structure"
    print(f"Query: {test_query}")
    
    response = agent.run(test_query)
    print(f"\nResponse: {response}...")
    
    print("\n" + "=" * 60)


    response = agent.run("""Create a complete tailored resume for a the position.
    Use the job URL: https://www.google.com/about/careers/applications/jobs/results/115044372650566342-software-engineer-ii-ios-google-notifications?location=Tel%20Aviv%2C%20Israel&q=%22Software%20Engineer%22
    my profile is at data/user_profile_resume_format.yaml
    create a resume tailored to the job description based on my profile, and save it as pdf. also create a detailed report of changes made.
    Name the output: 'test_resume'""")