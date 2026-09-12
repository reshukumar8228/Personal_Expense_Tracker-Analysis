import streamlit as st
from database.db import get_connection, seed_demo_data
from utils.helpers import CURRENCY_SYMBOLS

def render_settings(user: dict):
    """Render User Profile Settings & App Configuration page."""
    user_id = user["id"]

    st.markdown("## ⚙️ Account Settings & Preferences")
    st.markdown("<p class='page-subtitle'>Customize your currency, visual theme, and profile details</p>", unsafe_allow_html=True)

    tab_profile, tab_preferences, tab_danger = st.tabs(["👤 Profile Information", "🎨 Preferences & Theme", "⚠️ Data Management"])

    # Tab 1: Profile Information
    with tab_profile:
        st.subheader("Update Profile Details")
        with st.form("update_profile_form"):
            curr_username = user.get("username", "")
            curr_email = user.get("email", "")

            new_email = st.text_input("Email Address", value=curr_email)
            submit_profile = st.form_submit_button("Save Profile Changes", type="primary")

            if submit_profile:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET email = ? WHERE id = ?
                """, (new_email, user_id))
                conn.commit()
                conn.close()

                st.session_state.user["email"] = new_email
                st.success("Profile details updated successfully!")
                st.rerun()

    # Tab 2: Preferences & Theme
    with tab_preferences:
        st.subheader("Currency & Theme Preferences")
        with st.form("preferences_form"):
            curr_currency = user.get("currency", "USD")
            curr_theme = user.get("theme", "Dark Fintech")

            currency_options = list(CURRENCY_SYMBOLS.keys())
            curr_idx = currency_options.index(curr_currency) if curr_currency in currency_options else 0
            new_currency = st.selectbox("Preferred Currency", currency_options, index=curr_idx)

            theme_options = ["Dark Fintech", "Light Modern"]
            theme_idx = theme_options.index(curr_theme) if curr_theme in theme_options else 0
            new_theme = st.selectbox("Dashboard Theme", theme_options, index=theme_idx)

            submit_pref = st.form_submit_button("Save Preferences", type="primary")
            if submit_pref:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET currency = ?, theme = ? WHERE id = ?
                """, (new_currency, new_theme, user_id))
                conn.commit()
                conn.close()

                st.session_state.user["currency"] = new_currency
                st.session_state.user["theme"] = new_theme
                st.success("Preferences updated! Reloading application...")
                st.rerun()

    # Tab 3: Data Management & Reset
    with tab_danger:
        st.subheader("Data Reset & Demo Seeder")
        st.warning("Re-seeding demo data will populate your account with 6 months of realistic transaction history for testing.")

        d_col1, d_col2 = st.columns(2)
        with d_col1:
            if st.button("🚀 Reload Demo Sample Data", use_container_width=True, type="primary"):
                seed_demo_data(user_id)
                st.success("Sample transaction, budget, and goal data loaded!")
                st.rerun()

        with d_col2:
            if st.button("🗑️ Clear All My Data", use_container_width=True):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM budgets WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM savings_goals WHERE user_id = ?", (user_id,))
                conn.commit()
                conn.close()
                st.success("All your transactions and budgets have been cleared.")
                st.rerun()
