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

def register_user(full_name: str, email: str, password: str, currency: str = "USD") -> tuple[bool, str]:
    """Register a new user in the database with full name, email, and hashed password."""
    full_name = full_name.strip()
    email = email.strip()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Derive base username from full name or email
        base_username = full_name.lower().replace(" ", "_")
        base_username = "".join(c for c in base_username if c.isalnum() or c == "_")
        if not base_username:
            base_username = email.split("@")[0].strip() or "user"

        username = base_username
        # Prevent collision if derived username already exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            username = f"{base_username}_{secrets.token_hex(2)}"

        pw_hash, salt = hash_password(password)
        cursor.execute("""
            INSERT INTO users (username, full_name, email, password_hash, salt, currency)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, full_name, email, pw_hash, salt, currency))
        user_id = cursor.lastrowid
        conn.commit()

        # Seed default categories for new user
        seed_default_categories(user_id)
        return True, "Your account has been created successfully! Please log in to continue."
    except Exception as e:
        err_msg = str(e)
        if "UNIQUE constraint failed: users.email" in err_msg or "users_email_key" in err_msg or "unique constraint" in err_msg.lower():
            return False, "This email address is already registered. Please log in instead."
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
        return None, "Invalid email/username or password."

    user_dict = dict(user)
    if verify_password(password, user_dict["password_hash"], user_dict["salt"]):
        return user_dict, "Login successful!"
    return None, "Invalid email/username or password."

def init_session_state():
    """Initialize Streamlit session state keys if not already set."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

def render_auth_page():
    """Render Login & Registration UI with modern fintech styling, eye toggle, and structured auth flow."""
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
                st.session_state.auth_active_tab = "login"
                st.query_params.clear()
                st.rerun()

        elif action == "signup":
            name = (params.get("full_name") or params.get("name") or params.get("signup_name") or "").strip()
            email = params.get("email", "").strip()
            password = params.get("password", "")

            if not name:
                st.session_state.auth_error = "Full Name is required."
                st.session_state.auth_active_tab = "signup"
                st.query_params.clear()
                st.rerun()
            elif not email or "@" not in email or "." not in email:
                st.session_state.auth_error = "Please enter a valid email address."
                st.session_state.auth_active_tab = "signup"
                st.query_params.clear()
                st.rerun()
            elif len(password) < 6:
                st.session_state.auth_error = "Password must be at least 6 characters long."
                st.session_state.auth_active_tab = "signup"
                st.query_params.clear()
                st.rerun()
            else:
                success, msg = register_user(name, email, password)
                if success:
                    # Account created: Do NOT redirect directly to dashboard. Route to Login with success message.
                    st.session_state.auth_success = "Your account has been created successfully! Please log in to continue."
                    st.session_state.auth_active_tab = "login"
                    st.query_params.clear()
                    st.rerun()
                else:
                    st.session_state.auth_error = msg
                    st.session_state.auth_active_tab = "signup"
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
                    INSERT INTO users (username, full_name, email, password_hash, salt, currency)
                    VALUES ('demouser', 'Demo User', 'demo@expensetracker.app', ?, ?, 'USD')
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

    # Determine active tab
    active_tab = st.session_state.pop("auth_active_tab", "login")
    login_checked = "checked" if active_tab == "login" else ""
    signup_checked = "checked" if active_tab == "signup" else ""
    slider_left = "0%" if active_tab == "login" else "50%"
    login_margin_left = "0%" if active_tab == "login" else "-50%"

    # Error & Success message banners
    error_html = ""
    if "auth_error" in st.session_state and st.session_state.auth_error:
        error_html = f'<div style="background: #fee2e2; border: 1px solid #ef4444; color: #b91c1c; padding: 12px 16px; border-radius: 12px; margin-bottom: 20px; font-size: 14px; text-align: center; font-weight: 500; display: flex; align-items: center; justify-content: center; gap: 8px;"><span>❌</span> <span>{st.session_state.auth_error}</span></div>'
        del st.session_state.auth_error

    success_html = ""
    if "auth_success" in st.session_state and st.session_state.auth_success:
        success_html = f'<div style="background: #dcfce7; border: 1px solid #22c55e; color: #15803d; padding: 12px 16px; border-radius: 12px; margin-bottom: 20px; font-size: 14px; text-align: center; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 4px 12px rgba(34, 197, 94, 0.15);"><span>✅</span> <span>{st.session_state.auth_success}</span></div>'
        del st.session_state.auth_success

    auth_ui_html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');

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
      max-width: 400px;
      background: #ffffff;
      padding: 32px 28px;
      border-radius: 18px;
      box-shadow: 0px 20px 35px rgba(0, 0, 0, 0.25);
      margin: 0 auto;
    }}

    .wrapper .title-text {{
      display: flex;
      width: 200%;
    }}

    .wrapper .title-text .title {{
      width: 50%;
      font-size: 28px;
      font-weight: 700;
      text-align: center;
      color: #0f172a;
      transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }}

    .wrapper .title-text .title.login {{
      margin-left: {login_margin_left};
    }}

    .wrapper .slide-controls {{
      position: relative;
      display: flex;
      height: 48px;
      width: 100%;
      overflow: hidden;
      margin: 24px 0 10px 0;
      justify-content: space-between;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      background: #f8fafc;
    }}

    .slide-controls .slide {{
      height: 100%;
      width: 100%;
      font-size: 16px;
      font-weight: 600;
      text-align: center;
      line-height: 46px;
      cursor: pointer;
      z-index: 1;
      transition: all 0.4s ease;
      user-select: none;
    }}

    .slide-controls label.login {{
      color: {'#ffffff' if active_tab == 'login' else '#475569'};
    }}

    .slide-controls label.signup {{
      color: {'#ffffff' if active_tab == 'signup' else '#475569'};
    }}

    .slide-controls .slider-tab {{
      position: absolute;
      height: 100%;
      width: 50%;
      left: {slider_left};
      z-index: 0;
      border-radius: 12px;
      background: -webkit-linear-gradient(left, #003366, #004080, #0059b3, #0073e6);
      background: linear-gradient(to right, #003366, #004080, #0059b3, #0073e6);
      transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
      box-shadow: 0 4px 12px rgba(0, 64, 128, 0.3);
    }}

    input[type="radio"] {{
      display: none;
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
      transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }}

    .form-container .form-inner form.login {{
      margin-left: {login_margin_left};
    }}

    .form-inner form .field {{
      height: 48px;
      width: 100%;
      margin-top: 16px;
      position: relative;
    }}

    .form-inner form .field input {{
      height: 100%;
      width: 100%;
      outline: none;
      padding-left: 16px;
      padding-right: 16px;
      border-radius: 12px;
      border: 1.5px solid #e2e8f0;
      font-size: 15px;
      transition: all 0.25s ease;
      background: #f8fafc;
      color: #0f172a;
      box-sizing: border-box;
      font-family: inherit;
    }}

    .form-inner form .field.password-field input {{
      padding-right: 48px !important;
    }}

    .form-inner form .field input:focus {{
      border-color: #0059b3;
      background: #ffffff;
      box-shadow: 0 0 0 3px rgba(0, 89, 179, 0.15);
    }}

    .form-inner form .field input::placeholder {{
      color: #94a3b8;
      font-size: 14px;
    }}

    .toggle-password-btn {{
      position: absolute;
      right: 10px;
      top: 50%;
      transform: translateY(-50%);
      background: transparent;
      border: none;
      cursor: pointer;
      padding: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #64748b;
      border-radius: 8px;
      transition: all 0.2s ease;
      outline: none;
      z-index: 5;
    }}

    .toggle-password-btn:hover {{
      color: #004080;
      background: rgba(0, 64, 128, 0.08);
    }}

    .toggle-password-btn:focus-visible {{
      outline: 2px solid #0059b3;
    }}

    .form-inner form .switch-tab-link {{
      text-align: center;
      margin-top: 22px;
      font-size: 14px;
      color: #64748b;
    }}

    .form-inner form .switch-tab-link a {{
      color: #0059b3;
      font-weight: 600;
      text-decoration: none;
      cursor: pointer;
      transition: color 0.2s;
    }}

    .form-inner form .switch-tab-link a:hover {{
      color: #003366;
      text-decoration: underline;
    }}

    form .btn {{
      height: 48px;
      width: 100%;
      border-radius: 12px;
      position: relative;
      overflow: hidden;
      margin-top: 22px;
      box-shadow: 0 4px 14px rgba(0, 64, 128, 0.25);
    }}

    form .btn .btn-layer {{
      height: 100%;
      width: 300%;
      position: absolute;
      left: -100%;
      background: -webkit-linear-gradient(right, #003366, #004080, #0059b3, #0073e6);
      background: linear-gradient(to right, #003366, #004080, #0059b3, #0073e6);
      border-radius: 12px;
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
      color: #ffffff;
      padding-left: 0;
      border-radius: 12px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
      letter-spacing: 0.02em;
      font-family: inherit;
    }}

    .demo-btn-wrapper {{
      text-align: center;
      margin-top: 20px;
    }}

    .demo-link-btn {{
      display: inline-block;
      padding: 10px 24px;
      background: rgba(255, 255, 255, 0.15);
      border: 1px solid rgba(255, 255, 255, 0.35);
      border-radius: 12px;
      color: #ffffff !important;
      text-decoration: none !important;
      font-size: 14px;
      font-weight: 600;
      backdrop-filter: blur(10px);
      transition: all 0.25s ease;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }}

    .demo-link-btn:hover {{
      background: rgba(255, 255, 255, 0.28);
      border-color: #ffffff;
      transform: translateY(-1px);
    }}
    </style>

    <div class="wrapper">
      {error_html}
      {success_html}
      <div class="title-text">
        <div class="title login">Welcome Back</div>
        <div class="title signup">Create Account</div>
      </div>
      <div class="form-container">
        <div class="slide-controls">
          <input type="radio" name="slide" id="login" {login_checked}>
          <input type="radio" name="slide" id="signup" {signup_checked}>
          <label for="login" class="slide login">Login</label>
          <label for="signup" class="slide signup">Sign Up</label>
          <div class="slider-tab"></div>
        </div>
        <div class="form-inner">
          <!-- LOGIN FORM -->
          <form action="" method="GET" class="login" id="loginForm">
            <input type="hidden" name="auth_action" value="login">
            <div class="field">
              <input type="text" name="email" id="loginEmail" placeholder="Email Address or Username" required autocomplete="username">
            </div>
            <div class="field password-field">
              <input type="password" name="password" id="loginPass" placeholder="Password" required autocomplete="current-password">
              <button type="button" class="toggle-password-btn" id="toggleLoginPass" aria-label="Show password" title="Show password">
                <svg class="eye-open" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg class="eye-closed" style="display:none;" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              </button>
            </div>
            <div class="field btn">
              <div class="btn-layer"></div>
              <input type="submit" id="loginSubmitBtn" value="Login">
            </div>
            <div class="switch-tab-link">Don't have an account? <a href="#" id="signupNowLink">Sign up now</a></div>
          </form>

          <!-- SIGNUP FORM -->
          <form action="" method="GET" class="signup" id="signupForm">
            <input type="hidden" name="auth_action" value="signup">
            <div class="field">
              <input type="text" name="full_name" id="signupName" placeholder="Full Name" required autocomplete="name">
            </div>
            <div class="field">
              <input type="email" name="email" id="signupEmail" placeholder="Email Address" required autocomplete="email">
            </div>
            <div class="field password-field">
              <input type="password" name="password" id="signupPass" placeholder="Password (min 6 characters)" required autocomplete="new-password">
              <button type="button" class="toggle-password-btn" id="toggleSignupPass" aria-label="Show password" title="Show password">
                <svg class="eye-open" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
                <svg class="eye-closed" style="display:none;" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                  <line x1="1" y1="1" x2="23" y2="23"></line>
                </svg>
              </button>
            </div>
            <div class="field btn">
              <div class="btn-layer"></div>
              <input type="submit" id="signupSubmitBtn" value="Create Account">
            </div>
            <div class="switch-tab-link">Already have an account? <a href="#" id="loginNowLink">Log in</a></div>
          </form>
        </div>
      </div>
    </div>

    <div class="demo-btn-wrapper">
      <a href="?auth_action=demo" class="demo-link-btn">⚡ Instant Demo Access</a>
    </div>

    <script>
    (function() {{
      const loginText = document.querySelector(".title-text .title.login");
      const loginForm = document.querySelector(".form-container .form-inner form.login");
      const loginBtn = document.querySelector("label.login");
      const signupBtn = document.querySelector("label.signup");
      const signupLink = document.getElementById("signupNowLink");
      const loginLink = document.getElementById("loginNowLink");
      const signupForm = document.getElementById("signupForm");
      const loginFormEl = document.getElementById("loginForm");
      const loginRadio = document.getElementById("login");
      const signupRadio = document.getElementById("signup");
      const sliderTab = document.querySelector(".slider-tab");

      function switchToSignup() {{
        if (signupRadio) signupRadio.checked = true;
        if (loginForm) loginForm.style.marginLeft = "-50%";
        if (loginText) loginText.style.marginLeft = "-50%";
        if (sliderTab) sliderTab.style.left = "50%";
        if (loginBtn) loginBtn.style.color = "#475569";
        if (signupBtn) signupBtn.style.color = "#ffffff";
      }}

      function switchToLogin() {{
        if (loginRadio) loginRadio.checked = true;
        if (loginForm) loginForm.style.marginLeft = "0%";
        if (loginText) loginText.style.marginLeft = "0%";
        if (sliderTab) sliderTab.style.left = "0%";
        if (loginBtn) loginBtn.style.color = "#ffffff";
        if (signupBtn) signupBtn.style.color = "#475569";
      }}

      if (signupBtn) signupBtn.onclick = switchToSignup;
      if (loginBtn) loginBtn.onclick = switchToLogin;

      if (signupLink) {{
        signupLink.onclick = function(e) {{
          e.preventDefault();
          switchToSignup();
          return false;
        }};
      }}

      if (loginLink) {{
        loginLink.onclick = function(e) {{
          e.preventDefault();
          switchToLogin();
          return false;
        }};
      }}

      // Password Toggle Helper
      function setupPasswordToggle(toggleBtnId, inputId) {{
        const btn = document.getElementById(toggleBtnId);
        const input = document.getElementById(inputId);
        if (!btn || !input) return;

        btn.addEventListener('click', function(e) {{
          e.preventDefault();
          e.stopPropagation();
          const isPassword = input.type === 'password';
          input.type = isPassword ? 'text' : 'password';
          btn.setAttribute('aria-label', isPassword ? 'Hide password' : 'Show password');
          btn.setAttribute('title', isPassword ? 'Hide password' : 'Show password');

          const eyeOpen = btn.querySelector('.eye-open');
          const eyeClosed = btn.querySelector('.eye-closed');
          if (eyeOpen && eyeClosed) {{
            eyeOpen.style.display = isPassword ? 'none' : 'block';
            eyeClosed.style.display = isPassword ? 'block' : 'none';
          }}
          input.focus();
        }});
      }}

      setupPasswordToggle('toggleLoginPass', 'loginPass');
      setupPasswordToggle('toggleSignupPass', 'signupPass');

      // Form validation
      if (signupForm) {{
        signupForm.onsubmit = function(e) {{
          const nameInput = document.getElementById("signupName");
          const emailInput = document.getElementById("signupEmail");
          const passInput = document.getElementById("signupPass");

          const name = nameInput ? nameInput.value.trim() : "";
          const email = emailInput ? emailInput.value.trim() : "";
          const pass = passInput ? passInput.value : "";

          if (!name) {{
            e.preventDefault();
            alert("Please enter your Full Name.");
            if (nameInput) nameInput.focus();
            return false;
          }}
          if (!email || !email.includes("@")) {{
            e.preventDefault();
            alert("Please enter a valid email address.");
            if (emailInput) emailInput.focus();
            return false;
          }}
          if (pass.length < 6) {{
            e.preventDefault();
            alert("Password must be at least 6 characters long.");
            if (passInput) passInput.focus();
            return false;
          }}

          const submitBtn = document.getElementById("signupSubmitBtn");
          if (submitBtn) {{
            submitBtn.value = "Creating Account...";
          }}
          return true;
        }};
      }}

      if (loginFormEl) {{
        loginFormEl.onsubmit = function(e) {{
          const emailInput = document.getElementById("loginEmail");
          const passInput = document.getElementById("loginPass");

          const email = emailInput ? emailInput.value.trim() : "";
          const pass = passInput ? passInput.value : "";

          if (!email || !pass) {{
            e.preventDefault();
            alert("Please enter your email/username and password.");
            return false;
          }}
          const submitBtn = document.getElementById("loginSubmitBtn");
          if (submitBtn) {{
            submitBtn.value = "Logging in...";
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
