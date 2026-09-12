import streamlit as st
import hashlib
import os
import secrets
from database.db import get_connection, seed_default_categories, seed_demo_data

from utils.css import inject_auth_css

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
        # Prevent collision if derived username already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            username = f"{username}_{secrets.token_hex(2)}"

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
        if "UNIQUE constraint failed: users.email" in err_msg:
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
    """Render Login & Registration UI using exact HTML, CSS, and JS slider design."""
    # 1. Process query parameters for login, signup, or instant demo
    params = dict(st.query_params)
    if "auth_action" in params:
        action = params.get("auth_action")
        if action == "login":
            email = params.get("email", "").strip()
            password = params.get("password", "")
            user, msg = login_user(email, password)
            if user:
                st.session_state.user = user
                st.session_state.authenticated = True
                st.query_params.clear()
                st.rerun()
            else:
                st.session_state.auth_error = msg
                st.query_params.clear()
                st.rerun()

        elif action == "signup":
            email = params.get("email", "").strip()
            password = params.get("password", "")
            confirm = params.get("confirm", "")
            if confirm and password != confirm:
                st.session_state.auth_error = "Passwords do not match."
                st.query_params.clear()
                st.rerun()
            elif len(password) < 6:
                st.session_state.auth_error = "Password must be at least 6 characters long."
                st.query_params.clear()
                st.rerun()
            else:
                username = email.split("@")[0].strip() or "user"
                success, msg = register_user(username, email, password)
                if success:
                    user, _ = login_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.authenticated = True
                        st.query_params.clear()
                        st.rerun()
                    else:
                        st.session_state.auth_success = msg
                        st.query_params.clear()
                        st.rerun()
                else:
                    st.session_state.auth_error = msg
                    st.query_params.clear()
                    st.rerun()

        elif action == "demo":
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

            seed_demo_data(user_id)

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_dict = dict(cursor.fetchone())
            conn.close()

            st.session_state.user = user_dict
            st.session_state.authenticated = True
            st.query_params.clear()
            st.rerun()

    # Error & Success message banners
    error_html = ""
    if "auth_error" in st.session_state and st.session_state.auth_error:
        error_html = f'<div style="background: #fee2e2; border: 1px solid #ef4444; color: #b91c1c; padding: 10px 14px; border-radius: 12px; margin-bottom: 18px; font-size: 14px; text-align: center; font-weight: 500;">❌ {st.session_state.auth_error}</div>'
        del st.session_state.auth_error

    success_html = ""
    if "auth_success" in st.session_state and st.session_state.auth_success:
        success_html = f'<div style="background: #dcfce7; border: 1px solid #22c55e; color: #15803d; padding: 10px 14px; border-radius: 12px; margin-bottom: 18px; font-size: 14px; text-align: center; font-weight: 500;">✅ {st.session_state.auth_success}</div>'
        del st.session_state.auth_success

    auth_ui_html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css?family=Poppins:400,500,600,700&display=swap');

    html, body, .stApp {{
      background: -webkit-linear-gradient(left, #003366, #004080, #0059b3, #0073e6) !important;
      background: linear-gradient(to right, #003366, #004080, #0059b3, #0073e6) !important;
      font-family: 'Poppins', sans-serif !important;
      min-height: 100vh;
      margin: 0;
      padding: 0;
    }}

    #MainMenu {{ display: none !important; }}
    header[data-testid="stHeader"] {{ display: none !important; }}
    footer {{ display: none !important; }}
    [data-testid="stToolbar"] {{ display: none !important; }}
    [data-testid="stSidebar"] {{ display: none !important; }}

    .main .block-container {{
      max-width: 440px !important;
      padding-top: 45px !important;
      padding-bottom: 45px !important;
      margin: 0 auto !important;
    }}

    ::selection {{
      background: #1a75ff;
      color: #fff;
    }}

    .wrapper {{
      overflow: hidden;
      max-width: 390px;
      background: #fff;
      padding: 30px;
      border-radius: 15px;
      box-shadow: 0px 15px 25px rgba(0,0,0,0.2);
      margin: 0 auto;
    }}

    .wrapper .title-text {{
      display: flex;
      width: 200%;
    }}

    .wrapper .title {{
      width: 50%;
      font-size: 35px;
      font-weight: 600;
      text-align: center;
      color: #000;
      transition: all 0.6s cubic-bezier(0.68,-0.55,0.265,1.55);
    }}

    .wrapper .slide-controls {{
      position: relative;
      display: flex;
      height: 50px;
      width: 100%;
      overflow: hidden;
      margin: 30px 0 10px 0;
      justify-content: space-between;
      border: 1px solid lightgrey;
      border-radius: 15px;
    }}

    .slide-controls .slide {{
      height: 100%;
      width: 100%;
      color: #fff;
      font-size: 18px;
      font-weight: 500;
      text-align: center;
      line-height: 48px;
      cursor: pointer;
      z-index: 1;
      transition: all 0.6s ease;
    }}

    .slide-controls label.signup {{
      color: #000;
    }}

    .slide-controls .slider-tab {{
      position: absolute;
      height: 100%;
      width: 50%;
      left: 0;
      z-index: 0;
      border-radius: 15px;
      background: -webkit-linear-gradient(left,#003366,#004080,#0059b3, #0073e6);
      background: linear-gradient(to right,#003366,#004080,#0059b3, #0073e6);
      transition: all 0.6s cubic-bezier(0.68,-0.55,0.265,1.55);
    }}

    input[type="radio"] {{
      display: none;
    }}

    #signup:checked ~ .slider-tab {{
      left: 50%;
    }}

    #signup:checked ~ label.signup {{
      color: #fff;
      cursor: default;
      user-select: none;
    }}

    #signup:checked ~ label.login {{
      color: #000;
      cursor: pointer;
    }}

    #login:checked ~ label.signup {{
      color: #000;
      cursor: pointer;
    }}

    #login:checked ~ label.login {{
      cursor: default;
      user-select: none;
    }}

    .wrapper .form-container {{
      width: 100%;
      overflow: hidden;
    }}

    .form-container .form-inner {{
      display: flex;
      width: 200%;
    }}

    .form-container .form-inner form {{
      width: 50%;
      transition: all 0.6s cubic-bezier(0.68,-0.55,0.265,1.55);
    }}

    .form-inner form .field {{
      height: 50px;
      width: 100%;
      margin-top: 20px;
    }}

    .form-inner form .field input {{
      height: 100%;
      width: 100%;
      outline: none;
      padding-left: 15px;
      border-radius: 15px;
      border: 1px solid lightgrey;
      border-bottom-width: 2px;
      font-size: 17px;
      transition: all 0.3s ease;
      background: #fff;
      color: #000;
      box-sizing: border-box;
    }}

    .form-inner form .field input:focus {{
      border-color: #1a75ff;
    }}

    .form-inner form .field input::placeholder {{
      color: #999;
      transition: all 0.3s ease;
    }}

    form .field input:focus::placeholder {{
      color: #1a75ff;
    }}

    .form-inner form .pass-link {{
      margin-top: 8px;
    }}

    .form-inner form .signup-link {{
      text-align: center;
      margin-top: 28px;
      font-size: 15px;
      color: #333;
    }}

    .form-inner form .pass-link a,
    .form-inner form .signup-link a {{
      color: #1a75ff;
      text-decoration: none;
      cursor: pointer;
    }}

    .form-inner form .pass-link a:hover,
    .form-inner form .signup-link a:hover {{
      text-decoration: underline;
    }}

    form .btn {{
      height: 50px;
      width: 100%;
      border-radius: 15px;
      position: relative;
      overflow: hidden;
      margin-top: 22px;
    }}

    form .btn .btn-layer {{
      height: 100%;
      width: 300%;
      position: absolute;
      left: -100%;
      background: -webkit-linear-gradient(right,#003366,#004080,#0059b3, #0073e6);
      background: linear-gradient(to right,#003366,#004080,#0059b3, #0073e6);
      border-radius: 15px;
      transition: all 0.4s ease;
    }}

    form .btn:hover .btn-layer {{
      left: 0;
    }}

    form .btn input[type="submit"] {{
      height: 100%;
      width: 100%;
      z-index: 1;
      position: relative;
      background: none;
      border: none;
      color: #fff;
      padding-left: 0;
      border-radius: 15px;
      font-size: 20px;
      font-weight: 500;
      cursor: pointer;
    }}

    .demo-btn-wrapper {{
      text-align: center;
      margin-top: 20px;
    }}

    .demo-link-btn {{
      display: inline-block;
      padding: 9px 22px;
      background: rgba(255, 255, 255, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.35);
      border-radius: 12px;
      color: #ffffff !important;
      text-decoration: none !important;
      font-size: 14px;
      font-weight: 500;
      backdrop-filter: blur(8px);
      transition: all 0.25s ease;
      cursor: pointer;
    }}

    .demo-link-btn:hover {{
      background: rgba(255, 255, 255, 0.28);
      border-color: #ffffff;
    }}
    </style>

    <div class="wrapper">
      {error_html}
      {success_html}
      <div class="title-text">
        <div class="title login">Login Form</div>
        <div class="title signup">Signup Form</div>
      </div>
      <div class="form-container">
        <div class="slide-controls">
          <input type="radio" name="slide" id="login" checked>
          <input type="radio" name="slide" id="signup">
          <label for="login" class="slide login">Login</label>
          <label for="signup" class="slide signup">Signup</label>
          <div class="slider-tab"></div>
        </div>
        <div class="form-inner">
          <form action="" method="GET" class="login" id="loginForm">
            <input type="hidden" name="auth_action" value="login">
            <div class="field">
              <input type="text" name="email" id="loginEmail" placeholder="Email Address" required>
            </div>
            <div class="field">
              <input type="password" name="password" id="loginPass" placeholder="Password" required>
            </div>
            <div class="pass-link"><a href="#" id="forgotPassLink">Forgot password?</a></div>
            <div class="field btn">
              <div class="btn-layer"></div>
              <input type="submit" value="Login">
            </div>
            <div class="signup-link">Not a member? <a href="#" id="signupNowLink">Signup now</a></div>
          </form>
          <form action="" method="GET" class="signup" id="signupForm">
            <input type="hidden" name="auth_action" value="signup">
            <div class="field">
              <input type="text" name="email" id="signupEmail" placeholder="Email Address" required>
            </div>
            <div class="field">
              <input type="password" name="password" id="signupPass" placeholder="Password" required>
            </div>
            <div class="field">
              <input type="password" name="confirm" id="signupConfirm" placeholder="Confirm password" required>
            </div>
            <div class="field btn">
              <div class="btn-layer"></div>
              <input type="submit" value="Signup">
            </div>
          </form>
        </div>
      </div>
    </div>

    <div class="demo-btn-wrapper">
      <a href="?auth_action=demo" class="demo-link-btn">⚡ Instant Demo Access</a>
    </div>

    <script>
    (function() {{
      const loginText = document.querySelector(".title-text .login");
      const loginForm = document.querySelector("form.login");
      const loginBtn = document.querySelector("label.login");
      const signupBtn = document.querySelector("label.signup");
      const signupLink = document.querySelector("form .signup-link a");
      const forgotPass = document.getElementById("forgotPassLink");
      const signupForm = document.getElementById("signupForm");
      const loginRadio = document.getElementById("login");
      const signupRadio = document.getElementById("signup");

      if (signupBtn) {{
        signupBtn.onclick = (() => {{
          if (signupRadio) signupRadio.checked = true;
          if (loginForm) loginForm.style.marginLeft = "-50%";
          if (loginText) loginText.style.marginLeft = "-50%";
        }});
      }}
      if (loginBtn) {{
        loginBtn.onclick = (() => {{
          if (loginRadio) loginRadio.checked = true;
          if (loginForm) loginForm.style.marginLeft = "0%";
          if (loginText) loginText.style.marginLeft = "0%";
        }});
      }}
      if (signupLink) {{
        signupLink.onclick = ((e) => {{
          e.preventDefault();
          if (signupBtn) signupBtn.click();
          return false;
        }});
      }}
      if (forgotPass) {{
        forgotPass.onclick = ((e) => {{
          e.preventDefault();
          alert("Password Reset Info:\\nFor security in this local environment, please contact administrator or reset your password directly in the database.");
          return false;
        }});
      }}
      if (signupForm) {{
        signupForm.onsubmit = function(e) {{
          const p1 = document.getElementById("signupPass").value;
          const p2 = document.getElementById("signupConfirm").value;
          if (p1 !== p2) {{
            e.preventDefault();
            alert("Passwords do not match. Please verify.");
            return false;
          }}
          if (p1.length < 6) {{
            e.preventDefault();
            alert("Password must be at least 6 characters.");
            return false;
          }}
          return true;
        }};
      }}
    }})();
    </script>
    """

    st.html(auth_ui_html, unsafe_allow_javascript=True)

def logout_user():
    """Logout current user and clear session state."""
    st.session_state.user = None
    st.session_state.authenticated = False
    st.rerun()

