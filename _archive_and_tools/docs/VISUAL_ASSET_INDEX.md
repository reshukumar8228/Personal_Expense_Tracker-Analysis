# Visual Asset Index — Presentation & Architecture Assets

This document indexes all verified, presentation-ready visual assets generated and captured for the **Personal Expense Tracker — Finance & Intelligence Platform**. All assets are stored with both high-resolution PNG (2x retina) and vector SVG formats where applicable.

---

## 📸 Section 1: Application Screenshots (Real Running App)

All screenshots were captured directly from the live application running on `http://localhost:8501` under authenticated session context (`demouser`), using modern 1440×920 viewport dimensions with high-density retina rendering (device scale factor 2.0).

| Filename | Type | Recommended Slide | Description | Why It Matters |
| :--- | :---: | :---: | :--- | :--- |
| `01_auth_screen.png` | PNG | Slide 4 / Onboarding | Clean sliding login/signup card with eye toggles and 1-Click Instant Demo Access button. | Demonstrates frictionless onboarding and immediate usability without requiring tedious registration. |
| `02_dashboard_overview.png` | PNG | Slide 3 / Solution Overview | Executive dashboard with 5 Financial KPI cards (Income, Expenses, Net Balance, Savings Rate, Health Index 95/100). | Core value proposition: instant executive clarity on financial health and cashflow surplus. |
| `03_transactions_hub.png` | PNG | Slide 7 / Core Workflow | Transaction ledger with multi-criteria filters, summary stats bar, and single-row dataframe selection. | Demonstrates auditability, intuitive data manipulation, and full CRUD control over historical entries. |
| `04_budgets_monitoring.png` | PNG | Slide 7 / Budget Control | Monthly spending caps, color-coded progress bars, and multi-tier warning indicators (Healthy, Warning 99%). | Shows proactive budget discipline: visually alerts users before overspending causes financial distress. |
| `05_analytics_visualizations.png` | PNG | Slide 9 / Visual Analytics | Side-by-side monthly cash flow bar chart (Mar–Sep) and cumulative net balance upward trajectory. | Demonstrates multi-dimensional financial intelligence and long-term net worth accumulation. |
| `06_forecast_ml_engine.png` | PNG | Slide 8 / AI & ML Forecaster | Scikit-learn next-month predicted spend (₹3,181.30), 95% confidence bounds, and category bar chart. | Proves real machine learning capability: delivers forward-looking foresight rather than backwards-only reporting. |
| `07_insights_intelligence.png` | PNG | Slide 8 / Smart Insights | 50/30/20 standard financial rule compliance gauges and category spending surge anomaly alerts (+423% spike). | Demonstrates algorithmic financial advisory that pinpoints reckless spending habits automatically. |
| `08_savings_goals.png` | PNG | Slide 11 / Wealth Milestones | Goal cards (Emergency Fund 65%, Japan Vacation 51.4%, Macbook Pro 100%) with deposit funds popovers. | Bridges daily expense tracking with long-term wealth creation and milestone achievement. |
| `09_import_export_hub.png` | PNG | Slide 11 / Data Portability | Batch CSV/XLSX uploader (up to 200MB), sample template downloader, and FPDF2 multi-page PDF generator. | Enterprise-grade data portability: allows external bank imports and generates executive PDF reports. |
| `10_settings_preferences.png` | PNG | Slide 6 / Customization | Multi-currency selector (USD, EUR, GBP, INR, JPY, CAD, AUD), Dark/Light theme toggle, and demo re-seeder. | Shows global accessibility, personalized visual comfort, and rapid demo repeatability. |

---

## 📐 Section 2: Architecture & Workflow Diagrams (Vector SVG + PNG + Source)

All diagrams are styled in modern fintech aesthetics matching the project design system (Deep Navy `#080D2B`, Glassmorphic Cards `#151D4D`, Neon Accents `#4169E1`, `#38BDF8`, `#C52DDB`, `#10B981`).

| Diagram Name | SVG Asset | PNG Asset | Source (.mmd) | Recommended Slide | Why It Matters |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **System Architecture** | `architecture/system_architecture.svg` | `architecture/system_architecture.png` | `architecture/system_architecture.mmd` | Slide 5 | Establishes technical credibility: clarifies the 3-layer architecture, router, modules, and dual-database abstraction. |
| **End-to-End User Journey** | `workflow/user_journey.svg` | `workflow/user_journey.png` | `workflow/user_journey.mmd` | Slide 4 | Tells a clear human story: explains how a user moves from onboarding to data capture, monitoring, forecasting, and optimization. |
| **Technical Execution Flow** | `workflow/technical_workflow.svg` | `workflow/technical_workflow.png` | `workflow/technical_workflow.mmd` | Slide 7 | Explains runtime mechanics: shows session state gating, module dispatching, SQL dialect wrapping, and browser re-rendering. |
| **Data Flow Pipeline** | `dataflow/data_flow.svg` | `dataflow/data_flow.png` | `dataflow/data_flow.mmd` | Slide 7 | Illustrates the data lifecycle: shows how raw multi-source data is cleaned, stored, transformed, modeled, and exported. |
| **AI / ML Pipeline** | `ai_pipeline/ai_ml_pipeline.svg` | `ai_pipeline/ai_ml_pipeline.png` | `ai_pipeline/ai_ml_pipeline.mmd` | Slide 8 | Details the machine learning engine: feature matrix generation (lag-1, rolling-3), regression fitting, and 95% confidence intervals. |
| **Deployment Architecture** | `deployment/deployment_architecture.svg` | `deployment/deployment_architecture.png` | `deployment/deployment_architecture.mmd` | Slide 10 | Demonstrates production readiness: illustrates GitHub CI/CD, Streamlit Cloud hosting, and Supabase cloud pooler with SQLite fallback. |
| **Technology Stack** | `technology_stack/technology_stack.svg` | `technology_stack/technology_stack.png` | `technology_stack/technology_stack.mmd` | Slide 6 | Visual summary of engineering tools: categorizes Streamlit, Plotly, Scikit-learn, Supabase, SQLite, and FPDF2 into a cohesive stack. |

---

## 🗂️ File Tree of Presentation Assets

```
presentation_assets/
├── ai_pipeline/
│   ├── ai_ml_pipeline.mmd          # Mermaid source definition
│   ├── ai_ml_pipeline.png          # High-resolution 2x retina render
│   └── ai_ml_pipeline.svg          # Infinite-scaling vector diagram
├── architecture/
│   ├── system_architecture.mmd
│   ├── system_architecture.png
│   └── system_architecture.svg
├── dataflow/
│   ├── data_flow.mmd
│   ├── data_flow.png
│   └── data_flow.svg
├── deployment/
│   ├── deployment_architecture.mmd
│   ├── deployment_architecture.png
│   └── deployment_architecture.svg
├── screenshots/
│   ├── 01_auth_screen.png          # Onboarding & login
│   ├── 02_dashboard_overview.png   # Executive KPIs & health score
│   ├── 03_transactions_hub.png     # Ledger, filters & row selection
│   ├── 04_budgets_monitoring.png   # Spending caps & progress bars
│   ├── 05_analytics_visualizations.png # Plotly trajectory & cashflow
│   ├── 06_forecast_ml_engine.png   # Scikit-learn predictions & bounds
│   ├── 07_insights_intelligence.png# 50/30/20 & anomaly spike detector
│   ├── 08_savings_goals.png        # Milestones & deposit popovers
│   ├── 09_import_export_hub.png    # CSV/XLSX uploader & PDF generator
│   └── 10_settings_preferences.png # Multi-currency & theme settings
├── technology_stack/
│   ├── technology_stack.mmd
│   ├── technology_stack.png
│   └── technology_stack.svg
└── workflow/
    ├── technical_workflow.mmd
    ├── technical_workflow.png
    ├── technical_workflow.svg
    ├── user_journey.mmd
    ├── user_journey.png
    └── user_journey.svg
```
