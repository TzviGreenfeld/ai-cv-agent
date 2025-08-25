import os

# Define folder structure
folders = [
    "data",
    "templates",
    "outputs",
    "tools",
    "agent"
]

# Define files
files = [
    "data/user_profile.yaml",
    "templates/base_template.html",
    "outputs/.gitkeep",   # so git tracks empty folder
    "tools/__init__.py",
    "tools/job_reader.py",
    "tools/user_profile.py",
    "tools/cv_builder.py",
    "tools/pdf_exporter.py",
    "agent/cv_agent.py",
    "main.py",
    "requirements.txt"
]

def create_structure():
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")
    
    for file in files:
        with open(file, "w", encoding="utf-8") as f:
            pass
        print(f"Created file: {file}")

if __name__ == "__main__":
    create_structure()
    print("\n✅ Project structure created successfully.")
