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
    """Render modern SaaS Login & Registration UI."""
    st.markdown("""
        <div class="auth-brand-logo">
            <div class="auth-logo-icon">📉</div>
            <div>
                <div class="auth-headline">Personal Expense Tracker</div>
                <div class="auth-subtitle">Expense Intelligence & Financial Management Platform</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2.2, 1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        tab_login, tab_register, tab_demo = st.tabs(["🔒 Log In", "📝 Create Account", "⚡ Instant Demo"])

        with tab_login:
            st.markdown("<h3 style='margin-top: 10px; font-weight: 800;'>Welcome Back 👋</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #9AA8D1; font-size: 0.88rem; margin-bottom: 20px;'>Enter your credentials to access your financial dashboard</p>", unsafe_allow_html=True)

            show_login_pw = st.checkbox("👁️ Show Password", key="show_login_pw")
            with st.form("login_form"):
                username_input = st.text_input("Username or Email Address", placeholder="name@example.com or username")
                password_input = st.text_input(
                    "Password",
                    type="default" if show_login_pw else "password",
                    placeholder="••••••••"
                )

                c_rem, c_forgot = st.columns(2)
                with c_rem:
                    remember_me = st.checkbox("Remember me", value=True)
                with c_forgot:
                    with st.popover("Forgot Password?"):
                        st.caption("Password Reset Info")
                        st.info("For security reasons in this environment, please contact administrator or reset via database if locked out.")

                submit_login = st.form_submit_button("Log In to Dashboard 🚀", use_container_width=True, type="primary")

                if submit_login:
                    if not username_input or not password_input:
                        st.error("Please enter both username and password.")
                    else:
                        with st.spinner("Authenticating credentials..."):
                            user, msg = login_user(username_input, password_input)
                            if user:
                                st.session_state.user = user
                                st.session_state.authenticated = True
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(f"❌ {msg}")

        with tab_register:
            st.markdown("<h3 style='margin-top: 10px; font-weight: 800;'>Create Account ✨</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #9AA8D1; font-size: 0.88rem; margin-bottom: 20px;'>Get started with intelligent expense tracking and budget analytics</p>", unsafe_allow_html=True)

            show_reg_pw = st.checkbox("👁️ Show Password", key="show_reg_pw")
            with st.form("register_form"):
                reg_username = st.text_input("Username", placeholder="johndoe")
                reg_email = st.text_input("Email Address", placeholder="john@example.com")
                reg_password = st.text_input(
                    "Password",
                    type="default" if show_reg_pw else "password",
                    placeholder="At least 6 characters"
                )
                reg_confirm = st.text_input(
                    "Confirm Password",
                    type="default" if show_reg_pw else "password",
                    placeholder="Re-enter password"
                )
                reg_currency = st.selectbox("Preferred Currency", ["USD", "EUR", "GBP", "INR", "JPY", "CAD", "AUD"])

                submit_reg = st.form_submit_button("Create My Free Account 🚀", use_container_width=True, type="primary")

                if submit_reg:
                    if not reg_username or not reg_email or not reg_password:
                        st.error("⚠️ All fields are required to register.")
                    elif reg_password != reg_confirm:
                        st.error("⚠️ Passwords do not match. Please verify your entries.")
                    elif len(reg_password) < 6:
                        st.error("⚠️ Password must be at least 6 characters long.")
                    else:
                        with st.spinner("Creating your workspace..."):
                            success, msg = register_user(reg_username, reg_email, reg_password, reg_currency)
                            if success:
                                st.success(f"✅ {msg}")
                            else:
                                st.error(f"❌ {msg}")

        with tab_demo:
            st.markdown("<h3 style='margin-top: 10px; font-weight: 800;'>Instant Demo Access ⚡</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #9AA8D1; font-size: 0.88rem; margin-bottom: 20px;'>Experience the full platform immediately with pre-loaded 6-month transaction data!</p>", unsafe_allow_html=True)
            st.info("ℹ️ Demo mode populates realistic income, expenses, category budgets, and recurring subscriptions.")

            if st.button("🚀 Launch Instant Demo Account", use_container_width=True, type="primary"):
                with st.spinner("Initializing demo environment..."):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM users WHERE username = 'demouser'")
                    demo_user = cursor.fetchone()
                    if not demo_user:
                        pw_hash, salt = hash_password("demo1234")
                        cursor.execute("""
                            INSERT INTO users (username, email, password_hash, salt, currency)
                            VALUES ('demouser', 'demo@expensetracker.app', ?, ?, 'INR')
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
                    st.success("✅ Demo environment loaded!")
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

def logout_user():
    """Logout current user and clear session state."""
    st.session_state.user = None
    st.session_state.authenticated = False
    st.rerun()
