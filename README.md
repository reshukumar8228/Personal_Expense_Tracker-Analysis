# Personal Expense Tracker — Finance & Intelligence Platform

Personal Expense Tracker is an enterprise-ready, modern, and comprehensive financial management and predictive analytics web application built with **Python, Streamlit, Supabase PostgreSQL / SQLite, Pandas, NumPy, Plotly, Scikit-learn, OpenPyXL, and FPDF2**.

---

## Key Features

1. **User Authentication & Session Security**:
   - Registration, login, logout, and salted PBKDF2-HMAC-SHA256 password hashing.
   - User preferences persistence (currency selection & dark/light theme).
   - Instant Demo Mode populated with 6 months of realistic sample financial transactions.

2. **Personal Executive Dashboard**:
   - Financial KPI cards: Total Income, Total Expenses, Net Surplus, Savings Rate %, and Financial Health Index (0–100 score with dynamic visual badges).
   - Real-time Income vs Expense trend bars & Category breakdown pie chart.
   - Dynamic period filter (Current Month, Last 30 Days, Last 90 Days, YTD, All Time).
   - Quick Add Transaction modal/widget and active budget alert banners.

3. **Transactions Hub**:
   - Full CRUD operations: Add, Edit, Delete, and Search transactions.
   - Multi-criteria filtering (Date range, Transaction Type, Category, Payment Method, Text search in notes).
   - Recurring Subscription & Expense Manager (Rent, Utilities, Streaming services, etc.).

4. **Budget Management & Monitoring**:
   - Monthly category spending caps with real-time tracking.
   - Color-coded visual progress indicators (<75% Green, 75–99% Amber Warning, ≥100% Critical Red Alert).
   - Total monthly budget headroom calculation.

5. **Advanced Analytics & Visualizations**:
   - **Pie & Donut Charts**: Category expense and income distribution.
   - **Bar Charts**: Side-by-side monthly income vs expense comparison.
   - **Line Charts**: Cumulative cash flow and daily balance trajectory.
   - **Histogram & Box Plots**: Transaction size frequency distribution and outlier purchase detection.
   - **Treemap**: Hierarchical spending tree (Type → Category → Payment Method).
   - **Heatmap**: Expenditure frequency by Day of Week vs Week of Month.

6. **Machine Learning Expense Forecasting**:
   - `Scikit-learn` predictive model (Linear & Random Forest Regression) trained on historical monthly time-series.
   - Next-month expenditure forecasting with category-wise breakdown.
   - Trend direction indicators and confidence analysis.

7. **Smart Insights & Financial Intelligence**:
   - 50/30/20 Rule compliance analyzer (Needs vs Wants vs Savings).
   - Category spending spike anomaly detector (>25% surge vs 3-month average).
   - Recurring subscription auditor and automated personalized recommendations.

8. **Savings Goals Tracker**:
   - Milestone tracking (Emergency Fund, Vacation, Car, Gadgets).
   - Deposit logger and progress tracking towards target dates.

9. **Import & Export Hub**:
   - **CSV & Excel Import**: Drag-and-drop upload with validation, column checking, and preview before batch insertion.
   - **CSV & Excel Export**: Export full/filtered transaction logs and multi-sheet formatted Excel workbooks (`openpyxl`).
   - **PDF Report Generator**: Multi-page branded PDF reports (`FPDF2`) with executive summaries, budget progress, category tables, and recent logs.

10. **Fintech Design System**:
    - Sleek modern custom CSS styling with rounded cards, metric badges, custom navigation pills, responsive layouts, and Dark/Light mode toggle.

---

## Technology Stack

- **Frontend & Application Framework**: [Streamlit](https://streamlit.io/)
- **Database Layer**: Supabase PostgreSQL (Cloud Database) with automatic local SQLite fallback for offline execution
- **Data Processing**: Pandas, NumPy
- **Interactive Visualizations**: Plotly Express & Plotly Graph Objects
- **Machine Learning**: Scikit-Learn (`LinearRegression`, `RandomForestRegressor`)
- **Excel & PDF Export**: OpenPyXL, FPDF2
- **Testing**: Pytest & Unittest

---

## Database Configuration

The application automatically connects to Supabase PostgreSQL when configured, or seamlessly falls back to a local SQLite database (`database/expense_tracker.db`) if no cloud credentials are provided.

### Supabase Setup (Optional)
1. Create a project at **[supabase.com](https://supabase.com)**.
2. Navigate to **Project Settings -> Database -> Connection String** and copy your URI.
3. Configure your `.env` file in the project root:
   ```env
   DATABASE_URL=postgresql://postgres.yourprojectref:yourpassword@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
4. Alternatively, for **Streamlit Community Cloud**, paste your connection string under **App Settings -> Secrets**:
   ```toml
   DATABASE_URL = "postgresql://postgres.yourprojectref:yourpassword@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
   ```

---

## Quick Setup & Installation

### 1. Clone & Navigate to Project Directory
```bash
git clone <repository-url>
cd Personal_Expense_Tracker_2
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Application
```bash
streamlit run app.py
```

### 4. Run Automated Test Suite
```bash
pytest
```
*Or using unittest:*
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## Clean Project Structure

```
Personal_Expense_Tracker_2/
├── .streamlit/                      # Streamlit theme & server configuration
│   └── config.toml
├── database/                        # Database manager & storage
│   ├── db.py                        # Dual-engine DB layer (Supabase / SQLite) & seeders
│   └── expense_tracker.db           # SQLite database
├── modules/                         # Core application page modules
│   ├── auth.py                      # User authentication & PBKDF2 hashing
│   ├── dashboard.py                 # Executive KPI cards & financial health score
│   ├── transactions.py              # Transaction CRUD, search, and recurring manager
│   ├── budgets.py                   # Category budget limits & alert tracking
│   ├── analytics.py                 # Interactive Plotly charts & spending heatmaps
│   ├── ml_engine.py                 # Scikit-learn expense forecasting models
│   ├── savings.py                   # Milestone savings goals & timelines
│   ├── insights.py                  # Financial intelligence & 50/30/20 breakdown
│   ├── import_export.py             # CSV/Excel/PDF import and export pipelines
│   └── settings.py                  # User profile, currency selector, theme toggles
├── utils/                           # Design system & utilities
│   ├── css.py                       # Modern fintech CSS styling (Dark/Light mode)
│   └── helpers.py                   # Currency formatters, date helpers, color tokens
├── tests/                           # Pytest automated test suite
│   ├── test_auth.py                 # Password hashing & auth tests
│   ├── test_db.py                   # Database schema & CRUD tests
│   ├── test_export.py               # Export engine tests
│   └── test_ml.py                   # ML forecasting regression tests
├── app.py                           # Application main entrypoint
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore configuration
├── README.md                        # Primary project documentation
│
└── _archive_and_tools/              # Auxiliary assets & tools
    ├── docs/                        # Architecture reports & presentation assets
    ├── scripts/                     # Screen capture & SVG rendering scripts
    └── web_showcase/                # Auxiliary web showcase boilerplate
```

---

## Quality Assurance & Testing

All major subsystems are verified via automated unit and integration tests:
- **Authentication**: Salted PBKDF2 password generation and validation.
- **Database Engine**: Schema auto-initialization, dual-engine PostgreSQL/SQLite CRUD, and demo dataset population.
- **Machine Learning Engine**: Regression forecasting accuracy and fallback behavior on sparse datasets.
- **Export Formats**: Validates CSV structure, multi-sheet Excel generation, and PDF page construction.
