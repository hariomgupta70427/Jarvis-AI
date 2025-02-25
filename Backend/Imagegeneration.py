import asyncio
from random import randint
from PIL import Image
import requests
import os
from time import sleep
from dotenv import get_key

# API details for the Hugging Face Stable Diffusion model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Function to open and display images
def open_images(prompt):
    folder_path = "Data"  # Folder where the images are stored
    prompt = prompt.replace(" ", "_")  # Replace spaces in prompt with underscores

    # Generate the filenames for the images
    Files = [f"{prompt}{i}.jpg" for i in range(1, 4)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Pause for 1 second before showing the next image

        except IOError:
            print(f"Unable to open {image_path}")

# Async function to send a query to the Hugging Face API
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.content  # Direct binary image data
    else:
        print("Error in response:", response.status_code, response.text)
        return None

# Async function to generate images and save them
async def generate_images(prompt: str):
    tasks = []

    for _ in range(3):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_data_list = await asyncio.gather(*tasks)

    for i, image_data in enumerate(image_data_list):
        if image_data:
            file_path = f"Data/{prompt.replace(' ', '_')}{i + 1}.jpg"
            with open(file_path, "wb") as f:
                f.write(image_data)
            print(f"Image {i+1} saved successfully at {file_path}!")

# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_images(prompt))
    open_images(prompt)

# Main loop to check and process image generation requests
while True:
    try:
        # Ensure file exists
        file_path = r"Frontend/Files/ImageGeneration.data"
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("False,False")

        # Read the status and prompt from the data file
        with open(file_path, "r") as f:
            Data = f.read().strip()
        
        if not Data:
            continue

        Prompt, Status = Data.split(",")

        # If the status indicates an image generation request
        if Status.strip().lower() == "true":
            print(f"Generating Images for: {Prompt.strip()}...")
            GenerateImages(prompt=Prompt.strip())

            # Reset the status to False after image generation
            with open(file_path, "w") as f:
                f.write("False,False")
            break
        else:
            sleep(1)  # Wait for 1 second before checking again

    except Exception as e:
        print(f"Error: {e}")
        sleep(1)  # Avoid CPU overuse
