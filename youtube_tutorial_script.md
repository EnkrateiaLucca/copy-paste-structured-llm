# Smart Contact Form YouTube Tutorial Script

## Introduction (1-2 minutes)
"Hey everyone! Today I'm going to show you how to build this cool Smart Contact Form application that uses AI to automatically extract contact information from any text you copy. Let me show you a quick demo..."

[DEMO: Show yourself copying some text with contact info, clicking the Smart Fill button, and watching the form fill automatically]

"Pretty neat, right? This app uses OpenAI's GPT models to parse contact details from any text in your clipboard. By the end of this tutorial, you'll have built this complete application with both a Python backend and a simple frontend."

## Project Overview (2 minutes)
"Let's quickly go over what we're building:

1. A backend server using Python, FastAPI, and OpenAI's API
2. A frontend with two forms - one for contact information and another for job details
3. A 'Smart Fill' feature that grabs text from your clipboard and uses AI to extract the relevant information

This is how the app works:
- You copy text containing information (like contact details or job listings)
- Click the 'Smart Fill' button on our webpage
- Our backend grabs the text from your clipboard
- The text is sent to OpenAI's API for processing
- The extracted information is returned and automatically fills the form fields

Let's get started!"

## Setup (3 minutes)
"First, let's set up our project structure.

```
smart-contact-form/
├── app.py           # Backend server
├── index.html       # Contact form page
├── job.html         # Job form page
├── requirements.txt # Python dependencies
├── .env.example     # Example environment variables
└── README.md        # Project documentation
```

Before we start coding, make sure you have Python installed. We'll also need a few dependencies:"

[SHOW: Installing dependencies]
```bash
pip install fastapi uvicorn python-dotenv openai pyperclip pydantic
```

"You'll also need an OpenAI API key for this project. If you don't have one, you can get it from the OpenAI website. We'll use a .env file to store it securely."

## Building the Backend (5-7 minutes)
"Let's start by creating our backend. This will be a FastAPI server that communicates with OpenAI's API.

First, let's create our app.py file:"

[CODE WALKTHROUGH: app.py]
```python
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pyperclip
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes only. In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

"Now let's define our data models using Pydantic. We'll create one for contact information and another for job information:"

```python
class ContactInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

class JobInfo(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    description: str | None = None
```

"Next, let's create the functions that will extract information using OpenAI's API:"

```python
def extract_contact_info(text: str) -> ContactInfo:
    """Extract contact information from text using OpenAI's API."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts contact information from text. "
                              "Extract name, email, and phone number if present. "
                              "Return only JSON format with null for missing fields."
                },
                {
                    "role": "user",
                    "content": f"Extract contact information from this text: {text}"
                }
            ],
            response_format={ "type": "json_object" }
        )
        
        # Parse the response
        result = response.choices[0].message.content
        return ContactInfo.model_validate_json(result)
    except Exception as e:
        print(f"Error extracting contact info: {e}")
        return ContactInfo()
```

"We'll create a similar function for job information:"

```python
def extract_job_info(text: str) -> JobInfo:
    """Extract job information from text using OpenAI's API."""
    try:
        response = openai.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts job information from text. "
                              "Extract job title, company name, location, and job description if present. "
                              "Return only JSON format with null for missing fields."
                },
                {
                    "role": "user",
                    "content": f"Extract job information from this text: {text}"
                }
            ],
            response_format=JobInfo
        )
        
        # Parse the response
        result = response.choices[0].message.parsed
        return result
    except Exception as e:
        print(f"Error extracting job info: {e}")
        return JobInfo()
```

"Finally, let's create our API endpoints and start the server:"

```python
@app.get("/get-data")
async def get_data():
    """Get the latest clipboard content and process it for contact information."""
    try:
        # Get clipboard content
        clipboard_text = pyperclip.paste()
        if not clipboard_text:
            raise HTTPException(status_code=400, detail="No text found in clipboard")
        
        # Process the text
        contact_info = extract_contact_info(clipboard_text)
        return contact_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-job-data")
async def get_job_data():
    """Get the latest clipboard content and process it for job information."""
    try:
        # Get clipboard content
        clipboard_text = pyperclip.paste()
        if not clipboard_text:
            raise HTTPException(status_code=400, detail="No text found in clipboard")
        
        # Process the text
        job_info = extract_job_info(clipboard_text)
        return job_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 12345))
    uvicorn.run(app, host="127.0.0.1", port=port)
```

"That completes our backend! The server will run on localhost port 12345, and it has two endpoints: one for contact information and one for job information."

## Building the Frontend - Contact Form (4-5 minutes)
"Now let's create our frontend. We'll start with the contact form in index.html:"

[CODE WALKTHROUGH: index.html - focusing on structure and key elements]
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Form Extractor</title>
    <style>
        /* CSS styling here... */
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="index.html" class="active">Contact Form</a>
            <a href="job.html">Job Form</a>
        </div>
        <h1>Contact Information Extractor</h1>
        <form id="contactForm">
            <div class="form-group">
                <label for="name-input">Name</label>
                <input type="text" id="name-input" placeholder="Enter name">
            </div>
            <div class="form-group">
                <label for="email-input">Email</label>
                <input type="email" id="email-input" placeholder="Enter email">
            </div>
            <div class="form-group">
                <label for="phone-input">Phone</label>
                <input type="tel" id="phone-input" placeholder="Enter phone number">
            </div>
            <button type="button" id="smart-fill">Smart Fill</button>
        </form>
        <div id="status" class="status"></div>
    </div>

    <script>
        document.getElementById('smart-fill').addEventListener('click', async () => {
            const button = document.getElementById('smart-fill');
            const status = document.getElementById('status');
            
            // Disable button and show loading state
            button.disabled = true;
            button.textContent = 'Loading...';
            status.className = 'status';
            status.textContent = '';

            try {
                // Call the backend API
                const response = await fetch('http://localhost:12345/get-data');
                if (!response.ok) {
                    throw new Error('Failed to get data from clipboard');
                }

                const data = await response.json();

                // Update form fields
                if (data.name) document.getElementById('name-input').value = data.name;
                if (data.email) document.getElementById('email-input').value = data.email;
                if (data.phone) document.getElementById('phone-input').value = data.phone;

                // Show success message
                status.className = 'status success';
                status.textContent = 'Form filled successfully!';
            } catch (error) {
                // Show error message
                status.className = 'status error';
                status.textContent = 'Error: ' + error.message;
            } finally {
                // Reset button state
                button.disabled = false;
                button.textContent = 'Smart Fill';
            }
        });
    </script>
</body>
</html>
```

"Let me explain some key parts of this code:
1. We have a simple form with fields for name, email, and phone
2. The 'Smart Fill' button triggers JavaScript that:
   - Calls our backend API
   - Takes the response data
   - Fills the form fields automatically
3. We also have a status message that shows success or error feedback
4. The navigation lets us switch between contact and job forms"

## Building the Frontend - Job Form (3-4 minutes)
"Now let's create the job form in job.html. It's very similar to the contact form but with different fields:"

[CODE WALKTHROUGH: job.html - focusing on the differences]
```html
<!-- The structure is similar to index.html, but with different form fields -->
<form id="jobForm">
    <div class="form-group">
        <label for="title-input">Job Title</label>
        <input type="text" id="title-input" placeholder="Enter job title">
    </div>
    <div class="form-group">
        <label for="company-input">Company</label>
        <input type="text" id="company-input" placeholder="Enter company name">
    </div>
    <div class="form-group">
        <label for="location-input">Location</label>
        <input type="text" id="location-input" placeholder="Enter job location">
    </div>
    <div class="form-group">
        <label for="description-input">Job Description</label>
        <textarea id="description-input" placeholder="Enter job description"></textarea>
    </div>
    <button type="button" id="smart-fill">Smart Fill</button>
</form>

<!-- The JavaScript is also similar, but it calls a different API endpoint -->
<script>
    document.getElementById('smart-fill').addEventListener('click', async () => {
        // ...similar code to index.html...
        const response = await fetch('http://localhost:12345/get-job-data');
        // ...handle the response...
    });
</script>
```

"The job form works exactly the same way as the contact form, but it extracts different information and calls a different endpoint."

## Setting Up Environment Variables (2 minutes)
"Let's set up our environment variables. Create a file named .env.example:"

```
OPENAI_API_KEY=your_openai_api_key_here
PORT=12345
```

"Copy this to a new file named .env and replace 'your_openai_api_key_here' with your actual OpenAI API key."

## Running the Application (2 minutes)
"Now let's run our application! First, start the backend server:"

```bash
python app.py
```

"You should see output indicating that the server is running on http://127.0.0.1:12345.

To use the application:
1. Open index.html or job.html in your web browser
2. Copy some text containing contact or job information
3. Click the 'Smart Fill' button
4. Watch as the form fields are automatically populated!"

## Testing with Sample Data (3 minutes)
"Let's test our application with some sample data. Here's an example of contact information you can copy:"

```
For project inquiries, please reach out to Maria Silva at her email, maria.silva@example.com, or give her a call at +351 912 345 678.
```

"And here's an example of job information:"

```
TechCorp Inc. is hiring a Senior Software Engineer in San Francisco, CA. The role requires 5+ years of experience in Python and JavaScript, with specific expertise in FastAPI and React. The position offers a competitive salary and comprehensive benefits package.
```

[DEMO: Copy each example and show the form being filled]

## How It Works - The Magic Behind the Scenes (3 minutes)
"Let's talk about how this application actually works:

1. When you copy text, it's stored in your system clipboard
2. When you click 'Smart Fill', our JavaScript makes a request to our local server
3. The server gets the text from your clipboard using pyperclip
4. The server sends the text to OpenAI's API with specific instructions on what to extract
5. OpenAI processes the text and returns structured data (name, email, phone or job details)
6. Our server sends this data back to the frontend
7. The JavaScript takes this data and fills the form fields

The real magic is in the prompt we send to OpenAI. We're asking it to extract specific information and return it in a structured JSON format that our application can easily work with."

## Conclusion and Next Steps (2 minutes)
"And there you have it! You've built a Smart Contact Form application that uses AI to automatically extract and fill information. This is just a starting point - there are many ways you could extend this:

1. Add more form types for different information (addresses, product details, etc.)
2. Improve the UI with animations and better feedback
3. Add validation to ensure the extracted information is correct
4. Deploy the application to a server so it can be used by others
5. Implement clipboard monitoring for automatic filling without clicking a button

I hope you found this tutorial helpful! If you liked it, please give it a thumbs up and subscribe for more tech tutorials. If you have any questions, leave them in the comments below.

Thanks for watching!"

## Credits (1 minute)
"This project uses the following technologies:
- Python with FastAPI
- OpenAI's GPT models
- HTML, CSS, and JavaScript
- Pyperclip for clipboard access

# YouTube Presentation Tips

## Video Structure
1. **Introduction (1-2 min)**
   - Start with a demo to quickly show what you're building
   - Explain the problem this solves (manually filling forms is tedious)
   - Outline what viewers will learn

2. **Walkthrough (15-20 min)**
   - Follow the script in logical sections
   - Show code on screen while explaining key concepts
   - Use split-screen when possible (code + terminal/browser)

3. **Demo (3-5 min)**
   - Show the working application with real examples
   - Highlight both success cases and potential errors

4. **Conclusion (1-2 min)**
   - Recap what was built
   - Suggest extensions/improvements
   - Call to action (like, subscribe, comment)

## Visual Presentation
- **Screen Setup**
  - Use a code editor with good syntax highlighting (VS Code works well)
  - Increase font size for better visibility
  - Consider a clean theme with good contrast

- **Browser Window**
  - Use a new browser window without distracting bookmarks/extensions
  - Zoom in to 125-150% when showing the forms

- **Terminal**
  - Use a larger font size
  - Consider a colored terminal for better readability

## Delivery Tips
- **Pace**
  - Speak clearly and at a moderate pace
  - Pause briefly after explaining complex concepts
  - Give viewers time to absorb information

- **Engagement**
  - Explain your thought process as you code
  - Point out interesting or tricky parts
  - Encourage viewers to code along

- **Technical Details**
  - Explain key concepts like API interactions, JSON parsing
  - Don't get bogged down in minor details
  - Focus on the AI integration aspects

## Preparation Checklist
- [ ] Test the complete workflow before recording
- [ ] Prepare sample text examples in a text file for easy access
- [ ] Set up your OpenAI API key and test it works
- [ ] Have all files ready and organized in your editor
- [ ] Close unnecessary applications to avoid distractions
- [ ] Check microphone and screen recording settings

## Common Questions to Address
1. "How much does this cost to run?" (OpenAI API pricing)
2. "Can this work with other types of information?"
3. "How accurate is the AI extraction?"
4. "Could this be used in a production environment?"
5. "What security considerations should I be aware of?"