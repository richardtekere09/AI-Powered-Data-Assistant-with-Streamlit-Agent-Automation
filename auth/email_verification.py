"""
Email verification page for AI Data Assistant
"""

import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config.database import get_db_session
from services.user_service import UserService
from services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Email Verification - AI Data Assistant", page_icon="📧", layout="wide"
)


def load_css():
    """Load CSS styles."""
    css_path = Path(__file__).parent.parent / "static" / "style.css"

    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback CSS
        st.markdown(
            """
        <style>
        .success-card {
            background: white;
            border: 1px solid #E2E8F0;
            padding: 2rem;
            border-radius: 16px;
            margin: 2rem auto;
            max-width: 600px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #16A34A;
        }
        .error-card {
            background: white;
            border: 1px solid #E2E8F0;
            padding: 2rem;
            border-radius: 16px;
            margin: 2rem auto;
            max-width: 600px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #DC2626;
        }
        .feature-card {
            background: white;
            border: 1px solid #E2E8F0;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
            unsafe_allow_html=True,
        )


def verify_email_token(token: str) -> tuple[bool, str, str]:
    """Verify email token and return result."""
    try:
        with get_db_session() as db:
            user_service = UserService(db)
            email_service = EmailService()

            # Verify email
            success, message = user_service.verify_email(token)

            if success:
                # Get user details for welcome email
                user = user_service.get_user_by_verification_token(token)
                if user:
                    # Send welcome email
                    try:
                        email_service.send_welcome_email(
                            to_email=user.email, username=user.username
                        )
                    except Exception as e:
                        logger.warning(f"Welcome email failed: {e}")

                    return True, message, user.username
                else:
                    return True, message, "User"
            else:
                return False, message, ""

    except Exception as e:
        logger.error(f"Error during email verification: {e}")
        return False, "An error occurred during verification", ""


def show_verification_success(username: str):
    """Show verification success message."""
    st.markdown(
        f"""
        <div class="success-card">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎉</div>
            <h1>Email Verified Successfully!</h1>
            <p>Welcome to AI Data Assistant, <strong>{username}</strong>!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.success(
        "✅ Your email has been verified successfully! You can now log in to your account."
    )
    st.balloons()

    # Next steps
    with st.expander("🚀 What's Next?", expanded=True):
        st.markdown("""
        **1. Sign In to Your Account**
        - Use your username and password to log in
        - Access all the powerful features of AI Data Assistant
        
        **2. Upload Your First Dataset**
        - Start with CSV or Excel files
        - Get instant insights and visualizations
        
        **3. Explore AI-Powered Analysis**
        - Ask questions about your data in plain English
        - Generate comprehensive reports and charts
        - Discover hidden patterns and correlations
        """)

    # Login button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 Sign In Now", type="primary", use_container_width=True):
            st.switch_page("app.py")

    # Features preview
    st.markdown("---")
    st.markdown("### ✨ Ready to Transform Your Data Analysis?")

    col1, col2, col3 = st.columns(3)

    features = [
        {
            "icon": "📊",
            "title": "Statistical Analysis",
            "description": "Comprehensive data summaries, correlation analysis, and hypothesis testing.",
        },
        {
            "icon": "📈",
            "title": "Interactive Charts",
            "description": "Create beautiful visualizations with natural language commands.",
        },
        {
            "icon": "🤖",
            "title": "AI-Powered Insights",
            "description": "Get intelligent recommendations and automated pattern recognition.",
        },
    ]

    for col, feature in zip([col1, col2, col3], features):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div style="font-size: 2rem; text-align: center; margin-bottom: 1rem;">{feature["icon"]}</div>
                    <h3 style="text-align: center; margin: 0 0 1rem 0;">{feature["title"]}</h3>
                    <p style="text-align: center; margin: 0;">{feature["description"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def show_verification_error(message: str):
    """Show verification error message."""
    st.markdown(
        """
        <div class="error-card">
            <div style="font-size: 3rem; margin-bottom: 1rem;">❌</div>
            <h1>Verification Failed</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.error(f"❌ {message}")

    # Help options
    with st.expander("🔧 Need Help?", expanded=True):
        st.markdown("""
        **Common Issues and Solutions:**
        
        **1. Token Expired**
        - Verification links expire after 24 hours
        - Request a new verification email
        
        **2. Invalid Token**
        - Make sure you clicked the complete link from your email
        - Check that the URL wasn't truncated
        
        **3. Already Verified**
        - If you've already verified your email, you can log in directly
        
        **4. Still Having Issues?**
        - Contact support with your email address
        - We'll help you get verified quickly
        """)

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Try Again", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("🔐 Back to Login", use_container_width=True):
            st.switch_page("app.py")


def main():
    """Main email verification page function."""
    # Load CSS
    load_css()

    # Get token from URL parameters
    query_params = st.experimental_get_query_params()
    token = query_params.get("token", [None])[0]

    if not token:
        st.error(
            "❌ No verification token provided. Please check your email for the complete verification link."
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔐 Back to Login", use_container_width=True):
                st.switch_page("app.py")
        st.stop()

    # Show loading state
    with st.spinner("🔍 Verifying your email..."):
        success, message, username = verify_email_token(token)

    if success:
        show_verification_success(username)
    else:
        show_verification_error(message)


if __name__ == "__main__":
    main()
