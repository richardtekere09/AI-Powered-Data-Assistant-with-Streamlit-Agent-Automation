#!/usr/bin/env python3
"""
Fix admin user password and verification status
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import bcrypt

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

def fix_admin_user():
    """Fix admin user password and verification."""
    try:
        from config.database import get_db_session
        from models.user import User
        
        print("🔧 Fixing admin user...")
        
        with get_db_session() as db:
            # Find admin user
            admin_user = db.query(User).filter(User.username == "admin").first()
            
            if not admin_user:
                print("❌ Admin user not found in database")
                
                # Create admin user
                print("🔨 Creating admin user...")
                password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                admin_user = User(
                    username="admin",
                    email="admin@example.com",
                    password_hash=password_hash,
                    is_verified=True,  # Mark as verified
                    is_active=True
                )
                
                db.add(admin_user)
                db.commit()
                print("✅ Admin user created and verified")
                return True
            
            else:
                print(f"👤 Found admin user: {admin_user.email}")
                
                # Fix password hash
                correct_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                admin_user.password_hash = correct_hash
                
                # Mark as verified
                admin_user.is_verified = True
                admin_user.is_active = True
                admin_user.verification_token = None
                admin_user.verification_expires = None
                
                db.commit()
                print("✅ Admin password fixed and account verified")
                
                # Test the password
                test_password = "admin123"
                if bcrypt.checkpw(test_password.encode('utf-8'), admin_user.password_hash.encode('utf-8')):
                    print("✅ Password verification test passed")
                else:
                    print("❌ Password verification test failed")
                
                return True
    
    except Exception as e:
        print(f"❌ Error fixing admin user: {e}")
        return False

def fix_richard_user():
    """Fix richard user verification."""
    try:
        from config.database import get_db_session
        from models.user import User
        
        print("\n🔧 Fixing richard user...")
        
        with get_db_session() as db:
            # Find richard user
            richard_user = db.query(User).filter(User.username == "richard").first()
            
            if richard_user:
                print(f"👤 Found richard user: {richard_user.email}")
                
                # Mark as verified
                richard_user.is_verified = True
                richard_user.is_active = True
                richard_user.verification_token = None
                richard_user.verification_expires = None
                
                db.commit()
                print("✅ Richard user verified")
                
                # Test password
                if bcrypt.checkpw("richard09".encode('utf-8'), richard_user.password_hash.encode('utf-8')):
                    print("✅ Richard password verification test passed")
                else:
                    print("❌ Richard password verification test failed")
                
                return True
            else:
                print("❌ Richard user not found")
                return False
    
    except Exception as e:
        print(f"❌ Error fixing richard user: {e}")
        return False

def test_login_after_fix():
    """Test login after fixes."""
    print("\n🧪 Testing login after fixes...")
    
    try:
        from auth.login import authenticate_with_database
        
        test_users = [
            ("admin", "admin123"),
            ("richard", "richard09")
        ]
        
        for username, password in test_users:
            print(f"\n🔐 Testing {username}/{password}:")
            success, name, extra = authenticate_with_database(username, password)
            
            if success:
                print(f"✅ Login successful: {name}")
            else:
                print(f"❌ Login failed")
                if extra:
                    print(f"   Details: {extra}")
    
    except Exception as e:
        print(f"❌ Login test failed: {e}")

def main():
    """Main function."""
    print("🔧 AI Data Assistant - Password Fix Tool")
    print("=" * 50)
    
    # Fix admin user
    fix_admin_user()
    
    # Fix richard user
    fix_richard_user()
    
    # Test login
    test_login_after_fix()
    
    print("\n🎉 Fixes completed!")
    print("📋 You should now be able to login with:")
    print("   👤 admin / admin123")
    print("   👤 richard / richard09")
    print("\n🚀 Try running your app again: streamlit run app.py")

if __name__ == "__main__":
    main()