"""
User registration page for AI Data Assistant
"""

import streamlit as st
import re
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
    page_title="Create Account - AI Data Assistant", page_icon="🚀", layout="wide"
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
        .main-header {
            background: linear-gradient(135deg, #2563EB 0%, #0D9488 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 16px;
            margin: 2rem 0;
            text-align: center;
        }
        .feature-card {
            background: white;
            border: 1px solid #E2E8F0;
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .welcome-card {
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
        </style>
        """,
            unsafe_allow_html=True,
        )


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, "Password is strong"


def validate_username(username: str) -> tuple[bool, str]:
    """Validate username format."""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 20:
        return False, "Username must be less than 20 characters"

    if not re.match(r"^[a-zA-Z0-9_-]+$", username):
        return (
            False,
            "Username can only contain letters, numbers, underscores, and hyphens",
        )

    return True, "Username is valid"


def show_registration_success(username: str, email: str):
    """Show registration success message."""
    st.markdown(
        f"""
        <div class="welcome-card">
            <h2>🎉 Account Created Successfully!</h2>
            <p>Welcome to AI Data Assistant, <strong>{username}</strong>!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.success(
        f"✅ Account created! Please check your email ({email}) for a verification link."
    )
    #st.balloons()

    # Next steps
    with st.expander("📧 What's Next?", expanded=True):
        st.markdown(f"""
        **1. Check Your Email ({email})**
        - Look for an email from richardtekere02@gmail.com
        - Check your spam folder if you don't see it
        
        **2. Click the Verification Link**
        - Click the verification link in the email
        - This will activate your account
        
        **3. Start Analyzing Data**
        - Once verified, you can log in and start uploading datasets
        - Get AI-powered insights and create visualizations
        """)

    # Login button with proper navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
        <div style="text-align: center; margin: 2rem 0;">
            <a href="/" style="display: inline-block; background: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600;">
                🔐 Go to Login Page
            </a>
        </div>
        """,
            unsafe_allow_html=True,
        )


def show_registration_form():
    """Display the user registration form."""
    st.markdown(
        """
        <div class="main-header">
            <h1>🚀 Create Your Account</h1>
            <p>Join AI Data Assistant and unlock the power of intelligent data analysis</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Back to login link at top
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
        <div style="text-align: center; margin-bottom: 2rem;">
            <a href="/" style="color: #2563EB; text-decoration: none; font-weight: 600;">
                ← Back to Login
            </a>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Registration form
    with st.form("registration_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input(
                "Username *",
                placeholder="Choose a username",
                help="3-20 characters, letters, numbers, underscores, hyphens only",
            )

            email = st.text_input(
                "Email Address *",
                placeholder="your.email@example.com",
                help="We'll send a verification email to this address",
            )

        with col2:
            password = st.text_input(
                "Password *",
                type="password",
                placeholder="Create a strong password",
                help="At least 8 characters with uppercase, lowercase, number, and special character",
            )

            confirm_password = st.text_input(
                "Confirm Password *",
                type="password",
                placeholder="Confirm your password",
            )

        # Terms and conditions
        terms_accepted = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy *",
            help="You must accept the terms to create an account",
        )

        # Submit button
        submitted = st.form_submit_button(
            "🚀 Create Account", type="primary", use_container_width=True
        )

        if submitted:
            # Validate form data
            validation_errors = []

            # Username validation
            if not username:
                validation_errors.append("Username is required")
            else:
                is_valid, message = validate_username(username)
                if not is_valid:
                    validation_errors.append(f"Username: {message}")

            # Email validation
            if not email:
                validation_errors.append("Email is required")
            elif not validate_email(email):
                validation_errors.append("Please enter a valid email address")

            # Password validation
            if not password:
                validation_errors.append("Password is required")
            else:
                is_valid, message = validate_password(password)
                if not is_valid:
                    validation_errors.append(f"Password: {message}")

            # Confirm password
            if password != confirm_password:
                validation_errors.append("Passwords do not match")

            # Terms acceptance
            if not terms_accepted:
                validation_errors.append("You must accept the terms and conditions")

            # If validation passes, create user
            if not validation_errors:
                try:
                    with get_db_session() as db:
                        user_service = UserService(db)
                        email_service = EmailService()

                        # Create user
                        success, message, user = user_service.create_user(
                            username=username, email=email, password=password
                        )

                        if success and user:
                            st.info(
                                "🔄 Creating account and sending verification email..."
                            )

                            # Send verification email
                            email_sent = email_service.send_verification_email(
                                to_email=email,
                                username=username,
                                verification_token=user.verification_token,
                            )

                            if email_sent:
                                show_registration_success(username, email)
                                st.stop()  # Stop execution to show success message
                            else:
                                st.warning(
                                    f"✅ Account created successfully! "
                                    f"However, verification email could not be sent to {email}. "
                                )

                                # Show manual verification option for development
                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    if st.button(
                                        "✅ Verify Account Manually", type="primary"
                                    ):
                                        user.mark_verified()
                                        db.commit()
                                        st.success(
                                            "✅ Account verified! You can now log in."
                                        )
                                        st.balloons()

                                with col2:
                                    if st.button("📧 Resend Email"):
                                        st.rerun()
                        else:
                            st.error(f"❌ {message}")

                except Exception as e:
                    logger.error(f"Error during user registration: {e}")
                    st.error(f"❌ An error occurred during registration: {str(e)}")

                    # Show debug info in development
                    if os.getenv("DEBUG", "false").lower() == "true":
                        st.exception(e)

            else:
                # Display validation errors
                st.error("❌ Please fix the following errors:")
                for error in validation_errors:
                    st.error(f"• {error}")


def show_features():
    """Show app features to encourage registration."""
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center;">
            <h2>✨ Why Choose AI Data Assistant?</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    features = [
        {
            "icon": "📊",
            "title": "Advanced Analytics",
            "description": "Comprehensive statistical analysis, correlation studies, and hypothesis testing with AI-powered insights.",
        },
        {
            "icon": "📈",
            "title": "Smart Visualizations",
            "description": "Create beautiful, interactive charts and dashboards with natural language commands.",
        },
        {
            "icon": "🤖",
            "title": "AI-Powered Insights",
            "description": "Get intelligent recommendations and automated pattern recognition from your data.",
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


def main():
    """Main registration page function."""
    # Load CSS
    load_css()

    # Show registration form
    show_registration_form()

    # Show features
    show_features()


if __name__ == "__main__":
    main()
