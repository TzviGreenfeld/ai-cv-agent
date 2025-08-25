from agent.cv_agent import create_cv_agent

def main():
    agent = create_cv_agent()
    result = agent.run(
        "Read the job description from 'https://example.com/job'. "
        "Use user data from 'data/employment.md', 'data/projects.md', 'data/skills.md'. "
        "Fill the 'templates/base_template.html' and export as PDF."
    )
    print("Agent result:", result)

if __name__ == "__main__":
    main()
