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
# ---- Auth ----
authenticator = get_authenticator()
name, auth_status, username = authenticator.login(location="sidebar")

if auth_status is False:
    st.error("Username/password is incorrect")
    st.stop()
elif auth_status is None:
    st.info("Please enter your username and password.")
    st.stop()

# Optional UI: logout button + welcome label
col1, col2 = st.columns([1, 3])
with col1:
    authenticator.logout(location='sidebar')
with col2:
    st.caption(f"Welcome, **{name}**")

# ---- Main App ----

# Minimal CSS for better performance
st.markdown(
    """
<style>
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #ecf0f1;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "analysis_count" not in st.session_state:
    st.session_state.analysis_count = 0

# Header - simplified
st.title("AI Data Assistant")
st.caption("Advanced data analysis powered by Groq AI")

# Sidebar - simplified
with st.sidebar:
    st.header("Data Upload")

    uploaded_file = st.file_uploader("Select CSV or Excel file", type=["csv", "xlsx"])

    # Dataset statistics - only show if data exists
    if st.session_state.df is not None:
        st.header("Dataset Overview")
        st.metric("Rows", f"{len(st.session_state.df):,}")
        st.metric("Columns", len(st.session_state.df.columns))
        st.metric("Analyses", st.session_state.analysis_count)

    # Analysis capabilities
    with st.expander("Analysis Capabilities"):
        st.markdown("""
        **Statistical Analysis**
        - Descriptive statistics
        - Correlation analysis
        - Distribution analysis
        
        **Data Visualization**
        - Charts and graphs
        - Trend analysis
        - Pattern identification
        
        **Data Quality**
        - Missing value analysis
        - Outlier detection
        - Data profiling
        """)

# File upload handling - simplified and faster
if uploaded_file and uploaded_file not in st.session_state.get(
    "processed_files", set()
):
    try:
        # Add file to processed set to avoid reprocessing
        if "processed_files" not in st.session_state:
            st.session_state.processed_files = set()
        st.session_state.processed_files.add(uploaded_file)

        # Fast file reading
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.session_state.df = df
        st.success(f"✅ Loaded {uploaded_file.name}")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# Main content - conditional layout based on data availability
if st.session_state.df is not None:
    # Data is loaded - show full layout
    col1, col2 = st.columns([3, 1])

    with col1:
        # Dataset summary
        st.markdown(
            '<div class="section-header">Dataset Summary</div>', unsafe_allow_html=True
        )

        # Metrics row
        metrics_cols = st.columns(4)
        with metrics_cols[0]:
            st.metric("Total Rows", f"{len(st.session_state.df):,}")
        with metrics_cols[1]:
            st.metric("Columns", len(st.session_state.df.columns))
        with metrics_cols[2]:
            numeric_cols = len(
                st.session_state.df.select_dtypes(include=["number"]).columns
            )
            st.metric("Numeric Columns", numeric_cols)
        with metrics_cols[3]:
            missing_data = st.session_state.df.isnull().sum().sum()
            st.metric("Missing Values", f"{missing_data:,}")

        # Data preview section
        st.markdown(
            '<div class="section-header">Data Preview</div>', unsafe_allow_html=True
        )

        preview_df = st.session_state.df.head(10)
        st.dataframe(preview_df, use_container_width=True, height=300)

        # Column information
        with st.expander("Column Information"):
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

        # Analysis interface
        st.markdown(
            '<div class="section-header">Data Analysis</div>', unsafe_allow_html=True
        )

        # Quick analysis options
        st.markdown("**Quick Analysis Options:**")
        suggestion_cols = st.columns(2)

        suggestions = [
            "Provide a statistical summary of the dataset",
            "Identify correlations between variables",
            "Analyze missing data patterns",
            "Generate descriptive statistics",
        ]

        for i, suggestion in enumerate(suggestions):
            with suggestion_cols[i % 2]:
                if st.button(suggestion, key=f"suggest_{i}"):
                    st.session_state.suggested_question = suggestion

        # Analysis input
        user_question = st.text_area(
            "Enter your analysis query:",
            placeholder="Ask questions about your data, request visualizations, or perform statistical analysis...",
            height=80,
        )

        # Handle suggested questions
        if "suggested_question" in st.session_state:
            user_question = st.session_state.suggested_question
            del st.session_state.suggested_question

        # Process analysis query - Updated Groq model
        if st.button("Analyze", type="primary") and user_question:
            with st.spinner("Processing analysis..."):
                try:
                    # Check API key first
                    if not GROQ_API_KEY:
                        st.error("❌ Please add GROQ_API_KEY to your .env file!")
                        st.info("Get free API key at: https://console.groq.com/")
                        st.stop()

                    # Progress indicator
                    progress_placeholder = st.empty()
                    progress_placeholder.info("Initializing AI agent...")

                    # Initialize Groq LLM with current model
                    llm = ChatGroq(
                        api_key=GROQ_API_KEY,
                        model="llama-3.3-70b-versatile",  # Updated current model
                        temperature=0,
                    )

                    # Create agent with Groq
                    memory = get_memory()
                    agent = create_pandas_dataframe_agent(
                        llm,
                        st.session_state.df,
                        verbose=False,
                        allow_dangerous_code=True,
                    )

                    progress_placeholder.info("Processing your query...")
                    response = agent.run(user_question)
                    progress_placeholder.empty()

                    # Update session state
                    st.session_state.chat_history.append(("User", user_question))
                    st.session_state.chat_history.append(("Assistant", response))
                    st.session_state.analysis_count += 1

                    # Display result
                    st.markdown("**Analysis Result:**")
                    st.markdown(
                        f"""
                    <div class="assistant-message chat-message">
                        {response}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                except Exception as e:
                    st.error(f"Analysis error: {str(e)}")
                    st.info(
                        "💡 **Troubleshooting:**\n- Check GROQ_API_KEY in .env file\n- Try alternative model: `llama-3.1-8b-instant`"
                    )

    with col2:
        # Analysis tools sidebar
        st.markdown(
            '<div class="section-header">Analysis Tools</div>', unsafe_allow_html=True
        )

        # Quick visualization
        if st.button("Generate Quick Visualization", use_container_width=True):
            numeric_cols = st.session_state.df.select_dtypes(include=["number"]).columns
            if len(numeric_cols) > 0:
                fig = px.histogram(
                    st.session_state.df,
                    x=numeric_cols[0],
                    title=f"Distribution: {numeric_cols[0]}",
                    color_discrete_sequence=["#3498db"],
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    title_font_size=14,
                    font=dict(size=12),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No numeric columns available for visualization.")

        # Data quality check
        if st.button("Data Quality Assessment", use_container_width=True):
            missing_data = st.session_state.df.isnull().sum().sum()
            total_cells = st.session_state.df.size
            completeness = (1 - missing_data / total_cells) * 100

            duplicates = st.session_state.df.duplicated().sum()

            quality_score = (
                "Excellent"
                if completeness > 95 and duplicates == 0
                else "Good"
                if completeness > 80
                else "Needs Attention"
            )

            st.markdown(
                f"""
            <div class="info-box">
                <h4>Data Quality Report</h4>
                <p><strong>Completeness:</strong> {completeness:.1f}%</p>
                <p><strong>Missing Values:</strong> {missing_data:,}</p>
                <p><strong>Duplicate Rows:</strong> {duplicates:,}</p>
                <p><strong>Overall Quality:</strong> {quality_score}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # Export options
        st.markdown("**Export Options**")
        if st.button("Download Sample Analysis", use_container_width=True):
            st.info("Export functionality can be implemented based on requirements.")

else:
    # No data loaded - show welcome screen without empty columns
    # Welcome header
    st.markdown("### Welcome to AI Data Assistant")
    st.markdown("Upload your dataset to begin advanced data analysis with Groq AI.")

    st.markdown("---")

    # Feature overview using columns
    st.markdown("#### What you can do:")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **📊 Data Analysis**
        
        Statistical summaries, correlation analysis, and pattern detection
        """)

    with col2:
        st.markdown("""
        **📈 Visualization** 
        
        Interactive charts, graphs, and data visualization
        """)

    with col3:
        st.markdown("""
        **🔍 Insights**
        
        AI-powered insights and recommendations
        """)

    st.markdown("---")
    st.markdown("*Supported formats: CSV, Excel | Maximum file size: 200MB*")

    # Getting started section
    st.markdown("#### Getting Started")
    st.info("""
    **Steps to begin:**
    1. Upload a CSV or Excel file using the sidebar
    2. Review your dataset preview and statistics
    3. Use quick analysis options or ask custom questions
    4. Generate visualizations and insights
    """)

    # Sample questions
    st.markdown("#### Example Analysis Questions")
    st.markdown("""
    - *"Show me the distribution of values in column X"*
    - *"What are the correlations between numerical variables?"*
    - *"Identify any outliers in the dataset"*
    - *"Create a summary report of key statistics"*
    - *"Which columns have the most missing data?"*
    """)

# Analysis history
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown(
        '<div class="section-header">Analysis History</div>', unsafe_allow_html=True
    )

    # Show recent analyses (last 4 pairs)
    recent_history = st.session_state.chat_history[-8:]  # Last 8 items = 4 Q&A pairs

    for i, (speaker, message) in enumerate(recent_history):
        if speaker == "User":
            st.markdown(
                f"""
            <div class="user-message chat-message">
                <strong>Query:</strong> {message}
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
            <div class="assistant-message chat-message">
                <strong>Analysis:</strong> {message}
            </div>
            """,
                unsafe_allow_html=True,
            )

    # History management
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("Clear History"):
            st.session_state.chat_history = []
            st.rerun()
    with col2:
        if st.button("Export History"):
            st.info("History export functionality available.")

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #95a5a6; font-size: 0.85rem;">AI Data Assistant | Powered by Groq AI 🚀</p>',
    unsafe_allow_html=True,
)
