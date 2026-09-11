import datetime

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
    "Salary": "💰",
    "Freelance": "💻",
    "Investments": "📈",
    "Other Income": "💵",
    "Housing & Rent": "🏠",
    "Groceries": "🛒",
    "Dining Out": "🍽️",
    "Transportation": "🚗",
    "Utilities": "💡",
    "Entertainment": "🎬",
    "Healthcare": "🏥",
    "Shopping": "🛍️",
    "Subscriptions": "📱",
    "Travel": "✈️",
    "Education": "📚",
    "Personal Care": "💅",
    "Miscellaneous": "📦",
}

CATEGORY_COLORS = {
    "Salary": "#10b981",
    "Freelance": "#059669",
    "Investments": "#047857",
    "Other Income": "#34d399",
    "Housing & Rent": "#ef4444",
    "Groceries": "#f59e0b",
    "Dining Out": "#ec4899",
    "Transportation": "#3b82f6",
    "Utilities": "#6366f1",
    "Entertainment": "#8b5cf6",
    "Healthcare": "#14b8a6",
    "Shopping": "#f97316",
    "Subscriptions": "#a855f7",
    "Travel": "#06b6d4",
    "Education": "#64748b",
    "Personal Care": "#e11d48",
    "Miscellaneous": "#94a3b8",
}

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
