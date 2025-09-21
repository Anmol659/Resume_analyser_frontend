import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import time
from typing import Dict, List, Optional
import base64

# Configuration
API_BASE_URL = "https://anmol1357-resume-checker-backend.hf.space"

# Page Configuration
st.set_page_config(
    page_title="Innomatics Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling - Simplified for Readability
st.markdown("""
    <style>
    /* Remove default Streamlit padding for a cleaner look */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Button styling */
    .stButton > button {
        background-color: #667eea;
        color: white;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        border: none;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5);
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        text-align: center;
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    
    .header-title {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.2rem;
        font-weight: 400;
    }
    
    /* Verdict styling */
    .verdict-high {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
    }
    
    .verdict-medium {
        background: linear-gradient(135deg, #f2994a 0%, #f2c94c 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
    }
    
    .verdict-low {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-block;
    }

    /* Footer styling */
    .footer {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        border-radius: 15px; 
        padding: 2rem; 
        margin-top: 3rem; 
        text-align: center; 
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'show_placement' not in st.session_state:
    st.session_state.show_placement = False

# Helper Functions
def make_api_request(method: str, endpoint: str, **kwargs) -> Optional[Dict]:
    """Make API request to backend"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        timeout = 120 
        response = requests.request(method, url, timeout=timeout, **kwargs)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def analyze_resumes(jd_file, resume_files):
    """Send JD and resumes for analysis"""
    files = [('job_description', (jd_file.name, jd_file.getvalue(), jd_file.type))]
    for resume_file in resume_files:
        files.append(('resumes', (resume_file.name, resume_file.getvalue(), resume_file.type)))
    
    result = make_api_request("POST", "/api/v1/resume", files=files)
    return result

def render_circular_progress(score: int, size: int = 200):
    """Render a circular progress indicator with readable text."""
    progress_color = "#38ef7d" if score >= 70 else "#f2c94c" if score >= 40 else "#f45c43"
    background_color = "#e0e0e0"
    text_color = "#262730" # Dark text color for all themes
    
    circumference = 2 * 3.14159 * 90
    offset = circumference - (score / 100) * circumference
    
    return f"""
    <div style="display: flex; justify-content: center; align-items: center; margin: 2rem 0;">
        <svg width="{size}" height="{size}" viewBox="0 0 200 200">
            <circle cx="100" cy="100" r="90" fill="none" stroke="{background_color}" stroke-width="15"/>
            <circle cx="100" cy="100" r="90" fill="none" stroke="{progress_color}" stroke-width="15"
                    stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                    stroke-linecap="round" transform="rotate(-90 100 100)"/>
            <text x="100" y="90" text-anchor="middle" font-size="36" font-weight="bold" fill="{text_color}">
                {score}%
            </text>
            <text x="100" y="120" text-anchor="middle" font-size="16" fill="{text_color}">
                Relevance
            </text>
        </svg>
    </div>
    """

def get_verdict_html(verdict: str):
    """Get styled verdict HTML"""
    verdict_class = f"verdict-{verdict.lower()}"
    emoji = "🎯" if verdict.lower() == "high" else "⚡" if verdict.lower() == "medium" else "📈"
    return f'<div class="{verdict_class}">{emoji} {verdict} Match</div>'

# Sidebar
with st.sidebar:
    st.title("🎯 Navigation")
    
    view_option = st.radio(
        "",
        ["🎓 Student Portal", "👔 Placement Team"],
        key="view_selector",
        label_visibility="collapsed"
    )
    
    st.session_state.show_placement = "Placement" in view_option
    
    st.markdown("---")
    st.subheader("💡 Tips for Success")
    st.markdown("""
        - Use keywords from the JD
        - Highlight relevant projects
        - Include certifications
        - Quantify achievements
    """)
    
    st.markdown("---")
    st.subheader("📊 System Stats")
    st.info("Powered by AI. Fast, accurate, and reliable analysis.")

# Main content area
with st.container():
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">📄 Innomatics Resume Analyzer</h1>
        <p class="header-subtitle">AI-Powered Resume Screening & Analysis System</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.show_placement:
        # --- Student Portal View ---
        st.header("🎓 Student Portal - Check Your Resume Match")
        st.markdown("Upload a job description and your resume to get instant AI-powered feedback.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 📋 Upload Job Description")
            jd_file = st.file_uploader("", type=['pdf', 'docx', 'txt'], key="jd_upload")
        with col2:
            st.markdown("##### 📄 Upload Your Resume(s)")
            resume_files = st.file_uploader("", type=['pdf', 'docx'], accept_multiple_files=True, key="resume_upload")
        
        if jd_file and resume_files:
            if st.button("🚀 Analyze Resume Match", type="primary", use_container_width=True):
                with st.spinner("🔍 AI is analyzing your documents... This may take a moment."):
                    st.session_state.analysis_result = analyze_resumes(jd_file, resume_files)
                
                if st.session_state.analysis_result:
                    st.success("✅ Analysis Complete! See your results below.")
                    st.balloons()
        
        # Display results for Student Portal
        if st.session_state.analysis_result:
            result = st.session_state.analysis_result
            st.markdown("---")
            st.header("📊 Your Analysis Results")
            st.info(f"**Job Analyzed:** {result.get('job_description_file', 'N/A')}")

            for idx, candidate in enumerate(result.get('results', [])):
                score = candidate.get('relevance_score', 0)
                verdict = candidate.get('verdict', 'Unknown')
                
                with st.expander(f"📄 {candidate.get('file_name')} - Score: {score}% ({verdict})", expanded=(idx == 0)):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(render_circular_progress(score), unsafe_allow_html=True)
                        st.markdown(f"<center>{get_verdict_html(verdict)}</center>", unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader("💡 AI Feedback")
                        feedback = candidate.get('feedback', 'No feedback available.')
                        st.info(feedback)
                        
                        missing_skills = candidate.get('missing_skills', [])
                        if missing_skills:
                            st.subheader("🎯 Skills Gap Analysis")
                            st.warning("**Consider adding these to your resume:**")
                            skills_cols = st.columns(3)
                            for i, skill in enumerate(missing_skills):
                                with skills_cols[i % 3]:
                                    st.markdown(f"• `{skill}`")

    else:
        # --- Placement Team View ---
        st.header("👔 Placement Team Dashboard")
        st.markdown("Batch analyze multiple resumes against job descriptions.")
        
        # Removed the "Analytics" tab
        tab1, tab2 = st.tabs(["📤 Batch Analysis", "📊 Results Overview"])
        
        with tab1:
            st.subheader("Upload JD and Resumes")
            col1, col2 = st.columns(2)
            with col1:
                jd_file = st.file_uploader("Job Description", type=['pdf', 'docx', 'txt'], key="placement_jd")
            with col2:
                resume_files = st.file_uploader("Candidate Resumes", type=['pdf', 'docx'], accept_multiple_files=True, key="placement_resumes")
            
            if jd_file and resume_files:
                if st.button("🚀 Start Batch Analysis", type="primary", use_container_width=True):
                    with st.spinner(f"Analyzing {len(resume_files)} resumes..."):
                        st.session_state.analysis_result = analyze_resumes(jd_file, resume_files)
                    if st.session_state.analysis_result:
                        st.success("✅ Batch analysis complete!")

        with tab2:
            if st.session_state.analysis_result:
                result = st.session_state.analysis_result
                st.subheader("Candidate Ranking Dashboard")

                if result.get('results'):
                    df = pd.DataFrame(result.get('results'))
                    df = df.sort_values('relevance_score', ascending=False)
                    
                    st.dataframe(
                        df[['file_name', 'relevance_score', 'verdict']],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "relevance_score": st.column_config.ProgressColumn(
                                "Match %",
                                format="%d%%",
                                min_value=0,
                                max_value=100,
                            ),
                        }
                    )

                    st.markdown("---")
                    st.subheader("📋 Detailed Analysis")
                    for _, row in df.iterrows():
                        with st.expander(f"{row['file_name']} - {row['relevance_score']}%"):
                            st.write("**Feedback:**")
                            st.info(row.get('feedback', 'N/A'))
                            if row.get('missing_skills'):
                                st.write("**Missing Skills:** ", ", ".join(row['missing_skills']))
            else:
                st.info("No analysis results yet. Please run a batch analysis first.")
        
    st.markdown("""
    <div class="footer">
        <h3 style="margin-bottom: 1rem;">🚀 Powered by Innomatics AI</h3>
        <p style="margin-bottom: 0;">Advanced Resume Analysis • Instant Feedback • Data-Driven Insights</p>
    </div>
    """, unsafe_allow_html=True)

