**Goal:** To create a system where copying text containing contact details (Name, Email, Phone) allows a *demo webpage* to automatically populate the correct fields upon a specific user action, using an LLM to parse the copied text.

**Core Components:**

1.  **Demo Webpage:** A simple HTML page with designated input fields and JavaScript to handle the interaction.
2.  **Local "Helper" Application:** A small program running in the background on your computer.
3.  **LLM Service:** An AI model accessed via an API to process the text.

---

**Prototype Outline:**

1.  **Demo Webpage (HTML & JavaScript):**
    * **Structure:** Basic HTML with clearly identified input fields for Name, Email, and Phone (e.g., using unique `id` attributes like `id="name-input"`).
    * **Trigger:** Instead of hijacking the standard paste (Ctrl+V/Cmd+V), add a dedicated button like "Smart Fill" or "Paste Contact Info".
    * **Communication:** When the button is clicked, the page's JavaScript will need to request the processed data from the Local Helper Application (likely via a simple local web request, e.g., to `http://localhost:PORT/get-data`).
    * **Population:** Upon receiving structured data (like JSON) from the Helper App, the JavaScript will populate the corresponding input fields using their IDs.

2.  **Local "Helper" Application (Background Process):**
    * **Technology:** Could be built using Python, Node.js, or another language capable of system tasks.
    * **Clipboard Access:** Needs to monitor the system clipboard for changes. When text is copied, it stores it temporarily.
    * **LLM Interaction:** When triggered (either automatically upon copy or when the webpage requests data), it sends the stored clipboard text to an LLM.
    * **Prompting for Structure:** It specifically instructs the LLM to extract Name, Email, and Phone Number and return them in a consistent format (e.g., JSON: `{"name": "...", "email": "...", "phone": "..."}`). This is the "structured output" part.
    * **Local Server:** Runs a minimal web server on a specific port (e.g., `localhost:12345`) to listen for requests from the demo webpage. When the webpage asks for data (e.g., hits the `/get-data` endpoint), this server provides the latest structured data obtained from the LLM. It needs to handle CORS (Cross-Origin Resource Sharing) to allow the webpage to fetch data.

3.  **LLM Service (AI Brain):**
    * **Function:** Receives raw text from the Helper Application.
    * **Task:** Parses the text based on the prompt to identify the required entities (Name, Email, Phone).
    * **Output:** Returns the extracted information in the requested structured format (JSON).

**Simplified Workflow:**

1.  User copies text containing contact info.
2.  Local Helper App detects the copy and stores the text.
3.  User goes to the Demo Webpage and clicks the "Smart Fill" button.
4.  Webpage JavaScript requests data from the Helper App's local server.
5.  Helper App sends the copied text to the LLM, asking for structured JSON.
6.  LLM returns the structured data (e.g., `{"name": "...", "email": "...", "phone": "..."}`).
7.  Helper App sends this JSON back to the webpage.
8.  Webpage JavaScript receives the JSON and fills the Name, Email, and Phone fields accordingly.

This outline focuses on a feasible prototype by using a dedicated button and a simple local server for communication between the webpage and the background helper application.