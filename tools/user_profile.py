import yaml
from pathlib import Path

def read_user_profile(file_path: str = "data/user_profile.yaml") -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"{file_path} not found")
    with open(path, "r") as f:
        return yaml.safe_load(f)
