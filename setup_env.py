import os

def setup_env():
    """Create or update the .env file with required API keys"""
    
    # Check if .env file exists
    if os.path.exists(".env"):
        print("Found existing .env file. Checking for required keys...")
        
        # Read existing .env file
        with open(".env", "r") as f:
            env_content = f.read()
            
        # Parse existing values
        env_vars = {}
        for line in env_content.split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    else:
        print("Creating new .env file...")
        env_vars = {}
    
    # Set default values if not present
    if "Username" not in env_vars:
        env_vars["Username"] = "User"
    
    if "Assistantname" not in env_vars:
        env_vars["Assistantname"] = "Jarvis"
    
    if "InputLanguage" not in env_vars:
        env_vars["InputLanguage"] = "en-US"
    
    if "AssistantVoice" not in env_vars:
        env_vars["AssistantVoice"] = "en-US-ChristopherNeural"
    
    # Check for API keys
    api_keys = {
        "CohereAPIKey": "Cohere API key",
        "GroqAPIKey": "Groq API key",
        "HuggingFaceAPIKey": "HuggingFace API key"
    }
    
    for key, description in api_keys.items():
        if key not in env_vars or env_vars[key] == "your_" + key.lower():
            print(f"\n{description} is required for full functionality.")
            new_value = input(f"Enter your {description} (or press Enter to skip for now): ")
            if new_value:
                env_vars[key] = new_value
            else:
                env_vars[key] = "your_" + key.lower()
                print(f"Warning: {description} not set. Some features may not work correctly.")
    
    # Write updated .env file
    with open(".env", "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print("\n.env file has been updated successfully!")
    print("You can run this script again anytime to update your API keys.")

if __name__ == "__main__":
    setup_env() 