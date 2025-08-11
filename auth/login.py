"""
Enhanced login system for AI Data Assistant with database integration
"""

import streamlit as st
import toml
import os
from streamlit_authenticator import Authenticate
from services.user_service import UserService
from services.email_service import EmailService
from config.database import get_db_session
import logging

logger = logging.getLogger(__name__)


def load_config(path: str = "config.toml"):
    """Load configuration from TOML file."""
    if not os.path.exists(path):
        st.error("Missing config.toml for authentication.")
        st.stop()
    with open(path, "r") as f:
        return toml.load(f)


def get_authenticator():
    """Get authenticator instance."""
    config = load_config()

    # Use positional arguments instead of keyword arguments
    authenticator = Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["preauthorized"],
    )
    return authenticator


def get_database_authenticator():
    """Get database-based authenticator for new users."""
    return DatabaseAuthenticator()


class DatabaseAuthenticator:
    """Database-based authentication system."""

    def __init__(self):
        self.name = None
        self.username = None
        self.authentication_status = None

    def login(self, location: str = "main") -> tuple[str, bool, str]:
        """Handle user login with database authentication."""
        try:
            with get_db_session() as db:
                user_service = UserService(db)

                # Create login form
                if location == "sidebar":
                    with st.sidebar:
                        return self._show_login_form(user_service)
                else:
                    return self._show_login_form(user_service)

        except Exception as e:
            logger.error(f"Error during database authentication: {e}")
            st.error("Authentication service unavailable. Please try again later.")
            return None, False, None

    def _show_login_form(self, user_service: UserService) -> tuple[str, bool, str]:
        """Show login form and handle authentication."""
        st.markdown("### Sign In")

        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input(
                "Password", type="password", placeholder="Enter your password"
            )

            col1, col2 = st.columns([1, 1])
            with col1:
                submit_button = st.form_submit_button(
                    "Log In", type="primary", use_container_width=True
                )

            with col2:
                if st.form_submit_button("Forgot Password?", use_container_width=True):
                    st.session_state.show_forgot_password = True

            if submit_button:
                if username and password:
                    # Authenticate user
                    success, message, user = user_service.authenticate_user(
                        username, password
                    )

                    if success and user:
                        if not user.is_verified:
                            st.error(
                                "Please verify your email address before signing in. Check your email for a verification link."
                            )
                            return None, False, username

                        if not user.is_active:
                            st.error(
                                "Your account has been deactivated. Please contact support."
                            )
                            return None, False, username

                        # Login successful
                        self.name = user.username
                        self.username = user.username
                        self.authentication_status = True

                        st.success(f"Welcome back, {user.username}!")
                        st.rerun()

                        return user.username, True, user.username
                    else:
                        st.error(f"{message}")
                        return None, False, username
                else:
                    st.error("Please enter both username and password")
                    return None, False, None

        # Show registration link
        st.markdown("---")
        st.markdown(
            """
            <div class="text-center">
                <p>Don't have an account? 
                    <a href="auth/registration.py" target="_self" class="link-primary">
                        Create one here
                    </a>
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return None, False, None

    def logout(self, button_name: str, location: str = "main"):
        """Handle user logout."""
        if location == "sidebar":
            with st.sidebar:
                if st.button(button_name):
                    self.name = None
                    self.username = None
                    self.authentication_status = False
                    st.session_state.clear()
                    st.rerun()
        else:
            if st.button(button_name):
                self.name = None
                self.username = None
                self.authentication_status = False
                st.session_state.clear()
                st.rerun()


def show_forgot_password_form():
    """Show forgot password form."""
    st.markdown("### Reset Password")

    with st.form("forgot_password_form"):
        email = st.text_input("Email Address", placeholder="Enter your email address")
        submit_button = st.form_submit_button(
            "Send Reset Link", type="primary", use_container_width=True
        )

        if submit_button:
            if email:
                try:
                    with get_db_session() as db:
                        user_service = UserService(db)
                        email_service = EmailService()

                        # Create password reset token
                        success, message, reset_token = (
                            user_service.create_password_reset_token(email)
                        )

                        if success and reset_token:
                            # Send password reset email
                            user = user_service.get_user_by_email(email)
                            if user:
                                email_sent = email_service.send_password_reset_email(
                                    to_email=email,
                                    username=user.username,
                                    reset_token=reset_token,
                                )

                                if email_sent:
                                    st.success(
                                        f"Password reset link sent to {email}. "
                                        "Please check your email and follow the instructions."
                                    )
                                else:
                                    st.warning(
                                        "Reset link created but email could not be sent. "
                                        "Please contact support."
                                    )
                            else:
                                st.error("User not found")
                        else:
                            st.error(f"{message}")

                except Exception as e:
                    logger.error(f"Error during password reset: {e}")
                    st.error("An error occurred. Please try again later.")
            else:
                st.error("Please enter your email address")

    # Back to login link
    st.markdown("---")
    if st.button("← Back to Login"):
        st.session_state.show_forgot_password = False
        st.rerun()


def get_hybrid_authenticator():
    """Get hybrid authenticator that tries database first, then falls back to config file."""
    # Try database authentication first
    try:
        db_auth = get_database_authenticator()
        return db_auth
    except Exception as e:
        logger.warning(
            f"Database authentication unavailable, falling back to config: {e}"
        )
        # Fall back to config file authentication
        return get_authenticator()
