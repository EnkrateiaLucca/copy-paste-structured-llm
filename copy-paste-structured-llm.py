#!/usr/bin/env python
# coding: utf-8

# In[8]:


# This code will take an image of a form and extract the pydantic object from it using
# Claude API

import anthropic
import base64
import httpx
import re
from datetime import datetime

MODEL = "claude-3-7-sonnet-20250219"

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_python_code(text):
    """Extract code between <python> tags"""
    pattern = r'<python>(.*?)</python>'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def save_outputs(raw_output, extracted_code=None):
    """Save both raw output and extracted code to files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save raw output
    raw_filename = f"form_analysis_raw_{timestamp}.txt"
    with open(raw_filename, "w") as f:
        f.write(raw_output)
    print(f"Raw output saved to: {raw_filename}")
    
    # Save extracted code if available
    if extracted_code:
        code_filename = f"form_model_{timestamp}.py"
        with open(code_filename, "w") as f:
            f.write("from pydantic import BaseModel\n\n")  # Add import statement
            f.write(extracted_code)
        print(f"Extracted Pydantic model saved to: {code_filename}")

client = anthropic.Anthropic()

prompt = """
Create the appropriate pydantic object with the attributes from this input forms page you see in front of you.
Your output python code should be enclosed by xml tags like
<python> and </python>.
Output:
"""

# Read and encode the image
image_path = "./job_form.png"
try:
    img_data = encode_image_to_base64(image_path)
except FileNotFoundError:
    print(f"Error: Could not find image file at {image_path}")
    exit(1)
except Exception as e:
    print(f"Error encoding image: {str(e)}")
    exit(1)

# Create the message with the encoded image
try:
    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ],
    )
    
    # Get the raw output
    raw_output = message.content[0].text
    
    # Extract Python code from between XML tags
    extracted_code = extract_python_code(raw_output)
    
    # Save both outputs
    save_outputs(raw_output, extracted_code)
    
    # Print the extracted code to console
    if extracted_code:
        print("\nExtracted Pydantic Model:")
        print("-" * 40)
        print(extracted_code)
    else:
        print("\nNo Python code found between <python> tags in the output.")
        
except Exception as e:
    print(f"Error calling Claude API: {str(e)}")


# # Getting Locations with Gemini 2.5 Pro

# In[16]:


from google import genai
from google.genai import types
import PIL.Image
import os
import base64
from io import BytesIO

# Load the image
image = PIL.Image.open('./window-screenshot.png')

# Convert the image to base64
buffered = BytesIO()
image.save(buffered, format="PNG")
image_bytes = buffered.getvalue()
image_base64 = base64.b64encode(image_bytes).decode('utf-8')

# Define the prompt
prompt_input_forms_locations = 'Point to the locations of the input forms with no more than 10 items. The answer should follow the json format: [{"point": <point>, "label": <label1>}, ...]. The points are in [y, x] format normalized to 0-1000.'

# Construct the contents list
contents = [
    {
        "role": "user",
        "parts": [
            {"text": prompt_input_forms_locations},
            {
                "inlineData": {
                    "mimeType": "image/png",
                    "data": image_base64
                }
            }
        ]
    }
]

# Initialize the client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# Generate content
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=contents
)

# Print the response
print(response.text)


# In[ ]:





# In[17]:


def parse_form_locations(json_output):
    """
    Parse the form locations output from the model and return points and labels.
    
    Args:
        json_output (str or list): Either a JSON string (possibly with markdown code blocks) 
                                  or an already parsed list of dictionaries
    
    Returns:
        tuple: Two lists containing:
            - points: List of [y, x] coordinates
            - labels: List of corresponding labels
    """
    import json
    import re
    
    # If input is a string, try to extract and parse JSON
    if isinstance(json_output, str):
        # Remove markdown code blocks if present
        json_str = re.sub(r'```json\n|\n```', '', json_output)
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}")
    else:
        # Assume it's already parsed
        data = json_output
    
    # Extract points and labels
    points = []
    labels = []
    
    for item in data:
        points.append(item["point"])
        labels.append(item["label"])
    
    return points, labels

# Parse the output
points, labels = parse_form_locations(response.text)

# Print the results
print("Points:", points)
print("Labels:", labels)

# You can also access specific points and labels by index
for i, (point, label) in enumerate(zip(points, labels)):
    print(f"Form {i+1}: {label} at position {point}")


# In[18]:


# not rows and columns
points = points[2:]
labels = labels[2:]


# In[31]:


import pyautogui
import time

def automate_text_input(points, texts, delay=0.5):
    """
    Automatically click on specified coordinates and type text.
    
    Args:
        points (list): List of [x, y] coordinates where to click
        texts (list): List of strings to type at each coordinate
        delay (float): Delay in seconds between actions (default: 0.5)
    """
    # Safety check
    if len(points) != len(texts):
        raise ValueError("Number of points must match number of texts")
    
    # Give user time to switch to the target window
    print("Starting in 3 seconds... Switch to your target window!")
    time.sleep(2)
    
    # Set up pyautogui safety features
    pyautogui.FAILSAFE = True  # Move mouse to upper-left corner to abort
    pyautogui.PAUSE = delay    # Add delay between actions
    
    # Process each point and text pair
    for (x, y), text in zip(points, texts):
        # Move to position and click
        pyautogui.click(x, y)
        time.sleep(delay)  # Wait a bit after clicking
        
        # Type the text
        pyautogui.write(text)
        time.sleep(delay)  # Wait a bit after typing


# In[32]:


# Using the points from the clipboard
relative_points = [[1462, 420], [771, 419]]
screen_points = [(881, 448), (1618, 449)]

texts = ["Basketball", "Lebron James"]
automate_text_input(screen_points, texts)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# ![](./window-screenshot.png)
