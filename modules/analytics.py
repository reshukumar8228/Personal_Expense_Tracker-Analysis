import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from database.db import get_connection
from utils.helpers import format_currency
from utils.css import get_plotly_layout

def render_analytics(user: dict):
    """Render Advanced Financial Analytics & Interactive Visualizations page."""
    currency = user.get("currency", "USD")
    user_theme = user.get("theme", "Dark Fintech")
    user_id = user["id"]

    st.markdown("## 📈 Analytics & Financial Intelligence")
    st.markdown("<p class='page-subtitle'>Multi-dimensional interactive charts, spending heatmaps, treemaps, and outlier detection</p>", unsafe_allow_html=True)

    conn = get_connection()
    tx_df = pd.read_sql_query("""
        SELECT * FROM transactions WHERE user_id = ? ORDER BY date ASC
    """, conn, params=(user_id,))
    conn.close()

    if tx_df.empty:
        st.warning("No transaction data available. Please add transactions or load demo data to view analytics.")
        return

    tx_df["date"] = pd.to_datetime(tx_df["date"])
    tx_df["year_month"] = tx_df["date"].dt.strftime("%Y-%m")
    tx_df["day_name"] = tx_df["date"].dt.day_name()
    tx_df["day_of_week"] = tx_df["date"].dt.dayofweek
    tx_df["week_of_month"] = tx_df["date"].apply(lambda d: (d.day - 1) // 7 + 1)

    # Date range selector filter
    col1, col2 = st.columns(2)
    with col1:
        min_date = tx_df["date"].min().date()
        max_date = tx_df["date"].max().date()
        date_range = st.date_input("Filter Date Range", value=(min_date, max_date))

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_d, end_d = date_range
        filtered_df = tx_df[(tx_df["date"].dt.date >= start_d) & (tx_df["date"].dt.date <= end_d)].copy()
    else:
        filtered_df = tx_df.copy()

    tab_overview, tab_distribution, tab_treemap, tab_heatmap = st.tabs([
        "📊 Monthly & Trend Analysis",
        "📦 Distribution & Outliers (Box Plot & Hist)",
        "🌳 Category Treemap",
        "🔥 Spending Heatmap"
    ])

    # Tab 1: Monthly Trends & Cumulative Balance Line Chart
    with tab_overview:
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("🗓️ Monthly Income vs Expenses")
            m_summary = filtered_df.groupby(["year_month", "type"])["amount"].sum().unstack(fill_value=0).reset_index()
            fig_bar = go.Figure()
            if "income" in m_summary.columns:
                fig_bar.add_trace(go.Bar(x=m_summary["year_month"], y=m_summary["income"], name="Income", marker_color="#4169E1"))
            if "expense" in m_summary.columns:
                fig_bar.add_trace(go.Bar(x=m_summary["year_month"], y=m_summary["expense"], name="Expense", marker_color="#C52DDB"))
            l_bar = get_plotly_layout(user_theme)
            l_bar.update(barmode="group", height=350)
            fig_bar.update_layout(l_bar)
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            st.subheader("📈 Cumulative Cash Flow Trajectory")
            cum_df = filtered_df.sort_values("date").copy()
            cum_df["signed_amount"] = cum_df.apply(lambda r: r["amount"] if r["type"] == "income" else -r["amount"], axis=1)
            cum_df["cumulative_balance"] = cum_df["signed_amount"].cumsum()

            fig_line = px.line(
                cum_df,
                x="date",
                y="cumulative_balance",
                title="Cumulative Net Balance Over Time",
                labels={"cumulative_balance": f"Balance ({currency})", "date": "Date"}
            )
            fig_line.update_traces(line_color="#879BFF", line_width=3)
            l_line = get_plotly_layout(user_theme)
            l_line.update(height=350)
            fig_line.update_layout(l_line)
            st.plotly_chart(fig_line, use_container_width=True)

    # Tab 2: Histograms & Box Plots for Outlier Detection
    with tab_distribution:
        exp_df = filtered_df[filtered_df["type"] == "expense"]
        if not exp_df.empty:
            d1, d2 = st.columns(2)
            theme_palette = ["#4169E1", "#879BFF", "#C52DDB", "#8B3DCE", "#38BDF8", "#F59E0B", "#E052F2"]

            with d1:
                st.subheader("📊 Expense Transaction Size Histogram")
                fig_hist = px.histogram(
                    exp_df,
                    x="amount",
                    nbins=20,
                    color="category",
                    color_discrete_sequence=theme_palette,
                    title="Transaction Size Distribution",
                    labels={"amount": f"Transaction Amount ({currency})"}
                )
                l_hist = get_plotly_layout(user_theme)
                l_hist.update(height=350)
                fig_hist.update_layout(l_hist)
                st.plotly_chart(fig_hist, use_container_width=True)

            with d2:
                st.subheader("📦 Category Spending Box Plot (Outliers)")
                fig_box = px.box(
                    exp_df,
                    x="category",
                    y="amount",
                    color="category",
                    color_discrete_sequence=theme_palette,
                    title="Outlier Purchase Detection per Category",
                    labels={"amount": f"Amount ({currency})"}
                )
                l_box = get_plotly_layout(user_theme)
                l_box.update(height=350, showlegend=False)
                fig_box.update_layout(l_box)
                st.plotly_chart(fig_box, use_container_width=True)

    # Tab 3: Hierarchical Category Treemap
    with tab_treemap:
        st.subheader("🌳 Category Expenditure Treemap")
        exp_df = filtered_df[filtered_df["type"] == "expense"]
        if not exp_df.empty:
            fig_tree = px.treemap(
                exp_df,
                path=["type", "category", "payment_method"],
                values="amount",
                color="amount",
                color_continuous_scale="Purples",
                title="Hierarchical Breakdown of Expenses"
            )
            l_tree = get_plotly_layout(user_theme)
            l_tree.update(height=450)
            fig_tree.update_layout(l_tree)
            st.plotly_chart(fig_tree, use_container_width=True)

    # Tab 4: Spending Heatmap (Day of Week vs Week of Month)
    with tab_heatmap:
        st.subheader("🔥 Day of Week Spending Heatmap")
        exp_df = filtered_df[filtered_df["type"] == "expense"]
        if not exp_df.empty:
            days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            heatmap_data = exp_df.pivot_table(
                index="day_name",
                columns="week_of_month",
                values="amount",
                aggfunc="sum",
                fill_value=0
            ).reindex(days_order)

            fig_heat = px.imshow(
                heatmap_data,
                labels=dict(x="Week of Month", y="Day of Week", color=f"Spend ({currency})"),
                x=[f"Week {w}" for w in heatmap_data.columns],
                y=heatmap_data.index,
                color_continuous_scale="Magma",
                aspect="auto"
            )
            l_heat = get_plotly_layout(user_theme)
            l_heat.update(height=400)
            fig_heat.update_layout(l_heat)
            st.plotly_chart(fig_heat, use_container_width=True)
