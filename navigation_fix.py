"""
Simple navigation fix for AI Data Assistant
This creates proper links and handles routing
"""

import streamlit as st
import subprocess
import sys
import os


def create_registration_link():
    """Create a working registration link."""

    # Method 1: Direct file execution
    if st.button("🚀 Create New Account", use_container_width=True):
        try:
            # Try to run the registration page directly
            registration_path = os.path.join("auth", "registration.py")
            if os.path.exists(registration_path):
                # Use streamlit run command
                subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "streamlit",
                        "run",
                        registration_path,
                        "--server.port",
                        "8502",
                    ]
                )
                st.success("✅ Opening registration page...")
                st.info("🌐 Registration page opening on port 8502")
            else:
                st.error("❌ Registration page not found")
        except Exception as e:
            st.error(f"❌ Navigation error: {e}")


def create_direct_registration_page():
    """Create registration functionality directly in main app."""

    # Check if we should show registration
    if st.session_state.get("show_registration", False):
        show_inline_registration()
    else:
        # Show registration button
        if st.button("🚀 Create New Account", use_container_width=True):
            st.session_state.show_registration = True
            st.rerun()


def show_inline_registration():
    """Show registration form inline in the main app."""
    st.markdown("### 🚀 Create Your Account")

    # Back button
    if st.button("← Back to Login", key="back_to_login"):
        st.session_state.show_registration = False
        st.rerun()

    with st.form("inline_registration_form"):
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="your.email@example.com")

        with col2:
            password = st.text_input(
                "Password", type="password", placeholder="Create password"
            )
            confirm_password = st.text_input(
                "Confirm Password", type="password", placeholder="Confirm password"
            )

        terms = st.checkbox("I agree to the Terms of Service")

        if st.form_submit_button("🚀 Create Account", type="primary"):
            if not all([username, email, password, confirm_password, terms]):
                st.error("❌ Please fill all fields and accept terms")
            elif password != confirm_password:
                st.error("❌ Passwords do not match")
            else:
                try:
                    # Import registration logic
                    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                    from config.database import get_db_session
                    from services.user_service import UserService
                    from services.email_service import EmailService

                    with get_db_session() as db:
                        user_service = UserService(db)
                        email_service = EmailService()

                        # Create user
                        success, message, user = user_service.create_user(
                            username, email, password
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
                                    f"✅ Account created! Check {email} for verification."
                                )
                                st.balloons()
                            else:
                                st.warning(
                                    "✅ Account created but email failed to send."
                                )
                                # Manual verification for development
                                if st.button("✅ Verify Manually (Dev Mode)"):
                                    user.mark_verified()
                                    db.commit()
                                    st.success("Account verified!")
                        else:
                            st.error(f"❌ {message}")

                except Exception as e:
                    st.error(f"❌ Registration failed: {e}")


def test_navigation_methods():
    """Test different navigation methods."""
    st.markdown("### 🧪 Navigation Test Methods")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Method 1: Direct Link**")
        st.markdown(
            """
        <a href="auth/registration.py" target="_blank" style="display: inline-block; background: #2563EB; color: white; padding: 8px 16px; text-decoration: none; border-radius: 6px;">
            📝 Register (Link)
        </a>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("**Method 2: New Port**")
        if st.button("📝 Register (Port)", key="reg_port"):
            try:
                subprocess.Popen(
                    [
                        sys.executable,
                        "-m",
                        "streamlit",
                        "run",
                        "auth/registration.py",
                        "--server.port",
                        "8502",
                    ]
                )
                st.success("Opening on port 8502")
            except Exception as e:
                st.error(f"Error: {e}")

    with col3:
        st.markdown("**Method 3: Inline**")
        if st.button("📝 Register (Inline)", key="reg_inline"):
            st.session_state.show_registration = True
            st.rerun()


def main():
    """Test navigation methods."""
    st.title("🧪 Navigation Debug Tool")

    # Test different methods
    test_navigation_methods()

    # Show inline registration if requested
    if st.session_state.get("show_registration", False):
        show_inline_registration()


if __name__ == "__main__":

    main()
