#!/usr/bin/env python3

"""
Unified script that:
  1) Calls Anthropic to produce a Pydantic model from a form screenshot
  2) Calls Gemini to detect on-screen field locations from a screenshot
  3) Uses OpenAI to parse clipboard text into the model
  4) Uses PyAutoGUI to fill the identified fields with extracted data

Requires the following environment variables or placeholders:
  - ANTHROPIC_API_KEY
  - GEMINI_API_KEY
  - OPENAI_API_KEY

Adjust code as needed (model names, endpoints, file paths, etc.).
"""

import os
import base64
import re
import time
from datetime import datetime
import json
import pyautogui
import pyperclip
import anthropic
from openai import OpenAI
import requests

MODEL_PYDANTIC_OBJECTS = "claude-3-7-sonnet-20250219"
MODEL_PARSE_TEXT = "gpt-4o"
# The Google Gemini Python SDK
try:
    from google import genai
except ImportError:
    print("You must install `google-genai` (and dependencies) for Gemini usage.")
    raise

# For demonstration, Pydantic 2.x
try:
    from pydantic import BaseModel, ValidationError
except ImportError:
    print("You must install pydantic>=2.0.")
    raise


# -----------------------------------------------------------------------------
# 1) Step One: Anthropic (Claude) to create a Pydantic model from screenshot
# -----------------------------------------------------------------------------

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY_HERE")
anthropic_client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

def encode_image_to_base64(image_path: str) -> str:
    """Read image file and base64-encode."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def extract_python_code(text: str) -> str:
    """
    Extract code between <python> and </python> tags.
    If none found, returns empty string.
    """
    pattern = r"<python>(.*?)</python>"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def call_anthropic_for_pydantic(image_path: str) -> str:
    """
    Sends a screenshot to Claude (Anthropic) with instructions:
      - "Create the appropriate pydantic object with the attributes for the input forms."
    Returns the raw textual response from Claude, which should have <python> ... </python>.
    """
    print("\n=== [1] Sending screenshot to Anthropic (Claude) to produce Pydantic model ===")
    # The user’s custom prompt
    prompt_message = """
Create the appropriate pydantic object with the attributes from this input forms page you see in front of you.
Output your Python code enclosed by XML tags <python> and </python>.
"""
    image_b64 = encode_image_to_base64(image_path)

    # Important note: This usage is conceptual. The real Anthropic Chat API
    # might differ in usage/parameters. Adjust to your environment’s requirements.
    # The typical chat calls are more like anthropic_client.completions.create(...)
    # but the user’s snippet references an older "messages.create" approach.
    # 
    # If your version differs, adapt accordingly.
    message = anthropic_client.completions.create(
        model=MODEL_PYDANTIC_OBJECTS,  # or whichever Claude model you have
        max_tokens_to_sample=1024,
        prompt=anthropic.HUMAN_PROMPT
            + f"""{prompt_message}
Here's the form as an image:
[base64 image]
{image_b64}
"""
            + anthropic.AI_PROMPT,
    )

    raw_text = message.completion
    return raw_text


# -----------------------------------------------------------------------------
# 2) Step Two: Gemini to detect on-screen field locations
# -----------------------------------------------------------------------------

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

def call_gemini_for_locations(image_path: str) -> list:
    """
    Sends the same screenshot to Gemini, requesting field coordinates in JSON:
      e.g. [{'point': [y, x], 'label': '...'}, ...]
    Returns the result as a Python list of dicts.
    """
    print("\n=== [2] Sending screenshot to Gemini to get form field coordinates ===")
    # Simple prompt
    gemini_prompt = ("Point to the locations of the input forms with no more than 10 items. "
                     "The answer should be JSON like: "
                     "[{'point': [y, x], 'label': '...'}, ...]. "
                     "Points in range 0-1000 for y, x.")

    image_b64 = encode_image_to_base64(image_path)

    g_client = genai.Client(api_key=GEMINI_API_KEY)
    contents = [
        {
            "role": "user",
            "parts": [
                {"text": gemini_prompt},
                {
                    "inlineData": {
                        "mimeType": "image/png",
                        "data": image_b64
                    }
                }
            ]
        }
    ]
    response = g_client.models.generate_content(model="gemini-2.0", contents=contents)
    raw_output = response.text.strip()

    # Try to parse out JSON
    try:
        # Remove possible code block fences
        cleaned = re.sub(r"```json\s*|\s*```", "", raw_output)
        return json.loads(cleaned)
    except json.JSONDecodeError:
        print("Gemini response did not parse as JSON. Raw output below:\n", raw_output)
        return []


# -----------------------------------------------------------------------------
# 3) Step Three: Use OpenAI to parse raw text from clipboard into the Pydantic data
# -----------------------------------------------------------------------------

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def parse_text_with_openai(raw_text: str, instructions: str) -> str:
    """
    Example function that calls OpenAI ChatCompletion to parse raw_text
    according to 'instructions' (the system prompt).
    Returns a JSON string.

    The user is modeling that they want structured JSON from GPT.
    Adjust model, prompt, etc. as needed.
    """
    print("\n=== [3] Sending raw text to OpenAI to parse into structured JSON ===")

    messages = [
        {
            "role": "system",
            "content": instructions
        },
        {
            "role": "user",
            "content": raw_text
        }
    ]

    response = openai_client.chat.completions.create(
        model=MODEL_PARSE_TEXT,
        messages=messages,
        temperature=0,
    )
    # The assistant's response presumably is JSON
    return response.choices[0].message.content.strip()


# -----------------------------------------------------------------------------
# 4) Automate the text input (PyAutoGUI)
# -----------------------------------------------------------------------------

def automate_text_input(points: list, text_fields: dict, offset=(0, 0), delay=0.5):
    """
    Given a list of 'points' from Gemini (each entry is {'point': [y, x], 'label': '...'}),
    and a dictionary 'text_fields' with the keys matching each 'label',
    click each location and type the associated text.

    offset: if you need to shift the coordinates to match actual screen pos, do so
    e.g., offset=(100, 200).
    """
    print("\n=== [4] Filling the form fields with PyAutoGUI ===")
    print("Starting in 3 seconds... Switch to your target window!")
    time.sleep(3)

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = delay

    for entry in points:
        label = entry["label"]
        coords = entry["point"]  # [y, x]
        y, x = coords  # note the user stored them as [y, x], but PyAutoGUI wants x,y
        # Adjust if needed
        screen_x = x + offset[0]
        screen_y = y + offset[1]

        # If we have text for this label in text_fields, fill it
        text_to_type = text_fields.get(label, "")
        print(f"  -> Label '{label}': Clicking {screen_x},{screen_y}, Typing '{text_to_type}'")

        pyautogui.click(screen_x, screen_y)
        time.sleep(delay)
        pyautogui.write(text_to_type)
        time.sleep(delay)


# -----------------------------------------------------------------------------
# Putting it all together in a single "main" flow
# -----------------------------------------------------------------------------

class UnifiedFormExtractor:
    """
    Demonstrates the pipeline:
      1) use Claude to get a Pydantic definition from form screenshot
      2) parse the code from <python> tags
      3) optionally write that code to a file, or dynamically create the model
      4) use Gemini to get coordinates
      5) read the user’s clipboard text
      6) parse text with OpenAI into JSON
      7) fill the fields with PyAutoGUI
    """

    def __init__(self, form_image_path: str):
        self.form_image_path = form_image_path
        self.model_code = ""
        self.parsed_locations = []

    def run_pipeline(self):
        # Step 1: Anthropic -> get Pydantic code
        raw_claude_output = call_anthropic_for_pydantic(self.form_image_path)
        code = extract_python_code(raw_claude_output)
        self.model_code = code
        if not code:
            print("No <python> ... </python> code was found in Claude's response.")
        else:
            print("\n[Claude] Extracted Pydantic Code:\n", code)

        # Step 2: Gemini -> get field coordinates
        gemini_data = call_gemini_for_locations(self.form_image_path)
        if not gemini_data:
            print("No data from Gemini. Exiting.")
            return
        self.parsed_locations = gemini_data

        # For demonstration, let's say the user has the text in the clipboard
        text_in_clipboard = pyperclip.paste()
        if not text_in_clipboard.strip():
            print("Clipboard is empty. Copy some text first. Exiting.")
            return

        # Step 3: parse text with OpenAI
        # Suppose the instructions to OpenAI is "Return JSON with keys matching the model"
        # We'll assume we want: name, email, phone, etc. This is your custom system prompt.
        system_instructions = (
            "You are an assistant that extracts the following fields from the user's text. "
            "Return valid JSON with exactly these keys: ['name','email','phone']. "
            "Set missing fields to null."
        )
        openai_json_string = parse_text_with_openai(text_in_clipboard, system_instructions)

        # Step 4: Convert the returned JSON string to a dict
        try:
            extracted_data = json.loads(openai_json_string)
        except json.JSONDecodeError:
            print("OpenAI's response wasn't valid JSON. Response was:\n", openai_json_string)
            return

        # Let’s assume the location labels from Gemini are "Name", "Email", "Phone"
        # or you can do some best-guess matching. We'll do a naive approach:
        #   - "label" from gemini might be "Name", "Email", "Phone" (case sensitive)
        #   - extracted_data might be: {"name": "...", "email": "...", "phone": "..."}
        # We'll build a dictionary so that "Name" -> extracted_data['name'], etc.

        # Adjust as needed to match your naming conventions from the Claude/Gemini steps.
        text_fields_for_gui = {
            "Name": extracted_data.get("name", "") or "",
            "Email": extracted_data.get("email", "") or "",
            "Phone": extracted_data.get("phone", "") or "",
        }

        # Step 5: Fill the fields with PyAutoGUI
        # If the points from Gemini are in range [0..1000], you need a suitable offset
        # or scaling to match actual screen coords. Let's assume offset=(0,0) for now.
        automate_text_input(self.parsed_locations, text_fields_for_gui, offset=(0, 0))


def main():
    # Provide your local screenshot path of the form
    screenshot_path = "./assets/contact_form_google.png"  # or whichever form screenshot you have
    pipeline = UnifiedFormExtractor(screenshot_path)
    pipeline.run_pipeline()

if __name__ == "__main__":
    main()
