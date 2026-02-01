# Jarvis AI Assistant

A versatile AI assistant with speech recognition, text-to-speech, image generation, and automation capabilities.

## Features

- **Voice Interaction**: Speak to Jarvis and hear responses
- **Text Chat**: Type messages when voice isn't practical
- **Image Generation**: Generate images based on text prompts
- **Web Search**: Get real-time information from the web
- **System Automation**: Control applications and perform system tasks
- **Modern GUI**: Clean, dark-themed interface with message bubbles

## Setup

### Prerequisites

- Python 3.8 or higher
- Required Python packages (install using `pip install -r Requirements.txt`)
- API keys for:
  - HuggingFace (image generation)
  - Cohere (chat capabilities)
  - Groq (optional, for enhanced responses)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Jarvis-AI.git
   cd Jarvis-AI
   ```

2. Install dependencies:
   ```
   pip install -r Requirements.txt
   ```

3. Set up environment variables:
   ```
   python setup_env.py
   ```
   This will create a `.env` file where you can enter your API keys.

### Configuration

The `.env` file contains important configuration settings:

```
Username=User                       # Your name
Assistantname=Jarvis                # Assistant name
InputLanguage=en-US                 # Speech recognition language
AssistantVoice=en-US-ChristopherNeural  # TTS voice
CohereAPIKey=your_cohere_api_key    # Cohere API key
GroqAPIKey=your_groq_api_key        # Groq API key
HuggingFaceAPIKey=your_huggingface_api_key  # HuggingFace API key
```

## Usage

1. Start the application:
   ```
   python main.py
   ```

2. Interact with Jarvis:
   - Click the microphone button to speak
   - Type in the text field for text input
   - Say "generate image [description]" to create images
   - Ask questions to get information from the web or chatbot

## Troubleshooting

### Speech Recognition Issues

If speech recognition stops working:
- Check your microphone connection
- Ensure you have a stable internet connection
- Try restarting the application
- Use the text input as an alternative

### Image Generation Issues

If image generation fails:
- Verify your HuggingFace API key is correct in the `.env` file
- Check your internet connection
- Run `python test_image_generation.py` to test the functionality
- Try simpler prompts with fewer details

### General Issues

- Run individual components for testing:
  ```
  python Backend/SpeechToText.py  # Test speech recognition
  python Backend/Imagegeneration.py  # Test image generation
  ```
- Check log messages in the console for error details

## Project Structure

- **Frontend/**: GUI and user interface components
  - **Files/**: Data files for GUI-backend communication
  - **Graphics/**: Icons and visual assets
  - **GUI.py**: Main GUI implementation

- **Backend/**: Core functionality modules
  - **SpeechToText.py**: Speech recognition
  - **textToSpeech.py**: Text-to-speech conversion
  - **Chatbot.py**: Chat functionality
  - **Imagegeneration.py**: Image generation
  - **RealtimeSearchEngine.py**: Web search capabilities
  - **Automation.py**: System automation tasks
  - **Model.py**: Decision-making model

- **Data/**: Storage for chat logs, generated images, etc.

## License

[Your License Information]

## Credits

[Your Credits Information] 