import unittest
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.import_export import generate_pdf_report

class TestExport(unittest.TestCase):

    def test_pdf_report_generation(self):
        user = {"username": "TestUser", "currency": "USD"}
        sample_tx = pd.DataFrame([
            {"date": "2026-09-01", "type": "income", "category": "Salary", "amount": 5000.0, "payment_method": "Bank Transfer", "notes": "Salary"},
            {"date": "2026-09-02", "type": "expense", "category": "Groceries", "amount": 150.0, "payment_method": "Credit Card", "notes": "Supermarket"}
        ])
        sample_budgets = pd.DataFrame([
            {"category": "Groceries", "monthly_limit": 500.0, "year_month": "2026-09"}
        ])

        pdf_bytes = generate_pdf_report(user, sample_tx, sample_budgets)
        self.assertIsNotNone(pdf_bytes)
        self.assertGreater(len(pdf_bytes), 1000, "PDF bytes should be generated successfully")

if __name__ == "__main__":
    unittest.main()
