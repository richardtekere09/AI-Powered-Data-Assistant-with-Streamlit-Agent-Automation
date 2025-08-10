"""
Code execution utilities for the AI Data Assistant.
Handles safe execution of generated code and analysis tasks.
"""
# import secrets
# print(secrets.token_hex(32))

import streamlit as st
import pandas as pd
from langchain_experimental.agents.agent_toolkits.pandas.base import (
    create_pandas_dataframe_agent,
)
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def safe_exec(code_string, local_vars=None):
    """
    Safely execute Python code string with restricted scope.

    Args:
        code_string (str): Python code to execute
        local_vars (dict): Local variables to make available to the code

    Returns:
        dict: Results of code execution
    """
    if local_vars is None:
        local_vars = {}

    # Restricted globals for safety
    safe_globals = {
        "__builtins__": {
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "print": print,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "max": max,
            "min": min,
            "sum": sum,
            "abs": abs,
            "round": round,
        },
        "pd": pd,
    }

    try:
        exec(code_string, safe_globals, local_vars)
        return local_vars
    except Exception as e:
        st.error(f"Code execution error: {str(e)}")
        return {}


def create_analysis_agent(df):
    """
    Create a pandas dataframe agent for AI analysis.

    Args:
        df (pd.DataFrame): The dataframe to analyze

    Returns:
        Agent: Configured analysis agent
    """
    if not GROQ_API_KEY:
        st.error("❌ GROQ_API_KEY not found. Please add it to your .env file.")
        st.info("🔑 Get your API key at: https://console.groq.com/")
        return None

    try:
        llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama-3.3-70b-versatile",
            temperature=0,
        )

        agent = create_pandas_dataframe_agent(
            llm,
            df,
            verbose=False,
            allow_dangerous_code=True,
        )

        return agent
    except Exception as e:
        st.error(f"Failed to create analysis agent: {str(e)}")
        return None


def run_analysis(agent, question):
    """
    Execute analysis using the AI agent.

    Args:
        agent: The analysis agent
        question (str): The analysis question

    Returns:
        str: Analysis response
    """
    try:
        response = agent.run(question)
        return response
    except Exception as e:
        st.error(f"Analysis execution failed: {str(e)}")
        return f"Error during analysis: {str(e)}"


def generate_suggestions(df):
    """
    Generate smart analysis suggestions based on dataframe structure.

    Args:
        df (pd.DataFrame): The dataframe to analyze

    Returns:
        list: List of suggested analysis questions
    """
    suggestions = []

    numeric_cols = df.select_dtypes(include=["number"]).columns
    categorical_cols = df.select_dtypes(include=["object"]).columns

    # Generate data-specific suggestions
    if len(numeric_cols) > 1:
        suggestions.append(
            f"Analyze correlations between {numeric_cols[0]} and {numeric_cols[1]}"
        )
        suggestions.append(
            f"Compare statistical distributions of {numeric_cols[0]} vs {numeric_cols[1]}"
        )

    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        suggestions.append(
            f"Examine {numeric_cols[0]} patterns across {categorical_cols[0]} categories"
        )

    if len(categorical_cols) > 1:
        suggestions.append(
            f"Cross-tabulate {categorical_cols[0]} and {categorical_cols[1]} relationships"
        )

    # Add general suggestions
    suggestions.extend(
        [
            "Generate comprehensive statistical summary report",
            "Identify outliers and anomalies in the dataset",
            "Create data quality assessment with recommendations",
            "Analyze missing data patterns and suggest handling strategies",
        ]
    )

    return suggestions
