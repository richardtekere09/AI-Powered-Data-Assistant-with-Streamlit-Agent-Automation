"""
User registration page for AI Data Assistant
"""

import streamlit as st
import re
from services.user_service import UserService
from services.email_service import EmailService
from config.database import get_db_session
import logging

logger = logging.getLogger(__name__)


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


def show_registration_form():
    """Display the user registration form."""
    st.markdown(
        """
        <div class="centered-container-large">
            <h1>Create Your Account</h1>
            <p class="form-description">
                Join AI Data Assistant and unlock the power of intelligent data analysis
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Create form
    with st.form("registration_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                help="3-20 characters, letters, numbers, underscores, hyphens only",
            )

            email = st.text_input(
                "Email Address",
                placeholder="Enter your email address",
                help="We'll send a verification email to this address",
            )

        with col2:
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a strong password",
                help="At least 8 characters with uppercase, lowercase, number, and special character",
            )

            confirm_password = st.text_input(
                "Confirm Password", type="password", placeholder="Confirm your password"
            )

        # Terms and conditions
        terms_accepted = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy",
            help="You must accept the terms to create an account",
        )

        # Submit button
        submit_button = st.form_submit_button(
            "Create Account", type="primary", use_container_width=True
        )

        if submit_button:
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
                            # Send verification email
                            email_sent = email_service.send_verification_email(
                                to_email=email,
                                username=username,
                                verification_token=user.verification_token,
                            )

                            if email_sent:
                                st.success(
                                    f"Account created successfully! Please check your email ({email}) "
                                    "for a verification link to complete your registration."
                                )

                                # Show next steps
                                with st.expander("📧 What's Next?", expanded=True):
                                    st.markdown("""
                                    **1. Check Your Email**
                                    - Look for an email from AI Data Assistant
                                    - Check your spam folder if you don't see it
                                    
                                    **2. Verify Your Email**
                                    - Click the verification link in the email
                                    - Or copy and paste the link into your browser
                                    
                                    **3. Start Using the App**
                                    - Once verified, you can log in and start analyzing data
                                    - Upload your datasets and get AI-powered insights
                                    """)

                                # Add a note about email configuration
                                if not email_service.smtp_username:
                                    st.warning(
                                        "**Note:** Email service is not configured. "
                                        "Please contact an administrator to verify your account manually."
                                    )

                            else:
                                st.warning(
                                    f"Account created but verification email could not be sent. "
                                    f"Please contact support to verify your account."
                                )
                        else:
                            st.error(f"{message}")

                except Exception as e:
                    logger.error(f"Error during user registration: {e}")
                    st.error(
                        " An error occurred during registration. Please try again later."
                    )
            else:
                # Display validation errors
                st.error("Please fix the following errors:")
                for error in validation_errors:
                    st.error(f"• {error}")


def show_login_link():
    """Show link to login page."""
    st.markdown("---")
    st.markdown(
        """
        <div class="text-center">
            <p>Already have an account? 
                <a href="?page=login" target="_self" class="link-primary">
                    Sign in here
                </a>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_features():
    """Show app features to encourage registration."""
    st.markdown("---")
    st.markdown(
        """
        <div class="centered-container">
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
                <div class="feature-display">
                    <div class="feature-icon">{feature["icon"]}</div>
                    <h3 class="feature-title">{feature["title"]}</h3>
                    <p class="feature-description">{feature["description"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def main():
    """Main registration page function."""
    st.set_page_config(
        page_title="Create Account - AI Data Assistant", page_icon="🚀", layout="wide"
    )

    # CSS styles are loaded from external file

    # Show registration form
    show_registration_form()

    # Show features
    show_features()

    # Show login link
    show_login_link()


if __name__ == "__main__":
    main()
