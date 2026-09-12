import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.auth import hash_password, verify_password, register_user, login_user
from database.db import init_db

class TestAuth(unittest.TestCase):

    def setUp(self):
        init_db()

    def test_hash_and_verify_password(self):
        password = "SecurePassword123!"
        pw_hash, salt = hash_password(password)

        self.assertIsNotNone(pw_hash)
        self.assertIsNotNone(salt)

        # Verify correct password
        self.assertTrue(verify_password(password, pw_hash, salt))

        # Verify incorrect password
        self.assertFalse(verify_password("WrongPassword", pw_hash, salt))

    def test_register_and_login_user(self):
        import time
        unique_id = int(time.time() * 1000)
        full_name = "Rahul Sharma"
        email = f"rahul_{unique_id}@example.com"
        password = "MySecurePassword123"

        success, msg = register_user(full_name, email, password)
        self.assertTrue(success, f"Registration failed: {msg}")

        # Attempt login
        user, login_msg = login_user(email, password)
        self.assertIsNotNone(user, f"Login failed: {login_msg}")
        self.assertEqual(user["email"], email)
        self.assertEqual(user["full_name"], full_name)

        # Duplicate registration with same email should fail
        dup_success, dup_msg = register_user(full_name, email, password)
        self.assertFalse(dup_success)
        self.assertIn("already registered", dup_msg.lower())

if __name__ == "__main__":
    unittest.main()
