import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import json
import time
from typing import Dict, List, Optional
import base64

# Configuration
API_BASE_URL = "https://anmol1357-resume_checker_backend.hf.space"

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
    st.session_state.current_view = 'Placement Team'
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'selected_job_id' not in st.session_state:
    st.session_state.selected_job_id = None
if 'candidates' not in st.session_state:
    st.session_state.candidates = []
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# Helper Functions
def make_api_request(method: str, endpoint: str, **kwargs) -> Optional[Dict]:
    """Make API request to backend"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.request(method, url, timeout=30, **kwargs)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def fetch_jobs():
    """Fetch all available jobs from the backend"""
    result = make_api_request("GET", "/api/v1/jobs")
    if result:
        st.session_state.jobs = result.get('jobs', [])
        return result.get('jobs', [])
    return []

def upload_job_description(file):
    """Upload job description to backend"""
    files = {'file': (file.name, file.getvalue(), file.type)}
    result = make_api_request("POST", "/api/v1/jobs", files=files)
    return result

def fetch_candidates(job_id: str):
    """Fetch candidates for a specific job"""
    result = make_api_request("GET", f"/api/v1/jobs/{job_id}/candidates")
    if result:
        st.session_state.candidates = result.get('candidates', [])
        return result.get('candidates', [])
    return []

def analyze_resume(job_id: str, resume_file):
    """Send resume for analysis"""
    files = {'file': (resume_file.name, resume_file.getvalue(), resume_file.type)}
    data = {'job_id': job_id}
    result = make_api_request("POST", "/api/v1/analyze", files=files, data=data)
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

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🎯 Navigation")
    view_option = st.radio(
        "Select View:",
        ["Placement Team", "Student Portal"],
        key="view_selector"
    )
    st.session_state.current_view = view_option
    
    st.markdown("---")
    st.markdown("### 📊 Quick Stats")
    total_jobs = len(st.session_state.jobs) if st.session_state.jobs else 0
    st.metric("Active Job Postings", total_jobs)
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("This system uses AI to analyze resume relevance against job descriptions, helping both recruiters and students optimize the hiring process.")

# Main Application
st.markdown('<h1 class="header-title">📄 Innomatics Resume Analyzer</h1>', unsafe_allow_html=True)

# Placement Team View
if st.session_state.current_view == "Placement Team":
    st.markdown("## 👔 Placement Team Dashboard")
    
    tab1, tab2 = st.tabs(["📤 Upload JD", "👥 Candidate Review"])
    
    with tab1:
        st.markdown("### Upload Job Description")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            jd_file = st.file_uploader(
                "Choose a Job Description file",
                type=['txt', 'pdf'],
                help="Upload a text or PDF file containing the job description"
            )
            
            if jd_file is not None:
                if st.button("🚀 Process Job Description", type="primary"):
                    with st.spinner("Processing job description..."):
                        result = upload_job_description(jd_file)
                        
                    if result:
                        st.success("✅ Job Description uploaded successfully!")
                        
                        # Display extracted details
                        st.markdown("### 📋 Extracted Job Details")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Role Title:** {result.get('title', 'N/A')}")
                            st.markdown(f"**Department:** {result.get('department', 'N/A')}")
                            st.markdown(f"**Experience Required:** {result.get('experience', 'N/A')}")
                        
                        with col2:
                            st.markdown(f"**Location:** {result.get('location', 'N/A')}")
                            st.markdown(f"**Job ID:** `{result.get('job_id', 'N/A')}`")
                        
                        if result.get('skills'):
                            st.markdown("**Must-Have Skills:**")
                            skills_cols = st.columns(4)
                            for idx, skill in enumerate(result.get('skills', [])):
                                with skills_cols[idx % 4]:
                                    st.markdown(f"• {skill}")
                        
                        # Refresh jobs list
                        fetch_jobs()
        
        with col2:
            st.markdown("### 📊 Recent Uploads")
            recent_jobs = fetch_jobs()
            if recent_jobs:
                for job in recent_jobs[:5]:
                    st.markdown(f"• {job.get('title', 'Untitled')} - {job.get('date', '')}")
    
    with tab2:
        st.markdown("### 👥 Candidate Review Dashboard")
        
        # Job selection
        jobs = fetch_jobs()
        if jobs:
            job_titles = [f"{job.get('title', 'Untitled')} (ID: {job.get('id', 'N/A')})" for job in jobs]
            selected_job = st.selectbox("Select Job Position:", job_titles)
            
            if selected_job:
                job_id = selected_job.split("ID: ")[1].rstrip(")")
                st.session_state.selected_job_id = job_id
                
                if st.button("🔄 Load Candidates"):
                    with st.spinner("Fetching candidate data..."):
                        candidates = fetch_candidates(job_id)
                    
                    if candidates:
                        st.success(f"Found {len(candidates)} candidates")
                        st.session_state.candidates = candidates
        
        # Display candidates
        if st.session_state.candidates:
            st.markdown("### 📊 Candidate Analysis")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                verdict_filter = st.multiselect(
                    "Filter by Verdict:",
                    ["High", "Medium", "Low"],
                    default=["High", "Medium", "Low"]
                )
            with col2:
                min_score = st.slider("Minimum Score:", 0, 100, 0)
            with col3:
                max_score = st.slider("Maximum Score:", 0, 100, 100)
            
            # Filter candidates
            filtered_candidates = [
                c for c in st.session_state.candidates
                if c.get('verdict', '') in verdict_filter
                and min_score <= c.get('score', 0) <= max_score
            ]
            
            # Display table
            if filtered_candidates:
                df = pd.DataFrame(filtered_candidates)
                df['score'] = df['score'].apply(lambda x: f"{x}%")
                
                # Display with custom styling
                st.dataframe(
                    df[['name', 'score', 'verdict']],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Detailed view
                st.markdown("### 🔍 Detailed Analysis")
                for idx, candidate in enumerate(filtered_candidates):
                    with st.expander(f"📋 {candidate['name']} - Score: {candidate['score']}%"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Relevance Score:** {candidate['score']}%")
                            st.markdown(f"**Verdict:** {candidate['verdict']}")
                            st.markdown(f"**Email:** {candidate.get('email', 'N/A')}")
                        
                        with col2:
                            if candidate.get('missing_skills'):
                                st.markdown("**Missing Skills:**")
                                for skill in candidate['missing_skills']:
                                    st.markdown(f"• {skill}")
                            
                            if candidate.get('missing_certifications'):
                                st.markdown("**Missing Certifications:**")
                                for cert in candidate['missing_certifications']:
                                    st.markdown(f"• {cert}")
            else:
                st.info("No candidates match the selected filters")
        else:
            st.info("No candidates found. Please load candidates for a job position.")

# Student View
else:
    st.markdown("## 🎓 Student Portal")
    
    tab1, tab2 = st.tabs(["📤 Submit Resume", "📊 View Results"])
    
    with tab1:
        st.markdown("### Submit Your Resume for Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Fetch available jobs
            jobs = fetch_jobs()
            
            if jobs:
                job_options = [f"{job.get('title', 'Untitled')} - {job.get('department', '')}" for job in jobs]
                selected_job_str = st.selectbox(
                    "Select the position you're applying for:",
                    job_options,
                    help="Choose the job description to match your resume against"
                )
                
                # Extract job ID
                selected_job_idx = job_options.index(selected_job_str)
                selected_job_id = jobs[selected_job_idx].get('id')
                
                resume_file = st.file_uploader(
                    "Upload your resume",
                    type=['pdf', 'docx'],
                    help="Upload your resume in PDF or DOCX format"
                )
                
                if resume_file and selected_job_id:
                    if st.button("🚀 Analyze My Resume", type="primary"):
                        with st.spinner("Analyzing your resume... This may take a moment."):
                            result = analyze_resume(selected_job_id, resume_file)
                        
                        if result:
                            st.session_state.analysis_result = result
                            st.success("✅ Analysis complete! Check the Results tab.")
                            st.balloons()
            else:
                st.warning("No job positions available. Please contact the placement team.")
        
        with col2:
            st.markdown("### 💡 Tips for Better Scores")
            st.info("""
            • Use keywords from the job description
            • Highlight relevant projects
            • Include certifications
            • Quantify achievements
            • Keep format clean and ATS-friendly
            """)
    
    with tab2:
        if st.session_state.analysis_result:
            result = st.session_state.analysis_result
            
            st.markdown("### 📊 Your Resume Analysis Results")
            
            # Score display
            score = result.get('relevance_score', 0)
            render_score_gauge(score)
            
            # Verdict
            verdict = result.get('verdict', 'Unknown')
            verdict_color = {
                'High': '#28a745',
                'Medium': '#ffc107', 
                'Low': '#dc3545'
            }.get(verdict, '#6c757d')
            
            st.markdown(f"""
            <div style="text-align: center; margin: 2rem 0;">
                <h2>Fit Verdict: <span style="color: {verdict_color};">{verdict}</span></h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Detailed feedback
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ❌ Missing Elements")
                
                if result.get('missing_skills'):
                    st.markdown("**Skills to Add:**")
                    for skill in result['missing_skills']:
                        st.markdown(f"• {skill}")
                
                if result.get('missing_certifications'):
                    st.markdown("**Certifications to Consider:**")
                    for cert in result['missing_certifications']:
                        st.markdown(f"• {cert}")
                
                if result.get('missing_projects'):
                    st.markdown("**Project Ideas:**")
                    for project in result['missing_projects']:
                        st.markdown(f"• {project}")
            
            with col2:
                st.markdown("### 💡 Personalized Suggestions")
                
                if result.get('suggestions'):
                    for suggestion in result['suggestions']:
                        st.info(f"💡 {suggestion}")
                else:
                    st.info("Your resume looks good! Consider adding more specific examples that demonstrate your skills.")
            
            # Export option
            if st.button("📥 Download Analysis Report"):
                report = f"""
                Resume Analysis Report
                ======================
                Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                
                Relevance Score: {score}%
                Verdict: {verdict}
                
                Missing Skills:
                {chr(10).join(['- ' + s for s in result.get('missing_skills', [])])}
                
                Missing Certifications:
                {chr(10).join(['- ' + c for c in result.get('missing_certifications', [])])}
                
                Suggestions:
                {chr(10).join(['- ' + s for s in result.get('suggestions', [])])}
                """
                
                b64 = base64.b64encode(report.encode()).decode()
                href = f'<a href="data:file/txt;base64,{b64}" download="resume_analysis_{datetime.now().strftime("%Y%m%d")}.txt">Download Report</a>'
                st.markdown(href, unsafe_allow_html=True)
        else:
            st.info("📤 Please submit your resume in the 'Submit Resume' tab to see analysis results.")
            
            # Sample analysis preview
            if st.checkbox("View Sample Analysis"):
                st.markdown("### Sample Analysis Preview")
                render_score_gauge(75, "Sample Score")
                st.success("This is what your analysis will look like after submission!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 1rem;">
    <p>🚀 Powered by Innomatics Resume Analyzer | Built with Streamlit & FastAPI</p>
</div>
""", unsafe_allow_html=True)