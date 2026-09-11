import streamlit as st
import pandas as pd
import datetime
import io
from database.db import get_connection
from utils.helpers import format_currency
from fpdf import FPDF

class PDFReport(FPDF):
    """Custom FPDF Class for SmartSpend Executive Reports."""
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(14, 165, 233) # Bright Blue
        self.cell(0, 10, "SmartSpend - Financial Executive Intelligence Report", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(139, 148, 158)
        self.cell(0, 5, f"Generated on: {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def generate_pdf_report(user: dict, transactions_df: pd.DataFrame, budgets_df: pd.DataFrame) -> bytes:
    """Generate a clean, professional multi-page PDF financial report."""
    currency = user.get("currency", "USD")
    username = user.get("username", "User")

    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # User Executive Summary
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, f"Executive Financial Summary for: {username}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    total_inc = transactions_df[transactions_df["type"] == "income"]["amount"].sum() if not transactions_df.empty else 0.0
    total_exp = transactions_df[transactions_df["type"] == "expense"]["amount"].sum() if not transactions_df.empty else 0.0
    net_bal = total_inc - total_exp
    savings_rate = (net_bal / total_inc * 100) if total_inc > 0 else 0.0

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(45, 8, f"Total Income: {format_currency(total_inc, currency)}", border=1)
    pdf.cell(45, 8, f"Total Expenses: {format_currency(total_exp, currency)}", border=1)
    pdf.cell(45, 8, f"Net Surplus: {format_currency(net_bal, currency)}", border=1)
    pdf.cell(45, 8, f"Savings Rate: {savings_rate:.1f}%", border=1)
    pdf.ln(12)

    # Category Breakdown Table
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Expense Breakdown by Category", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(70, 7, "Category", border=1, fill=True)
    pdf.cell(50, 7, f"Total Spent ({currency})", border=1, fill=True)
    pdf.cell(60, 7, "Proportion of Expenses", border=1, fill=True)
    pdf.ln()

    if not transactions_df.empty:
        exp_df = transactions_df[transactions_df["type"] == "expense"]
        if not exp_df.empty:
            cat_totals = exp_df.groupby("category")["amount"].sum().reset_index()
            pdf.set_font("Helvetica", "", 9)
            for _, row in cat_totals.iterrows():
                c_name = row["category"]
                c_amt = row["amount"]
                pct = (c_amt / total_exp * 100) if total_exp > 0 else 0.0
                pdf.cell(70, 6, c_name, border=1)
                pdf.cell(50, 6, f"{c_amt:,.2f}", border=1)
                pdf.cell(60, 6, f"{pct:.1f}%", border=1)
                pdf.ln()

    pdf.ln(8)

    # Recent Transactions Table
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Recent Transactions Audit Log", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(241, 245, 249)
    pdf.cell(25, 6, "Date", border=1, fill=True)
    pdf.cell(20, 6, "Type", border=1, fill=True)
    pdf.cell(40, 6, "Category", border=1, fill=True)
    pdf.cell(30, 6, "Amount", border=1, fill=True)
    pdf.cell(30, 6, "Method", border=1, fill=True)
    pdf.cell(35, 6, "Notes", border=1, fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    recent = transactions_df.head(20) if not transactions_df.empty else pd.DataFrame()
    for _, r in recent.iterrows():
        pdf.cell(25, 6, str(r["date"]), border=1)
        pdf.cell(20, 6, str(r["type"]).capitalize(), border=1)
        pdf.cell(40, 6, str(r["category"])[:20], border=1)
        amt_str = f"+{r['amount']:,.2f}" if r["type"] == "income" else f"-{r['amount']:,.2f}"
        pdf.cell(30, 6, amt_str, border=1)
        pdf.cell(30, 6, str(r["payment_method"])[:18], border=1)
        pdf.cell(35, 6, str(r["notes"] or "")[:20], border=1)
        pdf.ln()

    return bytes(pdf.output())

def render_import_export(user: dict):
    """Render Data Import & Export Hub page."""
    currency = user.get("currency", "USD")
    user_id = user["id"]

    st.markdown("## 📥 Data Import & Export Hub")
    st.markdown("<p style='color: #8b949e;'>Import CSV/Excel data, export spreadsheets, and generate professional PDF reports</p>", unsafe_allow_html=True)

    conn = get_connection()
    tx_df = pd.read_sql_query("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", conn, params=(user_id,))
    budgets_df = pd.read_sql_query("SELECT * FROM budgets WHERE user_id = ?", conn, params=(user_id,))
    conn.close()

    tab_import, tab_export, tab_pdf = st.tabs(["📤 CSV / Excel Import", "📥 Excel & CSV Export", "📄 PDF Report Generator"])

    # Tab 1: CSV / Excel File Import
    with tab_import:
        st.subheader("📤 Batch Upload Financial Data")
        st.markdown("Upload a CSV or Excel file containing transaction entries.")

        # Template Downloaders
        st.markdown("##### Download Sample Import Template:")
        sample_df = pd.DataFrame([
            {"date": "2026-09-01", "type": "income", "category": "Salary", "amount": 5000.0, "payment_method": "Bank Transfer", "notes": "Monthly Salary"},
            {"date": "2026-09-02", "type": "expense", "category": "Housing & Rent", "amount": 1500.0, "payment_method": "Bank Transfer", "notes": "Apartment Rent"},
            {"date": "2026-09-05", "type": "expense", "category": "Groceries", "amount": 120.50, "payment_method": "Credit Card", "notes": "Weekly Supermarket"}
        ])

        csv_tmpl = sample_df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Sample CSV Template", data=csv_tmpl, file_name="smartspend_import_template.csv", mime="text/csv")

        uploaded_file = st.file_uploader("Choose CSV or XLSX file", type=["csv", "xlsx"])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df_upload = pd.read_csv(uploaded_file)
                else:
                    df_upload = pd.read_excel(uploaded_file)

                st.subheader("📋 Import Data Preview & Validation")
                required_cols = {"date", "type", "category", "amount", "payment_method"}
                uploaded_cols = set(df_upload.columns.str.lower())

                if not required_cols.issubset(uploaded_cols):
                    missing = required_cols - uploaded_cols
                    st.error(f"Validation Failed: Missing required columns: {missing}. Required columns: {list(required_cols)}")
                else:
                    st.success(f"File validated successfully! Found {len(df_upload)} rows.")
                    st.dataframe(df_upload.head(10), use_container_width=True)

                    if st.button("🚀 Confirm & Import Rows into Database", type="primary"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        imported_count = 0
                        for _, row in df_upload.iterrows():
                            notes_val = str(row.get("notes", "")) if pd.notna(row.get("notes")) else ""
                            cursor.execute("""
                                INSERT INTO transactions (user_id, date, type, category, amount, payment_method, notes)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (user_id, str(row["date"]), str(row["type"]).lower(), str(row["category"]), float(row["amount"]), str(row["payment_method"]), notes_val))
                            imported_count += 1
                        conn.commit()
                        conn.close()
                        st.success(f"Successfully imported {imported_count} transaction entries!")
                        st.rerun()

            except Exception as e:
                st.error(f"Error processing uploaded file: {e}")

    # Tab 2: Excel & CSV Export
    with tab_export:
        st.subheader("📥 Export Financial Records")
        if not tx_df.empty:
            e_col1, e_col2 = st.columns(2)

            with e_col1:
                st.markdown("#### Export as CSV")
                csv_data = tx_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download Transactions CSV",
                    data=csv_data,
                    file_name=f"smartspend_transactions_{datetime.date.today()}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with e_col2:
                st.markdown("#### Export as Multi-Sheet Excel Workbook")
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    tx_df.to_excel(writer, sheet_name="All Transactions", index=False)
                    if not tx_df.empty:
                        cat_summary = tx_df.groupby(["type", "category"])["amount"].sum().reset_index()
                        cat_summary.to_excel(writer, sheet_name="Category Summary", index=False)
                    if not budgets_df.empty:
                        budgets_df.to_excel(writer, sheet_name="Budgets", index=False)

                st.download_button(
                    "📊 Download Excel Workbook (.xlsx)",
                    data=excel_buffer.getvalue(),
                    file_name=f"smartspend_full_report_{datetime.date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.info("No records available for export.")

    # Tab 3: PDF Report Generator
    with tab_pdf:
        st.subheader("📄 Professional PDF Executive Report")
        st.markdown("Generate a print-ready PDF financial report complete with executive metrics and transaction tables.")
        if not tx_df.empty:
            if st.button("⚙️ Generate PDF Report", type="primary", use_container_width=True):
                with st.spinner("Building PDF document..."):
                    pdf_bytes = generate_pdf_report(user, tx_df, budgets_df)
                    st.download_button(
                        "📄 Download PDF Financial Report",
                        data=pdf_bytes,
                        file_name=f"smartspend_report_{datetime.date.today()}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        else:
            st.info("No data available to generate PDF report.")
