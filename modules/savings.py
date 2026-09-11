import streamlit as st
import pandas as pd
import datetime
from database.db import get_connection
from utils.helpers import format_currency

def render_savings(user: dict):
    """Render Savings Goals Tracker page."""
    currency = user.get("currency", "USD")
    user_id = user["id"]

    st.markdown("## 🎯 Savings Goals & Wealth Accumulation")
    st.markdown("<p style='color: #8b949e;'>Track progress towards major financial milestones and long-term targets</p>", unsafe_allow_html=True)

    conn = get_connection()
    goals_df = pd.read_sql_query("""
        SELECT * FROM savings_goals WHERE user_id = ? ORDER BY created_at DESC
    """, conn, params=(user_id,))

    tab_goals, tab_add = st.tabs(["🏆 Active Savings Goals", "➕ Create Savings Goal"])

    with tab_goals:
        if not goals_df.empty:
            for _, goal in goals_df.iterrows():
                g_id = goal["id"]
                name = goal["name"]
                target = goal["target_amount"]
                current = goal["current_amount"]
                target_date = goal["target_date"]
                status = goal["status"]
                notes = goal["notes"]

                pct = (current / target) if target > 0 else 0.0
                pct_clamped = min(1.0, max(0.0, float(pct)))

                with st.container():
                    st.markdown(f"""
                    <div class="spend-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="margin: 0; color: #38bdf8;">🎯 {name}</h3>
                            <span class="health-badge {'health-excellent' if pct >= 1.0 else 'health-good'}">{status} ({pct*100:.1f}%)</span>
                        </div>
                        <p style="color: #8b949e; margin-top: 4px; font-size: 0.9rem;">Target Date: <b>{target_date}</b> | {notes or 'No notes'}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    c_prog, c_action = st.columns([3, 1])

                    with c_prog:
                        st.progress(pct_clamped)
                        st.caption(f"Saved **{format_currency(current, currency)}** of **{format_currency(target, currency)}** | Remaining: **{format_currency(max(0.0, target - current), currency)}**")

                    with c_action:
                        with st.popover("💰 Deposit Funds"):
                            with st.form(f"deposit_form_{g_id}"):
                                add_amt = st.number_input("Deposit Amount", min_value=1.0, step=25.0, value=100.0)
                                if st.form_submit_button("Add to Goal", type="primary"):
                                    new_curr = current + add_amt
                                    new_status = "Completed" if new_curr >= target else "In Progress"
                                    cursor = conn.cursor()
                                    cursor.execute("""
                                        UPDATE savings_goals
                                        SET current_amount = ?, status = ?
                                        WHERE id = ? AND user_id = ?
                                    """, (new_curr, new_status, g_id, user_id))
                                    conn.commit()
                                    st.success(f"Added {format_currency(add_amt, currency)} to {name}!")
                                    st.rerun()

                    st.markdown("<br>", unsafe_allow_html=True)

        else:
            st.info("No savings goals active. Switch to 'Create Savings Goal' to set your first target!")

    with tab_add:
        st.subheader("➕ Create New Savings Target")
        with st.form("add_goal_form"):
            g_name = st.text_input("Goal Name", placeholder="e.g. Emergency Fund, House Downpayment, Vacation")
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                g_target = st.number_input("Target Amount", min_value=10.0, step=100.0, value=5000.0)
                g_initial = st.number_input("Initial Saved Amount", min_value=0.0, step=50.0, value=500.0)
            with g_col2:
                g_date = st.date_input("Target Date", value=datetime.date.today() + datetime.timedelta(days=180))
                g_notes = st.text_input("Notes", placeholder="e.g. 6-month safety net reserve")

            if st.form_submit_button("Create Goal", type="primary", use_container_width=True):
                if not g_name:
                    st.error("Please enter a goal name.")
                else:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO savings_goals (user_id, name, target_amount, current_amount, target_date, status, notes)
                        VALUES (?, ?, ?, ?, ?, 'In Progress', ?)
                    """, (user_id, g_name, g_target, g_initial, g_date.strftime("%Y-%m-%d"), g_notes))
                    conn.commit()
                    st.success(f"Goal '{g_name}' created successfully!")
                    st.rerun()

    conn.close()
