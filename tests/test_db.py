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
        full_name = "Test User Full Name"
        email = f"test_{int(time.time()*1000)}@expensetracker.app"

        cursor.execute("""
            INSERT INTO users (username, full_name, email, password_hash, salt, currency)
            VALUES (?, ?, ?, 'hash123', 'salt123', 'USD')
        """, (uname, full_name, email))
        user_id = cursor.lastrowid
        conn.commit()

        cursor.execute("SELECT full_name FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        self.assertEqual(row["full_name"], full_name)
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

    def test_current_month_seed_data_no_future_dates_and_has_expenses(self):
        """Verify that demo seed data contains current month expenses and no future-dated transactions."""
        conn = get_connection()
        cursor = conn.cursor()

        uname = f"testuser_dates_{int(time.time()*1000)}"
        cursor.execute("""
            INSERT INTO users (username, full_name, email, password_hash, salt, currency)
            VALUES (?, 'Date Test User', ?, 'hash123', 'salt123', 'USD')
        """, (uname, f"{uname}@example.com"))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        seed_demo_data(user_id)

        import datetime
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        current_ym = datetime.date.today().strftime("%Y-%m")

        conn = get_connection()
        # 1. No future transactions
        future_df = pd.read_sql_query(
            "SELECT * FROM transactions WHERE user_id = ? AND date > ?",
            conn, params=(user_id, today_str)
        )
        self.assertTrue(future_df.empty, f"Seeded demo data should not have future transactions: {future_df.to_dict('records')}")

        # 2. Current month has both income and expense transactions
        current_df = pd.read_sql_query(
            "SELECT * FROM transactions WHERE user_id = ? AND date LIKE ?",
            conn, params=(user_id, f"{current_ym}%")
        )
        conn.close()

        self.assertFalse(current_df.empty, "Current month must contain transactions")
        curr_income = current_df[current_df["type"] == "income"]
        curr_expense = current_df[current_df["type"] == "expense"]
        self.assertFalse(curr_income.empty, "Current month must have income transactions")
        self.assertFalse(curr_expense.empty, "Current month must have expense transactions (not 0)")
        self.assertGreater(curr_expense["amount"].sum(), 0.0, "Current month total expenses must be greater than 0")

if __name__ == "__main__":
    unittest.main()
