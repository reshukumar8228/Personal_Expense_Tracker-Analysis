import sqlite3
import os
import datetime
import random
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), "smartspend.db")

def get_connection():
    """Get a SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    """Initialize database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            currency TEXT DEFAULT 'USD',
            theme TEXT DEFAULT 'Dark Fintech',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Categories Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
            icon TEXT DEFAULT '🏷️',
            color TEXT DEFAULT '#3b82f6',
            UNIQUE(user_id, name, type),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # Clean any historical duplicates if table already existed without UNIQUE constraint
    cursor.execute("""
        DELETE FROM categories
        WHERE id NOT IN (
            SELECT MIN(id) FROM categories GROUP BY user_id, name, type
        )
    """)

    # 3. Transactions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            notes TEXT,
            is_recurring INTEGER DEFAULT 0,
            recurring_frequency TEXT DEFAULT 'Monthly',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # 4. Budgets Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            monthly_limit REAL NOT NULL,
            year_month TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, category, year_month),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    # 5. Savings Goals Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS savings_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0.0,
            target_date TEXT NOT NULL,
            status TEXT DEFAULT 'In Progress',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

def seed_default_categories(user_id: int, conn=None):
    """Seed standard categories for a new user."""
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    cursor = conn.cursor()

    default_cats = [
        # Income categories
        ("Salary", "income", "💰", "#10b981"),
        ("Freelance", "income", "💻", "#059669"),
        ("Business", "income", "🏢", "#047857"),
        ("Investment", "income", "📈", "#34d399"),
        ("Interest", "income", "🪙", "#6ee7b7"),
        ("Bonus", "income", "🎁", "#a7f3d0"),
        ("Gift", "income", "🎈", "#10b981"),
        ("Rental Income", "income", "🔑", "#059669"),
        ("Refund", "income", "↩️", "#34d399"),
        ("Investments", "income", "📈", "#34d399"),
        ("Other Income", "income", "💵", "#34d399"),
        
        # Expense categories
        ("Food & Dining", "expense", "🍽️", "#ec4899"),
        ("Rent / Housing", "expense", "🏠", "#ef4444"),
        ("Transportation", "expense", "🚗", "#3b82f6"),
        ("Shopping", "expense", "🛍️", "#f97316"),
        ("Utilities & Bills", "expense", "💡", "#6366f1"),
        ("Healthcare", "expense", "🏥", "#14b8a6"),
        ("Education", "expense", "📚", "#64748b"),
        ("Entertainment", "expense", "🎬", "#8b5cf6"),
        ("Travel", "expense", "✈️", "#06b6d4"),
        ("Insurance", "expense", "🛡️", "#38bdf8"),
        ("Subscriptions", "expense", "📱", "#a855f7"),
        ("Personal Care", "expense", "💅", "#e11d48"),
        ("Housing & Rent", "expense", "🏠", "#ef4444"),
        ("Groceries", "expense", "🛒", "#f59e0b"),
        ("Dining Out", "expense", "🍽️", "#ec4899"),
        ("Utilities", "expense", "💡", "#6366f1"),
        ("Miscellaneous", "expense", "📦", "#64748b"),
    ]

    for name, c_type, icon, color in default_cats:
        cursor.execute("""
            INSERT OR IGNORE INTO categories (user_id, name, type, icon, color)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, name, c_type, icon, color))

    if should_close:
        conn.commit()
        conn.close()

def seed_demo_data(user_id: int):
    """Seed 6 months of realistic transaction, budget, and savings goal data for demo user."""
    conn = get_connection()
    cursor = conn.cursor()

    # Clear existing demo user data first
    cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM budgets WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM savings_goals WHERE user_id = ?", (user_id,))

    seed_default_categories(user_id, conn=conn)

    today = datetime.date.today()
    # Generate 6 months of history
    months = []
    for i in range(6, -1, -1):
        # Calculate year and month back i months
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))

    payment_methods = ["Credit Card", "Debit Card", "Bank Transfer", "UPI", "Cash"]

    for year, month in months:
        ym_str = f"{year}:{month:02d}".replace(":", "-")
        # 1. Add Income
        salary_date = datetime.date(year, month, 1).strftime("%Y-%m-%d")
        cursor.execute("""
            INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes)
            VALUES (?, ?, 'income', 'Salary', 5200.00, 'Bank Transfer', 'Monthly Salary Direct Deposit')
        """, (user_id, salary_date))

        if random.random() > 0.4:
            fl_day = random.randint(10, 22)
            fl_date = datetime.date(year, month, fl_day).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes)
                VALUES (?, ?, 'income', 'Freelance', ?, 'Bank Transfer', 'UI/UX Design Consulting')
            """, (user_id, fl_date, round(random.uniform(400, 1200), 2)))

        # 2. Add Fixed Expenses
        # Rent
        cursor.execute("""
            INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes, is_recurring, recurring_frequency)
            VALUES (?, ?, 'expense', 'Housing & Rent', 1650.00, 'Bank Transfer', 'Monthly Apartment Rent', 1, 'Monthly')
        """, (user_id, datetime.date(year, month, 3).strftime("%Y-%m-%d")))

        # Utilities
        cursor.execute("""
            INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes, is_recurring, recurring_frequency)
            VALUES (?, ?, 'expense', 'Utilities', ?, 'Credit Card', 'Electric & Fiber Water Bill', 1, 'Monthly')
        """, (user_id, datetime.date(year, month, 5).strftime("%Y-%m-%d"), round(random.uniform(140, 210), 2)))

        # Subscriptions
        cursor.execute("""
            INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes, is_recurring, recurring_frequency)
            VALUES (?, ?, 'expense', 'Subscriptions', 45.99, 'Credit Card', 'Netflix, Spotify & Cloud Storage', 1, 'Monthly')
        """, (user_id, datetime.date(year, month, 7).strftime("%Y-%m-%d")))

        # 3. Add Variable Expenses throughout month
        # Groceries (3-4 times a month)
        for g in range(4):
            day = random.randint(g * 7 + 1, min((g + 1) * 7, 28))
            g_date = datetime.date(year, month, day).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes)
                VALUES (?, ?, 'expense', 'Groceries', ?, ?, 'Weekly Supermarket Shopping')
            """, (user_id, g_date, round(random.uniform(90, 180), 2), random.choice(payment_methods)))

        # Dining Out (4-6 times)
        for _ in range(random.randint(4, 6)):
            day = random.randint(1, 28)
            d_date = datetime.date(year, month, day).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes)
                VALUES (?, ?, 'expense', 'Dining Out', ?, ?, 'Dinner / Coffee with friends')
            """, (user_id, d_date, round(random.uniform(25, 95), 2), random.choice(payment_methods)))

        # Transportation
        for _ in range(random.randint(2, 4)):
            day = random.randint(1, 28)
            t_date = datetime.date(year, month, day).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes)
                VALUES (?, ?, 'expense', 'Transportation', ?, ?, 'Fuel / Rideshare')
            """, (user_id, t_date, round(random.uniform(30, 80), 2), random.choice(payment_methods)))

        # Shopping / Entertainment occasionally
        if random.random() > 0.3:
            s_day = random.randint(5, 25)
            s_date = datetime.date(year, month, s_day).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes)
                VALUES (?, ?, 'expense', 'Shopping', ?, ?, 'Apparel / Gadgets')
            """, (user_id, s_date, round(random.uniform(60, 250), 2), "Credit Card"))

        # Set Monthly Budgets for current & recent months
        budgets_config = [
            ("Housing & Rent", 1700.0),
            ("Groceries", 650.0),
            ("Dining Out", 350.0),
            ("Transportation", 250.0),
            ("Utilities", 250.0),
            ("Subscriptions", 60.0),
            ("Entertainment", 200.0),
            ("Shopping", 300.0),
        ]
        for cat, limit in budgets_config:
            cursor.execute("""
                INSERT INTO budgets (user_id, category, monthly_limit, year_month)
                VALUES (?, ?, ?, ?)
            """, (user_id, cat, limit, ym_str))

    # Add Savings Goals
    cursor.execute("""
        INSERT INTO savings_goals (user_id, name, target_amount, current_amount, target_date, status, notes)
        VALUES (?, 'Emergency Fund', 10000.00, 6500.00, '2026-12-31', 'In Progress', '6 months living expenses reserve')
    """, (user_id,))
    cursor.execute("""
        INSERT INTO savings_goals (user_id, name, target_amount, current_amount, target_date, status, notes)
        VALUES (?, 'Japan Vacation', 3500.00, 1800.00, '2026-10-15', 'In Progress', 'Flights and hotels for 2 week trip')
    """, (user_id,))
    cursor.execute("""
        INSERT INTO savings_goals (user_id, name, target_amount, current_amount, target_date, status, notes)
        VALUES (?, 'New Macbook Pro', 2500.00, 2500.00, '2026-06-01', 'Completed', 'M3 Max 16 inch')
    """, (user_id,))

    conn.commit()
    conn.close()
