# Task Break AI

An interactive AI tool that decomposes complex milestones into targeted work breakdown structures and renders an actionable checklist for progress tracking.

## Architecture Flow

1. **Streamlit UI**
   - `app.py` launches the Streamlit web application.
   - Users enter a major project, feature, or assignment into a text area.
   - A button triggers task breakdown generation.

2. **Configuration**
   - The app loads `GEMINI_API_KEY` from `st.secrets`.
   - If the key is missing, the app stops and displays an error.
   - If the key is present, it configures `google.generativeai` with the API key.

3. **Prompt Construction**
   - The app creates a structured prompt for Gemini.
   - The prompt asks for 4–6 actionable subtasks formatted as raw JSON.
   - Each task object must include `title` and `tip`.

4. **AI Request & Response**
   - The prompt is sent to `gemini-3.5-flash` through `google.generativeai.GenerativeModel`.
   - Gemini returns a text response expected to be valid JSON.

5. **Parsing & State Management**
   - `app.py` parses the AI response with `json.loads()`.
   - Parsed tasks are stored in `st.session_state.tasks_list`.
   - This preserves task state across UI interactions.

6. **Checklist Rendering**
   - The app displays each task as a checkbox.
   - Tips appear beneath each task.
   - Checked items show a completion indicator.

## Files

- `app.py` — Streamlit application and AI integration logic.
- `README.md` — Project overview and architecture flow.

## Requirements

- Python 3.10+
- `streamlit`
- `google-generativeai`

## Run Locally

1. Install dependencies:
   ```bash
   pip install streamlit google-generativeai
   ```
2. Set `GEMINI_API_KEY` in `.streamlit/secrets.toml`.
3. Start the app:
   ```bash
   streamlit run app.py
   ```

Architectecture flow-
User enters a major project or assignment in the Streamlit UI
App validates input and reads the Gemini API key from secure secrets
App sends a structured prompt to Google Gemini using google.generativeai
Gemini returns a JSON list of action items
App parses the JSON and stores tasks in Streamlit session state
App renders an interactive checklist for the user to track progress