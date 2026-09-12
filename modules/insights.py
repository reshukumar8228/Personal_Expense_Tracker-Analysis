import streamlit as st
import pandas as pd
import datetime
from database.db import get_connection
from utils.helpers import format_currency, CATEGORY_ICONS

def render_insights(user: dict):
    """Render Smart Insights & Financial Intelligence page."""
    currency = user.get("currency", "USD")
    user_id = user["id"]

    st.markdown("## 🧠 Smart Insights & Financial Intelligence")
    st.markdown("<p class='page-subtitle'>Data-driven recommendations, spending anomaly detection, and 50/30/20 rule breakdown</p>", unsafe_allow_html=True)

    conn = get_connection()
    tx_df = pd.read_sql_query("""
        SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC
    """, conn, params=(user_id,))
    conn.close()

    if tx_df.empty:
        st.warning("Insufficient data to generate smart insights. Add transactions or explore demo mode.")
        return

    tx_df["date"] = pd.to_datetime(tx_df["date"])
    tx_df["year_month"] = tx_df["date"].dt.strftime("%Y-%m")

    # 1. 50/30/20 Budget Breakdown Analysis
    st.subheader("⚖️ 50 / 30 / 20 Financial Rule Compliance")
    st.caption("Standard financial guideline: 50% Needs (Rent, Utilities, Groceries), 30% Wants (Dining, Shopping, Entertainment), 20% Savings.")

    # Needs categories
    needs_cats = ["Housing & Rent", "Groceries", "Utilities", "Healthcare", "Transportation"]
    wants_cats = ["Dining Out", "Entertainment", "Shopping", "Subscriptions", "Travel", "Personal Care", "Miscellaneous"]

    inc_df = tx_df[tx_df["type"] == "income"]
    exp_df = tx_df[tx_df["type"] == "expense"]

    total_inc = inc_df["amount"].sum() if not inc_df.empty else 0.0
    needs_spent = exp_df[exp_df["category"].isin(needs_cats)]["amount"].sum() if not exp_df.empty else 0.0
    wants_spent = exp_df[exp_df["category"].isin(wants_cats)]["amount"].sum() if not exp_df.empty else 0.0
    savings_accumulated = total_inc - (needs_spent + wants_spent)

    if total_inc > 0:
        needs_pct = (needs_spent / total_inc) * 100
        wants_pct = (wants_spent / total_inc) * 100
        savings_pct = (savings_accumulated / total_inc) * 100

        col_n, col_w, col_s = st.columns(3)
        with col_n:
            n_status = "✅ On Target" if needs_pct <= 55 else "⚠️ High"
            st.metric("Needs (Target: 50%)", f"{needs_pct:.1f}%", delta=f"{format_currency(needs_spent, currency)} ({n_status})")
        with col_w:
            w_status = "✅ On Target" if wants_pct <= 35 else "⚠️ High"
            st.metric("Wants (Target: 30%)", f"{wants_pct:.1f}%", delta=f"{format_currency(wants_spent, currency)} ({w_status})")
        with col_s:
            s_status = "✅ On Target" if savings_pct >= 20 else "🚨 Low"
            st.metric("Savings/Debt (Target: 20%)", f"{savings_pct:.1f}%", delta=f"{format_currency(savings_accumulated, currency)} ({s_status})")

    st.markdown("---")

    # 2. Spending Spike Anomaly Detector
    st.subheader("🔍 Category Spending Anomaly Detector")
    # Compare current month vs prior 3-month average per category
    months_list = sorted(tx_df["year_month"].unique(), reverse=True)
    if len(months_list) >= 2:
        curr_m = months_list[0]
        prev_months = months_list[1:4]

        curr_exp = tx_df[(tx_df["year_month"] == curr_m) & (tx_df["type"] == "expense")].groupby("category")["amount"].sum()
        prev_exp = tx_df[(tx_df["year_month"].isin(prev_months)) & (tx_df["type"] == "expense")].groupby("category")["amount"].mean()

        spikes = []
        for cat, curr_val in curr_exp.items():
            avg_val = prev_exp.get(cat, 0.0)
            if avg_val > 0 and curr_val > (1.25 * avg_val) and (curr_val - avg_val) >= 50.0:
                diff = curr_val - avg_val
                pct = ((curr_val - avg_val) / avg_val) * 100
                spikes.append((cat, curr_val, avg_val, diff, pct))

        if spikes:
            for cat, curr_val, avg_val, diff, pct in spikes:
                icon = CATEGORY_ICONS.get(cat, "🏷️")
                st.markdown(f"""
                <div class="custom-alert alert-warning">
                    ⚠️ <b>{icon} {cat} Spending Spike:</b> Spent <b>{format_currency(curr_val, currency)}</b> this month (+{pct:.0f}% higher than 3-month average of {format_currency(avg_val, currency)}).
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No abnormal spending spikes detected this month. Category expenditures align with historical averages.")
    else:
        st.info("At least 2 months of history are required for anomaly spike detection.")

    st.markdown("---")

    # 3. Actionable AI Recommendations List
    st.subheader("💡 Tailored Actionable Financial Advice")
    advice_list = []

    if total_inc > 0 and savings_pct < 15:
        advice_list.append("💰 <b>Boost Emergency Savings:</b> Your savings rate is under 15%. Automate a transfer of 10% of your income into your emergency fund on payday.")

    if wants_spent > (0.35 * total_inc) and total_inc > 0:
        advice_list.append("🍽️ <b>Review Dining & Shopping:</b> Wants expenditures account for over 35% of income. Try setting a weekly cash cap for discretionary eating out.")

    rec_subs = tx_df[(tx_df["is_recurring"] == 1) & (tx_df["type"] == "expense")]
    if not rec_subs.empty:
        rec_total = rec_subs["amount"].sum()
        advice_list.append(f"📱 <b>Audit Recurring Subscriptions:</b> You have active recurring subscriptions totaling <b>{format_currency(rec_total, currency)}</b> monthly. Review unused memberships.")

    if not advice_list:
        advice_list.append("🎉 <b>Outstanding Financial Health!</b> Your budget compliance, savings rate, and cash flow are in optimal alignment.")

    for adv in advice_list:
        st.markdown(f"""
        <div class="spend-card">
            {adv}
        </div>
        """, unsafe_allow_html=True)
