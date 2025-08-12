"""
Enhanced login system for AI Data Assistant with database integration
Fixed navigation for "Create New Account" button
"""

import streamlit as st
import toml
import os
import bcrypt
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def load_config(path: str = "config.toml"):
    """Load configuration from TOML file."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            return toml.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return None


def authenticate_with_config(
    username: str, password: str, config: dict
) -> Tuple[bool, Optional[str]]:
    """Authenticate using config file."""
    try:
        if username in config["credentials"]["usernames"]:
            user_data = config["credentials"]["usernames"][username]
            if user_data["password"] == password:
                return True, user_data["name"]
        return False, None
    except Exception as e:
        logger.error(f"Config authentication error: {e}")
        return False, None


def authenticate_with_database(
    username: str, password: str
) -> Tuple[bool, Optional[str], Optional[dict]]:
    """Authenticate using database."""
    try:
        # Import here to avoid circular imports
        from config.database import get_db_session
        from models.user import User

        with get_db_session() as db:
            # Find user by username or email
            user = (
                db.query(User)
                .filter((User.username == username) | (User.email == username))
                .first()
            )

            if not user:
                return False, None, None

            # Check password
            if not bcrypt.checkpw(
                password.encode("utf-8"), user.password_hash.encode("utf-8")
            ):
                return False, None, None

            # Check if user is verified
            if not user.is_verified:
                return False, None, {"error": "email_not_verified", "user": user}

            # Check if user is active
            if not user.is_active:
                return False, None, {"error": "account_deactivated", "user": user}

            # Update last login
            user.last_login = user.last_login or user.created_at
            db.commit()

            return True, user.username, {"user": user}

    except Exception as e:
        logger.error(f"Database authentication error: {e}")
        return False, None, {"error": "service_unavailable"}


class DatabaseAuthenticator:
    """Database-based authentication system."""

    def __init__(self):
        self.name = None
        self.username = None
        self.authentication_status = None

    def login(
        self, location: str = "main"
    ) -> Tuple[Optional[str], Optional[bool], Optional[str]]:
        """Handle user login with database authentication."""

        # Check if already authenticated
        if st.session_state.get("authentication_status") == True:
            self.authentication_status = True
            self.name = st.session_state.get("name")
            self.username = st.session_state.get("username")
            return self.name, self.authentication_status, self.username

        # Show login form
        if location == "sidebar":
            with st.sidebar:
                return self._show_login_form()
        else:
            return self._show_login_form()

    def _show_login_form(self) -> Tuple[Optional[str], Optional[bool], Optional[str]]:
        """Show login form and handle authentication."""
        st.markdown("### Sign In")

        # Check for forgot password state
        if st.session_state.get("show_forgot_password", False):
            return self._show_forgot_password_form()

        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input(
                "Password", type="password", placeholder="Enter your password"
            )

            col1, col2 = st.columns([1, 1])
            with col1:
                login_button = st.form_submit_button(
                    "Log In", type="primary", use_container_width=True
                )

            with col2:
                forgot_button = st.form_submit_button(
                    "Forgot Password?", use_container_width=True
                )

            if forgot_button:
                st.session_state.show_forgot_password = True
                st.rerun()

            if login_button:
                if username and password:
                    # Try database authentication first
                    success, name, extra = authenticate_with_database(
                        username, password
                    )

                    if success:
                        # Login successful
                        self.name = name
                        self.username = username
                        self.authentication_status = True

                        # Store in session state
                        st.session_state.authentication_status = True
                        st.session_state.name = name
                        st.session_state.username = username

                        st.success(f"✅ Welcome back, {name}!")
                        st.rerun()

                        return name, True, username
                    else:
                        # Check for specific errors
                        if extra and "error" in extra:
                            if extra["error"] == "email_not_verified":
                                st.error(
                                    "📧 Please verify your email address before signing in. "
                                    "Check your email for a verification link."
                                )
                            elif extra["error"] == "account_deactivated":
                                st.error(
                                    " Your account has been deactivated. "
                                    "Please contact support."
                                )
                            elif extra["error"] == "service_unavailable":
                                # Try config file authentication as fallback
                                config = load_config()
                                if config:
                                    config_success, config_name = (
                                        authenticate_with_config(
                                            username, password, config
                                        )
                                    )
                                    if config_success:
                                        self.name = config_name
                                        self.username = username
                                        self.authentication_status = True

                                        st.session_state.authentication_status = True
                                        st.session_state.name = config_name
                                        st.session_state.username = username

                                        st.success(f"✅ Welcome back, {config_name}!")
                                        st.rerun()

                                        return config_name, True, username

                                st.error(
                                    "🔧 Authentication service unavailable. Please try again later."
                                )
                        else:
                            st.error(" Invalid username or password")

                        return None, False, username
                else:
                    st.error(" Please enter both username and password")
                    return None, False, None

        # Show registration link - FIXED VERSION
        st.markdown("---")
        st.markdown("###  New User?")

        # # Method 1: Direct HTML link (most reliable)
        # base_url = os.getenv("BASE_URL", "http://localhost:8501")
        # registration_url = f"{base_url}/auth/registration"

        # st.markdown(
        #     f"""
        # <div style="text-align: center; padding: 1rem;">
        #     <a href="{registration_url}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #16A34A 0%, #0D9488 100%); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 1rem;">
        #         📝 Create New Account
        #     </a>
        # </div>
        # """,
        #     unsafe_allow_html=True,
        # )

        # st.markdown(
        #     """
        # <div style="text-align: center; margin-top: 0.5rem;">
        #     <p style="font-size: 0.9rem; color: #64748B;">
        #         Click above to register in a new tab
        #     </p>
        # </div>
        # """,
        #     unsafe_allow_html=True,
        # )

        # Method 2: Streamlit button as fallback
        if st.button(
            "Create New Account",
            use_container_width=True,
            help=" registration method for new users",
        ):
            st.session_state.show_registration_inline = True
            st.rerun()

        # Method 3: Show inline registration if requested
        if st.session_state.get("show_registration_inline", False):
            self._show_inline_registration()

        return None, None, None

    def _show_inline_registration(self):
        """Show inline registration form as fallback."""
        # st.markdown("### 📝 Quick Registration")

        # if st.button("← Back to Login", key="back_to_login"):
        #     st.session_state.show_registration_inline = False
        #     st.rerun()

        with st.form("inline_registration"):
            col1, col2 = st.columns(2)

            with col1:
                username = st.text_input("Username", placeholder="Choose username")
                email = st.text_input("Email", placeholder="your@email.com")

            with col2:
                password = st.text_input(
                    "Password", type="password", placeholder="Create password"
                )
                confirm_password = st.text_input(
                    "Confirm Password", type="password", placeholder="Confirm password"
                )

            terms = st.checkbox("I agree to the Terms of Service")
            submit = st.form_submit_button("Create Account", type="primary")

            if submit:
                if not all([username, email, password, confirm_password, terms]):
                    st.error(" Please fill all fields and accept terms")
                elif password != confirm_password:
                    st.error(" Passwords do not match")
                else:
                    try:
                        from config.database import get_db_session
                        from services.user_service import UserService
                        from services.email_service import EmailService

                        with get_db_session() as db:
                            user_service = UserService(db)
                            email_service = EmailService()

                            success, message, user = user_service.create_user(
                                username, email, password
                            )

                            if success and user:
                                email_sent = email_service.send_verification_email(
                                    to_email=email,
                                    username=username,
                                    verification_token=user.verification_token,
                                )

                                if email_sent:
                                    st.success(
                                        f"✅ Account created! Check {email} for verification."
                                    )
                                    st.balloons()
                                else:
                                    st.warning("✅ Account created but email failed.")
                                    if st.button("✅ Verify Now (Dev Mode)"):
                                        user.mark_verified()
                                        db.commit()
                                        st.success("Account verified!")
                            else:
                                st.error(f"{message}")
                    except Exception as e:
                        st.error(f"Registration failed: {e}")

    def _show_forgot_password_form(
        self,
    ) -> Tuple[Optional[str], Optional[bool], Optional[str]]:
        """Show forgot password form."""
        st.markdown("### 🔑 Reset Password")

        with st.form("forgot_password_form"):
            email = st.text_input(
                "Email Address", placeholder="Enter your email address"
            )

            col1, col2 = st.columns([1, 1])
            with col1:
                reset_button = st.form_submit_button(
                    "Send Reset Link", type="primary", use_container_width=True
                )
            with col2:
                back_button = st.form_submit_button(
                    "← Back to Login", use_container_width=True
                )

            if back_button:
                st.session_state.show_forgot_password = False
                st.rerun()

            if reset_button and email:
                try:
                    # Import here to avoid circular imports
                    from config.database import get_db_session
                    from services.user_service import UserService
                    from services.email_service import EmailService

                    with st.spinner("Sending reset link..."):
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
                                    email_sent = (
                                        email_service.send_password_reset_email(
                                            to_email=email,
                                            username=user.username,
                                            reset_token=reset_token,
                                        )
                                    )

                                    if email_sent:
                                        st.success(
                                            f"✅ Password reset link sent to {email}. "
                                            "Please check your email and follow the instructions."
                                        )
                                        st.info(
                                            "Check your email from richardtekere02@gmail.com"
                                        )
                                    else:
                                        st.warning(
                                            "🔧 Reset link created but email could not be sent. "
                                            "Please check your email configuration."
                                        )

                                        # Show debug info if in development mode
                                        if (
                                            os.getenv("DEBUG", "false").lower()
                                            == "true"
                                        ):
                                            st.code(f"Reset token: {reset_token}")
                                            st.info(
                                                "Development mode: Use this token to reset manually"
                                            )
                                else:
                                    st.error("User not found")
                            else:
                                st.error(f"{message}")

                except ImportError as e:
                    st.error(f"Import error: {e}")
                    st.error("🔧 Please check that all required files exist:")
                    st.code(
                        "config/database.py\nservices/user_service.py\nservices/email_service.py"
                    )

                except Exception as e:
                    logger.error(f"Error during password reset: {e}")
                    st.error("🔧 Service unavailable. Please try again later.")

                    # Show debug info if in development mode
                    if os.getenv("DEBUG", "false").lower() == "true":
                        st.exception(e)

        return None, None, None

    def logout(self, button_name: str, location: str = "main"):
        """Handle user logout."""
        logout_clicked = False

        if location == "sidebar":
            with st.sidebar:
                logout_clicked = st.button(button_name, use_container_width=True)
        else:
            logout_clicked = st.button(button_name)

        if logout_clicked:
            # Clear all authentication state
            self.name = None
            self.username = None
            self.authentication_status = None

            # Clear session state
            for key in list(st.session_state.keys()):
                if key in ["authentication_status", "name", "username", "current_user"]:
                    del st.session_state[key]

            st.success("✅ Logged out successfully!")
            st.rerun()


class ConfigAuthenticator:
    """Config file-based authentication system (fallback)."""

    def __init__(self, config: dict):
        self.config = config
        self.name = None
        self.username = None
        self.authentication_status = None

    def login(
        self, location: str = "main"
    ) -> Tuple[Optional[str], Optional[bool], Optional[str]]:
        """Handle user login with config file authentication."""

        # Check if already authenticated
        if st.session_state.get("authentication_status") == True:
            self.authentication_status = True
            self.name = st.session_state.get("name")
            self.username = st.session_state.get("username")
            return self.name, self.authentication_status, self.username

        if location == "sidebar":
            with st.sidebar:
                return self._show_login_form()
        else:
            return self._show_login_form()

    def _show_login_form(self) -> Tuple[Optional[str], Optional[bool], Optional[str]]:
        """Show login form for config authentication."""
        st.markdown("### Sign In")

        with st.form("config_login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input(
                "Password", type="password", placeholder="Enter your password"
            )

            login_button = st.form_submit_button(
                "Log In", type="primary", use_container_width=True
            )

            if login_button:
                if username and password:
                    success, name = authenticate_with_config(
                        username, password, self.config
                    )

                    if success:
                        self.name = name
                        self.username = username
                        self.authentication_status = True

                        st.session_state.authentication_status = True
                        st.session_state.name = name
                        st.session_state.username = username

                        st.success(f"✅ Welcome back, {name}!")
                        st.rerun()

                        return name, True, username
                    else:
                        st.error(" Invalid username or password")
                        return None, False, username
                else:
                    st.error("Please enter both username and password")
                    return None, False, None

        return None, None, None

    def logout(self, button_name: str, location: str = "main"):
        """Handle user logout."""
        logout_clicked = False

        if location == "sidebar":
            with st.sidebar:
                logout_clicked = st.button(button_name, use_container_width=True)
        else:
            logout_clicked = st.button(button_name)

        if logout_clicked:
            self.name = None
            self.username = None
            self.authentication_status = None

            for key in list(st.session_state.keys()):
                if key in ["authentication_status", "name", "username", "current_user"]:
                    del st.session_state[key]

            st.success("✅ Logged out successfully!")
            st.rerun()


def get_hybrid_authenticator():
    """Get hybrid authenticator that tries database first, then falls back to config file."""
    try:
        # Try database authentication first
        db_auth = DatabaseAuthenticator()
        return db_auth
    except Exception as e:
        logger.warning(
            f"Database authentication unavailable, falling back to config: {e}"
        )

        # Fall back to config file authentication
        config = load_config()
        if config:
            return ConfigAuthenticator(config)
        else:
            st.error(
                "❌ No authentication system available. Please check your configuration."
            )
            st.stop()


def show_forgot_password_form():
    """Show forgot password form (standalone function for compatibility)."""
    st.markdown("###  Reset Password")

    with st.form("standalone_forgot_password_form"):
        email = st.text_input("Email Address", placeholder="Enter your email address")

        col1, col2 = st.columns([1, 1])
        with col1:
            reset_button = st.form_submit_button(
                "Send Reset Link", type="primary", use_container_width=True
            )
        with col2:
            back_button = st.form_submit_button(
                "← Back to Login", use_container_width=True
            )

        if back_button:
            st.session_state.show_forgot_password = False
            st.rerun()

        if reset_button and email:
            try:
                from config.database import get_db_session
                from services.user_service import UserService
                from services.email_service import EmailService

                with get_db_session() as db:
                    user_service = UserService(db)
                    email_service = EmailService()

                    success, message, reset_token = (
                        user_service.create_password_reset_token(email)
                    )

                    if success and reset_token:
                        user = user_service.get_user_by_email(email)
                        if user:
                            email_sent = email_service.send_password_reset_email(
                                to_email=email,
                                username=user.username,
                                reset_token=reset_token,
                            )

                            if email_sent:
                                st.success(f"✅ Reset link sent to {email}")
                            else:
                                st.warning(
                                    "🔧 Reset link created but email could not be sent."
                                )
                        else:
                            st.error("❌ User not found")
                    else:
                        st.error(f"❌ {message}")

            except Exception as e:
                logger.error(f"Password reset error: {e}")
                st.error("🔧 Service unavailable. Please try again later.")


# Compatibility functions for easy integration
def get_authenticator():
    """Get authenticator instance (backward compatibility)."""
    return get_hybrid_authenticator()


def get_database_authenticator():
    """Get database authenticator instance."""
    return DatabaseAuthenticator()
