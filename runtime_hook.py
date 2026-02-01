import os
import sys
import tempfile
import shutil

def create_required_directories():
    """Create required directories if they don't exist"""
    directories = ['Data', 'Frontend/Files']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def setup_environment():
    """Set up the environment for the frozen application"""
    # Get the base directory for the application
    if getattr(sys, 'frozen', False):
        # Running as a bundled executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # Running in a normal Python environment
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create a temporary directory for runtime files if needed
    temp_dir = os.path.join(tempfile.gettempdir(), 'JarvisAI')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Set environment variable for the application to know where to find resources
    os.environ['JARVIS_BASE_DIR'] = base_dir
    os.environ['JARVIS_TEMP_DIR'] = temp_dir
    
    # Create required directories
    create_required_directories()
    
    # Ensure .env file exists
    env_path = os.path.join(base_dir, '.env')
    if not os.path.exists(env_path):
        # Create a default .env file
        with open(env_path, 'w') as f:
            f.write("Username=User\n")
            f.write("Assistantname=Jarvis\n")
            f.write("InputLanguage=en-US\n")
            f.write("AssistantVoice=en-US-ChristopherNeural\n")
            f.write("CohereAPIKey=your_cohere_api_key\n")
            f.write("GroqAPIKey=your_groq_api_key\n")
            f.write("HuggingFaceAPIKey=your_huggingface_api_key\n")

# Run setup when this module is imported
setup_environment() 