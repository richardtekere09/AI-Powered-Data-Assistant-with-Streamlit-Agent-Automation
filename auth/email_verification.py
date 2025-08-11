"""
Email verification page for AI Data Assistant
"""

import streamlit as st
from services.user_service import UserService
from services.email_service import EmailService
from config.database import get_db_session
import logging

logger = logging.getLogger(__name__)


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
                    email_service.send_welcome_email(
                        to_email=user.email, username=user.username
                    )
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
        """
        <div class="status-container">
            <div class="status-icon-large">🎉</div>
            <h1 class="status-title-success">Email Verified Successfully!</h1>
            <p class="status-description">
                Welcome to AI Data Assistant, <strong>{username}</strong>!
            </p>
        </div>
        """.format(username=username),
        unsafe_allow_html=True,
    )

    # Success message
    st.success(
        "✅ Your email has been verified successfully! You can now log in to your account."
    )

    # Next steps
    with st.expander("🚀 What's Next?", expanded=True):
        st.markdown("""
        **1. Log In to Your Account**
        - Use your username and password to sign in
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
        if st.button("Sign In Now", type="primary", use_container_width=True):
            st.switch_page("app.py")

    # Features preview
    st.markdown("---")
    st.markdown(
        """
        <div class="centered-container">
            <h2>✨ Ready to Transform Your Data Analysis?</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
            "title": "AI Insights",
            "description": "Get intelligent recommendations and automated pattern recognition.",
        },
    ]

    for col, feature in zip([col1, col2, col3], features):
        with col:
            st.markdown(
                f"""
                <div class="feature-display">
                    <div class="feature-icon">{feature["icon"]}</div>
                    <h3 class="feature-title">{feature["title"]}</h3>
                    <p class="feature-description">{feature["description"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def show_verification_error(message: str):
    """Show verification error message."""
    st.markdown(
        """
        <div class="status-container">
            <div class="status-icon-large">❌</div>
            <h1 class="status-title-error">Verification Failed</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Error message
    st.error(f"❌ {message}")

    # Help options
    with st.expander("🔧 Need Help?", expanded=True):
        st.markdown("""
        **Common Issues and Solutions:**
        
        **1. Token Expired**
        - Verification links expire after 24 hours
        - Request a new verification email from your account
        
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
        if st.button("Try Again", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("Contact Support", use_container_width=True):
            st.info(
                "Please email support@aidataassistant.com with your email address and username."
            )

    # Alternative options
    st.markdown("---")
    st.markdown(
        """
        <div class="text-center">
            <p>Don't have an account yet? 
                <a href="auth/registration.py" target="_self" class="link-primary">
                    Create one here
                </a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_loading():
    """Show loading state during verification."""
    st.markdown(
        """
        <div class="status-container">
            <div class="status-icon-large">⏳</div>
            <h1>Verifying Your Email...</h1>
            <p>Please wait while we verify your email address.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.spinner("Verifying email..."):
        st.info("Processing verification token...")


def main():
    """Main email verification page function."""
    st.set_page_config(
        page_title="Email Verification - AI Data Assistant",
        page_icon="📧",
        layout="wide",
    )

    # CSS styles are loaded from external file

    # Get token from URL parameters
    token = st.experimental_get_query_params().get("token", [None])[0]

    if not token:
        st.error(
            "❌ No verification token provided. Please check your email for the complete verification link."
        )
        st.stop()

    # Show loading state
    show_loading()

    # Verify the token
    success, message, username = verify_email_token(token)

    # Clear loading state
    st.empty()

    if success:
        show_verification_success(username)
    else:
        show_verification_error(message)


if __name__ == "__main__":
    main()
