#!/usr/bin/env python3
"""
Fix the create_enginene typo
"""

import os
from pathlib import Path


def fix_typo_in_file(file_path):
    """Fix typo in a specific file"""
    try:
        with open(file_path, "r") as f:
            content = f.read()

        # Fix the typo
        if "create_enginene" in content:
            print(f"❌ Found 'create_enginene' in {file_path}")
            fixed_content = content.replace("create_enginene", "create_engine")

            with open(file_path, "w") as f:
                f.write(fixed_content)

            print(f"✅ Fixed typo in {file_path}")
            return True
        else:
            print(f"✅ No typo in {file_path}")
            return False

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Fix the typo"""
    print("🔧 Fixing create_enginene typo")
    print("=" * 40)

    # Files to check
    files_to_fix = [
        "config/database.py",
        "models/user.py",
        "services/user_service.py",
        "services/email_service.py",
        "auth/login.py",
    ]

    fixed_count = 0

    for file_path in files_to_fix:
        if Path(file_path).exists():
            if fix_typo_in_file(file_path):
                fixed_count += 1
        else:
            print(f"⚠️ {file_path} not found")

    print(f"\n🎉 Fixed typos in {fixed_count} files")

    # Test imports
    print("\n🧪 Testing imports...")
    try:
        from sqlalchemy import create_engine

        print("✅ SQLAlchemy import works!")

        import config.database

        print("✅ config.database import works!")

        from config.database import get_db_session

        print("✅ get_db_session import works!")

        print("\n🚀 Try running your app now: streamlit run app.py")

    except Exception as e:
        print(f"❌ Still failing: {e}")


if __name__ == "__main__":
    main()
