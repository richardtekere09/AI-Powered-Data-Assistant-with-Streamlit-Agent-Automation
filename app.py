import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
st.set_page_config(page_title="AI-Powered Data Assistant", layout="wide")

# App title
st.title(" AI-Powered Data Assistant")

# Session state
if "df" not in st.session_state:
    st.session_state.df = None

# Sidebar
st.sidebar.header("Upload Your Dataset")
uploaded_file = st.sidebar.file_uploader(
    "Choose a CSV or Excel file", type=["csv", "xlsx"]
)

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.session_state.df = df
        st.success(f"Uploaded `{uploaded_file.name}` successfully.")
    except Exception as e:
        st.error(f"Failed to read file: {e}")

# Display preview
if st.session_state.df is not None:
    st.subheader("📊 Data Preview")
    st.dataframe(st.session_state.df.head())

    # Placeholder for question input
    st.subheader("💬 Ask a Question About Your Data")
    user_question = st.text_input("e.g., What are the top 5 countries by revenue?")

    if user_question:
        st.info("🔧 AI response coming soon — let's integrate LangChain next!")

else:
    st.info("Please upload a CSV or Excel file to get started.")
