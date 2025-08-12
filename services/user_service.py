# services/user_service.py
"""
User service for authentication and user management
"""

import bcrypt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.user import User, EmailVerificationToken, PasswordResetToken, UserSession
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user-related operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_user(
        self, username: str, email: str, password: str
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Create a new user account.

        Args:
            username: Unique username
            email: User email address
            password: Plain text password

        Returns:
            Tuple of (success, message, user_object)
        """
        try:
            # Check if username already exists
            existing_user = (
                self.db.query(User).filter(User.username == username).first()
            )
            if existing_user:
                return False, "Username already exists", None

            # Check if email already exists
            existing_email = self.db.query(User).filter(User.email == email).first()
            if existing_email:
                return False, "Email already registered", None

            # Hash password
            password_hash = bcrypt.hashpw(
                password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

            # Create user
            user = User(username=username, email=email, password_hash=password_hash)

            # Generate verification token
            user.generate_verification_token()

            # Add to database
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            logger.info(f"User created successfully: {username}")
            return True, "User created successfully", user

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error during user creation: {e}")
            return False, "User with this information already exists", None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {e}")
            return False, "An error occurred during user creation", None

    def authenticate_user(
        self, username: str, password: str
    ) -> Tuple[bool, str, Optional[User]]:
        """
        Authenticate user credentials.

        Args:
            username: Username or email
            password: Plain text password

        Returns:
            Tuple of (success, message, user_object)
        """
        try:
            # Find user by username or email
            user = (
                self.db.query(User)
                .filter((User.username == username) | (User.email == username))
                .first()
            )

            if not user:
                return False, "Invalid username or password", None

            # Check password
            if not bcrypt.checkpw(
                password.encode("utf-8"), user.password_hash.encode("utf-8")
            ):
                return False, "Invalid username or password", None

            # Update last login
            user.update_last_login()
            self.db.commit()

            logger.info(f"User authenticated successfully: {user.username}")
            return True, "Authentication successful", user

        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return False, "Authentication service unavailable", None

    def verify_email(self, token: str) -> Tuple[bool, str]:
        """
        Verify email using verification token.

        Args:
            token: Verification token

        Returns:
            Tuple of (success, message)
        """
        try:
            user = self.db.query(User).filter(User.verification_token == token).first()

            if not user:
                return False, "Invalid verification token"

            if user.is_verification_token_expired():
                return False, "Verification token has expired"

            if user.is_verified:
                return False, "Email already verified"

            # Mark as verified
            user.mark_verified()
            self.db.commit()

            logger.info(f"Email verified for user: {user.username}")
            return True, "Email verified successfully"

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during email verification: {e}")
            return False, "Verification service unavailable"

    def get_user_by_verification_token(self, token: str) -> Optional[User]:
        """Get user by verification token."""
        try:
            return self.db.query(User).filter(User.verification_token == token).first()
        except Exception as e:
            logger.error(f"Error getting user by verification token: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        try:
            return self.db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            return self.db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None

    def create_password_reset_token(
        self, email: str
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Create password reset token for user.

        Args:
            email: User email address

        Returns:
            Tuple of (success, message, reset_token)
        """
        try:
            user = self.get_user_by_email(email)
            if not user:
                return False, "No account found with this email", None

            if not user.is_verified:
                return False, "Please verify your email first", None

            # Generate reset token
            reset_token = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry

            # Create reset token record
            password_reset_token = PasswordResetToken(
                user_id=user.id, token=reset_token, expires_at=expires_at
            )

            self.db.add(password_reset_token)
            self.db.commit()

            logger.info(f"Password reset token created for user: {user.username}")
            return True, "Password reset token created", reset_token

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating password reset token: {e}")
            return False, "Password reset service unavailable", None

    def reset_password(self, token: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset user password using reset token.

        Args:
            token: Password reset token
            new_password: New plain text password

        Returns:
            Tuple of (success, message)
        """
        try:
            # Find reset token
            reset_token = (
                self.db.query(PasswordResetToken)
                .filter(PasswordResetToken.token == token)
                .first()
            )

            if not reset_token:
                return False, "Invalid reset token"

            if reset_token.is_expired():
                return False, "Reset token has expired"

            # Get user
            user = self.db.query(User).filter(User.id == reset_token.user_id).first()
            if not user:
                return False, "User not found"

            # Hash new password
            password_hash = bcrypt.hashpw(
                new_password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            user.password_hash = password_hash

            # Delete reset token
            self.db.delete(reset_token)
            self.db.commit()

            logger.info(f"Password reset successfully for user: {user.username}")
            return True, "Password reset successfully"

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resetting password: {e}")
            return False, "Password reset service unavailable"

    def create_user_session(self, user_id: int) -> Optional[str]:
        """Create a new user session."""
        try:
            session_token = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(days=30)  # 30 day expiry

            user_session = UserSession(
                user_id=user_id, session_token=session_token, expires_at=expires_at
            )

            self.db.add(user_session)
            self.db.commit()

            return session_token

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user session: {e}")
            return None

    def validate_session_token(self, token: str) -> Optional[User]:
        """Validate session token and return user."""
        try:
            user_session = (
                self.db.query(UserSession)
                .filter(UserSession.session_token == token)
                .first()
            )

            if not user_session or user_session.is_expired():
                return None

            return self.db.query(User).filter(User.id == user_session.user_id).first()

        except Exception as e:
            logger.error(f"Error validating session token: {e}")
            return None

    def revoke_session(self, token: str) -> bool:
        """Revoke a user session."""
        try:
            user_session = (
                self.db.query(UserSession)
                .filter(UserSession.session_token == token)
                .first()
            )

            if user_session:
                self.db.delete(user_session)
                self.db.commit()
                return True

            return False

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error revoking session: {e}")
            return False
