import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Personal Expense Tracker — Finance & Intelligence",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

from database.db import init_db
from utils.css import inject_custom_css
from modules.auth import init_session_state, render_auth_page, logout_user
from modules.dashboard import render_dashboard
from modules.transactions import render_transactions
from modules.budgets import render_budgets
from modules.analytics import render_analytics
from modules.ml_engine import render_ml_engine
from modules.savings import render_savings
from modules.insights import render_insights
from modules.import_export import render_import_export
from modules.settings import render_settings

def main():
    # 1. Initialize DB tables
    init_db()

    # 2. Initialize Auth Session State
    init_session_state()

    # 3. Check Authentication
    if not st.session_state.authenticated or not st.session_state.user:
        render_auth_page()
        return

    # User context
    user = st.session_state.user
    user_theme = user.get("theme", "Dark Fintech")

    # 4. Inject Dynamic CSS
    inject_custom_css(user_theme)

    # 5. Sidebar Navigation
    st.sidebar.markdown("""
        <div style="padding: 12px 6px 16px 6px; border-bottom: 1px solid rgba(135, 155, 255, 0.15); margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 36px; height: 36px; background: linear-gradient(135deg, #4169E1, #C52DDB); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; box-shadow: 0 4px 12px rgba(65, 105, 225, 0.35);">
                    📉
                </div>
                <div>
                    <div style="font-weight: 800; font-size: 0.98rem; letter-spacing: 0.05em; background: linear-gradient(135deg, #FFFFFF 0%, #879BFF 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">PERSONAL FINANCE</div>
                    <div style="font-size: 0.72rem; color: #6C7BAE; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;">Expense Intelligence</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"""
        <div class="sidebar-user-card">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, #879BFF, #4169E1); display: flex; align-items: center; justify-content: center; font-size: 0.9rem; font-weight: 700; color: #fff;">
                    {user.get('username', 'U')[0].upper()}
                </div>
                <div>
                    <div class="sidebar-user-name">{user.get('username', 'User')}</div>
                    <div class="sidebar-user-sub">Currency: <span style="color: #38BDF8; font-weight: 700;">{user.get('currency', 'USD')}</span></div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "💳 Transactions",
            "🎯 Budgets",
            "📈 Analytics",
            "🤖 Forecast",
            "🧠 Insights",
            "🎯 Savings Goals",
            "📥 Import & Export",
            "⚙️ Settings"
        ],
        index=0
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        logout_user()

    # 6. Page Router
    if page == "📊 Dashboard":
        render_dashboard(user)
    elif page == "💳 Transactions":
        render_transactions(user)
    elif page == "🎯 Budgets":
        render_budgets(user)
    elif page == "📈 Analytics":
        render_analytics(user)
    elif page == "🤖 Forecast":
        render_ml_engine(user)
    elif page == "🧠 Insights":
        render_insights(user)
    elif page == "🎯 Savings Goals":
        render_savings(user)
    elif page == "📥 Import & Export":
        render_import_export(user)
    elif page == "⚙️ Settings":
        render_settings(user)

if __name__ == "__main__":
    main()
