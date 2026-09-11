import streamlit as st
import pandas as pd
import datetime
from database.db import get_connection
from utils.helpers import format_currency, get_current_year_month, CATEGORY_ICONS

def render_budgets(user: dict):
    """Render Category Budget Management page."""
    currency = user.get("currency", "USD")
    user_id = user["id"]

    st.markdown("## 🎯 Budget Management & Monitoring")
    st.markdown("<p style='color: #8b949e;'>Set spending caps, track limits, and receive over-budget alerts</p>", unsafe_allow_html=True)

    b_col1, b_col2 = st.columns([2, 1])
    with b_col2:
        selected_ym = st.text_input("Selected Year-Month (YYYY-MM)", value=get_current_year_month())

    conn = get_connection()

    # Load Expense Categories (Deduplicated)
    categories_df = pd.read_sql_query("""
        SELECT DISTINCT name FROM categories WHERE user_id = ? AND type = 'expense' ORDER BY name
    """, conn, params=(user_id,))
    
    raw_cats = categories_df["name"].tolist() if not categories_df.empty else [
        "Housing & Rent", "Groceries", "Dining Out", "Transportation", "Utilities",
        "Entertainment", "Healthcare", "Shopping", "Subscriptions", "Travel", "Personal Care", "Miscellaneous"
    ]
    # Ensure strict uniqueness and order preservation
    expense_cats = list(dict.fromkeys(raw_cats))

    # Load Budgets for selected month
    budgets_df = pd.read_sql_query("""
        SELECT * FROM budgets WHERE user_id = ? AND year_month = ?
    """, conn, params=(user_id, selected_ym))
    budget_map = dict(zip(budgets_df["category"], budgets_df["monthly_limit"])) if not budgets_df.empty else {}

    # Load Actual Spend for selected month
    start_d = f"{selected_ym}-01"
    end_d = f"{selected_ym}-31"
    tx_df = pd.read_sql_query("""
        SELECT category, SUM(amount) as actual_spent
        FROM transactions
        WHERE user_id = ? AND type = 'expense' AND date >= ? AND date <= ?
        GROUP BY category
    """, conn, params=(user_id, start_d, end_d))

    actual_map = dict(zip(tx_df["category"], tx_df["actual_spent"])) if not tx_df.empty else {}

    tab_overview, tab_set = st.tabs(["📊 Budget Progress Overview", "⚙️ Configure Budget Limits"])

    with tab_overview:
        if budget_map:
            total_budget = sum(budget_map.values())
            total_actual = sum(actual_map.get(cat, 0.0) for cat in budget_map.keys())
            total_remaining = total_budget - total_actual

            # KPI Row
            k1, k2, k3 = st.columns(3)
            with k1:
                st.metric("Total Monthly Budget", format_currency(total_budget, currency))
            with k2:
                exp_color = "normal" if total_actual <= total_budget else "inverse"
                st.metric("Total Actual Spent", format_currency(total_actual, currency), delta=f"{((total_actual/total_budget)*100 if total_budget>0 else 0):.1f}% Used", delta_color=exp_color)
            with k3:
                rem_color = "normal" if total_remaining >= 0 else "inverse"
                st.metric("Remaining Budget", format_currency(total_remaining, currency), delta=f"{format_currency(total_remaining, currency)} left", delta_color=rem_color)

            st.markdown("---")
            st.subheader(f"Category Progress for {selected_ym}")

            for cat in expense_cats:
                if cat in budget_map:
                    limit = budget_map[cat]
                    spent = actual_map.get(cat, 0.0)
                    pct = (spent / limit) if limit > 0 else 0.0
                    icon = CATEGORY_ICONS.get(cat, "🏷️")

                    col_info, col_bar = st.columns([2, 3])
                    with col_info:
                        if pct >= 1.0:
                            badge = f"<span class='text-red' style='font-weight:700;'>🚨 OVER BUDGET ({pct*100:.0f}%)</span>"
                        elif pct >= 0.75:
                            badge = f"<span class='text-amber' style='font-weight:700;'>⚠️ Warning ({pct*100:.0f}%)</span>"
                        else:
                            badge = f"<span class='text-green' style='font-weight:700;'>✅ Healthy ({pct*100:.0f}%)</span>"

                        st.markdown(f"**{icon} {cat}**: Spent **{format_currency(spent, currency)}** of **{format_currency(limit, currency)}** | {badge}", unsafe_allow_html=True)

                    with col_bar:
                        st.progress(min(1.0, float(pct)))

        else:
            st.info(f"No budgets configured for {selected_ym}. Switch to the 'Configure Budget Limits' tab to set your monthly category caps.")

    with tab_set:
        st.subheader(f"Set Monthly Category Caps ({selected_ym})")
        st.markdown("Enter your max target spend limit for each expense category:")

        with st.form("set_budgets_form"):
            new_budgets = {}
            grid_cols = st.columns(2)
            for idx, cat in enumerate(expense_cats):
                col = grid_cols[idx % 2]
                icon = CATEGORY_ICONS.get(cat, "🏷️")
                existing_val = float(budget_map.get(cat, 0.0))
                with col:
                    new_budgets[cat] = st.number_input(f"{icon} {cat}", min_value=0.0, step=25.0, value=existing_val, key=f"b_in_{cat}")

            save_budgets_btn = st.form_submit_button("💾 Save Budget Limits", type="primary", use_container_width=True)
            if save_budgets_btn:
                cursor = conn.cursor()
                for cat, limit in new_budgets.items():
                    if limit > 0:
                        cursor.execute("""
                            INSERT INTO budgets (user_id, category, monthly_limit, year_month)
                            VALUES (?, ?, ?, ?)
                            ON CONFLICT(user_id, category, year_month)
                            DO UPDATE SET monthly_limit = excluded.monthly_limit
                        """, (user_id, cat, limit, selected_ym))
                    else:
                        cursor.execute("""
                            DELETE FROM budgets WHERE user_id = ? AND category = ? AND year_month = ?
                        """, (user_id, cat, selected_ym))
                conn.commit()
                st.success("Budgets saved successfully!")
                st.rerun()

    conn.close()
