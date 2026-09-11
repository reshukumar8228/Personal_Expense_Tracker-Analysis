import unittest
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import init_db, get_connection, seed_demo_data
from modules.ml_engine import predict_next_month_expenses

class TestMLEngine(unittest.TestCase):

    def setUp(self):
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        uname = f"ml_user_{int(time.time()*1000)}"
        email = f"ml_{int(time.time()*1000)}@test.com"
        cursor.execute("INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, 'h', 's')", (uname, email))
        self.user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        seed_demo_data(self.user_id)

    def test_ml_prediction(self):
        res = predict_next_month_expenses(self.user_id)
        self.assertEqual(res["status"], "success")
        self.assertGreater(res["predicted_total"], 0)
        self.assertIn("cat_predictions", res)
        self.assertGreaterEqual(res["upper_bound"], res["lower_bound"])

if __name__ == "__main__":
    unittest.main()
