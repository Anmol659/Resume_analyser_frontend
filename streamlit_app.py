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

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .score-high {
        color: #28a745;
        font-weight: bold;
    }
    .score-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .score-low {
        color: #dc3545;
        font-weight: bold;
    }
    .header-title {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'Student Portal' # Default to student view
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# Helper Functions
def make_api_request(method: str, endpoint: str, **kwargs) -> Optional[Dict]:
    """Make API request to backend"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        # Increase timeout for analysis
        timeout = 120 if "resume" in endpoint else 30
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
    
    # Corrected endpoint
    result = make_api_request("POST", "/api/v1/resume", files=files)
    return result

def get_score_color(score):
    """Get color class based on score"""
    if score >= 70:
        return "score-high"
    elif score >= 40:
        return "score-medium"
    else:
        return "score-low"

def render_score_gauge(score: int, title: str = "Relevance Score"):
    """Render a visual score gauge"""
    color = "#28a745" if score >= 70 else "#ffc107" if score >= 40 else "#dc3545"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center;">
            <h3>{title}</h3>
            <div style="position: relative; width: 200px; height: 100px; margin: 0 auto;">
                <svg width="200" height="100" style="transform: rotate(-90deg);">
                    <circle cx="100" cy="100" r="80" fill="none" stroke="#e0e0e0" stroke-width="20"/>
                    <circle cx="100" cy="100" r="80" fill="none" stroke="{color}" 
                            stroke-width="20" stroke-dasharray="{score * 2.51} 251" 
                            stroke-linecap="round"/>
                </svg>
                <div style="position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%);">
                    <span style="font-size: 2.5rem; font-weight: bold; color: {color};">{score}%</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Main Application ---
st.markdown('<h1 class="header-title">📄 Innomatics Resume Analyzer</h1>', unsafe_allow_html=True)

# Simplified interface
st.markdown("## 🚀 Get Started")
st.markdown("Upload a job description and one or more resumes to see the AI-powered analysis in action.")

col1, col2 = st.columns(2)
with col1:
    jd_file = st.file_uploader(
        "1. Upload Job Description",
        type=['pdf', 'docx', 'txt'],
        help="Upload the job description file."
    )

with col2:
    resume_files = st.file_uploader(
        "2. Upload Resumes",
        type=['pdf', 'docx'],
        accept_multiple_files=True,
        help="Upload one or more resume files."
    )

if jd_file and resume_files:
    if st.button("✨ Analyze Now", type="primary", use_container_width=True):
        with st.spinner("Analyzing documents... This may take a moment depending on the number of resumes."):
            analysis_result = analyze_resumes(jd_file, resume_files)
        
        if analysis_result:
            st.session_state.analysis_result = analysis_result
            st.success("✅ Analysis Complete!")
            st.balloons()
        else:
            st.error("Something went wrong during the analysis. Please check the logs.")

# Display results if available
if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")
    st.markdown(f"**Analysis for Job:** `{result.get('job_description_file', 'N/A')}`")
    st.markdown(f"**Firestore Job ID:** `{result.get('firestore_job_id', 'N/A')}`")

    # Display results for each candidate
    if result.get('results'):
        for candidate in result['results']:
            score = candidate.get('relevance_score', 0)
            verdict = candidate.get('verdict', 'Unknown')
            
            with st.expander(f"📄 **{candidate.get('file_name')}** - Score: {score}% ({verdict})", expanded=True):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    render_score_gauge(score)
                    verdict_color = get_score_color(score).split('-')[1]
                    st.markdown(f"<h4 style='text-align: center;'>Verdict: <span style='color: {verdict_color};'>{verdict}</span></h4>", unsafe_allow_html=True)

                with col2:
                    st.markdown("#### Key Feedback")
                    st.info(f"💡 {candidate.get('feedback', 'No feedback available.')}")
                    
                    missing_skills = candidate.get('missing_skills', [])
                    if missing_skills:
                        st.markdown("##### Areas for Improvement (Missing Skills)")
                        st.warning(" ".join([f"`{skill}`" for skill in missing_skills]))
    else:
        st.warning("No analysis results were returned from the API.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 1rem;">
    <p>🚀 Powered by Innomatics Resume Analyzer | Built with Streamlit & FastAPI</p>
</div>
""", unsafe_allow_html=True)
