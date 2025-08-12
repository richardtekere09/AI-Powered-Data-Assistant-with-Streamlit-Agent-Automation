#!/usr/bin/env python3
"""
Fix all import issues for AI Data Assistant
"""

import os
from pathlib import Path


def fix_circular_import_in_user_model():
    """Fix the circular import in models/user.py"""
    print("🔧 Fixing circular import in models/user.py...")

    user_model_path = Path("models/user.py")

    if user_model_path.exists():
        # Read the current file
        with open(user_model_path, "r") as f:
            content = f.read()

        # Check if it has the problematic line
        if "from models.user import User, EmailVerificationToken" in content:
            print("❌ Found circular import - fixing...")

            # Replace the file with the fixed version
            fixed_content = '''"""
User model for AI Data Assistant
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime, timedelta

# Create Base here to avoid circular imports
Base = declarative_base()


class User(Base):
    """User model for authentication and user management."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String(255), unique=True, index=True)
    verification_expires = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationships
    verification_tokens = relationship(
        "EmailVerificationToken", back_populates="user", cascade="all, delete-orphan"
    )
    password_reset_tokens = relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    def generate_verification_token(self):
        """Generate a new verification token."""
        self.verification_token = str(uuid.uuid4())
        self.verification_expires = datetime.utcnow() + timedelta(hours=24)
        return self.verification_token

    def is_verification_token_expired(self):
        """Check if verification token is expired."""
        if not self.verification_expires:
            return True
        return datetime.utcnow() > self.verification_expires

    def mark_verified(self):
        """Mark user as verified."""
        self.is_verified = True
        self.verification_token = None
        self.verification_expires = None

    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()


class EmailVerificationToken(Base):
    """Email verification token model."""

    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    user = relationship("User", back_populates="verification_tokens")

    def __repr__(self):
        return f"<EmailVerificationToken(id={self.id}, user_id={self.user_id})>"

    def is_expired(self):
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at


class PasswordResetToken(Base):
    """Password reset token model."""

    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    user = relationship("User", back_populates="password_reset_tokens")

    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id})>"

    def is_expired(self):
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at


class UserSession(Base):
    """User session model for managing active sessions."""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationship
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"

    def is_expired(self):
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
'''

            with open(user_model_path, "w") as f:
                f.write(fixed_content)

            print("✅ Fixed circular import in models/user.py")
            return True
        else:
            print("✅ models/user.py already fixed")
            return True
    else:
        print("❌ models/user.py not found")
        return False


def create_missing_init_files():
    """Create missing __init__.py files"""
    print("\n📁 Creating missing __init__.py files...")

    directories = ["config", "models", "services", "auth", "utils"]

    for directory in directories:
        init_file = Path(directory) / "__init__.py"
        if not init_file.exists():
            init_file.parent.mkdir(exist_ok=True)
            init_file.touch()
            print(f"✅ Created {init_file}")
        else:
            print(f"✅ {init_file} already exists")


def fix_database_config():
    """Fix database configuration to avoid circular imports"""
    print("\n🗄️ Fixing database configuration...")

    db_config_path = Path("config/database.py")

    if db_config_path.exists():
        with open(db_config_path, "r") as f:
            content = f.read()

        # Check if it needs fixing
        if "from models.user import Base" in content and "try:" not in content:
            print("🔧 Fixing database config...")

            # Replace the problematic import
            content = content.replace(
                "from models.user import Base",
                """try:
    from models.user import Base
    logger.info("Base imported successfully from models.user")
except ImportError as e:
    logger.error(f"Failed to import Base from models.user: {e}")
    Base = None""",
            )

            with open(db_config_path, "w") as f:
                f.write(content)

            print("✅ Fixed database config")
        else:
            print("✅ Database config already fixed")
    else:
        print("❌ config/database.py not found")


def test_imports():
    """Test if all imports work now"""
    print("\n🧪 Testing imports...")

    try:
        import models.user

        print("✅ models.user imported successfully")

        from models.user import User, Base

        print("✅ User and Base imported successfully")

        import config.database

        print("✅ config.database imported successfully")

        from config.database import get_db_session

        print("✅ get_db_session imported successfully")

        import services.user_service

        print("✅ services.user_service imported successfully")

        import services.email_service

        print("✅ services.email_service imported successfully")

        print("✅ All imports successful!")
        return True

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False


def main():
    """Main fix function"""
    print("🔧 AI Data Assistant - Import Fix Tool")
    print("=" * 60)

    # Fix circular imports
    success1 = fix_circular_import_in_user_model()

    # Create missing __init__.py files
    create_missing_init_files()

    # Fix database config
    fix_database_config()

    # Test imports
    success2 = test_imports()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All import issues fixed!")
        print("✅ You can now run: streamlit run app.py")
    else:
        print("❌ Some issues remain. Check the errors above.")

    print("\n💡 Next steps:")
    print("1. Run: streamlit run app.py")
    print("2. Test registration: Click 'Create New Account'")
    print("3. Test password reset: Click 'Forgot Password'")


if __name__ == "__main__":
    main()
