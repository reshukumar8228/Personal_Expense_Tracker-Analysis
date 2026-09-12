import sqlite3
import os
import datetime
import random
import hashlib

# Load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DB_PATH = os.path.join(os.path.dirname(__file__), "expense_tracker.db")

import urllib.parse

def normalize_db_url(url: str) -> str:
    """Safely URL-encode password in PostgreSQL connection strings if special chars exist."""
    if not url or not ("postgresql://" in url or "postgres://" in url):
        return url
    prefix = "postgresql://" if url.startswith("postgresql://") else "postgres://"
    rest = url[len(prefix):]
    if "@" in rest:
        last_at_idx = rest.rfind("@")
        credentials = rest[:last_at_idx]
        host_and_db = rest[last_at_idx + 1:]
        if ":" in credentials:
            user, password = credentials.split(":", 1)
            encoded_password = urllib.parse.quote_plus(urllib.parse.unquote_plus(password))
            return f"{prefix}{user}:{encoded_password}@{host_and_db}"
    return url

def get_db_url() -> str | None:
    """Detect PostgreSQL database URL from environment or Streamlit secrets."""
    url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    if not url:
        try:
            import streamlit as st
            if hasattr(st, "secrets"):
                if "DATABASE_URL" in st.secrets:
                    url = st.secrets["DATABASE_URL"]
                elif "postgres" in st.secrets and isinstance(st.secrets["postgres"], dict) and "url" in st.secrets["postgres"]:
                    url = st.secrets["postgres"]["url"]
        except Exception:
            pass

    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    if url:
        url = normalize_db_url(url.strip())

    return url

class PgCursorWrapper:
    """Wrapper cursor for PostgreSQL that translates SQLite queries to PostgreSQL dialect."""

    def __init__(self, pg_cursor):
        self._cursor = pg_cursor
        self.lastrowid = None

    def _transform_sql(self, sql: str) -> str:
        # 1. Replace sqlite_master query
        if "sqlite_master" in sql:
            sql = sql.replace(
                "SELECT name FROM sqlite_master WHERE type='table';",
                "SELECT table_name AS name FROM information_schema.tables WHERE table_schema='public';"
            )

        # 2. Replace INSERT OR IGNORE
        if "INSERT OR IGNORE INTO" in sql:
            sql = sql.replace("INSERT OR IGNORE INTO", "INSERT INTO")
            if "ON CONFLICT" not in sql:
                sql += " ON CONFLICT DO NOTHING"

        # 3. Handle lastrowid for INSERT statements
        is_insert = sql.strip().upper().startswith("INSERT")
        if is_insert and "RETURNING" not in sql.upper():
            sql = sql.rstrip("; ") + " RETURNING id"

        # 4. Replace positional ? with %s
        sql = sql.replace("?", "%s")
        return sql

    def execute(self, sql, params=None):
        transformed_sql = self._transform_sql(sql)
        is_insert = sql.strip().upper().startswith("INSERT")

        if params is not None:
            if isinstance(params, list):
                params = tuple(params)
            res = self._cursor.execute(transformed_sql, params)
        else:
            res = self._cursor.execute(transformed_sql)

        if is_insert and "RETURNING id" in transformed_sql.upper():
            try:
                row = self._cursor.fetchone()
                if row:
                    if isinstance(row, dict):
                        self.lastrowid = row.get('id')
                    elif hasattr(row, 'get'):
                        self.lastrowid = row.get('id')
                    else:
                        self.lastrowid = row[0]
            except Exception:
                pass

        return res

    def executemany(self, sql, seq_of_params):
        transformed_sql = self._transform_sql(sql)
        return self._cursor.executemany(transformed_sql, seq_of_params)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchmany(self, size=None):
        if size is None:
            return self._cursor.fetchmany()
        return self._cursor.fetchmany(size)

    def __iter__(self):
        return iter(self._cursor)

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class PgConnectionWrapper:
    """Wrapper connection for PostgreSQL to match SQLite connection interface."""

    def __init__(self, pg_conn):
        self._conn = pg_conn

    def cursor(self):
        import psycopg2.extras
        return PgCursorWrapper(self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor))

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)


def is_postgres(conn=None) -> bool:
    """Check if PostgreSQL/Supabase is configured and currently active."""
    if conn is not None:
        return isinstance(conn, PgConnectionWrapper)
    return get_db_url() is not None


def get_connection():
    """Get database connection (Supabase PostgreSQL if configured, otherwise local SQLite)."""
    db_url = get_db_url()

    if db_url:
        try:
            import psycopg2
            import psycopg2.extras
            pg_conn = psycopg2.connect(db_url)
            return PgConnectionWrapper(pg_conn)
        except Exception as e:
            print(f"[WARNING] Could not connect to PostgreSQL ({e}). Falling back to local SQLite.")

    # SQLite fallback
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    """Initialize database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    if isinstance(conn, PgConnectionWrapper):
        # PostgreSQL DDL Schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                full_name VARCHAR(255),
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                currency VARCHAR(10) DEFAULT 'USD',
                theme VARCHAR(50) DEFAULT 'Dark Fintech',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(20) CHECK(type IN ('income', 'expense')) NOT NULL,
                icon VARCHAR(50) DEFAULT '🏷️',
                color VARCHAR(50) DEFAULT '#3b82f6',
                UNIQUE(user_id, name, type),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                date VARCHAR(20) NOT NULL,
                type VARCHAR(20) CHECK(type IN ('income', 'expense')) NOT NULL,
                category VARCHAR(255) NOT NULL,
                amount REAL NOT NULL,
                payment_method VARCHAR(100) NOT NULL,
                notes TEXT,
                is_recurring INTEGER DEFAULT 0,
                recurring_frequency VARCHAR(50) DEFAULT 'Monthly',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                category VARCHAR(255) NOT NULL,
                monthly_limit REAL NOT NULL,
                year_month VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, category, year_month),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS savings_goals (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0.0,
                target_date VARCHAR(20) NOT NULL,
                status VARCHAR(50) DEFAULT 'In Progress',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
    else:
        # SQLite DDL Schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                currency TEXT DEFAULT 'USD',
                theme TEXT DEFAULT 'Dark Fintech',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

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

        cursor.execute("""
            DELETE FROM categories
            WHERE id NOT IN (
                SELECT MIN(id) FROM categories GROUP BY user_id, name, type
            )
        """)

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

    # Safe migration: ensure full_name column exists in users table
    try:
        if isinstance(conn, PgConnectionWrapper):
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);")
        else:
            cursor.execute("PRAGMA table_info(users);")
            columns = [row[1] if isinstance(row, (tuple, list)) else row["name"] for row in cursor.fetchall()]
            if "full_name" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT;")
    except Exception as e:
        pass

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
    months = []
    for i in range(6, -1, -1):
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
        cursor.execute("""
            INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes, is_recurring, recurring_frequency)
            VALUES (?, ?, 'expense', 'Housing & Rent', 1650.00, 'Bank Transfer', 'Monthly Apartment Rent', 1, 'Monthly')
        """, (user_id, datetime.date(year, month, 3).strftime("%Y-%m-%d")))

        cursor.execute("""
            INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes, is_recurring, recurring_frequency)
            VALUES (?, ?, 'expense', 'Utilities', ?, 'Credit Card', 'Electric & Fiber Water Bill', 1, 'Monthly')
        """, (user_id, datetime.date(year, month, 5).strftime("%Y-%m-%d"), round(random.uniform(140, 210), 2)))

        cursor.execute("""
            INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes, is_recurring, recurring_frequency)
            VALUES (?, ?, 'expense', 'Subscriptions', 45.99, 'Credit Card', 'Netflix, Spotify & Cloud Storage', 1, 'Monthly')
        """, (user_id, datetime.date(year, month, 7).strftime("%Y-%m-%d")))

        # 3. Add Variable Expenses throughout month
        for g in range(4):
            day = random.randint(g * 7 + 1, min((g + 1) * 7, 28))
            g_date = datetime.date(year, month, day).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes)
                VALUES (?, ?, 'expense', 'Groceries', ?, ?, 'Weekly Supermarket Shopping')
            """, (user_id, g_date, round(random.uniform(90, 180), 2), random.choice(payment_methods)))

        for _ in range(random.randint(4, 6)):
            day = random.randint(1, 28)
            d_date = datetime.date(year, month, day).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes)
                VALUES (?, ?, 'expense', 'Dining Out', ?, ?, 'Dinner / Coffee with friends')
            """, (user_id, d_date, round(random.uniform(25, 95), 2), random.choice(payment_methods)))

        for _ in range(random.randint(2, 4)):
            day = random.randint(1, 28)
            t_date = datetime.date(year, month, day).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes)
                VALUES (?, ?, 'expense', 'Transportation', ?, ?, 'Fuel / Rideshare')
            """, (user_id, t_date, round(random.uniform(30, 80), 2), random.choice(payment_methods)))

        if random.random() > 0.3:
            s_day = random.randint(5, 25)
            s_date = datetime.date(year, month, s_day).strftime("%Y-%m-%d")
            cursor.execute("""
                INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes)
                VALUES (?, ?, 'expense', 'Shopping', ?, ?, 'Apparel / Gadgets')
            """, (user_id, s_date, round(random.uniform(60, 250), 2), "Credit Card"))

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
