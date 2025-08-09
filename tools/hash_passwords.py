
from passlib.hash import bcrypt

# Replace these with your real plaintext passwords just for hashing
passwords = ["login1", "login2"]

for pwd in passwords:
    print(bcrypt.hash(pwd))
