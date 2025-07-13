"""
Streamlit "Project-to-Article" Generator

This is the main Streamlit application that provides the UI for uploading projects
and generating technical articles. It implements the UI requirements from FR-6.

Features:
- File upload widget (FR-1)
- Analysis depth selection (US-2)
- Article tone selection (US-3)
- LLM provider selection (US-4)
- Meta settings configuration (US-5)
- Article display with copy/download options (US-6)
"""

import streamlit as st
import os
from pathlib import Path
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our services
from services.parser import ProjectParser
from graph import ArticleGenerationWorkflow

# Page configuration
st.set_page_config(
    page_title="Project-to-Article Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .file-info {
        background-color: #e8f4fd;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.25rem 0;
        font-family: monospace;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if "project_analysis" not in st.session_state:
        st.session_state.project_analysis = None
    if "generated_article" not in st.session_state:
        st.session_state.generated_article = None
    if "processing_status" not in st.session_state:
        st.session_state.processing_status = "idle"


def render_header():
    """Render the main header."""
    st.markdown('<h1 class="main-header">📝 Project-to-Article Generator</h1>', unsafe_allow_html=True)
    st.markdown("""
    Transform your code projects into engaging technical articles with AI-powered analysis.
    Upload your project archive and get a well-structured article ready for publication.
    """)


def render_sidebar():
    """Render the sidebar with all configuration options (FR-6)."""
    st.sidebar.markdown('<h2 class="sidebar-header">⚙️ Configuration</h2>', unsafe_allow_html=True)
    
    # File Upload Section (US-1, FR-1)
    st.sidebar.markdown("### 📁 Project Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload your project archive",
        type=['zip', 'tar.gz', 'tgz'],
        help="Upload a ZIP or TAR.GZ file containing your project (max 20MB)"
    )
    
    if uploaded_file:
        st.sidebar.success(f"✅ Uploaded: {uploaded_file.name}")
        st.sidebar.info(f"Size: {uploaded_file.size / 1024 / 1024:.1f} MB")
    
    # Analysis Depth Selection (US-2, FR-2)
    st.sidebar.markdown("### 🔍 Analysis Depth")
    analysis_depth = st.sidebar.radio(
        "Choose analysis depth:",
        options=["Overview", "Detailed"],
        help="Overview: README & top-level files only. Detailed: Full source code analysis."
    )
    
    # Article Tone Selection (US-3, FR-4)
    st.sidebar.markdown("### 🎭 Article Tone")
    article_tone = st.sidebar.selectbox(
        "Select article tone:",
        options=["Explanatory", "Conversational", "Marketing"],
        help="Explanatory: Neutral/educational. Conversational: Casual/first-person. Marketing: Persuasive/product-focused."
    )
    
    # LLM Provider Selection (US-4, FR-5)
    st.sidebar.markdown("### 🤖 LLM Provider")
    llm_provider = st.sidebar.selectbox(
        "Choose LLM provider:",
        options=["OpenAI GPT-4", "Anthropic Claude", "Google Gemini"],
        help="Select your preferred AI model for article generation"
    )
    
    # API Key Management
    st.sidebar.markdown("### 🔑 API Configuration")
    
    # Show API key input based on selected provider
    api_key = None
    if llm_provider == "OpenAI GPT-4":
        api_key = st.sidebar.text_input(
            "OpenAI API Key:",
            type="password",
            help="Enter your OpenAI API key. Get one at https://platform.openai.com/api-keys",
            placeholder="sk-..."
        )
        if not api_key:
            st.sidebar.warning("⚠️ OpenAI API key required for GPT-4")
    elif llm_provider == "Anthropic Claude":
        api_key = st.sidebar.text_input(
            "Anthropic API Key:",
            type="password",
            help="Enter your Anthropic API key. Get one at https://console.anthropic.com/",
            placeholder="sk-ant-..."
        )
        if not api_key:
            st.sidebar.warning("⚠️ Anthropic API key required for Claude")
    elif llm_provider == "Google Gemini":
        api_key = st.sidebar.text_input(
            "Google API Key:",
            type="password",
            help="Enter your Google API key. Get one at https://makersuite.google.com/app/apikey",
            placeholder="AIza..."
        )
        if not api_key:
            st.sidebar.warning("⚠️ Google API key required for Gemini")
    
    # Meta Settings (US-5)
    st.sidebar.markdown("### 📝 Article Settings")
    article_title = st.sidebar.text_input(
        "Article Title (optional):",
        placeholder="e.g., Building a YouTube Summarizer with Python",
        help="Custom title for your article. Leave empty for auto-generation."
    )
    
    target_audience = st.sidebar.selectbox(
        "Target Audience:",
        options=["Beginner", "Intermediate", "Advanced"],
        help="Technical level of your target readers"
    )
    
    # Generate Button
    st.sidebar.markdown("---")
    
    # Show provider info
    if api_key:
        st.sidebar.success(f"✅ {llm_provider} configured")
    else:
        st.sidebar.info("ℹ️ Using mock LLM for testing")
    
    generate_button = st.sidebar.button(
        "🚀 Generate Article",
        type="primary",
        use_container_width=True,
        disabled=uploaded_file is None
    )
    
    return {
        "uploaded_file": uploaded_file,
        "analysis_depth": analysis_depth.lower(),
        "article_tone": article_tone,
        "llm_provider": llm_provider,
        "api_key": api_key,
        "article_title": article_title,
        "target_audience": target_audience,
        "generate_button": generate_button
    }


def render_main_pane():
    """Render the main content pane."""
    # Status and Progress Section
    if st.session_state.processing_status == "processing":
        with st.spinner("🔄 Analyzing project..."):
            st.info("Extracting and analyzing project files.")
    elif st.session_state.processing_status == "analyzing":
        with st.spinner("🤖 Generating article with AI..."):
            st.info("This may take up to 60 seconds for article generation.")
    
    # Project Analysis Results
    if st.session_state.project_analysis:
        st.markdown("### 📊 Project Analysis Results")
        
        analysis = st.session_state.project_analysis
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Files", analysis["total_files"])
        with col2:
            st.metric("Code Files", analysis["code_files"])
        with col3:
            st.metric("README Files", analysis["readme_files"])
        with col4:
            st.metric("Config Files", analysis["config_files"])
        
        # File Tree Display
        with st.expander("📁 View Project Structure", expanded=False):
            file_tree = analysis["file_tree"]
            
            # Show README files
            if file_tree["readme_files"]:
                st.markdown("**README Files:**")
                for readme in file_tree["readme_files"]:
                    st.markdown(f'<div class="file-info">📄 {readme["path"]}</div>', unsafe_allow_html=True)
            
            # Show config files
            if file_tree["config_files"]:
                st.markdown("**Configuration Files:**")
                for config in file_tree["config_files"]:
                    st.markdown(f'<div class="file-info">⚙️ {config["path"]}</div>', unsafe_allow_html=True)
            
            # Show code files (limited for overview)
            if file_tree["code_files"]:
                st.markdown("**Code Files:**")
                for code_file in file_tree["code_files"][:10]:  # Show first 10
                    st.markdown(f'<div class="file-info">💻 {code_file["path"]}</div>', unsafe_allow_html=True)
                
                if len(file_tree["code_files"]) > 10:
                    st.info(f"... and {len(file_tree['code_files']) - 10} more code files")
    
    # Generated Article Display (US-6)
    if st.session_state.generated_article:
        st.markdown("### 📄 Generated Article")
        
        # Article controls
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.success("Article copied to clipboard!")
                # Note: Actual clipboard functionality would require JavaScript
        with col2:
            st.download_button(
                label="💾 Download as Markdown",
                data=st.session_state.generated_article,
                file_name="generated_article.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        # Article content
        st.markdown("---")
        st.markdown(st.session_state.generated_article)
    
    # Welcome/Instructions
    elif st.session_state.processing_status == "idle":
        st.markdown("### 🎯 How to Use")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **1. Upload Your Project**
            - Zip your project folder
            - Upload the archive (max 20MB)
            - Supported: ZIP, TAR.GZ
            
            **2. Configure Settings**
            - Choose analysis depth
            - Select article tone
            - Pick LLM provider
            """)
        
        with col2:
            st.markdown("""
            **3. Generate Article**
            - Click "Generate Article"
            - Wait for processing (≤60s)
            - Review and download
            
            **4. Share Your Work**
            - Copy to clipboard
            - Download as Markdown
            - Publish to your blog
            """)
        
        st.markdown("---")
        st.markdown("### 📈 Success Metrics")
        st.markdown("""
        - **≥80%** of articles rated 4/5 or higher
        - **≤60 seconds** generation time for projects ≤5MB
        - **≥30%** returning user rate after 30 days
        """)


def process_project_upload(config: Dict):
    """Process the uploaded project file."""
    if not config["uploaded_file"] or not config["generate_button"]:
        return
    
    st.session_state.processing_status = "processing"
    
    try:
        # Initialize parser
        parser = ProjectParser(max_size_mb=20)
        
        # Process the project
        analysis_result = parser.process_project(
            uploaded_file=config["uploaded_file"],
            depth=config["analysis_depth"]
        )
        
        if analysis_result:
            st.session_state.project_analysis = analysis_result
            st.session_state.processing_status = "analyzing"
            
            # Initialize the article generation workflow
            workflow = ArticleGenerationWorkflow()
            
            # Create a serializable config for LangGraph (remove UploadedFile object)
            workflow_config = {
                "analysis_depth": config["analysis_depth"],
                "article_tone": config["article_tone"],
                "llm_provider": config["llm_provider"],
                "api_key": config.get("api_key"),
                "article_title": config["article_title"],
                "target_audience": config["target_audience"]
            }
            
            # Run the LangGraph workflow
            with st.spinner("🤖 Generating article with AI..."):
                workflow_result = workflow.run_workflow(analysis_result, workflow_config)
            
            if workflow_result["success"]:
                st.session_state.generated_article = workflow_result["article"]
                st.session_state.processing_status = "completed"
                st.success("✅ Article generated successfully!")
            else:
                st.error(f"❌ Article generation failed: {workflow_result.get('error', 'Unknown error')}")
                st.session_state.processing_status = "idle"
            
        else:
            st.error("❌ Failed to process project. Please check your upload and try again.")
            st.session_state.processing_status = "idle"
            
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.session_state.processing_status = "idle"


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar and get configuration
    config = render_sidebar()
    
    # Process project upload if requested
    process_project_upload(config)
    
    # Render main content
    render_main_pane()


if __name__ == "__main__":
    main() 