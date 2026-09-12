import streamlit as st
import hashlib
import os
import secrets
from database.db import get_connection, seed_default_categories, seed_demo_data

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash password with PBKDF2 HMAC SHA256 and salt."""
    if not salt:
        salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return pw_hash, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verify password against stored hash and salt."""
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == stored_hash

def register_user(username: str, email: str, password: str, currency: str = "USD") -> tuple[bool, str]:
    """Register a new user in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        pw_hash, salt = hash_password(password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, salt, currency)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, pw_hash, salt, currency))
        user_id = cursor.lastrowid
        conn.commit()

        # Seed categories for new user
        seed_default_categories(user_id)
        return True, "Registration successful! You can now log in."
    except Exception as e:
        err_msg = str(e)
        if "UNIQUE constraint failed: users.username" in err_msg:
            return False, "Username is already taken. Please choose another."
        elif "UNIQUE constraint failed: users.email" in err_msg:
            return False, "Email address is already registered."
        return False, f"Registration failed: {err_msg}"
    finally:
        conn.close()

def login_user(username_or_email: str, password: str) -> tuple[dict | None, str]:
    """Authenticate user with username/email and password."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE username = ? OR email = ?
    """, (username_or_email, username_or_email))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return None, "Invalid username/email or password."

    user_dict = dict(user)
    if verify_password(password, user_dict["password_hash"], user_dict["salt"]):
        return user_dict, "Login successful!"
    return None, "Invalid username/email or password."

def init_session_state():
    """Initialize Streamlit session state keys if not already set."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

def render_auth_page():
    """Render Login & Registration UI tabs."""
    st.markdown("<h1 style='text-align: center; font-weight: 800; background: linear-gradient(135deg, #879BFF, #C52DDB); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Personal Expense Tracker</h1>", unsafe_allow_html=True)
    st.markdown("<p class='page-subtitle' style='text-align: center; margin-bottom: 30px;'>Personal Finance & Expense Intelligence Platform</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register, tab_demo = st.tabs(["🔒 Log In", "📝 Register", "⚡ Quick Demo"])

        with tab_login:
            st.subheader("Welcome Back")
            with st.form("login_form"):
                username_input = st.text_input("Username or Email")
                password_input = st.text_input("Password", type="password")
                submit_login = st.form_submit_button("Log In", use_container_width=True, type="primary")

                if submit_login:
                    if not username_input or not password_input:
                        st.error("Please enter both username and password.")
                    else:
                        user, msg = login_user(username_input, password_input)
                        if user:
                            st.session_state.user = user
                            st.session_state.authenticated = True
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

        with tab_register:
            st.subheader("Create Your Account")
            with st.form("register_form"):
                reg_username = st.text_input("Username")
                reg_email = st.text_input("Email Address")
                reg_password = st.text_input("Password", type="password")
                reg_confirm = st.text_input("Confirm Password", type="password")
                reg_currency = st.selectbox("Preferred Currency", ["USD", "EUR", "GBP", "INR", "JPY", "CAD", "AUD"])
                submit_reg = st.form_submit_button("Register", use_container_width=True, type="primary")

                if submit_reg:
                    if not reg_username or not reg_email or not reg_password:
                        st.error("All fields are required.")
                    elif reg_password != reg_confirm:
                        st.error("Passwords do not match.")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters long.")
                    else:
                        success, msg = register_user(reg_username, reg_email, reg_password, reg_currency)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

        with tab_demo:
            st.subheader("Explore Personal Expense Tracker Instant Demo")
            st.info("Experience all features immediately with realistic 6-month sample financial data!")
            if st.button("🚀 Launch Demo Account", use_container_width=True, type="primary"):
                # Create or get demo user
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = 'demouser'")
                demo_user = cursor.fetchone()
                if not demo_user:
                    pw_hash, salt = hash_password("demo1234")
                    cursor.execute("""
                        INSERT INTO users (username, email, password_hash, salt, currency)
                        VALUES ('demouser', 'demo@expensetracker.app', ?, ?, 'USD')
                    """, (pw_hash, salt))
                    conn.commit()
                    user_id = cursor.lastrowid
                else:
                    user_id = demo_user["id"]

                conn.close()

                # Seed sample data for demo user
                seed_demo_data(user_id)

                # Fetch updated user object
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                user_dict = dict(cursor.fetchone())
                conn.close()

                st.session_state.user = user_dict
                st.session_state.authenticated = True
                st.success("Demo user loaded successfully!")
                st.rerun()

def logout_user():
    """Logout current user and clear session state."""
    st.session_state.user = None
    st.session_state.authenticated = False
    st.rerun()
