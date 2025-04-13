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

class ContactInfo(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

class JobInfo(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    description: str | None = None

class CourseProposal(BaseModel):
    course_title: str | None = None
    target_role: str | None = None
    course_level: str | None = None
    required_skills: str | None = None
    instructor_name: str | None = None
    instructor_entity: str | None = None
    course_description: str | None = None
    target_audience: str | None = None
    prerequisites: str | None = None

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

def extract_course_proposal(text: str) -> CourseProposal:
    """Extract course proposal information from text using OpenAI's API."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts course proposal information from text. "
                              "Extract course title, target role, course level, required skills, instructor name, "
                              "instructor entity, course description, target audience, and prerequisites if present. "
                              "Return only JSON format with null for missing fields."
                },
                {
                    "role": "user",
                    "content": f"Extract course proposal information from this text: {text}"
                }
            ],
            response_format={ "type": "json_object" }
        )
        
        # Parse the response
        result = response.choices[0].message.content
        return CourseProposal.model_validate_json(result)
    except Exception as e:
        print(f"Error extracting course proposal info: {e}")
        return CourseProposal()

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
        print("JOB INFORMATION OUTPUT:")
        print(job_info)
        print("--------------------------------")
        return job_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 12345))
    uvicorn.run(app, host="127.0.0.1", port=port) 