"""
User service for handling user operations
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from models.user import User, EmailVerificationToken, PasswordResetToken, UserSession
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service class for user management operations."""

    def __init__(self, db: Session):
        self.db = db

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def create_user(
        self, username: str, email: str, password: str
    ) -> Tuple[bool, str, Optional[User]]:
        """Create a new user account."""
        try:
            # Check if username or email already exists
            existing_user = (
                self.db.query(User)
                .filter((User.username == username) | (User.email == email))
                .first()
            )

            if existing_user:
                if existing_user.username == username:
                    return False, "Username already exists", None
                else:
                    return False, "Email already registered", None

            # Create new user
            user = User(
                username=username,
                email=email,
                password_hash=self.hash_password(password),
                is_verified=False,
            )

            # Generate verification token
            verification_token = user.generate_verification_token()

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            logger.info(f"User created successfully: {username}")
            return True, "User created successfully", user

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error creating user: {e}")
            return False, "User creation failed due to database constraint", None
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {e}")
            return False, "User creation failed", None

    def authenticate_user(
        self, username: str, password: str
    ) -> Tuple[bool, str, Optional[User]]:
        """Authenticate a user with username and password."""
        try:
            user = self.db.query(User).filter(User.username == username).first()

            if not user:
                return False, "Invalid username or password", None

            if not user.is_active:
                return False, "Account is deactivated", None

            if not self.verify_password(password, user.password_hash):
                return False, "Invalid username or password", None

            # Update last login
            user.update_last_login()
            self.db.commit()

            logger.info(f"User authenticated successfully: {username}")
            return True, "Authentication successful", user

        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return False, "Authentication failed", None

    def verify_email(self, token: str) -> Tuple[bool, str]:
        """Verify user email using verification token."""
        try:
            user = self.db.query(User).filter(User.verification_token == token).first()

            if not user:
                return False, "Invalid verification token"

            if user.is_verified:
                return False, "Email already verified"

            if user.is_verification_token_expired():
                return False, "Verification token has expired"

            # Mark user as verified
            user.mark_verified()
            self.db.commit()

            logger.info(f"Email verified successfully for user: {user.username}")
            return True, "Email verified successfully"

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error verifying email: {e}")
            return False, "Email verification failed"

    def resend_verification_email(self, email: str) -> Tuple[bool, str]:
        """Resend verification email to user."""
        try:
            user = self.db.query(User).filter(User.email == email).first()

            if not user:
                return False, "Email not found"

            if user.is_verified:
                return False, "Email already verified"

            # Generate new verification token
            verification_token = user.generate_verification_token()
            self.db.commit()

            logger.info(f"Verification email resent for user: {user.username}")
            return True, "Verification email sent"

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resending verification email: {e}")
            return False, "Failed to resend verification email"

    def create_password_reset_token(
        self, email: str
    ) -> Tuple[bool, str, Optional[str]]:
        """Create a password reset token for a user."""
        try:
            user = self.db.query(User).filter(User.email == email).first()

            if not user:
                return False, "Email not found", None

            if not user.is_active:
                return False, "Account is deactivated", None

            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=1)

            # Create or update reset token
            existing_token = (
                self.db.query(PasswordResetToken)
                .filter(PasswordResetToken.user_id == user.id)
                .first()
            )

            if existing_token:
                existing_token.token = reset_token
                existing_token.expires_at = expires_at
            else:
                reset_token_obj = PasswordResetToken(
                    user_id=user.id, token=reset_token, expires_at=expires_at
                )
                self.db.add(reset_token_obj)

            self.db.commit()

            logger.info(f"Password reset token created for user: {user.username}")
            return True, "Password reset token created", reset_token

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating password reset token: {e}")
            return False, "Failed to create password reset token", None

    def reset_password(self, token: str, new_password: str) -> Tuple[bool, str]:
        """Reset user password using reset token."""
        try:
            reset_token_obj = (
                self.db.query(PasswordResetToken)
                .filter(PasswordResetToken.token == token)
                .first()
            )

            if not reset_token_obj:
                return False, "Invalid reset token"

            if reset_token_obj.is_expired():
                return False, "Reset token has expired"

            # Update user password
            user = (
                self.db.query(User).filter(User.id == reset_token_obj.user_id).first()
            )
            if not user:
                return False, "User not found"

            user.password_hash = self.hash_password(new_password)

            # Remove reset token
            self.db.delete(reset_token_obj)
            self.db.commit()

            logger.info(f"Password reset successfully for user: {user.username}")
            return True, "Password reset successfully"

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error resetting password: {e}")
            return False, "Password reset failed"

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def update_user_profile(self, user_id: int, **kwargs) -> Tuple[bool, str]:
        """Update user profile information."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"

            # Update allowed fields
            allowed_fields = ["username", "email"]
            for field, value in kwargs.items():
                if field in allowed_fields and hasattr(user, field):
                    setattr(user, field, value)

            self.db.commit()
            logger.info(f"User profile updated for user ID: {user_id}")
            return True, "Profile updated successfully"

        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error updating user profile: {e}")
            return False, "Profile update failed due to database constraint"
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user profile: {e}")
            return False, "Profile update failed"

    def deactivate_user(self, user_id: int) -> Tuple[bool, str]:
        """Deactivate a user account."""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "User not found"

            user.is_active = False
            self.db.commit()

            logger.info(f"User deactivated: {user.username}")
            return True, "User deactivated successfully"

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating user: {e}")
            return False, "Failed to deactivate user"
