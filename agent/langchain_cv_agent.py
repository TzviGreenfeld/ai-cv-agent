
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
from tools.cv_builder import generate_cv_html
from tools.pdf_exporter import html_file_to_pdf
from tools.user_profile import read_user_profile

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
        def agent_read_job_description(url: str) -> str:
            """Fetch and extract job description from a URL"""
            return read_job_description(url)
        
        @tool
        def get_user_profile() -> str:
            """Get the user's profile information"""
            profile = read_user_profile()
            return str(profile)
        
        @tool
        def build_resume(output_path: str = "outputs/resume.html") -> str:
            """Build an HTML resume from user profile"""
            profile = read_user_profile()
            generate_cv_html(profile, output_path)
            return f"Resume created at: {output_path}"
        
        @tool
        def export_to_pdf(html_path: str, pdf_path: str = None) -> str:
            """Convert HTML resume to PDF"""
            if not pdf_path:
                pdf_path = html_path.replace('.html', '.pdf')
            html_file_to_pdf(html_path, pdf_path)
            return f"PDF created at: {pdf_path}"
        
        return [read_job_description, get_user_profile, build_resume, export_to_pdf]
    
    def _create_agent(self):
        """Create the LangChain agent"""
        # Simple prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful CV assistant. Use the available tools to help create tailored resumes."),
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
    
    agent = LangChainCVAgent()
    
    # Test query
    response = agent.run("Hello! Can you show me my profile?")
    print(f"\nResponse: {response}")
