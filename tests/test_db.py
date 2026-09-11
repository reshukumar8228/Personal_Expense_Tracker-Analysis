import unittest
import os
import sys
import time
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import get_connection, init_db, seed_demo_data

class TestDatabase(unittest.TestCase):

    def setUp(self):
        init_db()

    def test_init_db_tables(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cursor.fetchall()]

        self.assertIn("users", tables)
        self.assertIn("categories", tables)
        self.assertIn("transactions", tables)
        self.assertIn("budgets", tables)
        self.assertIn("savings_goals", tables)
        conn.close()

    def test_user_creation_and_seed_data(self):
        conn = get_connection()
        cursor = conn.cursor()

        uname = f"testuser_{int(time.time()*1000)}"
        email = f"test_{int(time.time()*1000)}@expensetracker.app"

        cursor.execute("""
            INSERT INTO users (username, email, password_hash, salt, currency)
            VALUES (?, ?, 'hash123', 'salt123', 'USD')
        """, (uname, email))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Seed demo data
        seed_demo_data(user_id)

        conn = get_connection()
        tx_df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id = ?", conn, params=(user_id,))
        budgets_df = pd.read_sql_query("SELECT * FROM budgets WHERE user_id = ?", conn, params=(user_id,))
        goals_df = pd.read_sql_query("SELECT * FROM savings_goals WHERE user_id = ?", conn, params=(user_id,))
        conn.close()

        self.assertFalse(tx_df.empty, "Transactions should be seeded")
        self.assertFalse(budgets_df.empty, "Budgets should be seeded")
        self.assertFalse(goals_df.empty, "Savings goals should be seeded")

if __name__ == "__main__":
    unittest.main()
