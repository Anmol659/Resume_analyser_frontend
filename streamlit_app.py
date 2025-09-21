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

# Custom CSS for better styling - Enhanced version
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .block-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem auto;
        max-width: 1400px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    
    /* File uploader styling */
    .stFileUploader {
        background: white;
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #764ba2;
        background: #f8f9ff;
    }
    
    .uploadedFile {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 10px;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 0;
        margin: -2rem -2rem 2rem -2rem;
        text-align: center;
        border-radius: 20px 20px 0 0;
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
    
    /* Score card styling */
    .score-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .score-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
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
    
    /* Expander styling */
    .streamlit-expander {
        background: white;
        border: 2px solid #f0f2f6;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .streamlit-expander:hover {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    /* Info box styling */
    .stAlert {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-left: 4px solid #667eea;
        border-radius: 10px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .sidebar .sidebar-content {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Metric styling */
    .metric-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 3px 15px rgba(0, 0, 0, 0.08);
        margin: 1rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        border: 2px solid #f0f2f6;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'Student Portal'
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'show_placement' not in st.session_state:
    st.session_state.show_placement = False

# Helper Functions
def make_api_request(method: str, endpoint: str, **kwargs) -> Optional[Dict]:
    """Make API request to backend"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
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
    
    # Using the correct endpoint
    result = make_api_request("POST", "/api/v1/resume", files=files)
    return result

def render_circular_progress(score: int, size: int = 200):
    """Render a circular progress indicator"""
    color = "#38ef7d" if score >= 70 else "#f2c94c" if score >= 40 else "#f45c43"
    background_color = "#e0e0e0"
    
    # Calculate the stroke dasharray for the circle
    circumference = 2 * 3.14159 * 90  # radius = 90
    offset = circumference - (score / 100) * circumference
    
    return f"""
    <div style="display: flex; justify-content: center; align-items: center; margin: 2rem 0;">
        <svg width="{size}" height="{size}" viewBox="0 0 200 200">
            <!-- Background circle -->
            <circle cx="100" cy="100" r="90" fill="none" stroke="{background_color}" stroke-width="15"/>
            <!-- Progress circle -->
            <circle cx="100" cy="100" r="90" fill="none" stroke="{color}" stroke-width="15"
                    stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                    stroke-linecap="round" transform="rotate(-90 100 100)"/>
            <!-- Score text -->
            <text x="100" y="90" text-anchor="middle" font-size="36" font-weight="bold" fill="{color}">
                {score}%
            </text>
            <text x="100" y="120" text-anchor="middle" font-size="16" fill="#666">
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
    st.markdown("""
    <div style="background: white; border-radius: 15px; padding: 1.5rem; margin-bottom: 1rem;">
        <h3 style="color: #667eea; margin-bottom: 1rem;">🎯 Navigation</h3>
    </div>
    """, unsafe_allow_html=True)
    
    view_option = st.radio(
        "",
        ["🎓 Student Portal", "👔 Placement Team"],
        key="view_selector"
    )
    
    if "Placement" in view_option:
        st.session_state.show_placement = True
    else:
        st.session_state.show_placement = False
    
    st.markdown("""
    <div style="background: white; border-radius: 15px; padding: 1.5rem; margin-top: 2rem;">
        <h4 style="color: #667eea;">💡 Tips for Success</h4>
        <ul style="color: #666; font-size: 0.9rem;">
            <li>Use keywords from JD</li>
            <li>Highlight relevant projects</li>
            <li>Include certifications</li>
            <li>Quantify achievements</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                border-radius: 15px; padding: 1.5rem; margin-top: 2rem; color: white; text-align: center;">
        <h4>📊 System Stats</h4>
        <p style="margin: 0.5rem 0;">Powered by AI</p>
        <p style="margin: 0.5rem 0; font-size: 0.9rem;">Fast • Accurate • Reliable</p>
    </div>
    """, unsafe_allow_html=True)

# Main content area
main_container = st.container()

with main_container:
    # Header
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">📄 Innomatics Resume Analyzer</h1>
        <p class="header-subtitle">AI-Powered Resume Screening & Analysis System</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.show_placement:
        # Student Portal View
        st.markdown("### 🎓 Student Portal - Check Your Resume Match")
        st.markdown("Upload a job description and your resume to get instant AI-powered feedback")
        
        # File uploaders with better layout
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📋 Step 1: Upload Job Description")
            jd_file = st.file_uploader(
                "",
                type=['pdf', 'docx', 'txt'],
                help="Upload the job description you're applying for",
                key="jd_upload"
            )
            
            if jd_file:
                st.success(f"✅ JD uploaded: {jd_file.name}")
        
        with col2:
            st.markdown("##### 📄 Step 2: Upload Your Resume(s)")
            resume_files = st.file_uploader(
                "",
                type=['pdf', 'docx'],
                accept_multiple_files=True,
                help="You can upload multiple resumes for batch analysis",
                key="resume_upload"
            )
            
            if resume_files:
                st.success(f"✅ {len(resume_files)} resume(s) uploaded")
                for resume in resume_files:
                    st.caption(f"• {resume.name}")
        
        # Analyze button
        if jd_file and resume_files:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Analyze Resume Match", type="primary", use_container_width=True):
                    with st.spinner("🔍 AI is analyzing your documents... This may take 30-60 seconds"):
                        progress = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress.progress(i + 1)
                        
                        analysis_result = analyze_resumes(jd_file, resume_files)
                        progress.empty()
                    
                    if analysis_result:
                        st.session_state.analysis_result = analysis_result
                        st.success("✅ Analysis Complete! See your results below.")
                        st.balloons()
        
        # Display results
        if st.session_state.analysis_result:
            result = st.session_state.analysis_result
            
            st.markdown("---")
            st.markdown("## 📊 Your Analysis Results")
            
            # Job info
            st.info(f"**📋 Job Analyzed:** {result.get('job_description_file', 'N/A')} | **🔖 Job ID:** `{result.get('firestore_job_id', 'N/A')}`")
            
            # Results for each resume
            if result.get('results'):
                for idx, candidate in enumerate(result['results']):
                    score = candidate.get('relevance_score', 0)
                    verdict = candidate.get('verdict', 'Unknown')
                    
                    # Create expandable card for each resume
                    with st.expander(f"📄 {candidate.get('file_name')} - Score: {score}% ({verdict})", expanded=(idx == 0)):
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            # Circular progress
                            st.markdown(render_circular_progress(score), unsafe_allow_html=True)
                            
                            # Verdict badge
                            st.markdown(f"<center>{get_verdict_html(verdict)}</center>", unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("#### 💡 AI Feedback")
                            feedback = candidate.get('feedback', 'No feedback available.')
                            st.info(feedback)
                            
                            missing_skills = candidate.get('missing_skills', [])
                            if missing_skills:
                                st.markdown("#### 🎯 Skills Gap Analysis")
                                st.warning("**Add these skills to improve your score:**")
                                
                                # Display skills in a grid
                                skills_cols = st.columns(3)
                                for i, skill in enumerate(missing_skills):
                                    with skills_cols[i % 3]:
                                        st.markdown(f"• `{skill}`")
                            
                            # Action items
                            st.markdown("#### ✅ Next Steps")
                            if score >= 70:
                                st.success("Great match! Your resume aligns well with the job requirements.")
                            elif score >= 40:
                                st.warning("Good start! Add the missing skills to improve your chances.")
                            else:
                                st.error("Consider tailoring your resume more closely to the job requirements.")
    
    else:
        # Placement Team View
        st.markdown("### 👔 Placement Team Dashboard")
        st.markdown("Batch analyze multiple resumes against job descriptions")
        
        tab1, tab2, tab3 = st.tabs(["📤 Batch Analysis", "📊 Results Overview", "📈 Analytics"])
        
        with tab1:
            st.markdown("#### Upload JD and Multiple Resumes for Batch Processing")
            
            col1, col2 = st.columns(2)
            
            with col1:
                jd_file = st.file_uploader(
                    "Job Description",
                    type=['pdf', 'docx', 'txt'],
                    key="placement_jd"
                )
            
            with col2:
                resume_files = st.file_uploader(
                    "Candidate Resumes (Multiple)",
                    type=['pdf', 'docx'],
                    accept_multiple_files=True,
                    key="placement_resumes"
                )
            
            if jd_file and resume_files:
                st.info(f"Ready to analyze {len(resume_files)} resumes against the job description")
                
                if st.button("🚀 Start Batch Analysis", type="primary", use_container_width=True):
                    with st.spinner(f"Analyzing {len(resume_files)} resumes..."):
                        analysis_result = analyze_resumes(jd_file, resume_files)
                    
                    if analysis_result:
                        st.session_state.analysis_result = analysis_result
                        st.success("✅ Batch analysis complete!")
        
        with tab2:
            if st.session_state.analysis_result:
                result = st.session_state.analysis_result
                
                st.markdown("#### Candidate Ranking Dashboard")
                
                if result.get('results'):
                    # Create DataFrame for better visualization
                    candidates_data = []
                    for r in result['results']:
                        candidates_data.append({
                            'Candidate': r.get('file_name', 'Unknown'),
                            'Score': r.get('relevance_score', 0),
                            'Verdict': r.get('verdict', 'Unknown'),
                            'Status': '✅ Good Fit' if r.get('relevance_score', 0) >= 70 else '⚠️ Review' if r.get('relevance_score', 0) >= 40 else '❌ Poor Fit'
                        })
                    
                    df = pd.DataFrame(candidates_data)
                    df = df.sort_values('Score', ascending=False)
                    
                    # Display top candidates
                    st.markdown("##### 🏆 Top Candidates")
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Score": st.column_config.ProgressColumn(
                                "Match %",
                                help="Relevance score",
                                format="%d%%",
                                min_value=0,
                                max_value=100,
                            ),
                        }
                    )
                    
                    # Detailed view
                    st.markdown("##### 📋 Detailed Analysis")
                    for candidate in result['results']:
                        with st.expander(f"{candidate.get('file_name')} - {candidate.get('relevance_score')}%"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Score", f"{candidate.get('relevance_score')}%")
                                st.metric("Verdict", candidate.get('verdict'))
                            with col2:
                                st.write("**Feedback:**")
                                st.write(candidate.get('feedback'))
                                if candidate.get('missing_skills'):
                                    st.write("**Skills Gap:**")
                                    st.write(", ".join(candidate.get('missing_skills')))
            else:
                st.info("No analysis results yet. Please run a batch analysis first.")
        
        with tab3:
            if st.session_state.analysis_result and st.session_state.analysis_result.get('results'):
                st.markdown("#### 📈 Recruitment Analytics")
                
                results = st.session_state.analysis_result['results']
                
                # Calculate statistics
                scores = [r.get('relevance_score', 0) for r in results]
                avg_score = sum(scores) / len(scores) if scores else 0
                high_fit = len([s for s in scores if s >= 70])
                medium_fit = len([s for s in scores if 40 <= s < 70])
                low_fit = len([s for s in scores if s < 40])
                
                # Display metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Average Score", f"{avg_score:.1f}%")
                with col2:
                    st.metric("High Fit", high_fit, delta=f"{(high_fit/len(scores)*100):.0f}%")
                with col3:
                    st.metric("Medium Fit", medium_fit, delta=f"{(medium_fit/len(scores)*100):.0f}%")
                with col4:
                    st.metric("Low Fit", low_fit, delta=f"{(low_fit/len(scores)*100):.0f}%")
                
                # Distribution chart (text-based)
                st.markdown("##### Score Distribution")
                chart_data = pd.DataFrame({
                    'Category': ['High (70-100)', 'Medium (40-69)', 'Low (0-39)'],
                    'Count': [high_fit, medium_fit, low_fit]
                })
                st.bar_chart(chart_data.set_index('Category'))
            else:
                st.info("Run an analysis to see analytics")

# Footer
st.markdown("---")
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 15px; padding: 2rem; margin-top: 3rem; text-align: center; color: white;">
    <h3 style="margin-bottom: 1rem;">🚀 Powered by Innomatics AI</h3>
    <p style="margin-bottom: 0;">Advanced Resume Analysis • Instant Feedback • Data-Driven Insights</p>
    <p style="font-size: 0.9rem; margin-top: 1rem; opacity: 0.9;">Built with Streamlit & FastAPI • Powered by LLMs</p>
</div>
""", unsafe_allow_html=True)