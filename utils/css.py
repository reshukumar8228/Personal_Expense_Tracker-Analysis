import streamlit as st

def get_plotly_layout(theme: str = "Dark Fintech") -> dict:
    """Return theme-aware Plotly layout configuration dictionary."""
    is_dark = theme != "Light Modern"
    if is_dark:
        font_color = "#94a3b8"
        grid_color = "rgba(255, 255, 255, 0.08)"
        zeroline_color = "rgba(255, 255, 255, 0.12)"
    else:
        font_color = "#334155"
        grid_color = "rgba(0, 0, 0, 0.08)"
        zeroline_color = "rgba(0, 0, 0, 0.12)"

    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": dict(color=font_color, family="Plus Jakarta Sans"),
        "xaxis": dict(
            showgrid=False,
            color=font_color,
            gridcolor=grid_color,
            zerolinecolor=zeroline_color
        ),
        "yaxis": dict(
            showgrid=True,
            color=font_color,
            gridcolor=grid_color,
            zerolinecolor=zeroline_color
        ),
        "legend": dict(font=dict(color=font_color))
    }

def inject_custom_css(theme: str = "Dark Fintech"):
    """Inject ultra-sleek modern CSS styling with Tailwind/Geist inspired design tokens."""
    is_dark = theme != "Light Modern"

    if is_dark:
        bg_main = "#090d16"
        bg_card = "#111827"
        bg_card_elevated = "#1f2937"
        border_color = "rgba(255, 255, 255, 0.08)"
        border_color_hover = "rgba(56, 189, 248, 0.4)"
        text_primary = "#f9fafb"
        text_secondary = "#9ca3af"
        text_muted = "#6b7280"
        accent_blue = "#38bdf8"
        accent_indigo = "#6366f1"
        accent_purple = "#c084fc"
        accent_green = "#34d399"
        accent_red = "#f87171"
        accent_amber = "#fbbf24"
        card_shadow = "0 10px 30px -5px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05)"
        glow_primary = "0 0 25px rgba(56, 189, 248, 0.2)"
        hero_title_gradient = "linear-gradient(135deg, #f9fafb 0%, #38bdf8 50%, #c084fc 100%)"
    else:
        bg_main = "#fafafa"
        bg_card = "#ffffff"
        bg_card_elevated = "#f1f5f9"
        border_color = "#e2e8f0"
        border_color_hover = "#cbd5e1"
        text_primary = "#0f172a"
        text_secondary = "#334155"
        text_muted = "#64748b"
        accent_blue = "#0284c7"
        accent_indigo = "#4f46e5"
        accent_purple = "#7e22ce"
        accent_green = "#10b981"
        accent_red = "#ef4444"
        accent_amber = "#d97706"
        card_shadow = "0 4px 20px -2px rgba(0, 0, 0, 0.06), 0 0 0 1px #e2e8f0"
        glow_primary = "0 0 15px rgba(2, 132, 199, 0.12)"
        hero_title_gradient = "linear-gradient(135deg, #0f172a 0%, #0284c7 50%, #7e22ce 100%)"

    css = f"""
    <style>
    /* Google Fonts import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .stApp {{
        background-color: {bg_main};
        color: {text_primary};
    }}

    /* Page Subtitle Utility */
    .page-subtitle {{
        color: {text_secondary} !important;
        font-size: 0.95rem;
        margin-top: -6px;
        margin-bottom: 20px;
    }}

    /* Sidebar User Profile Card */
    .sidebar-user-card {{
        background: {bg_card_elevated};
        padding: 12px 14px;
        border-radius: 12px;
        margin-bottom: 16px;
        border: 1px solid {border_color};
        box-shadow: {card_shadow};
    }}

    .sidebar-user-name {{
        font-size: 0.88rem;
        font-weight: 700;
        color: {text_primary} !important;
    }}

    .sidebar-user-sub {{
        font-size: 0.78rem;
        color: {text_secondary} !important;
    }}

    /* Hide default Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: {bg_card};
        border-right: 1px solid {border_color};
        box-shadow: 4px 0 24px rgba(0,0,0,0.06);
    }}

    /* Navigation Radio Items Restyling */
    [data-testid="stSidebar"] .stRadio > label,
    [data-testid="stSidebar"] .stRadio > label * {{
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: {text_muted} !important;
        margin-bottom: 12px !important;
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {{
        background: transparent;
        border: 1px solid transparent;
        padding: 10px 14px;
        border-radius: 10px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 4px;
        cursor: pointer;
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label * {{
        color: {text_secondary} !important;
        font-weight: 600;
        font-size: 0.92rem;
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover * {{
        background: rgba(2, 132, 199, 0.08);
        color: {text_primary} !important;
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] * {{
        background: linear-gradient(135deg, rgba(2, 132, 199, 0.12) 0%, rgba(99, 102, 241, 0.12) 100%);
        border: 1px solid rgba(2, 132, 199, 0.3);
        color: {accent_blue} !important;
        font-weight: 700;
        box-shadow: {glow_primary};
    }}

    /* Streamlit Metrics */
    [data-testid="stMetricValue"] {{
        color: {text_primary} !important;
        font-weight: 800 !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {text_secondary} !important;
        font-weight: 600 !important;
    }}

    /* Hero Banner Header Card */
    .hero-card {{
        background: linear-gradient(135deg, {bg_card} 0%, {bg_card_elevated} 100%);
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: {card_shadow};
        position: relative;
        overflow: hidden;
    }}

    .hero-card::after {{
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(2, 132, 199, 0.12) 0%, rgba(168, 85, 247, 0.06) 50%, transparent 70%);
        pointer-events: none;
    }}

    .hero-title {{
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 6px 0;
        background: {hero_title_gradient};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .hero-subtitle {{
        font-size: 0.95rem;
        color: {text_secondary};
        margin: 0;
    }}

    /* Metric Cards Grid */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }}

    .kpi-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 20px;
        position: relative;
        overflow: hidden;
        box-shadow: {card_shadow};
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }}

    .kpi-card:hover {{
        transform: translateY(-2px);
        border-color: {border_color_hover};
        box-shadow: {glow_primary};
    }}

    .kpi-card.border-income::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #10b981, #34d399);
    }}

    .kpi-card.border-expense::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #ef4444, #f87171);
    }}

    .kpi-card.border-balance::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #38bdf8);
    }}

    .kpi-card.border-savings::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #8b5cf6, #c084fc);
    }}

    .kpi-card.border-health::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
    }}

    .kpi-title {{
        font-size: 0.8rem;
        font-weight: 700;
        color: {text_secondary};
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    .kpi-value {{
        font-size: 1.7rem;
        font-weight: 800;
        color: {text_primary};
        letter-spacing: -0.02em;
        margin-bottom: 4px;
    }}

    .kpi-subtext {{
        font-size: 0.8rem;
        font-weight: 600;
        color: {text_muted};
    }}

    /* Financial Health Badge */
    .health-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }}

    .health-excellent {{
        background: rgba(16, 185, 129, 0.14);
        color: {accent_green};
        border: 1px solid rgba(16, 185, 129, 0.3);
    }}

    .health-good {{
        background: rgba(2, 132, 199, 0.14);
        color: {accent_blue};
        border: 1px solid rgba(2, 132, 199, 0.3);
    }}

    .health-fair {{
        background: rgba(245, 158, 11, 0.14);
        color: {accent_amber};
        border: 1px solid rgba(245, 158, 11, 0.3);
    }}

    .health-poor {{
        background: rgba(239, 68, 68, 0.14);
        color: {accent_red};
        border: 1px solid rgba(239, 68, 68, 0.3);
    }}

    /* Styled Alert Boxes */
    .custom-alert {{
        padding: 14px 18px;
        border-radius: 12px;
        margin-bottom: 16px;
        font-size: 0.9rem;
        line-height: 1.5;
        box-shadow: {card_shadow};
    }}

    .alert-warning {{
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.3);
        color: {text_primary};
    }}

    .alert-danger {{
        background: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: {text_primary};
    }}

    .alert-success {{
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: {text_primary};
    }}

    /* Spend Card Containers */
    .spend-card {{
        background: {bg_card};
        border: 1px solid {border_color};
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        color: {text_primary};
        box-shadow: {card_shadow};
        transition: border-color 0.2s ease;
    }}

    .spend-card:hover {{
        border-color: {border_color_hover};
    }}

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {bg_card};
        padding: 6px;
        border-radius: 12px;
        border: 1px solid {border_color};
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 40px;
        white-space: pre;
        border-radius: 8px;
        color: {text_secondary};
        font-weight: 600;
        font-size: 0.88rem;
        border: none;
        padding: 0 16px;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {bg_card_elevated} !important;
        color: {accent_blue} !important;
        border: 1px solid rgba(2, 132, 199, 0.3) !important;
        box-shadow: {glow_primary};
    }}

    /* Streamlit Buttons */
    .stButton > button {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 8px 16px !important;
        border: 1px solid {border_color} !important;
        background: {bg_card_elevated} !important;
        color: {text_primary} !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}

    .stButton > button:hover {{
        border-color: {accent_blue} !important;
        color: {accent_blue} !important;
        transform: translateY(-1px);
    }}

    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%) !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
    }}

    .stButton > button[kind="primary"]:hover {{
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45) !important;
        transform: translateY(-1px);
    }}

    /* Form Controls & Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox select {{
        border-radius: 10px !important;
        border: 1px solid {border_color} !important;
        background-color: {bg_card_elevated} !important;
        color: {text_primary} !important;
    }}

    /* Dataframe container */
    [data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid {border_color};
        box-shadow: {card_shadow};
    }}

    /* Progress bar */
    .stProgress > div > div > div > div {{
        border-radius: 10px;
        background: linear-gradient(90deg, #38bdf8, #8b5cf6);
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

