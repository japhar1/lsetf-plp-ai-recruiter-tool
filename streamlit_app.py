#!/usr/bin/env python3
"""
Streamlit UI for LSETF AI Recruitment Tool
Run with: streamlit run streamlit_app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import requests
import tempfile
import base64
import io

# Page configuration
st.set_page_config(
    page_title="LSETF AI Recruitment Tool",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #E8F5E8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4CAF50;
    }
    .candidate-card {
        background-color: #F5F5F5;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        border: 1px solid #E0E0E0;
    }
    .metric-card {
        background-color: #FFFFFF;
        padding: 1rem;
        margin: 0.5rem;
        border-radius: 0.5rem;
        border: 1px solid #E0E0E0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = 'https://lsetf-backend.wonderfulbush-d6fad849.eastus.azurecontainerapps.io'

def check_api_health():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def analyze_single_resume(uploaded_file):
    """Send a single resume to the API for analysis."""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(f"{API_BASE_URL}/api/analyze-candidate", files=files)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def analyze_batch_resumes(uploaded_files):
    """Send multiple resumes to the API for batch analysis."""
    try:
        files = []
        for uploaded_file in uploaded_files:
            files.append(("files", (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)))
        
        response = requests.post(f"{API_BASE_URL}/api/analyze-batch", files=files)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def display_candidate_results(result):
    """Display individual candidate results."""
    if not result.get("success"):
        st.error(f"Error: {result.get('error', 'Unknown error')}")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Score", f"{result['score']:.2f}/1.0")
    
    with col2:
        st.metric("Skills Score", f"{result['score_breakdown']['skills']:.2f}")
    
    with col3:
        st.metric("Education Score", f"{result['score_breakdown']['education']:.2f}")
    
    # Score breakdown chart
    breakdown_df = pd.DataFrame({
        'Category': list(result['score_breakdown'].keys()),
        'Score': list(result['score_breakdown'].values())
    })
    
    fig = px.bar(breakdown_df, x='Category', y='Score', title="Score Breakdown",
                 color='Category', color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(yaxis_range=[0, 1])
    st.plotly_chart(fig, use_container_width=True)
    
    # Extracted data
    st.subheader("📋 Extracted Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Skills Found:**")
        for skill in result['extracted_data']['skills']:
            st.success(f"• {skill.title()}")
    
    with col2:
        st.write("**Education:**")
        for edu in result['extracted_data']['education'][:3]:  # Show first 3 snippets
            st.info(f"• {edu[:100]}..." if len(edu) > 100 else f"• {edu}")

def display_batch_results(results):
    """Display batch processing results."""
    if not results.get("success"):
        st.error(f"Error: {results.get('error', 'Unknown error')}")
        return
    
    st.success(f"✅ Successfully analyzed {results['total_candidates']} candidates")
    
    # Create dataframe for visualization
    df_data = []
    for candidate in results['results']:
        df_data.append({
            'Rank': candidate['rank'],
            'Candidate ID': candidate['candidate_id'],
            'Score': candidate['score'],
            'Skills Score': candidate['score_breakdown']['skills'],
            'Education Score': candidate['score_breakdown']['education'],
            'Experience Score': candidate['score_breakdown']['experience'],
            'Skills Count': len(candidate['skills']),
            'Top Skills': ', '.join(candidate['skills'][:3])  # Show top 3 skills
        })
    
    df = pd.DataFrame(df_data)
    
    # Display ranking table
    st.subheader("🏆 Candidate Ranking")
    st.dataframe(df[['Rank', 'Candidate ID', 'Score', 'Skills Count', 'Top Skills']], 
                use_container_width=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.bar(df, x='Candidate ID', y='Score', title="Candidate Scores",
                     color='Score', color_continuous_scale='Viridis')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.scatter(df, x='Skills Score', y='Education Score', 
                         size='Score', color='Rank',
                         title="Skills vs Education Scores",
                         hover_data=['Candidate ID'])
        st.plotly_chart(fig2, use_container_width=True)
    
    # Show individual candidate details in expanders
    st.subheader("📊 Detailed Candidate Analysis")
    for candidate in results['results']:
        with st.expander(f"#{candidate['rank']} - {candidate['candidate_id']} (Score: {candidate['score']:.2f})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Score Breakdown:**")
                for category, score in candidate['score_breakdown'].items():
                    st.write(f"- {category.title()}: {score:.2f}")
            
            with col2:
                st.write("**Skills:**")
                for skill in candidate['skills']:
                    st.success(f"• {skill}")

def main():
    """Main Streamlit application."""
    # Header
    st.markdown('<h1 class="main-header">🎯 LSETF AI Recruitment Tool</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Candidate Selection for LSETF/PLP Programs")
    
    # Check API health
    if not check_api_health():
        st.error("🚨 API server is not running. Please start the FastAPI server first:")
        st.code("python -m app.main")
        return
    
    st.success("✅ Connected to AI analysis engine")
    
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    analysis_mode = st.sidebar.radio("Analysis Mode", ["Single Candidate", "Batch Processing"])
    
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Supported Formats:**
    - PDF (.pdf)
    - Word Documents (.docx, .doc)
    
    **How it works:**
    1. Upload resume(s)
    2. AI extracts skills, education, experience
    3. Candidates are scored and ranked
    4. Get actionable insights for selection
    """)
    
    # Main content
    if analysis_mode == "Single Candidate":
        st.header("👤 Single Candidate Analysis")
        
        uploaded_file = st.file_uploader(
            "Upload a resume (PDF or Word)",
            type=["pdf", "docx", "doc"],
            help="Upload a single candidate resume for analysis"
        )
        
        if uploaded_file is not None:
            st.success(f"📄 File uploaded: {uploaded_file.name}")
            
            if st.button("🚀 Analyze Candidate", type="primary"):
                with st.spinner("🤖 AI is analyzing the resume..."):
                    result = analyze_single_resume(uploaded_file)
                
                if result.get("success"):
                    st.markdown('<div class="success-box">✅ Analysis Complete!</div>', unsafe_allow_html=True)
                    display_candidate_results(result)
                else:
                    st.error("Analysis failed. Please try again.")
    
    else:  # Batch Processing
        st.header("👥 Batch Candidate Analysis")
        
        uploaded_files = st.file_uploader(
            "Upload multiple resumes",
            type=["pdf", "docx", "doc"],
            accept_multiple_files=True,
            help="Upload multiple resumes for batch analysis and ranking"
        )
        
        if uploaded_files:
            st.success(f"📄 {len(uploaded_files)} files uploaded")
            
            if st.button("🚀 Analyze Batch", type="primary"):
                with st.spinner("🤖 AI is analyzing resumes and ranking candidates..."):
                    results = analyze_batch_resumes(uploaded_files)
                
                if results.get("success"):
                    st.markdown('<div class="success-box">✅ Batch Analysis Complete!</div>', unsafe_allow_html=True)
                    display_batch_results(results)
                else:
                    st.error("Batch analysis failed. Please try again.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Built for LSETF/PLP Hackathon** 🚀  
    *AI-Driven Applicant Selection Tool*
    """)

if __name__ == "__main__":
    main()