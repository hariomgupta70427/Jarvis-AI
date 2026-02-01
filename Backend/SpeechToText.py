from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values

import os
import mtranslate as mt
import time
import speech_recognition as sr
import traceback
import random

# Load environment variables from the .env file.
try:
    env_vars = dotenv_values(".env")
    # Get the input language setting from the environment variables.
    InputLanguage = env_vars.get('InputLanguage', 'en-US')  # Default to en-US if not found
except Exception as e:
    print(f"Error loading .env file: {e}")
    InputLanguage = 'en-US'  # Default to English if there's an issue with .env

# Define the path for temporary files.
current_dir = os.getcwd()
TempDirPath = f"{current_dir}/Frontend/Files"
os.makedirs(TempDirPath, exist_ok=True)

# Global recognizer and microphone objects
recognizer = None
microphone = None

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    try:
        with open(f"{TempDirPath}/Status.data", "w", encoding="utf-8") as file:
            file.write(Status)
    except Exception as e:
        print(f"Error setting assistant status: {e}")

# Function to modify a query to ensure proper punctuation and formatting.
def QueryModifier(Query):
    if not Query:
        return "I didn't catch that."
        
    new_query = Query.lower().strip()
    query_words = new_query.split()
    
    if not query_words:
        return "I didn't catch that."
        
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    # Check if the query is a question and add a question mark if necessary.
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"

    else:
        # Add a period if the query is not a question.
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

# Function to translate text into English using the mtranslate library.
def UniversalTranslator(Text):
    try:
        english_translation = mt.translate(Text, "en", "auto")
        return english_translation.capitalize()
    except Exception as e:
        print(f"Error in translation: {e}")
        return Text.capitalize()

# Initialize speech recognition components
def initialize_speech_recognition():
    global recognizer, microphone
    
    try:
        # Create new instances to avoid potential resource issues
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        # List available microphones
        mic_list = sr.Microphone.list_microphone_names()
        print("Available microphones:")
        for i, mic_name in enumerate(mic_list):
            print(f"{i}: {mic_name}")
        
        # Adjust for ambient noise once at initialization
        with microphone as source:
            print("Initializing microphone and adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=2)
        
        # Set parameters for better recognition
        recognizer.pause_threshold = 1.0
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        
        print("Speech recognition initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing speech recognition: {e}")
        traceback.print_exc()
        return False

# Direct speech recognition using the system microphone
def native_speech_recognition():
    global recognizer, microphone
    
    # Ensure recognizer and microphone are initialized
    if recognizer is None or microphone is None:
        if not initialize_speech_recognition():
            return None
    
    try:
        with microphone as source:
            print("Listening... (native microphone)")
            SetAssistantStatus("Listening...")
            
            # Listen for speech with increased timeout
            print("Ready for speech input")
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=7)
            
            SetAssistantStatus("Processing...")
            
            # Try to recognize what was said with multiple language options
            try:
                # First try with specified language
                text = recognizer.recognize_google(audio, language=InputLanguage)
                print(f"Recognized: {text}")
            except:
                # If that fails, try with English
                try:
                    text = recognizer.recognize_google(audio, language="en-US")
                    print(f"Recognized with fallback to English: {text}")
                except:
                    # If that also fails, try with auto-detection
                    text = recognizer.recognize_google(audio)
                    print(f"Recognized with auto-detection: {text}")
            
            # If the input language is not English, translate it
            if InputLanguage.lower() != "en" and "en" not in InputLanguage.lower():
                SetAssistantStatus("Translating...")
                return QueryModifier(UniversalTranslator(text))
            else:
                return QueryModifier(text)
                
    except sr.WaitTimeoutError:
        print("Timeout - no speech detected")
        return None
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None
    except Exception as e:
        print(f"Error in native speech recognition: {e}")
        traceback.print_exc()
        
        # Try to reinitialize if there was an error
        print("Attempting to reinitialize speech recognition...")
        initialize_speech_recognition()
        return None

# Fallback to text input when speech recognition fails
def text_input_fallback():
    try:
        SetAssistantStatus("Speech recognition failed. Using text input...")
        print("\n>>> SPEECH RECOGNITION FAILED <<<")
        print(">>> Please type your command below <<<")
        text = input("Command: ")
        if text.strip():
            return text.strip()
        return None
    except Exception as e:
        print(f"Error in text input: {e}")
        return None

# Function to perform speech recognition.
def SpeechRecognition():
    # Initialize on first call
    global recognizer, microphone
    if recognizer is None or microphone is None:
        initialize_speech_recognition()
    
    # Try native speech recognition with multiple attempts
    max_attempts = 3
    current_attempt = 0
    
    while current_attempt < max_attempts:
        try:
            print(f"Speech recognition attempt {current_attempt + 1} of {max_attempts}")
            result = native_speech_recognition()
            if result:
                return result
            current_attempt += 1
            # Add a short delay between attempts to allow microphone to reset
            time.sleep(1)
        except Exception as e:
            print(f"Error during speech recognition attempt {current_attempt + 1}: {e}")
            traceback.print_exc()
            current_attempt += 1
            time.sleep(1)  # Short delay between attempts
    
    # If speech recognition fails, try text input as a fallback
    print("Speech recognition failed after multiple attempts")
    text_result = text_input_fallback()
    if text_result:
        return QueryModifier(text_result)
    
    # If all attempts fail, return a default message
    return "I'm having trouble hearing you. Please check your microphone settings."

# Reset speech recognition (call this when issues occur)
def reset_speech_recognition():
    global recognizer, microphone
    
    # Release resources if possible
    try:
        if microphone:
            del microphone
        if recognizer:
            del recognizer
    except:
        pass
    
    # Set to None to force reinitialization
    recognizer = None
    microphone = None
    
    # Reinitialize
    return initialize_speech_recognition()

# Main execution block.
if __name__ == "__main__":
    initialize_speech_recognition()
    while True:
        # Continuously perform speech recognition and print the recognized text.
        Text = SpeechRecognition()
        print(Text)
        
        # Reset after every 5 iterations to prevent resource issues
        if random.randint(1, 5) == 1:
            reset_speech_recognition()


