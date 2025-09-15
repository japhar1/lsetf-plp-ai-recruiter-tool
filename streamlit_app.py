import streamlit as st
import requests
import os
from pathlib import Path
import tempfile
import io

# Page configuration
st.set_page_config(
    page_title="LSETF AI Recruitment Tool",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
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
</style>
""", unsafe_allow_html=True)

# Configuration - USE YOUR ACTUAL BACKEND URL HERE
API_BASE_URL = "https://lsetf-backend.wonderfulbush-d6fad849.eastus.azurecontainerapps.io"

def check_api_health():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=10)
        return response.status_code == 200
    except:
        return False

def analyze_single_resume(uploaded_file):
    """Send a single resume to the API for analysis."""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(f"{API_BASE_URL}/api/analyze-candidate", files=files, timeout=30)
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
    
    # Score breakdown
    st.subheader("📋 Score Breakdown")
    for category, score in result['score_breakdown'].items():
        st.progress(score, text=f"{category.title()}: {score:.2f}")
    
    # Extracted data
    st.subheader("📋 Extracted Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Skills Found:**")
        for skill in result['extracted_data']['skills']:
            st.success(f"• {skill.title()}")
    
    with col2:
        st.write("**Education:**")
        for edu in result['extracted_data']['education'][:3]:
            st.info(f"• {edu[:100]}..." if len(edu) > 100 else f"• {edu}")

def main():
    """Main Streamlit application."""
    st.markdown('<h1 class="main-header">🎯 LSETF AI Recruitment Tool</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Candidate Selection for LSETF/PLP Programs")
    
    # Check API health
    if not check_api_health():
        st.error("🚨 Backend API server is not running. Please ensure the backend is deployed and accessible.")
        st.info(f"Backend URL: {API_BASE_URL}")
        st.info("Check: https://lsetf-backend.wonderfulbush-d6fad849.eastus.azurecontainerapps.io/api/health")
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
        st.info("Batch processing requires direct API access. Use the backend API endpoint for bulk processing.")
        st.code(f"POST {API_BASE_URL}/api/analyze-batch")
        st.write("Send multiple files to the API endpoint for batch analysis.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Built for LSETF/PLP Hackathon** 🚀  
    *AI-Driven Applicant Selection Tool*
    
    **Backend API**: {API_BASE_URL}
    """.format(API_BASE_URL=API_BASE_URL))

if __name__ == "__main__":
    main()