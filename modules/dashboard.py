import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
from database.db import get_connection
from utils.helpers import format_currency, get_current_year_month, get_user_categories
from utils.css import get_plotly_layout

def calculate_financial_health_score(income: float, expenses: float, budgets_df: pd.DataFrame, transactions_df: pd.DataFrame) -> tuple[int, str, str]:
    """Calculate Financial Health Index (0-100) and return score, status, and CSS badge class."""
    if income <= 0:
        return 50, "Fair", "health-fair"

    savings_rate = max(0.0, (income - expenses) / income)

    # 1. Savings Rate Score (max 40 pts)
    savings_score = min(40.0, (savings_rate / 0.20) * 40.0)

    # 2. Expense-to-Income Score (max 30 pts)
    exp_ratio = expenses / income
    if exp_ratio <= 0.50:
        exp_score = 30.0
    elif exp_ratio <= 0.70:
        exp_score = 25.0
    elif exp_ratio <= 0.90:
        exp_score = 15.0
    else:
        exp_score = 5.0

    # 3. Budget Adherence Score (max 30 pts)
    budget_score = 30.0
    if not budgets_df.empty and not transactions_df.empty:
        exp_tx = transactions_df[transactions_df["type"] == "expense"]
        if not exp_tx.empty:
            cat_totals = exp_tx.groupby("category")["amount"].sum().to_dict()
            over_budget_count = 0
            total_budgets = len(budgets_df)
            for _, row in budgets_df.iterrows():
                cat = row["category"]
                limit = row["monthly_limit"]
                spent = cat_totals.get(cat, 0.0)
                if spent > limit:
                    over_budget_count += 1
            if total_budgets > 0:
                compliance_ratio = 1.0 - (over_budget_count / total_budgets)
                budget_score = compliance_ratio * 30.0

    total_score = int(round(savings_score + exp_score + budget_score))
    total_score = max(0, min(100, total_score))

    if total_score >= 85:
        return total_score, "Excellent", "health-excellent"
    elif total_score >= 70:
        return total_score, "Good", "health-good"
    elif total_score >= 50:
        return total_score, "Fair", "health-fair"
    else:
        return total_score, "Needs Work", "health-poor"

def render_dashboard(user: dict):
    """Render Personal Executive Dashboard page."""
    currency = user.get("currency", "USD")
    username = user.get("username", "User")
    user_id = user["id"]

    # Header Card
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown(f"""
        <div class="hero-card">
            <div class="hero-title">Welcome back, {username}! 👋</div>
            <div class="hero-subtitle">Personal Expense Tracker Intelligence Overview & Real-Time Analytics</div>
        </div>
        """, unsafe_allow_html=True)
    with h_col2:
        month_option = st.selectbox(
            "📅 Analysis Period",
            ["Current Month", "Last 30 Days", "Last 90 Days", "Year to Date", "All Time"],
            index=0
        )

    # Calculate date range
    today = datetime.date.today()
    if month_option == "Current Month":
        start_date = datetime.date(today.year, today.month, 1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif month_option == "Last 30 Days":
        start_date = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif month_option == "Last 90 Days":
        start_date = (today - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif month_option == "Year to Date":
        start_date = datetime.date(today.year, 1, 1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    else:
        start_date = "1970-01-01"
        end_date = "2099-12-31"

    # Query Transactions
    conn = get_connection()
    tx_df = pd.read_sql_query("""
        SELECT * FROM transactions
        WHERE user_id = ? AND date >= ? AND date <= ?
        ORDER BY date DESC
    """, conn, params=(user_id, start_date, end_date))

    # Query Budgets for current month
    ym_current = get_current_year_month()
    budgets_df = pd.read_sql_query("""
        SELECT * FROM budgets WHERE user_id = ? AND year_month = ?
    """, conn, params=(user_id, ym_current))

    conn.close()

    total_income = tx_df[tx_df["type"] == "income"]["amount"].sum() if not tx_df.empty else 0.0
    total_expenses = tx_df[tx_df["type"] == "expense"]["amount"].sum() if not tx_df.empty else 0.0
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0

    health_score, health_status, health_class = calculate_financial_health_score(total_income, total_expenses, budgets_df, tx_df)

    # Top KPI Metric Cards Grid
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        st.markdown(f"""
        <div class="kpi-card border-income">
            <div class="kpi-title">💰 Total Income</div>
            <div class="kpi-value text-green">{format_currency(total_income, currency)}</div>
            <div class="kpi-subtext">↑ Gross Inflow</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="kpi-card border-expense">
            <div class="kpi-title">💸 Total Expenses</div>
            <div class="kpi-value text-red">{format_currency(total_expenses, currency)}</div>
            <div class="kpi-subtext">↓ Total Outflow</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        net_color = "text-green" if net_savings >= 0 else "text-red"
        st.markdown(f"""
        <div class="kpi-card border-balance">
            <div class="kpi-title">⚖️ Net Balance</div>
            <div class="kpi-value {net_color}">{format_currency(net_savings, currency)}</div>
            <div class="kpi-subtext">Net Surplus</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        sr_color = "text-green" if savings_rate >= 20 else ("text-amber" if savings_rate >= 10 else "text-red")
        st.markdown(f"""
        <div class="kpi-card border-savings">
            <div class="kpi-title">📈 Savings Rate</div>
            <div class="kpi-value {sr_color}">{savings_rate:.1f}%</div>
            <div class="kpi-subtext">Target: 20%+</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi5:
        st.markdown(f"""
        <div class="kpi-card border-health">
            <div class="kpi-title">🛡️ Health Index</div>
            <div class="kpi-value">{health_score} <span style="font-size: 0.85rem; color: #64748b;">/ 100</span></div>
            <div style="margin-top: 4px;"><span class="health-badge {health_class}">{health_status}</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Budget Alert Warning Banner if over-budget categories exist
    if not budgets_df.empty and not tx_df.empty:
        exp_tx = tx_df[tx_df["type"] == "expense"]
        if not exp_tx.empty:
            cat_totals = exp_tx.groupby("category")["amount"].sum().to_dict()
            over_cats = []
            for _, b_row in budgets_df.iterrows():
                c_name = b_row["category"]
                c_limit = b_row["monthly_limit"]
                c_spent = cat_totals.get(c_name, 0.0)
                if c_spent > c_limit:
                    over_cats.append((c_name, c_spent, c_limit))

            if over_cats:
                alert_text = " &nbsp;•&nbsp; ".join([f"<b>{c}</b>: Spent {format_currency(s, currency)} (Limit: {format_currency(l, currency)})" for c, s, l in over_cats])
                st.markdown(f"""
                <div class="custom-alert alert-danger">
                    🚨 <b>Budget Warning:</b> You have exceeded your monthly limit in {len(over_cats)} category/categories:<br>{alert_text}
                </div>
                """, unsafe_allow_html=True)

    # Visuals Row: Monthly Cash Flow & Category Breakdown
    c_chart1, c_chart2 = st.columns([3, 2])

    with c_chart1:
        st.subheader("📊 Income vs Expense Monthly Trajectory")
        if not tx_df.empty:
            df_grouped = tx_df.copy()
            df_grouped["date"] = pd.to_datetime(df_grouped["date"])

            # FIX: Use 'ME' (Month End) instead of deprecated 'M' for Pandas 3.0+
            df_monthly = df_grouped.groupby([pd.Grouper(key="date", freq="ME"), "type"])["amount"].sum().unstack(fill_value=0).reset_index()
            df_monthly["month_label"] = df_monthly["date"].dt.strftime("%b %Y")

            fig = go.Figure()
            if "income" in df_monthly.columns:
                fig.add_trace(go.Bar(
                    x=df_monthly["month_label"],
                    y=df_monthly["income"],
                    name="Income",
                    marker=dict(
                        color="#4169E1",
                        line=dict(color="#879BFF", width=1)
                    )
                ))
            if "expense" in df_monthly.columns:
                fig.add_trace(go.Bar(
                    x=df_monthly["month_label"],
                    y=df_monthly["expense"],
                    name="Expense",
                    marker=dict(
                        color="#C52DDB",
                        line=dict(color="#E052F2", width=1)
                    )
                ))

            user_theme = user.get("theme", "Dark Fintech")
            bar_layout = get_plotly_layout(user_theme)
            bar_layout.update(
                barmode="group",
                bargap=0.25,
                bargroupgap=0.1,
                margin=dict(l=20, r=20, t=20, b=20),
                height=340,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig.update_layout(bar_layout)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No transaction data available for the selected period.")

    with c_chart2:
        st.subheader("🍕 Spending Distribution")
        exp_df = tx_df[tx_df["type"] == "expense"] if not tx_df.empty else pd.DataFrame()
        if not exp_df.empty:
            cat_sum = exp_df.groupby("category")["amount"].sum().reset_index()
            colors_palette = ["#4169E1", "#879BFF", "#C52DDB", "#8B3DCE", "#38BDF8", "#F59E0B", "#E052F2", "#6C7BAE"]

            fig_pie = go.Figure(data=[go.Pie(
                labels=cat_sum["category"],
                values=cat_sum["amount"],
                hole=0.5,
                marker=dict(colors=colors_palette),
                textinfo="label+percent",
                insidetextorientation="radial"
            )])
            pie_layout = get_plotly_layout(user_theme)
            pie_layout.update(
                margin=dict(l=10, r=10, t=10, b=10),
                height=340,
                showlegend=False
            )
            fig_pie.update_layout(pie_layout)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense records found.")

    st.markdown("---")

    # Bottom Row: Recent Transactions Table & Quick Add Form
    r_col1, r_col2 = st.columns([3, 2])

    with r_col1:
        st.subheader("🕒 Recent Audit Log")
        if not tx_df.empty:
            display_df = tx_df[["date", "type", "category", "amount", "payment_method", "notes"]].head(8).copy()
            display_df["amount"] = display_df.apply(
                lambda r: f"+{format_currency(r['amount'], currency)}" if r['type'] == 'income' else f"-{format_currency(r['amount'], currency)}",
                axis=1
            )
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No recent entries.")

    with r_col2:
        st.subheader("⚡ Quick Entry")
        q_type = st.radio("Transaction Type", ["income", "expense"], horizontal=True, key="dash_q_type")
        q_categories = get_user_categories(user_id, q_type)

        q_category = st.selectbox("Category", q_categories, key=f"dash_q_cat_{q_type}")
        q_custom_cat = ""
        if q_category == "Other":
            q_custom_cat = st.text_input("Enter Custom Category Name", placeholder="e.g. Pet Care, Side Hustle", key=f"dash_q_custom_cat_{q_type}")

        with st.form("quick_add_form"):
            q_amount = st.number_input("Amount", min_value=0.01, step=1.0, value=30.0)
            q_date = st.date_input("Date", value=datetime.date.today())
            q_method = st.selectbox("Payment Method", ["Credit Card", "Debit Card", "Bank Transfer", "UPI", "Cash", "PayPal"])
            q_notes = st.text_input("Notes", placeholder="e.g. Lunch with team")

            q_submit = st.form_submit_button("Save Transaction", use_container_width=True, type="primary")
            if q_submit:
                final_cat = q_category
                if q_category == "Other":
                    if not q_custom_cat.strip():
                        st.error("Please enter a custom category name.")
                        st.stop()
                    final_cat = q_custom_cat.strip()
                    # Save custom category for future reuse
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR IGNORE INTO categories (user_id, name, type, icon, color)
                        VALUES (?, ?, ?, '🏷️', '#38bdf8')
                    """, (user_id, final_cat, q_type))
                    conn.commit()
                    conn.close()

                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, q_date.strftime("%Y-%m-%d"), q_type, final_cat, q_amount, q_method, q_notes))
                conn.commit()
                conn.close()
                st.success(f"Transaction recorded under '{final_cat}'!")
                st.rerun()
