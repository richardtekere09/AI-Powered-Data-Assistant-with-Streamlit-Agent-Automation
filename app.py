import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
from langchain_experimental.agents.agent_toolkits.pandas.base import (
    create_pandas_dataframe_agent,
)
from langchain_groq import ChatGroq
from memory.chat_memory import get_memory
from utils.code_executor import safe_exec
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
from auth.login import get_authenticator

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Page config
st.set_page_config(
    page_title="AI Data Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional CSS with dynamic features
st.markdown(
    """
<style>
    /* Color palette */
    :root {
        --background: #F8FAFC;
        --primary-text: #1E293B;
        --secondary-text: #64748B;
        --primary-accent: #2563EB;
        --secondary-accent: #0D9488;
        --success: #16A34A;
        --warning: #F59E0B;
        --error: #DC2626;
        --sidebar-bg: #1E293B;
        --sidebar-text: #F8FAFC;
        --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --hover-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }

    /* Base styling */
    .stApp {
        background-color: var(--background);
        color: var(--primary-text);
    }

    /* Dynamic background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: 
            radial-gradient(circle at 20% 80%, rgba(37, 99, 235, 0.03) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(13, 148, 136, 0.03) 0%, transparent 50%);
        pointer-events: none;
        z-index: -1;
    }

    /* Hide default streamlit elements but keep sidebar toggle */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, var(--primary-accent), var(--secondary-accent));
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: var(--card-shadow);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        pointer-events: none;
    }
    
    .main-header h1 {
        font-size: 2.75rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: -0.025em;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.25rem;
        margin: 0.75rem 0 0 0;
        opacity: 0.95;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }

    /* Animated welcome card for authenticated users */
    .welcome-card {
        background: linear-gradient(135deg, white, #F8FAFC);
        border: 1px solid #E2E8F0;
        padding: 2rem;
        border-radius: 16px;
        margin: 2rem auto;
        max-width: 800px;
        text-align: center;
        box-shadow: var(--card-shadow);
        border-left: 4px solid var(--primary-accent);
        animation: slideInUp 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .welcome-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(37, 99, 235, 0.1), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .welcome-card h2 {
        color: var(--primary-text);
        margin: 0 0 0.75rem 0;
        font-size: 1.75rem;
        font-weight: 600;
        position: relative;
        z-index: 1;
    }
    
    .welcome-card p {
        color: var(--secondary-text);
        margin: 0;
        font-size: 1.125rem;
        position: relative;
        z-index: 1;
    }

    /* Section headers */
    .section-header {
        font-size: 1.375rem;
        font-weight: 600;
        color: var(--primary-text);
        margin: 2.5rem 0 1.5rem 0;
        padding: 1rem 0;
        border-bottom: 2px solid #E2E8F0;
        position: relative;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 60px;
        height: 2px;
        background: var(--primary-accent);
    }

    /* Cards with hover effects */
    .feature-card {
        background: white;
        border: 1px solid #E2E8F0;
        padding: 1.75rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: var(--card-shadow);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--hover-shadow);
        border-color: var(--primary-accent);
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-accent), var(--secondary-accent));
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover::before {
        transform: scaleX(1);
    }
    
    .feature-card h3, .feature-card h4 {
        color: var(--primary-text);
        margin-top: 0;
    }
    
    .feature-card p {
        color: var(--secondary-text);
        line-height: 1.6;
    }

    /* Stats container with animations */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1.25rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: white;
        border: 1px solid #E2E8F0;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: var(--card-shadow);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stat-card:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: var(--hover-shadow);
        border-color: var(--primary-accent);
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary-accent);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover::before {
        transform: scaleX(1);
    }
    
    .stat-number {
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--primary-accent);
        margin: 0 0 0.5rem 0;
        line-height: 1.2;
        transition: color 0.3s ease;
    }
    
    .stat-card:hover .stat-number {
        color: var(--secondary-accent);
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: var(--secondary-text);
        font-weight: 500;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Enhanced upload area with drag-and-drop styling */
    .upload-area {
        background: linear-gradient(135deg, #F1F5F9, #F8FAFC);
        border: 2px dashed #CBD5E1;
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        margin: 1.5rem 0;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .upload-area:hover {
        border-color: var(--primary-accent);
        background: linear-gradient(135deg, #EFF6FF, #F0F9FF);
        transform: translateY(-2px);
        box-shadow: var(--hover-shadow);
    }
    
    .upload-area::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent 30%, rgba(37, 99, 235, 0.05) 50%, transparent 70%);
        transform: translateX(-100%);
        transition: transform 0.6s ease;
    }
    
    .upload-area:hover::before {
        transform: translateX(100%);
    }
    
    .upload-area h4 {
        color: var(--primary-text);
        margin: 0 0 0.75rem 0;
        font-size: 1.25rem;
        font-weight: 600;
    }
    
    .upload-area p {
        color: var(--secondary-text);
        margin: 0.5rem 0;
        font-size: 1rem;
    }

    /* Enhanced buttons with hover effects */
    .stButton > button {
        background: var(--primary-accent);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.925rem;
        box-shadow: var(--card-shadow);
        transition: all 0.3s ease;
        border: 1px solid transparent;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .stButton > button:hover {
        background: #1D4ED8;
        transform: translateY(-2px) scale(1.02);
        box-shadow: var(--hover-shadow);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }

    /* Smart suggestions styling */
    .suggestion-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .suggestion-button {
        background: white !important;
        color: var(--primary-text) !important;
        border: 1px solid #E2E8F0 !important;
        text-align: left !important;
        padding: 1rem 1.25rem !important;
        height: auto !important;
        min-height: 60px !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .suggestion-button:hover {
        border-color: var(--primary-accent) !important;
        background: #EFF6FF !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--hover-shadow) !important;
    }

    /* Sidebar styling - FIXED */
    .css-1d391kg {
        background: var(--sidebar-bg) !important;
    }
    
    .css-1d391kg .stMarkdown {
        color: var(--sidebar-text) !important;
    }
    
    .css-1d391kg .stMarkdown h1, 
    .css-1d391kg .stMarkdown h2, 
    .css-1d391kg .stMarkdown h3, 
    .css-1d391kg .stMarkdown h4 {
        color: var(--sidebar-text) !important;
        font-weight: 700 !important;
    }
    
    .css-1d391kg .stMarkdown .section-header {
        color: white !important;
        font-weight: 700 !important;
        border-bottom-color: rgba(255,255,255,0.3) !important;
    }

    /* Login form styling - FIXED */
    .css-1d391kg .stForm {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 1px solid #E2E8F0 !important;
        padding: 1.75rem !important;
        border-radius: 16px !important;
        box-shadow: var(--card-shadow) !important;
    }
    
    .css-1d391kg .stTextInput > div > div > input {
        background: white !important;
        border: 2px solid #D1D5DB !important;
        color: var(--primary-text) !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
        font-size: 1rem !important;
    }
    
    .css-1d391kg .stTextInput > div > div > input:focus {
        border-color: var(--primary-accent) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        outline: none !important;
    }
    
    .css-1d391kg .stTextInput label {
        color: var(--primary-text) !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
    }
    
    .css-1d391kg .stButton > button {
        background: var(--primary-accent) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        width: 100% !important;
    }

    /* Success/Error messages */
    .stSuccess {
        background: #F0FDF4 !important;
        border: 1px solid #BBF7D0 !important;
        color: var(--success) !important;
        border-radius: 12px !important;
    }
    
    .stError {
        background: #FEF2F2 !important;
        border: 1px solid #FECACA !important;
        color: var(--error) !important;
        border-radius: 12px !important;
    }
    
    .stInfo {
        background: #EFF6FF !important;
        border: 1px solid #BFDBFE !important;
        color: var(--primary-accent) !important;
        border-radius: 12px !important;
    }

    /* Form styling */
    .stForm {
        background: white;
        border: 1px solid #E2E8F0;
        padding: 1.75rem;
        border-radius: 16px;
        box-shadow: var(--card-shadow);
    }

    /* Analysis result with animation */
    .analysis-result {
        background: white;
        border: 1px solid #E2E8F0;
        border-left: 4px solid var(--secondary-accent);
        padding: 1.75rem;
        margin: 1.5rem 0;
        border-radius: 16px;
        box-shadow: var(--card-shadow);
        animation: slideInUp 0.5s ease-out;
    }
    
    .analysis-result h4 {
        color: var(--primary-text);
        margin-top: 0;
    }

    /* Interactive history */
    .history-item {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        margin: 1rem 0;
        transition: all 0.3s ease;
        overflow: hidden;
    }
    
    .history-item:hover {
        box-shadow: var(--hover-shadow);
        border-color: var(--primary-accent);
    }
    
    .history-item .streamlit-expanderHeader {
        background: #F8FAFC !important;
        border-bottom: 1px solid #E2E8F0 !important;
        transition: background 0.3s ease !important;
    }
    
    .history-item:hover .streamlit-expanderHeader {
        background: #EFF6FF !important;
    }

    /* Progress bar */
    .stProgress .st-bo {
        background: var(--primary-accent) !important;
    }

    /* Text area styling */
    .stTextArea textarea {
        border: 1px solid #D1D5DB !important;
        border-radius: 12px !important;
        background: white !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary-accent) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }

    /* Loading animation */
    .loading-pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---- Authentication ----
authenticator = get_authenticator()
name, auth_status, username = authenticator.login(location="sidebar")

if auth_status is False:
    st.error("Username or password is incorrect")
    st.stop()
elif auth_status is None:
    # Login welcome screen
    st.markdown(
        """
    <div class="main-header">
        <h1>AI Data Assistant</h1>
        <p>Advanced data analysis and insights platform</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
        <div class="feature-card">
            <h3 style="text-align: center;">Secure Access Required</h3>
            <p style="text-align: center; margin-bottom: 1.5rem;">
                Please authenticate using the sidebar to access your data analysis workspace.
            </p>
            <div style="text-align: center;">
                <h4>Platform Features:</h4>
                <p>AI-powered insights • Interactive visualizations • Pattern discovery • Statistical analysis</p>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    st.stop()

# ---- Main Application ----

# Personalized welcome message (centered)
st.markdown(
    f"""
<div class="welcome-card">
    <h2>Welcome back, {name}! 🎯</h2>
    <p>Your intelligent data analysis workspace is ready. Upload a dataset to unlock powerful insights and discover hidden patterns in your data.</p>
</div>
""",
    unsafe_allow_html=True,
)

# Logout in sidebar
authenticator.logout("Logout", location="sidebar")

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "analysis_count" not in st.session_state:
    st.session_state.analysis_count = 0
if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "stats_rendered" not in st.session_state:
    st.session_state.stats_rendered = False

# Check if user changed (logout/login cycle) and reset session
if st.session_state.current_user != username:
    st.session_state.current_user = username
    st.session_state.df = None
    st.session_state.chat_history = []
    st.session_state.analysis_count = 0
    st.session_state.processed_files = set()
    st.session_state.stats_rendered = False

# Dynamic stats display
if st.session_state.df is not None:
    completeness = (
        1 - st.session_state.df.isnull().sum().sum() / st.session_state.df.size
    ) * 100
    numeric_cols = len(st.session_state.df.select_dtypes(include=["number"]).columns)

    st.markdown(
        f"""
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number">{len(st.session_state.df):,}</div>
            <div class="stat-label">Total Rows</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(st.session_state.df.columns)}</div>
            <div class="stat-label">Columns</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{numeric_cols}</div>
            <div class="stat-label">Numeric Fields</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{completeness:.1f}%</div>
            <div class="stat-label">Data Complete</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{st.session_state.analysis_count}</div>
            <div class="stat-label">Analyses Run</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

# Enhanced sidebar
with st.sidebar:
    st.markdown(
        '<div class="section-header" style="color: white !important; font-weight: 700 !important; border-bottom-color: rgba(255,255,255,0.4) !important; font-size: 1.25rem !important;">📁 Data Upload</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose file",
        type=["csv", "xlsx"],
        help="Supported formats: CSV, Excel (max 200MB)",
    )

    if uploaded_file is None:
        st.markdown(
            """
        <div class="upload-area">
            <h4>📊 Ready for your data</h4>
            <p>Drop your CSV or Excel file here</p>
            <p>Maximum file size: 200MB</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Analysis capabilities
    with st.expander("🔍 Analysis Capabilities"):
        st.markdown("""
        **Statistical Analysis**
        - Descriptive statistics and summaries
        - Correlation and regression analysis
        - Distribution analysis and testing
        
        **Data Visualization**
        - Interactive charts and graphs
        - Trend analysis and forecasting
        - Pattern identification
        
        **Data Quality Assessment**
        - Missing value analysis
        - Outlier detection and treatment
        - Data profiling and validation
        """)

# Enhanced file upload handling
if uploaded_file:
    # Create a unique identifier for the file
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"

    if file_id not in st.session_state.get("processed_files", set()):
        try:
            with st.spinner("🔄 Processing your dataset..."):
                if "processed_files" not in st.session_state:
                    st.session_state.processed_files = set()
                st.session_state.processed_files.add(file_id)

                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)

                st.session_state.df = df
                st.session_state.stats_rendered = (
                    False  # Reset flag when new data is loaded
                )
                st.success(f"✅ Successfully loaded {uploaded_file.name}")

        except Exception as e:
            st.error(f"❌ Error loading file: {str(e)}")
            # Remove from processed files if there was an error
            if (
                "processed_files" in st.session_state
                and file_id in st.session_state.processed_files
            ):
                st.session_state.processed_files.remove(file_id)

# Stats cards - Show only once when data is available
if st.session_state.df is not None and not st.session_state.stats_rendered:
    completeness = (
        1 - st.session_state.df.isnull().sum().sum() / st.session_state.df.size
    ) * 100
    numeric_cols_count = len(
        st.session_state.df.select_dtypes(include=["number"]).columns
    )

    st.markdown(
        f"""
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number">{len(st.session_state.df):,}</div>
            <div class="stat-label">Total Rows</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(st.session_state.df.columns)}</div>
            <div class="stat-label">Columns</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{numeric_cols_count}</div>
            <div class="stat-label">Numeric Fields</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{completeness:.1f}%</div>
            <div class="stat-label">Data Complete</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{st.session_state.analysis_count}</div>
            <div class="stat-label">Analyses Run</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.session_state.stats_rendered = True  # Mark as rendered

# Main content
if st.session_state.df is not None:
    # Dataset overview
    st.markdown(
        '<div class="section-header">📊 Dataset Overview</div>', unsafe_allow_html=True
    )

    # Data preview
    with st.expander("📋 Data Preview", expanded=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.dataframe(
                st.session_state.df.head(10), use_container_width=True, height=350
            )

        with col2:
            memory_usage = st.session_state.df.memory_usage(deep=True).sum() / 1024**2
            text_cols = len(
                st.session_state.df.select_dtypes(include=["object"]).columns
            )
            numeric_cols = len(
                st.session_state.df.select_dtypes(include=["number"]).columns
            )

            st.markdown(
                f"""
            <div class="feature-card">
                <h4>📈 Dataset Summary</h4>
                <p><strong>Dimensions:</strong> {st.session_state.df.shape[0]:,} × {st.session_state.df.shape[1]}</p>
                <p><strong>Memory usage:</strong> {memory_usage:.1f} MB</p>
                <p><strong>Numeric columns:</strong> {numeric_cols}</p>
                <p><strong>Text columns:</strong> {text_cols}</p>
                <p><strong>Missing values:</strong> {st.session_state.df.isnull().sum().sum():,}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Column information
    with st.expander("🔍 Column Details"):
        col_info = pd.DataFrame(
            {
                "Column": st.session_state.df.columns,
                "Data Type": st.session_state.df.dtypes.astype(str),
                "Non-Null Count": st.session_state.df.count(),
                "Null Count": st.session_state.df.isnull().sum(),
                "Null Percentage": (
                    st.session_state.df.isnull().sum() / len(st.session_state.df) * 100
                ).round(2),
            }
        )
        st.dataframe(col_info, use_container_width=True)

    # Analysis interface
    st.markdown(
        '<div class="section-header">🧠 Analysis Center</div>', unsafe_allow_html=True
    )

    # Smart suggestions based on data types
    st.markdown("**🎯 Smart Suggestions Based on Your Data:**")

    numeric_cols = st.session_state.df.select_dtypes(include=["number"]).columns
    categorical_cols = st.session_state.df.select_dtypes(include=["object"]).columns

    suggestions = []

    # Generate data-specific suggestions
    if len(numeric_cols) > 1:
        suggestions.append(
            f"📊 Analyze correlations between {numeric_cols[0]} and {numeric_cols[1]}"
        )
        suggestions.append(
            f"📈 Compare statistical distributions of {numeric_cols[0]} vs {numeric_cols[1] if len(numeric_cols) > 1 else 'other variables'}"
        )

    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        suggestions.append(
            f"🔍 Examine {numeric_cols[0] if len(numeric_cols) > 0 else 'values'} patterns across {categorical_cols[0]} categories"
        )

    if len(categorical_cols) > 1:
        suggestions.append(
            f"📋 Cross-tabulate {categorical_cols[0]} and {categorical_cols[1]} relationships"
        )

    # Add general suggestions
    suggestions.extend(
        [
            "🎯 Generate comprehensive statistical summary report",
            "🔎 Identify outliers and anomalies in the dataset",
            "📊 Create data quality assessment with recommendations",
            "📈 Analyze missing data patterns and suggest handling strategies",
        ]
    )

    # Display suggestions in a grid
    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions[:6]):  # Show top 6 suggestions
        with cols[i % 2]:
            if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                st.session_state.suggested_question = (
                    suggestion.replace("📊 ", "")
                    .replace("📈 ", "")
                    .replace("🔍 ", "")
                    .replace("🎯 ", "")
                    .replace("🔎 ", "")
                    .replace("📋 ", "")
                )

    # Analysis input
    user_question = st.text_area(
        "💬 Ask anything about your data",
        placeholder="What insights would you like to discover? Ask me to create visualizations, find patterns, calculate statistics, or explore relationships in your data...",
        height=100,
        help="Try specific questions like: 'Show me the distribution of sales by region' or 'Find correlations in my dataset'",
    )

    # Handle suggested questions
    if "suggested_question" in st.session_state:
        user_question = st.session_state.suggested_question
        del st.session_state.suggested_question

    # Analysis execution
    if (
        st.button("🚀 Run Analysis", type="primary", use_container_width=True)
        and user_question
    ):
        if not GROQ_API_KEY:
            st.error("❌ GROQ_API_KEY not found. Please add it to your .env file.")
            st.info("🔑 Get your API key at: https://console.groq.com/")
            st.stop()

        with st.spinner("🤖 AI is analyzing your data..."):
            try:
                # Progress tracking
                progress = st.progress(0)
                status = st.empty()

                status.info("🔄 Initializing AI analysis engine...")
                progress.progress(25)

                llm = ChatGroq(
                    api_key=GROQ_API_KEY,
                    model="llama-3.3-70b-versatile",
                    temperature=0,
                )

                status.info("🧠 Creating data analysis agent...")
                progress.progress(50)

                agent = create_pandas_dataframe_agent(
                    llm,
                    st.session_state.df,
                    verbose=False,
                    allow_dangerous_code=True,
                )

                status.info("⚡ Processing analysis request...")
                progress.progress(75)

                response = agent.run(user_question)
                progress.progress(100)

                status.empty()
                progress.empty()

                # Update session state
                st.session_state.chat_history.append(("User", user_question))
                st.session_state.chat_history.append(("Assistant", response))
                st.session_state.analysis_count += 1

                # Display results
                st.markdown(
                    '<div class="section-header">🎯 Analysis Results</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"""
                <div class="analysis-result">
                    <h4>💡 Analysis Output</h4>
                    {response}
                </div>
                """,
                    unsafe_allow_html=True,
                )

            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.info(
                    "💡 Please verify your API key and try a simpler query if the error persists."
                )

else:
    # No data loaded - enhanced welcome
    st.markdown(
        '<div class="section-header">🚀 Getting Started</div>', unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
        <div class="feature-card">
            <h3 style="text-align: center;">📊 Upload Dataset to Begin</h3>
            <p style="text-align: center;">
                Use the sidebar to upload your CSV or Excel file and start analyzing your data with AI-powered insights and interactive visualizations.
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Platform capabilities
    st.markdown(
        '<div class="section-header">✨ Platform Capabilities</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class="feature-card">
            <h4>📊 Statistical Analysis</h4>
            <p>Comprehensive statistical summaries, correlation analysis, hypothesis testing, and advanced analytics capabilities.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="feature-card">
            <h4>📈 Data Visualization</h4>
            <p>Generate interactive charts, trend analyses, custom visualizations, and dynamic dashboards from your datasets.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="feature-card">
            <h4>🤖 AI Insights</h4>
            <p>Natural language queries with intelligent pattern recognition, automated insight generation, and predictive analytics.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

# Interactive analysis history
if st.session_state.chat_history:
    st.markdown(
        '<div class="section-header">📚 Analysis History</div>', unsafe_allow_html=True
    )

    recent_history = st.session_state.chat_history[-6:]  # Last 3 Q&A pairs

    for i in range(0, len(recent_history), 2):
        if i + 1 < len(recent_history):
            question = recent_history[i][1]
            answer = recent_history[i + 1][1]

            with st.container():
                st.markdown('<div class="history-item">', unsafe_allow_html=True)
                with st.expander(
                    f"💭 {question[:70]}..." if len(question) > 70 else f"💭 {question}"
                ):
                    st.markdown(
                        f"""
                    <div class="analysis-result">
                        <strong>🔍 Query:</strong> {question}<br><br>
                        <strong>🤖 Analysis:</strong><br>{answer}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    with col2:
        if st.button("📤 Export Session", use_container_width=True):
            st.info("📋 Session export functionality available upon request.")

# Footer
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; padding: 1.5rem; color: var(--secondary-text);">
    <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">🤖 AI Data Assistant</p>
    <p style="margin: 0; font-size: 0.875rem;">Powered by Groq AI • Built with Streamlit • Professional Data Analytics Platform</p>
</div>
""",
    unsafe_allow_html=True,
)
