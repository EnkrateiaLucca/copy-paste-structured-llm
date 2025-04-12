# Smart Contact Form

A simple application that uses AI to extract contact information from copied text and automatically fill form fields.

## Features

- Copy any text containing contact information
- Click "Smart Fill" to automatically populate form fields
- Extracts Name, Email, and Phone Number using OpenAI's GPT-3.5
- Modern, responsive UI
- Real-time feedback with success/error messages

## Setup

1. Clone this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your OpenAI API key:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and replace `your_openai_api_key_here` with your actual OpenAI API key.

## Running the Application

1. Start the backend server:
   ```bash
   python app.py
   ```
   This will start the server on `http://localhost:12345`

2. Open `index.html` in your web browser

## Usage

1. Copy any text containing contact information (name, email, phone)
2. Go to the webpage and click the "Smart Fill" button
3. The form fields will be automatically populated with the extracted information

## Example

Try copying this text:
```
Contact John Doe at johndoe@example.com or call (555) 123-4567
```
Then click "Smart Fill" to see the form fields populate automatically.

## Technical Details

- Backend: Python with FastAPI
- Frontend: HTML, CSS, JavaScript
- AI: OpenAI GPT-3.5 Turbo
- Clipboard Access: pyperclip library 