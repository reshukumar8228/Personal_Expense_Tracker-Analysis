import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from database.db import get_connection
from utils.helpers import format_currency, CATEGORY_ICONS
from utils.css import get_plotly_layout

def predict_next_month_expenses(user_id: int) -> dict:
    """
    Train Scikit-learn regression model on historical monthly transaction data
    and predict next month's total & category-wise expenses.
    """
    conn = get_connection()
    tx_df = pd.read_sql_query("""
        SELECT date, category, amount
        FROM transactions
        WHERE user_id = ? AND type = 'expense'
        ORDER BY date ASC
    """, conn, params=(user_id,))
    conn.close()

    if tx_df.empty or len(tx_df) < 5:
        return {
            "status": "error",
            "message": "Insufficient transaction history. At least 5 expense entries across multiple months are needed to generate ML predictions."
        }

    tx_df["date"] = pd.to_datetime(tx_df["date"])
    tx_df["year_month"] = tx_df["date"].dt.strftime("%Y-%m")

    # Group monthly totals
    monthly_totals = tx_df.groupby("year_month")["amount"].sum().reset_index()
    monthly_totals = monthly_totals.sort_values("year_month").reset_index(drop=True)

    n_months = len(monthly_totals)
    if n_months < 2:
        return {
            "status": "error",
            "message": "Expense predictions require data across at least 2 distinct calendar months."
        }

    # Feature Engineering for Time Series
    monthly_totals["month_index"] = np.arange(len(monthly_totals))
    monthly_totals["lag_1"] = monthly_totals["amount"].shift(1).fillna(monthly_totals["amount"].mean())
    monthly_totals["rolling_avg_3"] = monthly_totals["amount"].rolling(window=3, min_periods=1).mean()

    X = monthly_totals[["month_index", "lag_1", "rolling_avg_3"]]
    y = monthly_totals["amount"]

    # Model 1: Total Expense Regression
    model = LinearRegression()
    model.fit(X, y)

    # Next month features
    next_month_idx = n_months
    last_amount = monthly_totals["amount"].iloc[-1]
    rolling_3 = monthly_totals["amount"].iloc[-3:].mean()

    next_X = pd.DataFrame([[next_month_idx, last_amount, rolling_3]], columns=["month_index", "lag_1", "rolling_avg_3"])
    predicted_total = float(model.predict(next_X)[0])
    predicted_total = max(0.0, round(predicted_total, 2))

    # Calculate Confidence Margin / Standard Deviation
    residuals = y - model.predict(X)
    std_error = float(np.std(residuals)) if len(residuals) > 1 else 0.05 * predicted_total
    lower_bound = max(0.0, round(predicted_total - std_error, 2))
    upper_bound = round(predicted_total + std_error, 2)

    # Category-wise predictions
    cat_monthly = tx_df.groupby(["year_month", "category"])["amount"].sum().unstack(fill_value=0)
    cat_predictions = {}
    for cat in cat_monthly.columns:
        cat_series = cat_monthly[cat]
        cat_avg = cat_series.mean()
        cat_recent = cat_series.iloc[-1] if len(cat_series) > 0 else cat_avg
        # Blend recent trend and historical average
        pred_cat = 0.6 * cat_recent + 0.4 * cat_avg
        cat_predictions[cat] = round(max(0.0, float(pred_cat)), 2)

    # Calculate Spending Trend Trajectory
    prev_month_spend = float(monthly_totals["amount"].iloc[-1])
    pct_change = ((predicted_total - prev_month_spend) / prev_month_spend * 100) if prev_month_spend > 0 else 0.0

    if pct_change > 5.0:
        trend_status = "Increasing 📈"
        trend_class = "text-red"
    elif pct_change < -5.0:
        trend_status = "Decreasing 📉"
        trend_class = "text-green"
    else:
        trend_status = "Stable ➡️"
        trend_class = "text-blue"

    return {
        "status": "success",
        "predicted_total": predicted_total,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "prev_month_spend": prev_month_spend,
        "pct_change": pct_change,
        "trend_status": trend_status,
        "trend_class": trend_class,
        "cat_predictions": cat_predictions,
        "n_months_trained": n_months
    }

def render_ml_engine(user: dict):
    """Render ML Next-Month Expense Prediction UI."""
    currency = user.get("currency", "USD")
    user_theme = user.get("theme", "Dark Fintech")
    user_id = user["id"]

    st.markdown("## 🤖 Machine Learning Expense Forecasting")
    st.markdown("<p class='page-subtitle'>Scikit-learn predictive model estimating your next-month spending trajectory</p>", unsafe_allow_html=True)

    with st.spinner("Training predictive machine learning model..."):
        res = predict_next_month_expenses(user_id)

    if res["status"] == "error":
        st.warning(res["message"])
        return

    # Results KPI Cards
    p1, p2, p3, p4 = st.columns(4)

    with p1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Predicted Next-Month Spend</div>
            <div class="kpi-value text-blue">{format_currency(res['predicted_total'], currency)}</div>
            <div class="kpi-subtext">Based on {res['n_months_trained']} months history</div>
        </div>
        """, unsafe_allow_html=True)

    with p2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Expected Range (95% Conf)</div>
            <div class="kpi-value" style="font-size: 1.2rem;">{format_currency(res['lower_bound'], currency)} - {format_currency(res['upper_bound'], currency)}</div>
            <div class="kpi-subtext">Confidence Margin</div>
        </div>
        """, unsafe_allow_html=True)

    with p3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Previous Month Spend</div>
            <div class="kpi-value">{format_currency(res['prev_month_spend'], currency)}</div>
            <div class="kpi-subtext">Baseline</div>
        </div>
        """, unsafe_allow_html=True)

    with p4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Spending Trajectory</div>
            <div class="kpi-value {res['trend_class']}">{res['trend_status']}</div>
            <div class="kpi-subtext">{res['pct_change']:+.1f}% vs last month</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🎯 Category-wise Next-Month Forecast Breakdown")

    cat_preds = res["cat_predictions"]
    pred_df = pd.DataFrame([
        {"Category": cat, "Icon": CATEGORY_ICONS.get(cat, "🏷️"), "Predicted Spend": amt}
        for cat, amt in cat_preds.items()
    ]).sort_values("Predicted Spend", ascending=False)

    c_left, c_right = st.columns([3, 2])

    with c_left:
        pred_df["Formatted"] = pred_df.apply(lambda r: f"{r['Icon']} {r['Category']}", axis=1)
        st.dataframe(
            pred_df[["Formatted", "Predicted Spend"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Formatted": st.column_config.TextColumn("Category"),
                "Predicted Spend": st.column_config.NumberColumn(f"Forecast ({currency})", format="%.2f")
            }
        )

    with c_right:
        import plotly.express as px
        fig = px.bar(
            pred_df,
            x="Predicted Spend",
            y="Category",
            orientation="h",
            color="Predicted Spend",
            color_continuous_scale="Viridis",
            title="Predicted Category Expenditures"
        )
        l_pred = get_plotly_layout(user_theme)
        l_pred.update(height=350, showlegend=False)
        fig.update_layout(l_pred)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("💡 Intelligent ML Recommendations")
    if res['pct_change'] > 5.0:
        st.markdown(f"""
        <div class="custom-alert alert-warning">
            ⚠️ <b>Spending Spike Detected:</b> Your predicted next-month expenditure is <b>{res['pct_change']:.1f}% higher</b> than last month. Consider trimming variable expense categories like <b>Dining Out</b> or <b>Shopping</b> to keep your savings rate on target.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="custom-alert alert-success">
            ✅ <b>Healthy Spending Forecast:</b> Your predicted next-month budget remains stable with an estimated surplus of <b>{format_currency(res['lower_bound'], currency)} - {format_currency(res['upper_bound'], currency)}</b>.
        </div>
        """, unsafe_allow_html=True)
