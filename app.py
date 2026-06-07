import streamlit as st
import google.generativeai as genai
import json

# Page Configuration
st.set_page_config(page_title="Task Break AI ", layout="wide")

#  Dashboard Styling 
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    .workspace-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        border: 1px solid #e9ecef;
        margin-top: 20px;
    }
    .refinement-box {
        background-color: #f1f3f5;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #212529;
        margin: 10px 0;
    }
    div.stButton > button:first-child {
        background-color: #212529;
        color: white;
        border-radius: 6px;
        width: 100%;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Task Break AI ")
st.caption("Task Breakdown and Refinement Assistant for Agile Delivery Teams")
st.write("---")

#API Configuration
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("Configuration Error: GEMINI_API_KEY mapping missing from .streamlit/secrets.toml")
    st.stop()

# Layout Segmentation
with st.sidebar:
    st.subheader("⚙️ Control Panel Configuration")
    ai_persona = st.selectbox(
        "Target Delivery Consultant:",
        ["Principal Software Architect", "Agile Scrum Master / Delivery Lead", "Strategic Product Manager"]
    )
    task_depth = st.select_slider(
        "Work Breakdown Structure (WBS) Scope:",
        options=["Micro Sprint (3 Tasks)", "Standard Lifecycle (5 Tasks)", "Comprehensive Epic (7 Tasks)"],
        value="Standard Lifecycle (5 Tasks)"
    )

user_goal = st.text_area(
    "Objective Statement / Scope of Work:",
    placeholder="Define the overarching objective or feature requirement you intend to decompose...",
)


if "tasks_list" not in st.session_state:
    st.session_state.tasks_list = []
if "active_refinement_idx" not in st.session_state:
    st.session_state.active_refinement_idx = None

# Core AI 
if st.button("Generate Scope Breakdown ", type="primary"):
    if not user_goal.strip():
        st.warning("Action required: Please define an objective statement before generating.")
    else:
        with st.spinner(f"Compiling project lifecycle parameters from the lens of a {ai_persona}..."):
            try:
                model = genai.GenerativeModel('gemini-3.5-flash')
                steps_count = "3" if "Micro" in task_depth else ("5" if "Standard" in task_depth else "7")
                
                structured_prompt = f"""
                You are operating strictly under the professional profile of a {ai_persona}. 
                Decompose the following project objective statement into exactly {steps_count} logical, sequential execution steps.
                Your response must conform strictly to a raw, valid JSON array of objects without markdown block enclosures.
                Each JSON object must contain exactly three keys: "title", "tip", and "hours".
                The value of "hours" must be an integer representing a realistic industry estimation.
                The value of "tip" must incorporate industry-standard best practices, design patterns, or strategies aligned directly with your professional role. Keep tips under 25 words.
                
                Objective Statement: {user_goal}
                """
                
                response = model.generate_content(structured_prompt)
                st.session_state.tasks_list = json.loads(response.text.strip())
                st.session_state.active_refinement_idx = None # Reset sub-prompt windows
                
            except Exception as e:
                st.error(f"System Parsing Failure. Details: {e}")

# Render Metric Dashboard & Contextual Workspace
if st.session_state.tasks_list:
    st.write("##")
    
    # Live Calculations for Metrics Header Row
    total_tasks = len(st.session_state.tasks_list)
    total_hours = sum(int(item['hours']) for item in st.session_state.tasks_list)
    
    completed_count = 0
    completed_hours = 0
    for idx, item in enumerate(st.session_state.tasks_list):
        if st.session_state.get(f"task_{idx}", False):
            completed_count += 1
            completed_hours += int(item['hours'])
            
    progress_percentage = completed_count / total_tasks if total_tasks > 0 else 0
    
    # Display Analytics
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Deliverables Completed", f"{completed_count} / {total_tasks}")
    m_col2.metric("Project Sizing Estimation", f"{total_hours} Hours")
    m_col3.metric("Velocity Cleared", f"{completed_hours} Hours")
    st.progress(progress_percentage)
    
    st.markdown("<div class='workspace-card'>", unsafe_allow_html=True)
    st.subheader("📋 Core Work Breakdown Structure Workspace")
    st.write("")
    
    for idx, item in enumerate(st.session_state.tasks_list):
        # 3-Column Layout: Checklist Node | Time| Context Actions Link
        task_col, info_col, action_col = st.columns([0.5, 0.2, 0.3])
        
        with task_col:
            checked = st.checkbox(f"**{item['title']}**", key=f"task_{idx}")
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;* [{ai_persona} Advisory]: {item['tip']}*")
            
        with info_col:
            st.markdown(f"<div style='color: #6c757d; font-size: 0.9em; padding-top: 5px;'>Time: <b>{item['hours']} hrs</b></div>", unsafe_allow_html=True)
            if checked:
                st.markdown("<span style='color: #198754; font-size: 0.85em; font-weight: 600;'>🟢 Milestone Certified</span>", unsafe_allow_html=True)
                
        with action_col:
            # Contextual Query Tray
            if st.button(f"💬 Refine / Ask Advisor", key=f"refine_btn_{idx}"):
                st.session_state.active_refinement_idx = idx
                st.rerun()

        # --- Dynamic Contextual Query Tray Execution ---
        if st.session_state.active_refinement_idx == idx:
            st.markdown(f"<div class='refinement-box'>", unsafe_allow_html=True)
            st.markdown(f"**Contextual Assistant Layer:** Ask a question regarding *\"{item['title']}\"* or request specific task updates below.")
            
            refine_query = st.text_input(
                "Enter clarification query or modification instruction:",
                placeholder="e.g., Explain how to execute this step, or reduce the time requirement...",
                key=f"query_input_{idx}"
            )
            
            sub_col1, sub_col2 = st.columns([0.3, 0.7])
            with sub_col1:
                if st.button("Submit", key=f"submit_refine_{idx}"):
                    if refine_query.strip():
                        with st.spinner("Processing architectural modifications..."):
                            try:
                                model = genai.GenerativeModel('gemini-3.5-flash')
                                contextual_prompt = f"""
                                You are an expert consultant working inside an active scrum board.
                                We are focusing strictly on this single execution step:
                                Title: "{item['title']}"
                                Current Tip: "{item['tip']}"
                                Current Budget: {item['hours']} hours
                                
                                The user has the following question or instruction: "{refine_query}"
                                
                                Adjust or clarify this step. Return your answer STRICTLY as a raw JSON object matching the parent schema. No markdown fences.
                                Schema keys: "title", "tip", and "hours". 
                                - If they asked a question, answer it concisely inside the "tip" property.
                                - If they asked to modify the time or text, update "hours" or "title" accordingly.
                                Keep the "tip" under 40 words.
                                """
                                response = model.generate_content(contextual_prompt)
                                updated_node = json.loads(response.text.strip())
                                
                                # In-place variable override updating state registry memory completely database-free
                                st.session_state.tasks_list[idx] = updated_node
                                st.session_state.active_refinement_idx = None # Close tray
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Modification execution failed. Details: {e}")
            with sub_col2:
                if st.button("Cancel ", key=f"cancel_refine_{idx}"):
                    st.session_state.active_refinement_idx = None
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<hr style='margin: 15px 0; border: 0; border-top: 1px solid #e9ecef;'>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)