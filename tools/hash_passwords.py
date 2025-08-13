#!/usr/bin/env python3
"""
Generate bcrypt password hashes for init.sql
"""

import bcrypt


def generate_hash(password):
    """Generate bcrypt hash for password."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


# Generate hashes for your users
passwords = {"admin123": "admin", "richard09": "richard", "test123": "testuser"}

print("Password hashes for init.sql:")
print("-" * 50)

for password, username in passwords.items():
    hash_value = generate_hash(password)
    print(f"-- {username} (password: {password})")
    print(f"'{hash_value}',")
    print()

# Test the hashes work
print("Verification test:")
for password, username in passwords.items():
    test_hash = generate_hash(password)
    is_valid = bcrypt.checkpw(password.encode("utf-8"), test_hash.encode("utf-8"))
    print(f"✅ {username}/{password}: {'VALID' if is_valid else 'INVALID'}")
