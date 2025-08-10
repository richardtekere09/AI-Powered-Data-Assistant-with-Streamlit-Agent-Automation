"""
AI Data Assistant - Main Application
A professional data analysis platform with AI-powered insights.
"""

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os

# Import our custom modules
from auth.login import get_authenticator
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


# Load CSS styles
def load_css():
    """Load CSS styles from external file."""
    try:
        with open(
            "/Users/richard/AI-Powered-Data-Assistant-with-Streamlit-Agent-Automation/static/ style.css"
        ) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback to inline CSS if file not found
        st.markdown(
            """
        <style>
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
        .stApp { background-color: var(--background); color: var(--primary-text); }
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
        }
        @keyframes slideInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
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
        </style>
        """,
            unsafe_allow_html=True,
        )


# Load styles
load_css()


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
    """Handle user authentication."""
    authenticator = get_authenticator()
    name, auth_status, username = authenticator.login(location="sidebar")

    if auth_status is False:
        st.error("Username or password is incorrect")
        st.stop()
    elif auth_status is None:
        show_login_welcome()
        st.stop()

    return name, username, authenticator


def show_login_welcome():
    """Display welcome screen for non-authenticated users."""
    st.markdown(
        """
    <div class="main-header">
        <h1>AI Data Assistant</h1>
        <p>Advanced data analysis and insights platform</p>
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


def display_welcome_message(name):
    """Display personalized welcome message."""
    st.markdown(
        f"""
    <div class="welcome-card">
        <h2>Welcome back, {name}! </h2>
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


def setup_sidebar():
    """Setup sidebar with file upload and tools."""
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


def display_analysis_tools():
    """Display analysis tools in sidebar when data is available."""
    if st.session_state.df is not None:
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
            .eda-button-container .stButton > button::before {
                content: '' !important;
                position: absolute !important;
                top: 0 !important;
                left: -100% !important;
                width: 100% !important;
                height: 100% !important;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent) !important;
                transition: left 0.5s ease !important;
            }
            .eda-button-container .stButton > button:hover::before {
                left: 100% !important;
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
    if uploaded_file:
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
    st.markdown(
        '<div class="section-header">📊 Dataset Overview</div>', unsafe_allow_html=True
    )

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


def handle_ai_analysis():
    """Handle AI-powered data analysis."""
    st.markdown(
        '<div class="section-header">🧠 Analysis Center</div>', unsafe_allow_html=True
    )

    # Smart suggestions
    st.markdown("**🎯 Smart Suggestions Based on Your Data:**")
    suggestions = generate_suggestions(st.session_state.df)

    cols = st.columns(2)
    for i, suggestion in enumerate(suggestions[:6]):
        with cols[i % 2]:
            if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                st.session_state.suggested_question = suggestion

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


def handle_eda_generation():
    """Handle EDA report generation."""
    if st.session_state.get("generate_eda", False):
        st.session_state.generate_eda = False  # Reset flag
        generate_eda_report(st.session_state.df)


def handle_quick_visualizations():
    """Handle quick visualization generation."""
    if st.session_state.get("quick_viz", False):
        st.session_state.quick_viz = False  # Reset flag
        create_stats_visualization(st.session_state.df)


def display_getting_started():
    """Display getting started section for users without data."""
    st.markdown(
        '<div class="section-header"> Getting Started</div>', unsafe_allow_html=True
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
    if st.session_state.chat_history:
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
    name, username, authenticator = handle_authentication()

    # Reset session if user changed
    reset_user_session(username)

    # Display welcome message
    display_welcome_message(name)

    # Add logout in sidebar
    authenticator.logout("Logout", location="sidebar")

    # Setup sidebar and get uploaded file
    uploaded_file = setup_sidebar()

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
