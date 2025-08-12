"""
AI Data Assistant - Main Application
A professional data analysis platform with AI-powered insights.
"""

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import sys

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our custom modules
from auth.login import get_hybrid_authenticator

# Remove show_forgot_password_form import - it's handled within the authenticator class
from utils.code_executor import (
    create_analysis_agent,
    run_analysis,
    generate_suggestions,
)
from utils.charts import create_stats_visualization
from utils.report_generator import generate_eda_report

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


def load_css():
    """Load CSS styles from external file."""
    try:
        with open("static/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback to inline CSS if file not found
        st.markdown(
            """
        <style>
        .main-header {
            background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 16px;
            margin: 2rem 0;
            text-align: center;
        }
        .welcome-card {
            background: white;
            border: 1px solid #E2E8F0;
            padding: 2rem;
            border-radius: 16px;
            margin: 2rem auto;
            max-width: 800px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #2563EB;
        }
        .feature-card {
            background: white;
            border: 1px solid #E2E8F0;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        .feature-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.error(f"Error loading CSS: {e}")


def fix_sidebar_toggle():
    """Implement a robust sidebar toggle fix."""
    st.markdown(
        """
    <style>
    /* Ensure Streamlit's sidebar toggle button is always visible and functional */
    .css-1d391kg, .css-1lcbmhc, .css-17lntkn, .css-1kyxreq {
        transition: all 0.3s ease !important;
    }
    
    /* Fix for sidebar collapse button */
    button[kind="header"] {
        background: transparent !important;
        border: none !important;
        color: #262730 !important;
        z-index: 999999 !important;
        position: relative !important;
        pointer-events: auto !important;
    }
    
    /* Ensure sidebar toggle is always clickable */
    .css-1cypcdb, .css-1lcbmhc .css-1cypcdb {
        pointer-events: auto !important;
        z-index: 999999 !important;
        background: rgba(255, 255, 255, 0.9) !important;
        border-radius: 4px !important;
        padding: 4px !important;
        margin: 4px !important;
    }
    
    /* Make sure the hamburger menu icon is visible */
    .css-1cypcdb svg {
        color: #262730 !important;
        width: 24px !important;
        height: 24px !important;
    }
    
    /* Fix sidebar when collapsed */
    .css-1d391kg[data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(-100%) !important;
    }
    
    /* Sidebar expanded state */
    .css-1d391kg[data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0) !important;
    }
    
    /* Ensure main content doesn't overlap sidebar toggle */
    .css-18e3th9 {
        padding-left: 1rem !important;
    }
    
    /* Force sidebar visibility controls */
    .css-1d391kg {
        min-width: 21rem !important;
        max-width: 21rem !important;
    }
    
    /* Collapsed sidebar should be completely hidden except for toggle */
    .css-1d391kg.css-1lcbmhc {
        min-width: 0 !important;
        width: 0 !important;
        margin-left: 0 !important;
    }
    
    /* Override any custom CSS that might interfere */
    [data-testid="stSidebar"] * {
        pointer-events: auto !important;
    }
    
    /* Specific fix for toggle button container */
    .css-1cypcdb {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 32px !important;
        height: 32px !important;
        cursor: pointer !important;
        position: fixed !important;
        top: 0.75rem !important;
        left: 0.75rem !important;
        z-index: 999999 !important;
        background: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid rgba(0, 0, 0, 0.1) !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
    }
    
    .css-1cypcdb:hover {
        background: rgba(255, 255, 255, 1) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Ensure nothing blocks the sidebar toggle */
    .css-1cypcdb, 
    .css-1cypcdb * {
        pointer-events: auto !important;
        user-select: none !important;
    }
    
    /* Force re-render of sidebar components */
    @keyframes sidebar-fix {
        0% { transform: translateX(0); }
        100% { transform: translateX(0); }
    }
    
    .css-1d391kg {
        animation: sidebar-fix 0.1s ease-in-out;
    }
    </style>
    
    <script>
    // Force sidebar functionality to work
    setTimeout(function() {
        // Find all potential sidebar toggle buttons
        const toggleButtons = document.querySelectorAll('[data-testid="collapsedControl"]');
        const sidebarToggle = document.querySelector('.css-1cypcdb');
        const hamburgerBtns = document.querySelectorAll('button[kind="header"]');
        
        // Add click listeners to ensure functionality
        [toggleButtons, [sidebarToggle], hamburgerBtns].flat().forEach(btn => {
            if (btn) {
                btn.style.pointerEvents = 'auto';
                btn.style.zIndex = '999999';
                btn.style.position = 'relative';
            }
        });
        
        // Ensure sidebar can be toggled
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', function() {
                const sidebar = document.querySelector('[data-testid="stSidebar"]');
                if (sidebar) {
                    const isExpanded = sidebar.getAttribute('aria-expanded') === 'true';
                    sidebar.setAttribute('aria-expanded', !isExpanded);
                }
            });
        }
    }, 1000);
    </script>
    """,
        unsafe_allow_html=True,
    )

# Load styles
load_css()
fix_sidebar_toggle()


def initialize_session_state():
    """Initialize all session state variables."""
    session_vars = {
        "df": None,
        "chat_history": [],
        "analysis_count": 0,
        "processed_files": set(),
        "current_user": None,
        "stats_rendered": False,
        "show_embedded": False,
        "show_summary": False,
        "generate_eda": False,
        "quick_viz": False,
        "authentication_status": None,
        "name": None,
        "username": None,
        "show_forgot_password": False,
    }

    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value


def reset_user_session(username):
    """Reset session when user changes."""
    if st.session_state.current_user != username:
        st.session_state.current_user = username
        st.session_state.df = None
        st.session_state.chat_history = []
        st.session_state.analysis_count = 0
        st.session_state.processed_files = set()
        st.session_state.stats_rendered = False
        st.session_state.show_embedded = False
        st.session_state.show_summary = False


def handle_authentication():
    """Handle user authentication using hybrid system."""
    try:
        # Get the hybrid authenticator (tries database first, falls back to config)
        authenticator = get_hybrid_authenticator()

        # Handle login
        if hasattr(authenticator, "login"):
            # Database authenticator
            name, auth_status, username = authenticator.login(location="sidebar")

            # Store in session state
            st.session_state.authentication_status = auth_status
            st.session_state.name = name
            st.session_state.username = username

            return name, auth_status, username, authenticator
        else:
            # Config file authenticator (streamlit-authenticator)
            name, auth_status, username = authenticator.login("Login", "sidebar")

            # Store in session state
            st.session_state.authentication_status = auth_status
            st.session_state.name = name
            st.session_state.username = username

            return name, auth_status, username, authenticator

    except Exception as e:
        st.error(f"Authentication error: {e}")
        st.stop()


# def show_login_welcome():
    """Display welcome screen for non-authenticated users."""
    st.markdown(
        """
    <div class="main-header" style="background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%); color: white; padding: 3rem 2rem; border-radius: 16px; margin: 2rem 0; text-align: center;">
        <h1 style="margin: 0; font-size: 3rem; font-weight: 800;">AI Data Assistant</h1>
        <p style="margin: 1rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">Advanced data analysis and insights platform</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    features = [
        {
            "title": "📊 Statistical Analysis",
            "desc": "Comprehensive statistical summaries, correlation analysis, hypothesis testing, and advanced analytics capabilities.",
        },
        {
            "title": "📈 Data Visualization",
            "desc": "Generate interactive charts, trend analyses, custom visualizations, and dynamic dashboards from your datasets.",
        },
        {
            "title": "🤖 AI Insights",
            "desc": "Natural language queries with intelligent pattern recognition, automated insight generation, and predictive analytics.",
        },
    ]

    for i, (col, feature) in enumerate(zip([col1, col2, col3], features)):
        with col:
            st.markdown(
                f"""
            <div class="feature-card">
                <h4>{feature["title"]}</h4>
                <p>{feature["desc"]}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Additional information
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem;">
            <h3> Secure Login Required</h3>
            <p style="color: var(--secondary-text); font-size: 1.1rem;">
                Please use the sidebar to log in to your account or create a new one to start analyzing your data.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
def show_login_welcome():
    """Display welcome screen for non-authenticated users using custom CSS styles."""

    # Premium header using your CSS classes
    st.markdown(
        """
    <div class="main-header">
        <h1>AI Data Assistant</h1>
        <p>Professional data analysis and insights platform powered by AI</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Professional section header
    st.markdown(
        """
    <div class="section-header">Platform Capabilities</div>
    """,
        unsafe_allow_html=True,
    )

    # Create three columns for features using your feature-card class
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
        <div class="feature-card">
            <div style="font-size: 3rem; text-align: center; margin-bottom: 1rem;">⚡</div>
            <h3>Fast Analysis</h3>
            <p>Get instant insights from your data with powerful statistical tools and real-time processing capabilities.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
        <div class="feature-card">
            <div style="font-size: 3rem; text-align: center; margin-bottom: 1rem;">🤖</div>
            <h3>AI Powered</h3>
            <p>Ask questions in natural language and get intelligent responses powered by advanced machine learning.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
        <div class="feature-card">
            <div style="font-size: 3rem; text-align: center; margin-bottom: 1rem;">📈</div>
            <h3>Beautiful Visualizations</h3>
            <p>Create stunning charts and interactive dashboards that bring your data stories to life.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Welcome card section
    st.markdown(
        """
    <div class="welcome-card">
        <h2>🚀 Get Started</h2>
        <p>Sign in using the sidebar or create a new account to begin your data analysis journey with AI-powered insights.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # # Registration button with enhanced styling
    # col1, col2, col3 = st.columns([1, 2, 1])
    # with col2:
    #     if st.button("🚀 Create New Account", use_container_width=True, type="primary"):
    #         st.markdown(
    #             """
    #         <div class="analysis-result">
    #             <h4>📝 Registration Options</h4>
    #             <p><strong>Quick Registration:</strong></p>
    #             <p>1. <a href="auth/registration.py" target="_blank" style="color: var(--primary-600); text-decoration: none; font-weight: 600;">Open Registration Page →</a></p>
    #             <p>2. Or run in terminal: <code>streamlit run auth/registration.py --server.port 8502</code></p>
    #         </div>
    #         """,
    #             unsafe_allow_html=True,
    #         )

    # Info section using your CSS info styling
    st.markdown(
        """
    <div class="stInfo" style="padding: 1.5rem; margin: 2rem 0; border-radius: var(--radius-md);">
        <strong>👈 Quick Start:</strong> Use the sidebar on the left to sign in with your existing credentials
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Professional section header for features
    st.markdown(
        """
    <div class="section-header">Platform Features</div>
    """,
        unsafe_allow_html=True,
    )

    # Feature columns with enhanced styling
    feature_col1, feature_col2 = st.columns(2)

    with feature_col1:
        st.markdown(
            """
        <div class="feature-card">
            <h4>📊 Data Analysis Tools</h4>
            <p>• Statistical summaries and comprehensive analysis<br>
            • Correlation and regression analysis<br>
            • Missing value detection and handling<br>
            • Advanced data quality assessment</p>
        </div>
        
        <div class="feature-card">
            <h4>📈 Advanced Visualizations</h4>
            <p>• Interactive charts and dynamic plots<br>
            • Custom dashboards and reports<br>
            • Trend analysis and forecasting<br>
            • Professional export capabilities</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    with feature_col2:
        st.markdown(
            """
        <div class="feature-card">
            <h4>🤖 AI-Powered Features</h4>
            <p>• Natural language data queries<br>
            • Automated insights generation<br>
            • Intelligent pattern recognition<br>
            • Predictive analytics and modeling</p>
        </div>
        
        <div class="feature-card">
            <h4>🔒 Security & Privacy</h4>
            <p>• Enterprise-grade authentication<br>
            • End-to-end data encryption<br>
            • Privacy protection and compliance<br>
            • Granular access controls</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Statistics showcase using your stats-container
    st.markdown(
        """
    <div class="section-header">Platform Statistics</div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-number">10,000+</div>
            <div class="stat-label">Datasets Analyzed</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">50+</div>
            <div class="stat-label">Analysis Types</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">99.9%</div>
            <div class="stat-label">Accuracy Rate</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Availability</div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # # Final call-to-action with premium styling
    # col1, col2, col3 = st.columns([1, 2, 1])
    # with col2:
    #     st.markdown(
    #         """
    #     <div class="upload-area" style="text-align: center;">
    #         <h4>🎯 Ready to Transform Your Data?</h4>
    #         <p>Join thousands of data professionals who trust AI Data Assistant for their analytical needs.</p>
    #         <p><strong>Sign in</strong> using the sidebar to access your personalized dashboard and start analyzing your data with AI-powered tools.</p>
    #     </div>
    #     """,
    #         unsafe_allow_html=True,
    #     )

    # Professional footer section
    st.markdown(
        """
    <div class="analysis-result" style="text-align: center; margin-top: 3rem;">
        <h4>🌟 Why Choose AI Data Assistant?</h4>
        <p>Experience the perfect blend of powerful analytics, intuitive design, and cutting-edge AI technology. 
        Our platform transforms complex data analysis into simple, actionable insights that drive informed decision-making.</p>
        <p style="margin-top: 1.5rem; font-weight: 600; color: var(--accent-teal);">
            Start your data journey today! ✨
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

def display_welcome_message(name):
    """Display personalized welcome message."""
    st.markdown(
        f"""
    <div class="welcome-card">
        <h2>Welcome back, {name}! 🚀</h2>
        <p>Your intelligent data analysis workspace is ready. Upload a dataset to unlock powerful insights and discover hidden patterns in your data.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def display_stats_cards():
    """Display dynamic statistics cards."""
    if st.session_state.df is not None:
        completeness = (
            1 - st.session_state.df.isnull().sum().sum() / st.session_state.df.size
        ) * 100
        numeric_cols = len(
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


def setup_sidebar(authenticator):
    """Setup sidebar with authentication and file upload."""
    with st.sidebar:
        # Show logout button if authenticated
        if st.session_state.authentication_status:
            st.markdown(f"**Logged in as:** {st.session_state.name}")

            # Logout button
            if hasattr(authenticator, "logout"):
                # Database authenticator
                authenticator.logout("🚪 Logout", location="sidebar")
            else:
                # Config file authenticator
                authenticator.logout("🚪 Logout", "sidebar")

            st.markdown("---")

        # File upload section (only show if authenticated)
        if st.session_state.authentication_status:
            st.markdown(
                '<div style="color: white; font-weight: 700; font-size: 1.25rem; margin: 1rem 0;">📁 Data Upload</div>',
                unsafe_allow_html=True,
            )

            uploaded_file = st.file_uploader(
                "Choose file",
                type=["csv", "xlsx"],
                help="Supported formats: CSV, Excel (max 200MB)",
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
                
                **Automated EDA**
                - One-click comprehensive analysis
                - Professional HTML reports
                - Correlation heatmaps & distributions
                """)

            return uploaded_file
        else:
            return None


def display_analysis_tools():
    """Display analysis tools in sidebar when data is available."""
    if st.session_state.df is not None and st.session_state.authentication_status:
        with st.sidebar:
            st.markdown("---")
            st.markdown("**⚡ Quick Analysis Tools**")

            # Custom CSS for EDA buttons
            st.markdown(
                """
            <style>
            .eda-button-container .stButton > button {
                background: linear-gradient(135deg, #2563EB, #0D9488) !important;
                color: white !important;
                border: none !important;
                border-radius: 15px !important;
                padding: 1.2rem 1.5rem !important;
                font-weight: 600 !important;
                font-size: 0.95rem !important;
                width: 100% !important;
                height: 80px !important;
                box-shadow: 0 6px 20px rgba(37, 99, 235, 0.25) !important;
                transition: all 0.3s ease !important;
                position: relative !important;
                overflow: hidden !important;
                white-space: nowrap !important;
                text-overflow: ellipsis !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            .eda-button-container .stButton > button:hover {
                transform: translateY(-2px) scale(1.02) !important;
                box-shadow: 0 8px 25px rgba(37, 99, 235, 0.35) !important;
                background: linear-gradient(135deg, #1D4ED8, #0F766E) !important;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )

            st.markdown('<div class="eda-button-container">', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "Generate EDA Report",
                    use_container_width=True,
                    help="Create comprehensive automated analysis",
                    key="eda_report_btn",
                ):
                    st.session_state.generate_eda = True

            with col2:
                if st.button(
                    "Quick Visualizations",
                    use_container_width=True,
                    help="Generate beautiful instant charts",
                    key="quick_viz_btn",
                ):
                    st.session_state.quick_viz = True

            st.markdown("</div>", unsafe_allow_html=True)


def handle_file_upload(uploaded_file):
    """Handle file upload and processing."""
    if uploaded_file and st.session_state.authentication_status:
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"

        if file_id not in st.session_state.get("processed_files", set()):
            try:
                with st.spinner("Processing your dataset..."):
                    if "processed_files" not in st.session_state:
                        st.session_state.processed_files = set()
                    st.session_state.processed_files.add(file_id)

                    if uploaded_file.name.endswith(".csv"):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)

                    st.session_state.df = df
                    st.session_state.stats_rendered = False
                    st.success(f"✅ Successfully loaded {uploaded_file.name}")

            except Exception as e:
                st.error(f"❌ Error loading file: {str(e)}")
                if (
                    "processed_files" in st.session_state
                    and file_id in st.session_state.processed_files
                ):
                    st.session_state.processed_files.remove(file_id)


def display_dataset_overview():
    """Display dataset overview and details."""
    if st.session_state.df is not None:
        st.markdown(
            '<div class="section-header">📊 Dataset Overview</div>',
            unsafe_allow_html=True,
        )

        with st.expander("📋 Data Preview", expanded=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.dataframe(
                    st.session_state.df.head(10), use_container_width=True, height=350
                )

            with col2:
                memory_usage = (
                    st.session_state.df.memory_usage(deep=True).sum() / 1024**2
                )
                text_cols = len(
                    st.session_state.df.select_dtypes(include=["object"]).columns
                )
                numeric_cols = len(
                    st.session_state.df.select_dtypes(include=["number"]).columns
                )

                st.markdown(
                    f"""
                <div class="feature-card">
                    <h4>Dataset Summary</h4>
                    <p><strong>Dimensions:</strong> {st.session_state.df.shape[0]:,} × {st.session_state.df.shape[1]}</p>
                    <p><strong>Memory usage:</strong> {memory_usage:.1f} MB</p>
                    <p><strong>Numeric columns:</strong> {numeric_cols}</p>
                    <p><strong>Text columns:</strong> {text_cols}</p>
                    <p><strong>Missing values:</strong> {st.session_state.df.isnull().sum().sum():,}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

        # Data types
        with st.expander("🏷️ Data Types"):
            st.dataframe(
                st.session_state.df.dtypes.to_frame("Data Type"),
                use_container_width=True,
            )

        # Missing values
        with st.expander("❓ Missing Values Analysis"):
            missing_data = st.session_state.df.isnull().sum()
            if missing_data.sum() > 0:
                st.dataframe(
                    missing_data[missing_data > 0].to_frame("Missing Count"),
                    use_container_width=True,
                )
            else:
                st.markdown("✅ No missing values found!")

        # Basic statistics
        with st.expander("📈 Basic Statistics"):
            st.dataframe(st.session_state.df.describe(), use_container_width=True)

        # Column information
        with st.expander("🔍 Column Details"):
            col_info = pd.DataFrame(
                {
                    "Column": st.session_state.df.columns,
                    "Data Type": st.session_state.df.dtypes.astype(str),
                    "Non-Null Count": st.session_state.df.count(),
                    "Null Count": st.session_state.df.isnull().sum(),
                    "Null Percentage": (
                        st.session_state.df.isnull().sum()
                        / len(st.session_state.df)
                        * 100
                    ).round(2),
                }
            )
            st.dataframe(col_info, use_container_width=True)
    else:
        st.info("📁 Please upload a dataset to view its overview and statistics.")


def handle_ai_analysis():
    """Handle AI-powered data analysis."""
    st.markdown(
        '<div class="section-header">🧠 Analysis Center</div>', unsafe_allow_html=True
    )

    # Smart suggestions
    st.markdown("**🎯 Smart Suggestions Based on Your Data:**")
    try:
        suggestions = generate_suggestions(st.session_state.df)

        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions[:6]):
            with cols[i % 2]:
                if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                    st.session_state.suggested_question = suggestion
    except Exception as e:
        st.error(f"Error generating suggestions: {e}")

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

                status.info("Initializing AI analysis engine...")
                progress.progress(25)

                # Create analysis agent
                agent = create_analysis_agent(st.session_state.df)
                if agent is None:
                    progress.empty()
                    status.empty()
                    st.error("Failed to create analysis agent")
                    return

                status.info("🧠 Creating data analysis agent...")
                progress.progress(50)

                status.info("⚡ Processing analysis request...")
                progress.progress(75)

                # Run analysis
                response = run_analysis(agent, user_question)
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
                st.error(f"Analysis error: {e}")


def handle_eda_generation():
    """Handle EDA report generation."""
    if st.session_state.get("generate_eda", False):
        st.session_state.generate_eda = False  # Reset flag
        try:
            generate_eda_report(st.session_state.df)
        except Exception as e:
            st.error(f"EDA generation error: {e}")


def handle_quick_visualizations():
    """Handle quick visualization generation."""
    if st.session_state.get("quick_viz", False):
        st.session_state.quick_viz = False  # Reset flag
        try:
            create_stats_visualization(st.session_state.df)
        except Exception as e:
            st.error(f"Visualization error: {e}")


def display_getting_started():
    """Display getting started section for users without data."""
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

    capabilities = [
        {
            "title": "📊 Statistical Analysis",
            "desc": "Comprehensive statistical summaries, correlation analysis, hypothesis testing, and advanced analytics capabilities.",
        },
        {
            "title": "📈 Data Visualization",
            "desc": "Generate interactive charts, trend analyses, custom visualizations, and dynamic dashboards from your datasets.",
        },
        {
            "title": "🤖 AI Insights",
            "desc": "Natural language queries with intelligent pattern recognition, automated insight generation, and predictive analytics.",
        },
    ]

    for col, capability in zip([col1, col2, col3], capabilities):
        with col:
            st.markdown(
                f"""
            <div class="feature-card">
                <h4>{capability["title"]}</h4>
                <p>{capability["desc"]}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )


def display_analysis_history():
    """Display interactive analysis history."""
    if st.session_state.chat_history and st.session_state.authentication_status:
        st.markdown(
            '<div class="section-header">📚 Analysis History</div>',
            unsafe_allow_html=True,
        )

        recent_history = st.session_state.chat_history[-6:]  # Last 3 Q&A pairs

        for i in range(0, len(recent_history), 2):
            if i + 1 < len(recent_history):
                question = recent_history[i][1]
                answer = recent_history[i + 1][1]

                with st.container():
                    st.markdown('<div class="history-item">', unsafe_allow_html=True)
                    with st.expander(
                        f"💭 {question[:70]}..."
                        if len(question) > 70
                        else f"💭 {question}"
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
            if st.button("Clear History", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        with col2:
            if st.button("Export Session", use_container_width=True):
                st.info("Session export functionality available upon request.")


def display_footer():
    """Display application footer."""
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align: center; padding: 1.5rem; color: var(--secondary-text);">
        <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">🤖 AI Data Assistant</p>
        <p style="margin: 0; font-size: 0.875rem;">Powered by Groq AI • Built by Richard with Streamlit • Professional Data Analytics Platform</p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()

    # Handle authentication
    name, auth_status, username, authenticator = handle_authentication()

    # If authentication failed
    if auth_status is False:
        st.error("❌ Username or password is incorrect")
        with st.sidebar:
            if st.button("🔄 Try Again"):
                st.rerun()
        show_login_welcome()
        return

    # If not authenticated, show welcome screen
    if auth_status is None:
        show_login_welcome()
        return

    # User is authenticated - proceed with main app
    if auth_status:
        # Reset session if user changed
        reset_user_session(username)

        # Display welcome message
        display_welcome_message(name)

        # Setup sidebar and get uploaded file
        uploaded_file = setup_sidebar(authenticator)

        # Handle file upload
        handle_file_upload(uploaded_file)

        # Display analysis tools in sidebar (after file is processed)
        display_analysis_tools()

        # Display stats cards
        display_stats_cards()

        # Main content based on whether data is loaded
        if st.session_state.df is not None:
            # Display dataset overview
            display_dataset_overview()

            # Handle AI analysis
            handle_ai_analysis()

            # Handle EDA report generation
            handle_eda_generation()

            # Handle quick visualizations
            handle_quick_visualizations()
        else:
            # Display getting started section
            display_getting_started()

        # Display analysis history
        display_analysis_history()

        # Display footer
        display_footer()


if __name__ == "__main__":
    main()
