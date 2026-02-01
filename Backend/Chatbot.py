from groq import Groq  # Importing the Groq library to use its API.
from json import load, dump  # Importing functions to read and write JSON files.
import datetime  # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values  # Importing dotenv_values to read environment variables from a .env file.

# Load environment variables from the .env file.
try:
    env_vars = dotenv_values(".env")
    # Retrieve specific environment variables for username, assistant name, and API key.
    Username = env_vars.get("Username", "User")
    Assistantname = env_vars.get("Assistantname", "Jarvis")
    GroqAPIKey = env_vars.get("GroqAPIKey")
except Exception as e:
    print(f"Error loading .env file: {e}")
    Username = "User"
    Assistantname = "Jarvis"
    GroqAPIKey = None

# Initialize the Groq client using the provided API key.
client = Groq(api_key=GroqAPIKey)

# Define a system message that provides context to the AI chatbot about its role and behavior.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.

Instructions for your responses:
1. Provide detailed and descriptive answers to questions. Aim for 3-5 sentences minimum for most responses.
2. Include relevant facts, examples, and context in your answers.
3. Be conversational and engaging, but maintain professionalism.
4. Reply in only English, even if the question is in another language.
5. When explaining complex topics, break them down into clear, understandable parts.
6. For factual questions, provide comprehensive information rather than brief answers.
7. For opinion-based questions, present multiple perspectives when appropriate.
8. Do not mention your training data or model limitations.

Remember that users want informative, thorough responses that demonstrate your knowledge and helpfulness.
"""

# A list of system instructions for the chatbot.
SystemChatBot = [
    {"role": "system", "content": System}
]

# Function to get real-time date and time information.
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    return (f"Please use this real-time information if needed,\n"
            f"Day: {current_date_time.strftime('%A')}\n"
            f"Date: {current_date_time.strftime('%d')}\n"
            f"Month: {current_date_time.strftime('%B')}\n"
            f"Year: {current_date_time.strftime('%Y')}\n"
            f"Time: {current_date_time.strftime('%H')} hours {current_date_time.strftime('%M')} minutes {current_date_time.strftime('%S')} seconds.\n")

# Function to modify the chatbot's response for better formatting.
def AnswerModifier(Answer):
    return '\n'.join([line for line in Answer.split('\n') if line.strip()])

# Function to load chat history
def load_chat_log():
    try:
        with open(r"Data/ChatLog.json", "r") as f:
            return load(f)
    except (FileNotFoundError, ValueError):
        return []

# Function to save chat history
def save_chat_log(messages):
    with open(r"Data/ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

# Main chatbot function to handle user queries.
def ChatBot(Query):
    """This function sends the user's query to the chatbot and returns the AI's response."""
    try:
        messages = load_chat_log()
        messages.append({"role": "user", "content": Query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",  # Specify the AI model to use.
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=2048,  # Increased from 1024 to allow for more detailed responses
            temperature=0.8,  # Slightly increased for more creative responses
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""  # Initialize an empty string to store the AI's response.
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        save_chat_log(messages)
        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        save_chat_log([])  # Reset chat log on failure
        return ChatBot(Query)  # Retry the query after resetting the log.

# Main program entry point.
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        print(ChatBot(user_input))
