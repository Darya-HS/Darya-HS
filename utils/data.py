# This file is part of Study Planner Bot.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import json
import os

PROFILES = "profiles.json"
user_profiles = {}

def save_profiles():
    global user_profiles
    try:
        with open(PROFILES, "w") as file:
            json.dump(user_profiles, file, indent=4)
    except Exception as e:
        print(f"Error saving profiles: {e}")

def load_profiles():
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