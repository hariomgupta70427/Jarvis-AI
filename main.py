from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition, reset_speech_recognition
from Backend.Chatbot import ChatBot
from Backend.textToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep, time
import subprocess
import threading
import json
import os
import sys
import traceback
import random

# Load environment variables with error handling
try:
    env_vars = dotenv_values(".env")
    Username = env_vars.get("Username", "User")  # Default to "User" if not found
    Assistantname = env_vars.get("Assistantname", "Jarvis")  # Default to "Jarvis" if not found
except Exception as e:
    print(f"Error loading .env file: {e}. Using default values.")
    Username = "User"
    Assistantname = "Jarvis"

DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?'''

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

# Counter for speech recognition resets
speech_recognition_count = 0
last_reset_time = time()

# Path to the text input file
text_input_file = TempDirectoryPath('TextInput.data')

def ShowDefaultChatIfNoChats():
    try:
        # Ensure Data directory exists
        os.makedirs("Data", exist_ok=True)
        
        # Check if ChatLog.json exists and has content
        chat_log_path = r'Data/ChatLog.json'
        if not os.path.exists(chat_log_path) or os.path.getsize(chat_log_path) < 5:
            # Create a default ChatLog.json
            with open(chat_log_path, "w", encoding="utf-8") as file:
                file.write("[]")
            
            # Write default messages to data files
            with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                file.write("")

            with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
                file.write(DefaultMessage)
    except Exception as e:
        print(f"Error in ShowDefaultChatIfNoChats: {e}")
        traceback.print_exc()
        # Create a default ChatLog.json if it doesn't exist
        os.makedirs("Data", exist_ok=True)
        with open(r'Data/ChatLog.json', "w", encoding="utf-8") as file:
            file.write("[]")

def ReadChatLogJson():
    try:
        with open(r'Data/ChatLog.json', 'r', encoding='utf-8') as file:
            chatlog_data = json.load(file)
        return chatlog_data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading ChatLog.json: {e}")
        # Create a new empty chat log if there was an error
        with open(r'Data/ChatLog.json', "w", encoding="utf-8") as file:
            file.write("[]")
        return []

def ChatLogIntegration():
    try:
        json_data = ReadChatLogJson()
        formatted_chatlog = ""
        for entry in json_data:
            if entry["role"] == "user":
                formatted_chatlog += f"User: {entry['content']}\n"
            elif entry["role"] == "assistant":
                formatted_chatlog += f"Assistant: {entry['content']}\n"

        formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
        formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write(AnswerModifier(formatted_chatlog))
    except Exception as e:
        print(f"Error in ChatLogIntegration: {e}")
        traceback.print_exc()

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding="utf-8") as file:
            Data = file.read()
        
        if len(str(Data)) > 0:
            lines = Data.split('\n')
            result = '\n'.join(lines)
            
            with open(TempDirectoryPath('Responses.data'), "w", encoding="utf-8") as file:
                file.write(result)
    except Exception as e:
        print(f"Error in ShowChatsOnGUI: {e}")
        traceback.print_exc()

def InitialExecution():
    try:
        # Ensure all necessary directories exist
        os.makedirs("Data", exist_ok=True)
        os.makedirs("Frontend/Files", exist_ok=True)
        
        # Initialize data files
        with open(r'Frontend/Files/ImageGeneration.data', "w") as file:
            file.write("False,False")
            
        # Initialize text input file
        with open(text_input_file, "w", encoding="utf-8") as file:
            file.write("")
            
        SetMicrophoneStatus("True")
        ShowTextToScreen("")
        ShowDefaultChatIfNoChats()
        ChatLogIntegration()
        ShowChatsOnGUI()
        SetAssistantStatus("Available...")
    except Exception as e:
        print(f"Error in InitialExecution: {e}")
        traceback.print_exc()

InitialExecution()

def handle_image_generation(image_query):
    """Handle image generation requests"""
    try:
        # Ensure the prompt is properly formatted
        if image_query.startswith("generate image"):
            prompt = image_query.replace("generate image", "").strip()
        else:
            prompt = image_query.strip()
            
        print(f"Generating image with prompt: {prompt}")
        
        # Write to the image generation data file
        with open(r'Frontend/Files/ImageGeneration.data', "w") as file:
            file.write(f"{prompt},True")
        
        # Start the image generation process
        SetAssistantStatus("Generating image...")
        
        # Run the image generation script
        p = subprocess.Popen([sys.executable, r'Backend/Imagegeneration.py'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE, shell=False)
        subprocesses.append(p)
        
        # Wait for the process to complete or timeout
        try:
            stdout, stderr = p.communicate(timeout=180)  # Increased timeout to 3 minutes
            
            # Check for errors in stderr
            if stderr:
                error_text = stderr.decode('utf-8', errors='ignore')
                if error_text.strip():
                    print(f"Image generation error: {error_text}")
                    
            if p.returncode != 0:
                print(f"Image generation process exited with code {p.returncode}")
                
                # Check the status file for more detailed error information
                try:
                    with open(r'Frontend/Files/ImageGeneration.data', "r") as file:
                        status = file.read().strip()
                        if "API_KEY_MISSING" in status:
                            return False, "I need a valid HuggingFace API key to generate images. Please run setup_env.py to configure it."
                        elif "ERROR" in status:
                            return False, "I encountered an error while generating the image."
                except Exception:
                    pass
                    
                return False, "Image generation failed. Please check the console for error details."
                
            # Check if images were actually generated
            from Backend.Imagegeneration import sanitize_prompt
            safe_prompt = sanitize_prompt(prompt)
            image_files = [f for f in os.listdir("Data") if f.startswith(f"generate_image_{safe_prompt}") and f.endswith(".jpg")]
            
            if not image_files:
                return False, "I couldn't generate any images. The API might be experiencing issues."
                
            return True, f"I've generated {len(image_files)} images of {prompt} for you."
            
        except subprocess.TimeoutExpired:
            p.kill()
            print("Image generation timed out")
            return False, "Image generation took too long and timed out. Please try again with a simpler prompt."
            
    except Exception as e:
        print(f"Error in handle_image_generation: {e}")
        traceback.print_exc()
        return False, "I encountered an unexpected error while generating the image."

def check_for_text_input():
    """Check if there's text input from the GUI"""
    try:
        if os.path.exists(text_input_file):
            with open(text_input_file, "r", encoding="utf-8") as file:
                text = file.read().strip()
                
            if text:
                # Clear the file after reading
                with open(text_input_file, "w", encoding="utf-8") as file:
                    file.write("")
                    
                return text
        return None
    except Exception as e:
        print(f"Error checking for text input: {e}")
        traceback.print_exc()
        return None

def process_query(Query):
    """Process a query (from speech or text input)"""
    global speech_recognition_count
    
    try:
        ShowTextToScreen(f"{Username} : {Query}")
        SetAssistantStatus("Thinking ...")
        
        # Get decision from first layer model
        try:
            Decision = FirstLayerDMM(Query)
            print(f"\nDecision : {Decision}\n")
        except Exception as e:
            print(f"Error in FirstLayerDMM: {e}")
            traceback.print_exc()
            Decision = ["general " + Query]  # Default to general query if decision making fails

        G = any([i for i in Decision if i.startswith("general")])
        R = any([i for i in Decision if i.startswith("realtime")])

        # Merge queries for general and realtime decisions
        try:
            Mearged_query = " and ".join(
                [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
            )
        except Exception as e:
            print(f"Error merging queries: {e}")
            Mearged_query = Query  # Use original query if merging fails

        # Check for image generation requests
        ImageExecution = False
        ImageGenerationQuery = ""
        for queries in Decision:
            if "generate image" in queries:
                ImageGenerationQuery = str(queries)
                ImageExecution = True
                break

        # Check for automation tasks
        TaskExecution = False
        for queries in Decision:
            if not TaskExecution:
                if any(queries.startswith(func) for func in Functions):
                    try:
                        run(Automation(list(Decision)))
                        TaskExecution = True
                    except Exception as e:
                        print(f"Error in Automation: {e}")
                        traceback.print_exc()

        # Handle image generation
        if ImageExecution:
            try:
                # Inform user that we're generating an image
                image_prompt = ImageGenerationQuery.replace("generate image", "").strip()
                response = f"I'll generate images of {image_prompt} for you."
                ShowTextToScreen(f"{Assistantname} : {response}")
                SetAssistantStatus("Generating images...")
                TextToSpeech(response)
                
                # Handle the image generation
                success, message = handle_image_generation(ImageGenerationQuery)
                
                ShowTextToScreen(f"{Assistantname} : {message}")
                TextToSpeech(message)
                
                return True
                
            except Exception as e:
                print(f"Error starting ImageGeneration.py: {e}")
                traceback.print_exc()
                error_msg = "I encountered an error while trying to generate the image."
                ShowTextToScreen(f"{Assistantname} : {error_msg}")
                TextToSpeech(error_msg)
                return False

        # Handle realtime and general queries
        if G and R or R:
            try:
                SetAssistantStatus("Searching ...")
                Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                return True
            except Exception as e:
                print(f"Error in RealtimeSearchEngine: {e}")
                traceback.print_exc()
                Answer = "I encountered an error while searching. Please try again."
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                TextToSpeech(Answer)
                return False
        else:
            for Queries in Decision:
                try:
                    if "general" in Queries:
                        SetAssistantStatus("Thinking ...")
                        QueryFinal = Queries.replace("general ", "")
                        Answer = ChatBot(QueryModifier(QueryFinal))
                        ShowTextToScreen(f"{Assistantname} : {Answer}")
                        SetAssistantStatus("Answering ...")
                        TextToSpeech(Answer)
                        return True

                    elif "realtime" in Queries:
                        SetAssistantStatus("Searching ...")
                        QueryFinal = Queries.replace("realtime ", "")
                        Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                        ShowTextToScreen(f"{Assistantname} : {Answer}")
                        SetAssistantStatus("Answering ...")
                        TextToSpeech(Answer)
                        return True

                    elif "exit" in Queries:
                        QueryFinal = "Okay, Bye!"
                        Answer = ChatBot(QueryModifier(QueryFinal))
                        ShowTextToScreen(f"{Assistantname} : {Answer}")
                        SetAssistantStatus("Answering ...")
                        TextToSpeech(Answer)
                        SetAssistantStatus("Exiting...")
                        
                        # Clean up processes before exiting
                        cleanup_resources()
                        sys.exit(0)
                except Exception as e:
                    print(f"Error processing query '{Queries}': {e}")
                    traceback.print_exc()
        
        # If no decision was made, return a default message
        SetAssistantStatus("Thinking ...")
        Answer = "I'm not sure how to respond to that. Could you please rephrase?"
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering ...")
        TextToSpeech(Answer)
        return True
        
    except Exception as e:
        print(f"Error in process_query: {e}")
        traceback.print_exc()
        SetAssistantStatus("Error occurred")
        Answer = "I encountered an error. Please try again."
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        TextToSpeech(Answer)
        return False

def MainExecution():
    global speech_recognition_count, last_reset_time
    
    try:
        # Check if we need to reset speech recognition
        current_time = time()
        if speech_recognition_count >= 3 or (current_time - last_reset_time) > 300:  # Reset after 3 uses or 5 minutes
            print("Periodic reset of speech recognition...")
            reset_speech_recognition()
            speech_recognition_count = 0
            last_reset_time = current_time
        
        # First check for text input from GUI
        text_input = check_for_text_input()
        if text_input:
            print(f"Processing text input: {text_input}")
            return process_query(text_input)
            
        # If no text input, try speech recognition
        SetAssistantStatus("Listening ...")
        Query = SpeechRecognition()
        speech_recognition_count += 1
        
        # Check if speech recognition returned a valid query
        if not Query or Query == "I'm having trouble hearing you. Please check your microphone settings.":
            SetAssistantStatus("Speech recognition failed")
            ShowTextToScreen(f"{Assistantname} : I'm having trouble hearing you. Please check your microphone settings or type your message.")
            TextToSpeech("I'm having trouble hearing you. Please check your microphone settings or type your message.")
            sleep(2)
            SetAssistantStatus("Available...")
            return False
            
        return process_query(Query)
        
    except Exception as e:
        print(f"Error in MainExecution: {e}")
        traceback.print_exc()
        SetAssistantStatus("Error occurred")
        Answer = "I encountered an error. Please try again."
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        TextToSpeech(Answer)
        return False

def FirstThread():
    while True:
        try:
            CurrentStatus = GetMicrophoneStatus()

            if CurrentStatus == "True":
                result = MainExecution()
                # Add a short delay after processing to prevent CPU overuse
                sleep(1)
                if result:
                    SetAssistantStatus("Available...")
            else:
                AIStatus = GetAssistantStatus()

                if "Available..." in AIStatus:
                    sleep(0.1)
                else:
                    SetAssistantStatus("Available...")
        except Exception as e:
            print(f"Error in FirstThread: {e}")
            traceback.print_exc()
            sleep(1)  # Sleep briefly before continuing the loop

def SecondThread():
    try:
        GraphicalUserInterface()
    except Exception as e:
        print(f"Error in GUI: {e}")
        traceback.print_exc()
        sys.exit(1)  # Exit if GUI fails

def cleanup_resources():
    # Terminate all subprocesses
    for p in subprocesses:
        try:
            p.terminate()
        except Exception as e:
            print(f"Error terminating subprocess: {e}")

if __name__ == "__main__":
    try:
        # Make sure all necessary directories exist
        os.makedirs("Data", exist_ok=True)
        os.makedirs("Frontend/Files", exist_ok=True)
        
        # Create a default .env file if it doesn't exist
        if not os.path.exists(".env"):
            print("Creating default .env file...")
            with open(".env", "w") as f:
                f.write("Username=User\n")
                f.write("Assistantname=Jarvis\n")
                f.write("InputLanguage=en-US\n")
                f.write("AssistantVoice=en-US-ChristopherNeural\n")
                f.write("CohereAPIKey=your_cohere_api_key\n")
                f.write("GroqAPIKey=your_groq_api_key\n")
                f.write("HuggingFaceAPIKey=your_huggingface_api_key\n")
        
        thread1 = threading.Thread(target=FirstThread, daemon=True)
        thread1.start()
        SecondThread()
    except KeyboardInterrupt:
        print("Application terminated by user")
    except Exception as e:
        print(f"Error in main execution: {e}")
        traceback.print_exc()
    finally:
        cleanup_resources()




