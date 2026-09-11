import datetime
import pandas as pd
from database.db import get_connection

CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "INR": "₹",
    "JPY": "¥",
    "CAD": "CA$",
    "AUD": "A$",
}

CATEGORY_ICONS = {
    # Income
    "Salary": "💰",
    "Freelance": "💻",
    "Business": "🏢",
    "Investment": "📈",
    "Investments": "📈",
    "Interest": "🪙",
    "Bonus": "🎁",
    "Gift": "🎈",
    "Rental Income": "🔑",
    "Refund": "↩️",
    "Other Income": "💵",
    
    # Expense
    "Food & Dining": "🍽️",
    "Dining Out": "🍽️",
    "Groceries": "🛒",
    "Rent / Housing": "🏠",
    "Housing & Rent": "🏠",
    "Transportation": "🚗",
    "Shopping": "🛍️",
    "Utilities & Bills": "💡",
    "Utilities": "💡",
    "Healthcare": "🏥",
    "Education": "📚",
    "Entertainment": "🎬",
    "Travel": "✈️",
    "Insurance": "🛡️",
    "Subscriptions": "📱",
    "Personal Care": "💅",
    "Miscellaneous": "📦",
    "Other": "🏷️",
}

CATEGORY_COLORS = {
    "Salary": "#10b981",
    "Freelance": "#059669",
    "Business": "#047857",
    "Investment": "#34d399",
    "Investments": "#34d399",
    "Interest": "#6ee7b7",
    "Bonus": "#a7f3d0",
    "Gift": "#10b981",
    "Rental Income": "#059669",
    "Refund": "#34d399",
    
    "Food & Dining": "#ec4899",
    "Rent / Housing": "#ef4444",
    "Transportation": "#3b82f6",
    "Shopping": "#f97316",
    "Utilities & Bills": "#6366f1",
    "Healthcare": "#14b8a6",
    "Education": "#64748b",
    "Entertainment": "#8b5cf6",
    "Travel": "#06b6d4",
    "Insurance": "#38bdf8",
    "Subscriptions": "#a855f7",
    "Personal Care": "#e11d48",
    "Miscellaneous": "#94a3b8",
    "Other": "#94a3b8",
}

def get_user_categories(user_id: int, tx_type: str) -> list[str]:
    """Retrieve deduplicated category options for income or expense, incorporating defaults and user custom categories."""
    conn = get_connection()
    categories_df = pd.read_sql_query("""
        SELECT DISTINCT name FROM categories WHERE user_id = ? AND type = ? ORDER BY name
    """, conn, params=(user_id, tx_type))
    conn.close()

    db_cats = categories_df["name"].tolist() if not categories_df.empty else []

    if tx_type == "income":
        base_defaults = ["Salary", "Freelance", "Business", "Investment", "Interest", "Bonus", "Gift", "Rental Income", "Refund"]
    else:
        base_defaults = ["Food & Dining", "Rent / Housing", "Transportation", "Shopping", "Utilities & Bills", "Healthcare", "Education", "Entertainment", "Travel", "Insurance", "Subscriptions", "Personal Care"]

    # Combine db stored categories + base defaults without duplicates
    combined = list(dict.fromkeys(db_cats + base_defaults))
    if "Other" in combined:
        combined.remove("Other")
    combined.append("Other")

    return combined

def format_currency(amount: float, currency_code: str = "USD") -> str:
    """Format float amount into currency string."""
    symbol = CURRENCY_SYMBOLS.get(currency_code, "$")
    if amount is None:
        amount = 0.0
    return f"{symbol}{amount:,.2f}"

def get_month_name(year_month: str) -> str:
    """Convert YYYY-MM string into full Month Year string."""
    try:
        dt = datetime.datetime.strptime(year_month, "%Y-%m")
        return dt.strftime("%B %Y")
    except Exception:
        return year_month

def get_current_year_month() -> str:
    """Return current year-month as YYYY-MM."""
    return datetime.datetime.now().strftime("%Y-%m")
