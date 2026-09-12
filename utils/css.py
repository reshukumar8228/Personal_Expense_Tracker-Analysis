import streamlit as st

def get_plotly_layout(theme: str = "Dark Fintech") -> dict:
    """Return theme-aware Plotly layout configuration dictionary matching the deep navy dashboard reference."""
    is_dark = theme != "Light Modern"
    if is_dark:
        font_color = "#F1F4FF"
        secondary_color = "#9AA8D1"
        grid_color = "rgba(135, 155, 255, 0.08)"
        zeroline_color = "rgba(135, 155, 255, 0.15)"
    else:
        font_color = "#0F172A"
        secondary_color = "#475569"
        grid_color = "rgba(0, 0, 0, 0.08)"
        zeroline_color = "rgba(0, 0, 0, 0.12)"

    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": dict(color=font_color, family="Plus Jakarta Sans, sans-serif", size=12),
        "title": dict(font=dict(color=font_color, size=15, family="Plus Jakarta Sans, sans-serif")),
        "xaxis": dict(
            showgrid=False,
            color=secondary_color,
            gridcolor=grid_color,
            zerolinecolor=zeroline_color,
            tickfont=dict(color=secondary_color, size=11)
        ),
        "yaxis": dict(
            showgrid=True,
            color=secondary_color,
            gridcolor=grid_color,
            zerolinecolor=zeroline_color,
            tickfont=dict(color=secondary_color, size=11)
        ),
        "legend": dict(font=dict(color=font_color, size=11), bgcolor="rgba(0,0,0,0)")
    }

def inject_custom_css(theme: str = "Dark Fintech"):
    """Inject ultra-sleek modern CSS styling matching the Image 1 deep navy financial dashboard."""
    is_dark = theme != "Light Modern"

    if is_dark:
        bg_main = "#080D2B"
        bg_main_gradient = "linear-gradient(180deg, #080D2B 0%, #0D1238 100%)"
        bg_sidebar = "linear-gradient(180deg, #111942 0%, #0B1033 100%)"
        bg_card = "#151D4D"
        bg_card_gradient = "linear-gradient(145deg, #182254 0%, #121A42 100%)"
        bg_card_elevated = "#1B2663"
        bg_input = "#11173E"
        border_color = "#34458A"
        border_color_subtle = "rgba(135, 155, 255, 0.18)"
        border_color_hover = "#4169E1"
        text_primary = "#F1F4FF"
        text_secondary = "#9AA8D1"
        text_muted = "#6C7BAE"
        accent_blue = "#4169E1"
        accent_periwinkle = "#879BFF"
        accent_magenta = "#C52DDB"
        accent_purple = "#8B3DCE"
        accent_cyan = "#38BDF8"
        accent_green = "#38BDF8"  # Positive cashflow cyan-blue in dark mode
        accent_red = "#C52DDB"    # Tasteful magenta for expenses
        accent_amber = "#F59E0B"
        card_shadow = "0 8px 32px rgba(4, 7, 24, 0.5), 0 0 0 1px rgba(135, 155, 255, 0.15)"
        glow_primary = "0 0 24px rgba(65, 105, 225, 0.35)"
        glow_magenta = "0 0 24px rgba(197, 45, 219, 0.35)"
        hero_title_gradient = "linear-gradient(135deg, #F1F4FF 0%, #879BFF 50%, #C52DDB 100%)"
    else:
        bg_main = "#F8FAFC"
        bg_main_gradient = "#F8FAFC"
        bg_sidebar = "#FFFFFF"
        bg_card = "#FFFFFF"
        bg_card_gradient = "#FFFFFF"
        bg_card_elevated = "#F1F5F9"
        bg_input = "#FFFFFF"
        border_color = "#E2E8F0"
        border_color_subtle = "#E2E8F0"
        border_color_hover = "#94A3B8"
        text_primary = "#0F172A"
        text_secondary = "#334155"
        text_muted = "#64748B"
        accent_blue = "#0284C7"
        accent_periwinkle = "#6366F1"
        accent_magenta = "#D946EF"
        accent_purple = "#7E22CE"
        accent_cyan = "#0284C7"
        accent_green = "#10B981"
        accent_red = "#EF4444"
        accent_amber = "#D97706"
        card_shadow = "0 4px 20px -2px rgba(0, 0, 0, 0.06), 0 0 0 1px #E2E8F0"
        glow_primary = "0 0 15px rgba(2, 132, 199, 0.12)"
        glow_magenta = "0 0 15px rgba(217, 70, 239, 0.12)"
        hero_title_gradient = "linear-gradient(135deg, #0F172A 0%, #0284C7 50%, #7E22CE 100%)"

    css = f"""
    <style>
    /* Google Fonts import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .stApp {{
        background: {bg_main_gradient};
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
        background: {bg_card_gradient};
        padding: 14px 16px;
        border-radius: 14px;
        margin-bottom: 18px;
        border: 1px solid {border_color};
        box-shadow: {card_shadow};
    }}

    .sidebar-user-name {{
        font-size: 0.92rem;
        font-weight: 700;
        color: {text_primary} !important;
        letter-spacing: -0.01em;
    }}

    .sidebar-user-sub {{
        font-size: 0.8rem;
        color: {text_secondary} !important;
    }}

    /* Hide default Streamlit header chrome */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: {bg_sidebar} !important;
        border-right: 1px solid {border_color} !important;
        box-shadow: 6px 0 28px rgba(4, 7, 24, 0.4);
    }}

    /* Navigation Radio Items Restyling */
    [data-testid="stSidebar"] .stRadio > label,
    [data-testid="stSidebar"] .stRadio > label * {{
        font-size: 0.78rem !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        color: {text_muted} !important;
        margin-bottom: 14px !important;
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {{
        background: transparent;
        border: 1px solid transparent;
        padding: 11px 16px;
        border-radius: 12px;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 6px;
        cursor: pointer;
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label * {{
        color: {text_secondary} !important;
        font-weight: 600;
        font-size: 0.93rem;
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover,
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover * {{
        background: rgba(135, 155, 255, 0.12);
        color: {text_primary} !important;
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-checked="true"] * {{
        background: linear-gradient(135deg, rgba(65, 105, 225, 0.4) 0%, rgba(197, 45, 219, 0.3) 100%) !important;
        border: 1px solid rgba(135, 155, 255, 0.5) !important;
        color: {text_primary} !important;
        font-weight: 700 !important;
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
        background: linear-gradient(135deg, #151D4D 0%, #1D2A68 50%, #291B54 100%);
        border: 1px solid {border_color};
        border-radius: 18px;
        padding: 26px 30px;
        margin-bottom: 24px;
        box-shadow: {card_shadow};
        position: relative;
        overflow: hidden;
    }}

    .hero-card::after {{
        content: '';
        position: absolute;
        top: -40%;
        right: -8%;
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, rgba(135, 155, 255, 0.18) 0%, rgba(197, 45, 219, 0.12) 50%, transparent 70%);
        pointer-events: none;
    }}

    .hero-title {{
        font-size: 1.9rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 6px 0;
        background: {hero_title_gradient};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .hero-subtitle {{
        font-size: 0.96rem;
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
        background: {bg_card_gradient};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 22px;
        position: relative;
        overflow: hidden;
        box-shadow: {card_shadow};
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }}

    .kpi-card:hover {{
        transform: translateY(-3px);
        border-color: {border_color_hover};
        box-shadow: {glow_primary};
    }}

    .kpi-card.border-income::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4169E1, #38BDF8);
    }}

    .kpi-card.border-expense::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #C52DDB, #E052F2);
    }}

    .kpi-card.border-balance::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4169E1, #879BFF);
    }}

    .kpi-card.border-savings::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #8B3DCE, #C52DDB);
    }}

    .kpi-card.border-health::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #F59E0B, #879BFF);
    }}

    .kpi-title {{
        font-size: 0.8rem;
        font-weight: 700;
        color: {text_secondary};
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    .kpi-value {{
        font-size: 1.75rem;
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
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }}

    .health-excellent {{
        background: rgba(56, 189, 248, 0.16);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.4);
    }}

    .health-good {{
        background: rgba(65, 105, 225, 0.16);
        color: #879BFF;
        border: 1px solid rgba(135, 155, 255, 0.4);
    }}

    .health-fair {{
        background: rgba(245, 158, 11, 0.16);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.4);
    }}

    .health-poor {{
        background: rgba(197, 45, 219, 0.16);
        color: #C52DDB;
        border: 1px solid rgba(197, 45, 219, 0.4);
    }}

    /* Styled Alert Boxes */
    .custom-alert {{
        padding: 16px 20px;
        border-radius: 14px;
        margin-bottom: 18px;
        font-size: 0.92rem;
        line-height: 1.5;
        box-shadow: {card_shadow};
    }}

    .alert-warning {{
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.35);
        color: {text_primary};
    }}

    .alert-danger {{
        background: rgba(197, 45, 219, 0.12);
        border: 1px solid rgba(197, 45, 219, 0.4);
        color: {text_primary};
    }}

    .alert-success {{
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.4);
        color: {text_primary};
    }}

    /* Spend Card Containers */
    .spend-card {{
        background: {bg_card_gradient};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 18px;
        color: {text_primary};
        box-shadow: {card_shadow};
        transition: border-color 0.25s ease;
    }}

    .spend-card:hover {{
        border-color: {border_color_hover};
    }}

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        background-color: #111942;
        padding: 6px;
        border-radius: 14px;
        border: 1px solid {border_color};
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 42px;
        white-space: pre;
        border-radius: 10px;
        color: {text_secondary};
        font-weight: 600;
        font-size: 0.9rem;
        border: none;
        padding: 0 18px;
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #4169E1 0%, #C52DDB 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(135, 155, 255, 0.5) !important;
        box-shadow: {glow_primary};
    }}

    /* Streamlit Buttons */
    .stButton > button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        padding: 9px 18px !important;
        border: 1px solid {border_color} !important;
        background: {bg_card_elevated} !important;
        color: {text_primary} !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}

    .stButton > button:hover {{
        border-color: {accent_blue} !important;
        color: {text_primary} !important;
        box-shadow: {glow_primary} !important;
        transform: translateY(-1px);
    }}

    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #4169E1 0%, #879BFF 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(65, 105, 225, 0.4) !important;
    }}

    .stButton > button[kind="primary"]:hover {{
        box-shadow: 0 6px 24px rgba(197, 45, 219, 0.5) !important;
        transform: translateY(-1px);
    }}

    /* Form Controls & Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stDateInput input, [data-baseweb="select"] {{
        border-radius: 12px !important;
        border: 1px solid {border_color} !important;
        background-color: {bg_input} !important;
        color: {text_primary} !important;
    }}

    /* Dataframe container */
    [data-testid="stDataFrame"] {{
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid {border_color};
        box-shadow: {card_shadow};
        background: {bg_card};
    }}

    /* Progress bar */
    .stProgress > div > div > div > div {{
        border-radius: 10px;
        background: linear-gradient(90deg, #4169E1, #C52DDB);
    }}

    /* Expander styling */
    [data-testid="stExpander"] {{
        border-radius: 14px !important;
        border: 1px solid {border_color} !important;
        background: {bg_card_gradient} !important;
        box-shadow: {card_shadow} !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


