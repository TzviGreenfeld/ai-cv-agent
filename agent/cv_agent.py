from langchain.agents import initialize_agent, Tool
from langchain_openai import AzureChatOpenAI

from tools.job_reader import read_job_description
from tools.user_data import read_user_data
from tools.cv_builder import generate_cv_html
from tools.pdf_exporter import export_pdf

def create_cv_agent():
    tools = [
        Tool(name="read_job_description", func=read_job_description,
             description="Reads a job description from a URL"),
        Tool(name="read_user_data", func=read_user_data,
             description="Reads user-provided data like projects or skills"),
        Tool(name="generate_cv_html", func=generate_cv_html,
             description="Fills CV template with tailored content"),
        Tool(name="export_pdf", func=export_pdf,
             description="Exports CV HTML into PDF"),
    ]

    llm = AzureChatOpenAI(
        deployment_name="gpt-4", 
        temperature=0
    )

    return initialize_agent(tools, llm, agent="zero-shot-react-description")
