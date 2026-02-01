import asyncio
from random import randint
from PIL import Image
import requests
import os
from time import sleep
import traceback
from dotenv import dotenv_values
import sys

# Load environment variables with error handling
try:
    env_vars = dotenv_values(".env")
    HuggingFaceAPIKey = env_vars.get("HuggingFaceAPIKey")
    if not HuggingFaceAPIKey or HuggingFaceAPIKey == "your_huggingfaceapikey":
        print("Error: HuggingFaceAPIKey not found or not set in .env file")
        print("Please run setup_env.py to configure your API keys")
        # Write failure status to the data file
        os.makedirs("Frontend/Files", exist_ok=True)
        with open(r"Frontend/Files/ImageGeneration.data", "w") as f:
            f.write("False,API_KEY_MISSING")
        sys.exit(1)
except Exception as e:
    print(f"Error loading .env file: {e}")
    # Write failure status to the data file
    os.makedirs("Frontend/Files", exist_ok=True)
    with open(r"Frontend/Files/ImageGeneration.data", "w") as f:
        f.write("False,ENV_FILE_ERROR")
    sys.exit(1)

# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {HuggingFaceAPIKey}"}

# Function to extract the image prompt from the decision string
def extract_image_prompt(decision_string):
    if "generate image" in decision_string:
        # Extract the prompt part after "generate image"
        return decision_string.replace("generate image", "").strip()
    return decision_string.strip()

# Function to sanitize prompt for file naming
def sanitize_prompt(prompt):
    # Replace spaces with underscores and remove special characters
    sanitized = prompt.replace(" ", "_")
    sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
    return sanitized

# Function to open and display images
def open_images(prompt):
    folder_path = "Data"  # Folder where the images are stored
    
    # Use the same sanitization function for consistent naming
    safe_prompt = sanitize_prompt(prompt)
    
    # Generate the filenames for the images
    Files = [f"generate_image_{safe_prompt}{i}.jpg" for i in range(1, 4)]
    
    opened_images = 0
    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            opened_images += 1
            sleep(1)  # Pause for 1 second before showing the next image

        except IOError as e:
            print(f"Unable to open {image_path}: {e}")
    
    return opened_images > 0

# Async function to send a query to the Hugging Face API with retries
async def query(payload, max_retries=3, retry_delay=2):
    for attempt in range(max_retries):
        try:
            print(f"Sending request to API (attempt {attempt+1}/{max_retries}) with payload: {payload}")
            response = await asyncio.to_thread(
                requests.post, 
                API_URL, 
                headers=headers, 
                json=payload, 
                timeout=60
            )
            
            # Check if model is still loading
            if response.status_code == 503:
                estimated_time = response.json().get("estimated_time", 20)
                print(f"Model is loading. Waiting {estimated_time} seconds...")
                await asyncio.sleep(min(estimated_time, 30))  # Wait but cap at 30 seconds
                continue
                
            if response.status_code == 200:
                print("API request successful")
                return response.content  # Direct binary image data
            else:
                print(f"Error in response: {response.status_code}, {response.text}")
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    print(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    return None
        except requests.exceptions.Timeout:
            print(f"Request timed out (attempt {attempt+1}/{max_retries})")
            if attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)
                print(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                return None
        except Exception as e:
            print(f"Error in API request: {e}")
            traceback.print_exc()
            if attempt < max_retries - 1:
                wait_time = retry_delay * (attempt + 1)
                print(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                return None
    
    return None  # Return None if all retries failed

# Async function to generate images and save them
async def generate_images(prompt: str):
    # Ensure Data directory exists
    os.makedirs("Data", exist_ok=True)
    
    # Clean the prompt for better results
    clean_prompt = extract_image_prompt(prompt)
    print(f"Clean prompt for image generation: {clean_prompt}")
    
    # Create tasks for parallel image generation
    tasks = []
    for i in range(3):
        payload = {
            "inputs": f"{clean_prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",
            "wait_for_model": True
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
        # Add a slight delay between requests to avoid rate limiting
        await asyncio.sleep(1)

    print("Waiting for image generation tasks to complete...")
    image_data_list = await asyncio.gather(*tasks)
    
    success_count = 0
    # Use the same sanitization function for consistent naming
    safe_prompt = sanitize_prompt(clean_prompt)
    
    for i, image_data in enumerate(image_data_list):
        if image_data:
            file_path = f"Data/generate_image_{safe_prompt}{i + 1}.jpg"
            try:
                with open(file_path, "wb") as f:
                    f.write(image_data)
                print(f"Image {i+1} saved successfully at {file_path}!")
                success_count += 1
            except Exception as e:
                print(f"Error saving image {i+1}: {e}")
                traceback.print_exc()
    
    return success_count > 0

# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    try:
        print(f"Starting image generation for prompt: '{prompt}'")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(generate_images(prompt))
        
        if success:
            print("Images generated successfully, now opening them")
            return open_images(prompt)
        else:
            print("Failed to generate any images")
            return False
    except Exception as e:
        print(f"Error in GenerateImages: {e}")
        traceback.print_exc()
        return False

# Main loop to check and process image generation requests
def main():
    print("Image generation service started")
    
    try:
        # Ensure file exists and directory exists
        os.makedirs("Frontend/Files", exist_ok=True)
        file_path = r"Frontend/Files/ImageGeneration.data"
        
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("False,False")
                print("Created new ImageGeneration.data file")

        # Read the status and prompt from the data file
        with open(file_path, "r") as f:
            Data = f.read().strip()
            print(f"Read from ImageGeneration.data: '{Data}'")
        
        if not Data or "," not in Data:
            print("Invalid data format in ImageGeneration.data")
            with open(file_path, "w") as f:
                f.write("False,INVALID_FORMAT")
            return

        try:
            Prompt, Status = Data.split(",", 1)
            print(f"Parsed - Prompt: '{Prompt}', Status: '{Status}'")
        except ValueError:
            print(f"Invalid data format in ImageGeneration.data: {Data}")
            with open(file_path, "w") as f:
                f.write("False,INVALID_FORMAT")
            return

        # If the status indicates an image generation request
        if Status.strip().lower() == "true":
            print(f"Starting image generation for: '{Prompt.strip()}'")
            
            # First update status to processing
            with open(file_path, "w") as f:
                f.write(f"{Prompt},PROCESSING")
            
            success = GenerateImages(prompt=Prompt.strip())
            
            # Provide feedback on the result
            status_message = "True" if success else "Failed"
            
            # Reset the status after image generation
            with open(file_path, "w") as f:
                f.write(f"{Prompt},{status_message}")
            
            if success:
                print("Image generation completed successfully")
            else:
                print("Image generation failed")
        else:
            print(f"No image generation request found. Status: {Status}")

    except Exception as e:
        print(f"Error in main loop: {e}")
        traceback.print_exc()
        # Write error status
        try:
            with open(file_path, "w") as f:
                f.write("False,ERROR")
        except:
            pass

if __name__ == "__main__":
    main()
