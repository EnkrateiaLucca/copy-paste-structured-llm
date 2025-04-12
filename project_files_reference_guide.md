# Project Files Reference Guide

## Complete File List
- `app.py` - Backend server
- `index.html` - Contact form webpage
- `job.html` - Job form webpage
- `requirements.txt` - Python dependencies
- `.env.example` - Example environment variables file
- `README.md` - Project documentation
- `test_samples_contact_form.txt` - Sample texts for testing contact extraction
- `test_samples_job_form.txt` - Sample texts for testing job extraction

## Key Implementation Details

### Backend (app.py)
- Uses FastAPI for creating a REST API
- Includes two main endpoints:
  - `/get-data` - Extracts contact information
  - `/get-job-data` - Extracts job information
- Uses pyperclip to access the clipboard
- Uses OpenAI's API to process text and extract structured information
- Returns JSON responses to the frontend

### Frontend (index.html & job.html)
- Simple HTML forms with clean CSS styling
- JavaScript to handle API calls and form population
- User-friendly feedback messages
- Navigation between different form types

### Environment Setup
- OpenAI API key stored in `.env` file
- Server port configurable (default: 12345)

## Testing Tips
1. Start with small, clear examples before trying complex text
2. Make sure to fully copy the text before clicking "Smart Fill"
3. Check the browser console if issues occur (F12 to open developer tools)
4. Verify your OpenAI API key is working correctly

## Customization Options
- Change the OpenAI model in `app.py` (e.g., from "gpt-4o" to "gpt-3.5-turbo")
- Modify the system prompts to extract different or additional information
- Add new forms for other types of information extraction
- Customize CSS styling for different visual themes

## Deployment Considerations
- For production use, set specific allowed origins in the CORS middleware
- Consider rate limiting to manage OpenAI API usage
- Add authentication if deploying publicly
- Check clipboard access permissions on different operating systems