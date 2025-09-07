import yaml
from pathlib import Path

def read_user_profile(yaml_path: str = "data/user_profile_resume_format.yaml") -> dict:
    if not Path(yaml_path).exists():
        raise FileNotFoundError(f"YAML file not found: {yaml_path}")
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            raw_data = yaml.safe_load(f)
            if raw_data is None:
                raise ValueError("YAML file is empty or invalid")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return raw_data

if __name__ == "__main__":
    # Test reading user profile
    try:
        profile = read_user_profile("data/user_profile_resume_format.yaml")
        print("User Profile Data:")
        print(profile)
    except Exception as e:
        print(f"Error: {e}")