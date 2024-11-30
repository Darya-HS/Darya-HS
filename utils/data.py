
import json
import os

# Define the file path for profiles.json
PROFILES = "profiles.json"

# Global user profiles dictionary
user_profiles = {}

def save_profiles():
    """Save user profiles to a JSON file"""
    global user_profiles
    try:
        with open(PROFILES, "w") as file:
            json.dump(user_profiles, file, indent=4)
    except Exception as e:
        print(f"Error saving profiles: {e}")

def load_profiles():
    """Load user profiles from a JSON file"""
    global user_profiles
    try:
        if os.path.exists(PROFILES):
            with open(PROFILES, "r") as file:
                user_profiles = json.load(file)
        else:
            print("Profiles file not found. Starting fresh")
    except Exception as e:
        print(f"Error loading profiles: {e}")

load_profiles()