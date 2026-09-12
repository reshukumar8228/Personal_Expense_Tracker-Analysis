# Personal Expense Tracker — Finance & Intelligence Platform

Personal Expense Tracker is a complete, modern, and fully functional web application built with **Python, Streamlit, SQLite, Pandas, NumPy, Plotly, Scikit-learn, OpenPyXL, and FPDF2**.

---

## 🌟 Key Features

1. **User Authentication & Session Security**:
   - Registration, login, logout, and salted PBKDF2-HMAC-SHA256 password hashing.
   - User preferences persistence (currency selection & dark/light theme).
   - Quick Instant Demo mode populated with 6 months of realistic sample data.

2. **Personal Executive Dashboard**:
   - Financial KPI cards: Total Income, Total Expenses, Net Surplus, Savings Rate %, and Financial Health Index (0-100 score with visual badges).
   - Real-time Income vs Expense trend bars & Category breakdown pie chart.
   - Dynamic period filter (Current Month, Last 30 Days, Last 90 Days, YTD, All Time).
   - Quick Add Transaction widget and active budget alert banners.

3. **Transactions Hub**:
   - Full CRUD: Add, Edit, Delete, and Search transactions.
   - Multi-criteria filtering (Date range, Transaction Type, Category, Payment Method, Text search in notes).
   - Recurring Subscription & Expense Manager (Rent, Utilities, Streaming).

4. **Budget Management & Monitoring**:
   - Set monthly category spending caps.
   - Real-time color-coded progress indicators (<75% Green, 75-99% Amber Warning, ≥100% Critical Red Alert).
   - Total monthly budget headroom tracking.

5. **Advanced Analytics & Visualizations**:
   - **Pie & Donut Charts**: Category expense & income distribution.
   - **Bar Charts**: Side-by-side monthly income vs expense comparison.
   - **Line Charts**: Cumulative cash flow & daily balance trajectory.
   - **Histogram & Box Plots**: Transaction size frequency distribution and outlier purchase detection.
   - **Treemap**: Hierarchical spending tree (Type → Category → Payment Method).
   - **Heatmap**: Expenditure frequency by Day of Week vs Week of Month.

6. **Machine Learning Expense Forecasting**:
   - `Scikit-learn` predictive model (Linear & Random Forest Regression) trained on historical monthly time-series.
   - Forecasts total next-month expenses and category-wise predictions.
   - 95% confidence interval estimation and trend direction indicators (Increasing / Decreasing / Stable).

7. **Smart Insights & Financial Intelligence**:
   - 50/30/20 Rule compliance analyzer (Needs vs Wants vs Savings).
   - Category spending spike anomaly detector (>25% surge vs 3-month average).
   - Recurring subscription auditor.
   - Automated personalized financial recommendations.

8. **Savings Goals Tracker**:
   - Milestone tracking (Emergency Fund, Vacation, Car, Gadgets).
   - Deposit logger & progress indicators.

9. **Import & Export Hub**:
   - **CSV & Excel Import**: Drag-and-drop upload with validation, column check, and preview before batch insertion.
   - **CSV & Excel Export**: Export full/filtered transaction logs and multi-sheet formatted Excel workbooks (`openpyxl`).
   - **PDF Report Generator**: Multi-page branded PDF reports (`FPDF2`) with executive summaries, budget progress, category tables, and recent logs.

10. **Custom Fintech Design System**:
    - Sleek modern UI custom CSS styling with rounded cards, metric badges, custom pills, responsive layouts, and Dark/Light mode toggle.

---

## 🛠️ Technology Stack

- **Frontend & App Framework**: Streamlit
- **Database Layer**: Supabase PostgreSQL (Managed Cloud Database) with automatic local SQLite fallback for offline development
- **Data Processing**: Pandas, NumPy
- **Interactive Data Visualization**: Plotly Express & Plotly Graph Objects
- **Machine Learning**: Scikit-Learn (LinearRegression, RandomForestRegressor)
- **Excel & PDF Export**: OpenPyXL, FPDF2

---

## ⚡ Supabase Database Setup

1. Create a free account at **[supabase.com](https://supabase.com)** and create a new project.
2. Navigate to **Project Settings -> Database -> Connection String** and copy your URI connection string.
3. Create a `.env` file in the project root:
   ```env
   DATABASE_URL=postgresql://postgres.yourprojectref:yourpassword@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
4. Alternatively, if deploying on **Streamlit Community Cloud**, paste your connection string under **App Settings -> Secrets**:
   ```toml
   DATABASE_URL = "postgresql://postgres.yourprojectref:yourpassword@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
   ```

---

## 🚀 Quick Setup & Installation

### 1. Clone & Navigate to Project Directory
```bash
cd "d:\Projects\Personal_Expene_Tracker and Analysis"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Application
```bash
streamlit run app.py
```

### 4. Run Automated Unit Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```


---

## 📁 Folder Structure

```
.
├── app.py                      # Main Streamlit application entrypoint & routing
├── database/
│   └── db.py                   # SQLite DB initialization, models, CRUD operations, seed data generator
├── modules/
│   ├── auth.py                 # User authentication UI, session management, PBKDF2 hashing
│   ├── dashboard.py            # Financial KPI cards, Financial Health Score index, mini-charts
│   ├── transactions.py         # Transaction CRUD, search, filter, recurring expense logic
│   ├── budgets.py              # Category budget management, progress tracking & alerts
│   ├── analytics.py            # Plotly interactive charts (Pie, Bar, Line, Hist, Box, Treemap, Heatmap)
│   ├── ml_engine.py            # Scikit-learn expense forecasting model & trend analysis
│   ├── savings.py              # Savings goals tracker & estimated completion timeline
│   ├── insights.py             # Rule-based & statistical financial intelligence & 50/30/20 breakdown
│   ├── import_export.py        # CSV/Excel import with validation, CSV/Excel export, FPDF2 PDF report generator
│   └── settings.py             # User profile, currency selector ($/€/£/₹/¥/etc.), theme configuration
├── utils/
│   ├── css.py                  # Custom CSS injection for modern fintech styling (Dark/Light)
│   └── helpers.py              # Currency formatting, date helpers, color tokens
├── tests/
│   ├── test_db.py              # SQLite database schema & transaction CRUD tests
│   ├── test_auth.py            # Authentication & password hashing tests
│   ├── test_ml.py              # Machine learning prediction pipeline unit tests
│   └── test_export.py          # CSV/Excel/PDF export verification tests
├── requirements.txt            # Python dependencies
└── README.md                   # Full documentation & setup guide
```
