import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="SmartSpend — Personal Finance & Expense Intelligence",
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
        inject_custom_css("Dark Fintech")
        render_auth_page()
        return

    # User context
    user = st.session_state.user
    user_theme = user.get("theme", "Dark Fintech")

    # 4. Inject Dynamic CSS
    inject_custom_css(user_theme)

    # 5. Sidebar Navigation
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 10px 0;">
            <h2 style="margin: 0; background: linear-gradient(135deg, #0ea5e9, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;">SmartSpend</h2>
            <p style="font-size: 0.75rem; color: #8b949e; margin-top: 2px;">Expense Intelligence Platform</p>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);">
            <div style="font-size: 0.85rem; font-weight: 700; color: #f0f6fc;">👤 {user.get('username', 'User')}</div>
            <div style="font-size: 0.75rem; color: #8b949e;">Currency: <b>{user.get('currency', 'USD')}</b></div>
        </div>
    """, unsafe_allow_html=True)

    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Executive Dashboard",
            "💳 Transactions Hub",
            "🎯 Budget Management",
            "📈 Advanced Analytics",
            "🤖 ML Expense Forecast",
            "🧠 Smart Insights",
            "🎯 Savings Goals",
            "📥 Import & Export Hub",
            "⚙️ Settings"
        ],
        index=0
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        logout_user()

    # 6. Page Router
    if page == "📊 Executive Dashboard":
        render_dashboard(user)
    elif page == "💳 Transactions Hub":
        render_transactions(user)
    elif page == "🎯 Budget Management":
        render_budgets(user)
    elif page == "📈 Advanced Analytics":
        render_analytics(user)
    elif page == "🤖 ML Expense Forecast":
        render_ml_engine(user)
    elif page == "🧠 Smart Insights":
        render_insights(user)
    elif page == "🎯 Savings Goals":
        render_savings(user)
    elif page == "📥 Import & Export Hub":
        render_import_export(user)
    elif page == "⚙️ Settings":
        render_settings(user)

if __name__ == "__main__":
    main()
