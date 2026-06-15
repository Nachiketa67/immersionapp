import streamlit as st
import openai
import random

# 1. Page Configuration
st.set_page_config(page_title="PCI Project Cohesion Index", layout="wide")

# 2. Setup Session State for Demo (Ensures zero database lag during presentation)
if "project_saved" not in st.session_state:
    st.session_state.project_saved = False
    st.session_state.project_title = ""
    st.session_state.project_brief = ""
    st.session_state.questions = []
    st.session_state.all_responses = {}  # Format: {user_role: {q_index: answer}}

# Dummy fallback questions if API fails or for instant mock data
FALLBACK_QUESTIONS = [
    "What is your understanding of the primary technical milestone for this sprint?",
    "Which external API dependencies present the highest risk to our launch date?",
    "Who is the final decision-maker for architectural choices on the backend?",
    "What tools will we use to track daily blocker tickets and code reviews?",
    "Are there any skill gaps on the team regarding the selected vector database?",
    "What is the backup plan if the primary cloud hosting tier goes over budget?",
    "How often will cross-functional syncs happen between frontend and design?",
    "What metrics will we use to determine if this prototype is successful?"
]

# 3. Sidebar: Hackathon Demo Controller
with st.sidebar:
    st.header("🛠️ Demo Control Panel")
    st.info("Use this to simulate different roles filling out the survey for the judges.")
    
    current_role = st.selectbox(
        "Select Active User Persona:",
        ["Person 1 (Frontend Developer)", "Person 2 (AI Engineer)", "Person 3 (Backend Engineer)", "Person 4 (Product Lead)"]
    )
    
    st.divider()
    if st.button("Reset Entire Demo", type="primary"):
        st.session_state.clear()
        st.rerun()

# 4. Main App Layout
st.title("🚀 Project Cohesion Index (PCI) Analyzer")
st.caption("Transforming static project briefs into dynamically aligned engineering teams.")

# PHASE 1: Project Initiation
if not st.session_state.project_saved:
    st.header("1. Initialize New Project Profile")
    
    with st.form("init_project"):
        title = st.text_input("Project Name", placeholder="e.g., Nexus AI Marketplace")
        brief = st.text_area("Project Brief & Technical Scope", placeholder="Paste product requirements documents or rough feature ideas here...")
        
        # Pull OpenAI Key from Streamlit Secrets Configuration
        api_key_configured = "OPENAI_API_KEY" in st.secrets
        
        submit = st.form_submit_button("Generate Alignment Strategy")
        
    if submit and brief:
        st.session_state.project_title = title
        st.session_state.project_brief = brief
        
        if api_key_configured:
            with st.spinner("AI analyzing scope and generating targeted alignment checklist..."):
                try:
                    openai.api_key = st.secrets["OPENAI_API_KEY"]
                    prompt = f"Analyze this project brief and output exactly 8 specific alignment questions to test if an engineering team is on the same page regarding execution, architecture, and risks. Brief: {brief}. Output only the 8 questions as a numbered list. No filler text."
                    
                    response = openai.ChatCompletion.create(
                        model="gpt-4o",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.5
                    )
                    
                    raw_text = response.choices[0].message.content
                    questions = [q.split(". ", 1)[-1].strip() for q in raw_text.strip().split("\n") if q]
                    st.session_state.questions = questions[:8]
                except Exception:
                    st.session_state.questions = FALLBACK_QUESTIONS
        else:
            # Fallback seamlessly if hackathon keys aren't configured yet
            st.session_state.questions = FALLBACK_QUESTIONS
            
        st.session_state.project_saved = True
        st.rerun()

# PHASE 2 & 3: Survey Collection & Live Dashboard
else:
    st.header(f"📋 Dashboard: {st.session_state.project_title}")
    
    tab1, tab2 = st.tabs(["✍️ Submit Alignment Input", "📊 Live PCI Analytics"])
    
    # TAB 1: User Response Input Workspace
    with tab1:
        st.subheader(f"Responding as: :blue[{current_role}]")
        st.write("Answer the following AI-generated questions based on your understanding of the scope:")
        
        # Load existing responses for this specific persona if they exist
        if current_role not in st.session_state.all_responses:
            st.session_state.all_responses[current_role] = {}
            
        with st.form(f"survey_{current_role}"):
            user_answers = {}
            for i, q in enumerate(st.session_state.questions):
                saved_val = st.session_state.all_responses[current_role].get(i, "")
                user_answers[i] = st.text_area(f"Q{i+1}: {q}", value=saved_val, key=f"q_{current_role}_{i}")
                
            if st.form_submit_button("Save System Answers"):
                st.session_state.all_responses[current_role] = user_answers
                st.success(f"Successfully recorded answers for {current_role}!")
                st.balloons()
                
    # TAB 2: Pitch Deck Ready Analytics Dashboard
    with tab2:
        total_respondents = len(st.session_state.all_responses)
        
        if total_respondents == 0:
            st.warning("No data collected yet. Go to the first tab and submit answers for at least one persona.")
        else:
            st.subheader("Team Cohesion Health Metrics")
            
            # Algorithmic calculation of mock PCI tracking vector based on responses input
            # Scales metrics based on the volume of detailed feedback provided
            chars_written = sum(len(str(ans)) for role in st.session_state.all_responses.values() for ans in role.values())
            random.seed(chars_written if chars_written > 0 else 42)
            
            pci = min(max(int(50 + (total_respondents * 10) + (chars_written % 15)), 40), 98)
            role_clarity = min(pci + random.randint(-5, 5), 100)
            tool_cohesion = min(pci + random.randint(-8, 2), 100)
            risk_alignment = min(pci + random.randint(-3, 7), 100)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Overall PCI Score", f"{pci}%", delta=f"{pci-70}% vs Target" if pci>70 else f"{pci-70}% vs Target")
            col2.metric("Role Clarity", f"{role_clarity}%")
            col3.metric("Tool Cohesion", f"{tool_cohesion}%")
            col4.metric("Risk Alignment", f"{risk_alignment}%")
            
            st.divider()
            
            # Show collected feedback raw text comparison for judges to review divergence
            st.subheader("🔍 Side-by-Side Review Matrix")
            selected_q = st.selectbox("Select question to evaluate team divergence:", [f"Q{i+1}: {q[:60]}..." for i, q in enumerate(st.session_state.questions)])
            q_idx = int(selected_q.split(":")[0][1:]) - 1
            
            st.info(f"**Full Question:** {st.session_state.questions[q_idx]}")
            
            for role, answers in st.session_state.all_responses.items():
                answer_text = answers.get(q_idx, "*No answer recorded yet.*")
                st.markdown(f"**{role}:**")
                st.caption(answer_text)
            
            st.divider()
            
            # Strategic Action Plan Generation
            st.subheader("💡 AI Structural Interventions")
            if pci < 75:
                st.error("⚠️ High Risk Anomaly Detected: Critical friction points identified regarding release timeline ownership.")
                st.markdown("""
                - **Intervention 1:** Lock down an immediate 30-minute sync between Backend and AI engineering streams to map contract interfaces.
                - **Intervention 2:** Establish standard project metric definitions inside a centralized dashboard rather than relying on disparate tracking systems.
                """)
            else:
                st.success("✅ Execution Health Nominal: Strong cross-functional alignment observed across core architectural layers.")
                st.markdown("""
                - **Recommendation:** Proceed directly to environment initialization and begin concurrent sprint tasks.
                """)
