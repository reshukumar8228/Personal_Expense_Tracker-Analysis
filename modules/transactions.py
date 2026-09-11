import streamlit as st
import pandas as pd
import datetime
from database.db import get_connection
from utils.helpers import format_currency, CATEGORY_ICONS, get_user_categories

def render_transactions(user: dict):
    """Render Transactions Management page."""
    currency = user.get("currency", "USD")
    user_id = user["id"]

    st.markdown("## 💳 Transactions Hub")
    st.markdown("<p style='color: #8b949e;'>Add, manage, search, and audit all your financial records</p>", unsafe_allow_html=True)

    tab_view, tab_add, tab_recurring = st.tabs(["📋 View & Filter", "➕ Add Transaction", "🔁 Recurring Expenses"])

    conn = get_connection()

    # Tab 1: View & Filter Transactions
    with tab_view:
        with st.expander("🔍 Search & Multi-Criteria Filters", expanded=True):
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            with f_col1:
                filter_type = st.selectbox("Transaction Type", ["All", "income", "expense"], key="tx_filter_type")
            with f_col2:
                if filter_type == "income":
                    cat_options = ["All"] + get_user_categories(user_id, "income")
                elif filter_type == "expense":
                    cat_options = ["All"] + get_user_categories(user_id, "expense")
                else:
                    inc_c = get_user_categories(user_id, "income")
                    exp_c = get_user_categories(user_id, "expense")
                    cat_options = ["All"] + list(dict.fromkeys(inc_c + exp_c))
                
                filter_cat = st.selectbox("Category", cat_options, key=f"tx_filter_cat_{filter_type}")
            with f_col3:
                filter_method = st.selectbox("Payment Method", ["All", "Credit Card", "Debit Card", "Bank Transfer", "UPI", "Cash", "PayPal"])
            with f_col4:
                search_query = st.text_input("Search Notes", placeholder="e.g. Starbucks")

            d_col1, d_col2 = st.columns(2)
            with d_col1:
                start_d = st.date_input("From Date", value=datetime.date(datetime.date.today().year, 1, 1))
            with d_col2:
                end_d = st.date_input("To Date", value=datetime.date.today())

        # Construct dynamic SQL query
        query = "SELECT * FROM transactions WHERE user_id = ? AND date >= ? AND date <= ?"
        params = [user_id, start_d.strftime("%Y-%m-%d"), end_d.strftime("%Y-%m-%d")]

        if filter_type != "All":
            query += " AND type = ?"
            params.append(filter_type)
        if filter_cat != "All":
            query += " AND category = ?"
            params.append(filter_cat)
        if filter_method != "All":
            query += " AND payment_method = ?"
            params.append(filter_method)
        if search_query:
            query += " AND notes LIKE ?"
            params.append(f"%{search_query}%")

        query += " ORDER BY date DESC, id DESC"

        tx_df = pd.read_sql_query(query, conn, params=params)

        if not tx_df.empty:
            # Stats Summary Bar
            total_inc = tx_df[tx_df["type"] == "income"]["amount"].sum()
            total_exp = tx_df[tx_df["type"] == "expense"]["amount"].sum()
            st.info(f"Showing **{len(tx_df)}** transactions | Total Income: **{format_currency(total_inc, currency)}** | Total Expenses: **{format_currency(total_exp, currency)}** | Net: **{format_currency(total_inc - total_exp, currency)}**")

            # Table view
            display_df = tx_df.copy()
            display_df["icon"] = display_df["category"].apply(lambda c: CATEGORY_ICONS.get(c, "🏷️"))
            display_df["Formatted Category"] = display_df["icon"] + " " + display_df["category"]
            display_df["Formatted Amount"] = display_df.apply(
                lambda r: f"+{format_currency(r['amount'], currency)}" if r['type'] == 'income' else f"-{format_currency(r['amount'], currency)}",
                axis=1
            )

            cols_to_show = ["id", "date", "type", "Formatted Category", "Formatted Amount", "payment_method", "notes", "is_recurring"]
            st.dataframe(
                display_df[cols_to_show],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": st.column_config.NumberColumn("ID", width="small"),
                    "date": st.column_config.TextColumn("Date"),
                    "type": st.column_config.TextColumn("Type"),
                    "Formatted Category": st.column_config.TextColumn("Category"),
                    "Formatted Amount": st.column_config.TextColumn("Amount"),
                    "payment_method": st.column_config.TextColumn("Payment Method"),
                    "notes": st.column_config.TextColumn("Notes"),
                    "is_recurring": st.column_config.CheckboxColumn("Recurring?")
                }
            )

            # Action Bar: Edit or Delete Transaction
            st.markdown("#### 🛠️ Manage Selected Transaction")
            e_col1, e_col2 = st.columns([1, 2])
            with e_col1:
                selected_id = st.number_input("Enter Transaction ID to Modify/Delete", min_value=1, step=1, value=int(tx_df.iloc[0]["id"]))

            target_tx = tx_df[tx_df["id"] == selected_id]
            if not target_tx.empty:
                tx_row = target_tx.iloc[0]
                with e_col2:
                    act_col1, act_col2 = st.columns(2)
                    with act_col2:
                        if st.button("🗑️ Delete Transaction", type="primary", use_container_width=True):
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (selected_id, user_id))
                            conn.commit()
                            st.success(f"Transaction #{selected_id} deleted!")
                            st.rerun()

                    with act_col1:
                        with st.popover("✏️ Edit Transaction"):
                            st.subheader(f"Edit Transaction #{selected_id}")
                            edit_type = st.radio("Type", ["income", "expense"], index=0 if tx_row["type"] == "income" else 1, horizontal=True, key=f"edit_t_{selected_id}")
                            edit_cats = get_user_categories(user_id, edit_type)

                            cat_idx = edit_cats.index(tx_row["category"]) if tx_row["category"] in edit_cats else (len(edit_cats) - 1 if "Other" in edit_cats else 0)
                            edit_cat = st.selectbox("Category", edit_cats, index=cat_idx, key=f"edit_c_{selected_id}_{edit_type}")
                            edit_custom_cat = ""
                            if edit_cat == "Other":
                                edit_custom_cat = st.text_input("Enter Custom Category Name", value=tx_row["category"] if tx_row["category"] not in edit_cats else "", key=f"edit_cust_{selected_id}_{edit_type}")

                            with st.form(f"edit_form_{selected_id}"):
                                edit_date = st.date_input("Date", value=datetime.datetime.strptime(tx_row["date"], "%Y-%m-%d").date())
                                edit_amount = st.number_input("Amount", min_value=0.01, value=float(tx_row["amount"]))
                                edit_method = st.selectbox("Payment Method", ["Credit Card", "Debit Card", "Bank Transfer", "UPI", "Cash", "PayPal"])
                                edit_notes = st.text_input("Notes", value=str(tx_row["notes"] or ""))
                                edit_rec = st.checkbox("Is Recurring?", value=bool(tx_row["is_recurring"]))

                                if st.form_submit_button("Save Changes", type="primary"):
                                    final_edit_cat = edit_cat
                                    if edit_cat == "Other":
                                        if not edit_custom_cat.strip():
                                            st.error("Please enter a custom category name.")
                                            st.stop()
                                        final_edit_cat = edit_custom_cat.strip()
                                        cursor = conn.cursor()
                                        cursor.execute("""
                                            INSERT OR IGNORE INTO categories (user_id, name, type, icon, color)
                                            VALUES (?, ?, ?, '🏷️', '#38bdf8')
                                        """, (user_id, final_edit_cat, edit_type))
                                        conn.commit()

                                    cursor = conn.cursor()
                                    cursor.execute("""
                                        UPDATE transactions
                                        SET date = ?, type = ?, category = ?, amount = ?, payment_method = ?, notes = ?, is_recurring = ?
                                        WHERE id = ? AND user_id = ?
                                    """, (edit_date.strftime("%Y-%m-%d"), edit_type, final_edit_cat, edit_amount, edit_method, edit_notes, 1 if edit_rec else 0, selected_id, user_id))
                                    conn.commit()
                                    st.success("Transaction updated!")
                                    st.rerun()

        else:
            st.warning("No transactions found matching the selected criteria.")

    # Tab 2: Add New Transaction
    with tab_add:
        st.subheader("➕ Create New Financial Entry")
        a_type = st.radio("Transaction Type", ["income", "expense"], horizontal=True, key="tx_tab_add_type")
        available_cats = get_user_categories(user_id, a_type)

        a_col1, a_col2 = st.columns(2)
        with a_col1:
            a_category = st.selectbox("Category", available_cats, key=f"tx_tab_add_cat_{a_type}")

        with a_col2:
            a_custom_cat = ""
            if a_category == "Other":
                a_custom_cat = st.text_input("Enter Custom Category Name", placeholder="e.g. Pet Care, Side Hustle", key=f"tx_tab_add_custom_cat_{a_type}")

        with st.form("full_add_tx_form"):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                a_date = st.date_input("Date", value=datetime.date.today())
                a_amount = st.number_input("Amount", min_value=0.01, step=1.0, value=50.0)

            with f_col2:
                a_method = st.selectbox("Payment Method", ["Credit Card", "Debit Card", "Bank Transfer", "UPI", "Cash", "PayPal"])
                a_notes = st.text_input("Notes / Description", placeholder="e.g. Grocery restock at Costco")

            a_col_rec1, a_col_rec2 = st.columns(2)
            with a_col_rec1:
                a_is_rec = st.checkbox("Mark as Recurring Transaction")
            with a_col_rec2:
                a_rec_freq = st.selectbox("Recurring Frequency", ["Weekly", "Monthly", "Yearly"])

            sub_btn = st.form_submit_button("➕ Add Transaction", type="primary", use_container_width=True)
            if sub_btn:
                final_a_cat = a_category
                if a_category == "Other":
                    if not a_custom_cat.strip():
                        st.error("Please enter a custom category name.")
                        st.stop()
                    final_a_cat = a_custom_cat.strip()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT OR IGNORE INTO categories (user_id, name, type, icon, color)
                        VALUES (?, ?, ?, '🏷️', '#38bdf8')
                    """, (user_id, final_a_cat, a_type))
                    conn.commit()

                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes, is_recurring, recurring_frequency)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, a_date.strftime("%Y-%m-%d"), a_type, final_a_cat, a_amount, a_method, a_notes, 1 if a_is_rec else 0, a_rec_freq))
                conn.commit()
                st.success(f"New transaction created under '{final_a_cat}'!")
                st.rerun()

    # Tab 3: Recurring Expenses & Subscriptions
    with tab_recurring:
        st.subheader("🔁 Subscription & Recurring Expense Tracker")
        rec_df = pd.read_sql_query("""
            SELECT * FROM transactions
            WHERE user_id = ? AND is_recurring = 1
            ORDER BY amount DESC
        """, conn, params=(user_id,))

        if not rec_df.empty:
            total_rec_monthly = rec_df[rec_df["type"] == "expense"]["amount"].sum()
            st.metric("Total Monthly Recurring Subscriptions", format_currency(total_rec_monthly, currency))

            st.dataframe(
                rec_df[["date", "category", "amount", "recurring_frequency", "payment_method", "notes"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No recurring expenses or subscriptions flagged. Toggle 'Is Recurring' when adding transactions to track them here!")

    conn.close()
