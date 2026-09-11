import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.auth import hash_password, verify_password

class TestAuth(unittest.TestCase):

    def test_hash_and_verify_password(self):
        password = "SecurePassword123!"
        pw_hash, salt = hash_password(password)

        self.assertIsNotNone(pw_hash)
        self.assertIsNotNone(salt)

        # Verify correct password
        self.assertTrue(verify_password(password, pw_hash, salt))

        # Verify incorrect password
        self.assertFalse(verify_password("WrongPassword", pw_hash, salt))

if __name__ == "__main__":
    unittest.main()
