"""
Password reset page for AI Data Assistant
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
import logging

logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Reset Password - AI Data Assistant", page_icon="🔑", layout="wide"
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
            background: linear-gradient(135deg, #F59E0B 0%, #DC2626 100%);
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
            max-width: 600px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #F59E0B;
        }
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
        </style>
        """,
            unsafe_allow_html=True,
        )


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


def verify_reset_token(token: str) -> tuple[bool, str, str]:
    """Verify reset token and return result."""
    try:
        with get_db_session() as db:
            # Find the reset token
            from models.user import PasswordResetToken, User

            reset_token_obj = (
                db.query(PasswordResetToken)
                .filter(PasswordResetToken.token == token)
                .first()
            )

            if not reset_token_obj:
                return False, "Invalid or expired reset token", ""

            if reset_token_obj.is_expired():
                return (
                    False,
                    "Reset token has expired. Please request a new password reset.",
                    "",
                )

            # Get user
            user = db.query(User).filter(User.id == reset_token_obj.user_id).first()
            if not user:
                return False, "User not found", ""

            return True, "Token is valid", user.username

    except Exception as e:
        logger.error(f"Error verifying reset token: {e}")
        return False, "An error occurred during verification", ""


def reset_password(token: str, new_password: str) -> tuple[bool, str]:
    """Reset password using token."""
    try:
        with get_db_session() as db:
            user_service = UserService(db)
            success, message = user_service.reset_password(token, new_password)
            return success, message
    except Exception as e:
        logger.error(f"Error resetting password: {e}")
        return False, "An error occurred during password reset"


def show_password_reset_form(token: str, username: str):
    """Show password reset form."""
    st.markdown(
        f"""
        <div class="welcome-card">
            <h2>🔑 Reset Your Password</h2>
            <p>Create a new password for your account: <strong>{username}</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("password_reset_form"):
        st.markdown("### 🔐 New Password")

        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter your new password",
            help="At least 8 characters with uppercase, lowercase, number, and special character",
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Confirm your new password",
        )

        # Password strength indicator
        if new_password:
            is_valid, message = validate_password(new_password)
            if is_valid:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")

        submit_button = st.form_submit_button(
            "🔄 Reset Password", type="primary", use_container_width=True
        )

        if submit_button:
            validation_errors = []

            # Password validation
            if not new_password:
                validation_errors.append("New password is required")
            else:
                is_valid, message = validate_password(new_password)
                if not is_valid:
                    validation_errors.append(f"Password: {message}")

            # Confirm password
            if new_password != confirm_password:
                validation_errors.append("Passwords do not match")

            if not validation_errors:
                # Reset password
                with st.spinner("🔄 Resetting your password..."):
                    success, message = reset_password(token, new_password)

                if success:
                    show_password_reset_success(username)
                    st.stop()
                else:
                    st.error(f"❌ {message}")
            else:
                # Display validation errors
                for error in validation_errors:
                    st.error(f"❌ {error}")


def show_password_reset_success(username: str):
    """Show password reset success message."""
    st.markdown(
        f"""
        <div class="success-card">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎉</div>
            <h2>Password Reset Successful!</h2>
            <p>Your password has been updated successfully, <strong>{username}</strong>!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.success("✅ Your password has been reset successfully!")
    st.balloons()

    # Login button with JavaScript redirect
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
        <div style="text-align: center; margin: 2rem 0;">
            <a href="/" style="display: inline-block; background: #16A34A; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600;">
                🔐 Sign In Now
            </a>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Auto-redirect after 3 seconds
    st.markdown("---")
    st.info("🔄 You will be redirected to the login page in a moment...")

    # JavaScript auto-redirect
    st.markdown(
        """
    <script>
    setTimeout(function() {
        window.location.href = '/';
    }, 3000);
    </script>
    """,
        unsafe_allow_html=True,
    )


def show_error_message(message: str):
    """Show error message for invalid tokens."""
    st.markdown(
        """
        <div class="main-header" style="background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);">
            <h1>❌ Password Reset Failed</h1>
            <p>There was an issue with your password reset request</p>
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
        - Password reset links expire after 1 hour
        - Request a new password reset from the login page
        
        **2. Invalid Token**
        - Make sure you clicked the complete link from your email
        - Check that the URL wasn't truncated
        
        **3. Already Used**
        - Reset tokens can only be used once
        - Request a new reset if needed
        
        **4. Still Having Issues?**
        - Contact support at richardtekere02@gmail.com
        - We'll help you reset your password manually
        """)

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Try Again", use_container_width=True):
            st.rerun()

    with col2:
        st.markdown(
            """
        <div style="text-align: center;">
            <a href="/" style="display: inline-block; background: #2563EB; color: white; padding: 8px 16px; text-decoration: none; border-radius: 6px; font-weight: 600; width: 90%;">
                🔐 Back to Login
            </a>
        </div>
        """,
            unsafe_allow_html=True,
        )


def main():
    """Main password reset page function."""
    # Load CSS
    load_css()

    # Get token from URL parameters
    query_params = st.experimental_get_query_params()
    token = query_params.get("token", [None])[0]

    if not token:
        st.error(
            "❌ No reset token provided. Please check your email for the complete reset link."
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                """
            <div style="text-align: center; margin: 2rem 0;">
                <a href="/" style="display: inline-block; background: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600;">
                    🔐 Back to Login
                </a>
            </div>
            """,
                unsafe_allow_html=True,
            )
        st.stop()

    # Verify the token
    with st.spinner("🔍 Verifying reset token..."):
        valid, message, username = verify_reset_token(token)

    if valid:
        show_password_reset_form(token, username)
    else:
        show_error_message(message)


if __name__ == "__main__":
    main()
