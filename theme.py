# ============================================================
# theme.py — Sci-fi neon theme CSS generation
# ============================================================
import config


def get_google_fonts_import() -> str:
    """HTML style block importing Orbitron and Share Tech Mono from Google Fonts."""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');
    </style>
    """


def get_main_css() -> str:
    """Complete CSS string for the sci-fi neon dashboard theme."""
    c = config.COLORS
    fh = config.FONT_HEADING
    fb = config.FONT_BODY
    accent_rgb = _hex_to_rgb(c["cyan"])
    panel_rgb = _hex_to_rgb(c["panel_bg"])
    green_rgb = _hex_to_rgb(c["green"])
    sidebar_text = "#d4f3ff"

    return f"""
    /* ===== Global ===== */
    .stApp {{
        background: linear-gradient(180deg, {c['dark_bg']} 0%, {c['panel_bg']} 50%, {c['mid_bg']} 100%);
        color: {c['text']};
        font-family: '{fb}', monospace;
    }}

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {c['panel_bg']} 0%, {c['dark_bg']} 100%);
        border-right: 1px solid rgba({accent_rgb}, 0.15);
    }}
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] label {{
        color: {sidebar_text} !important;
        font-family: '{fb}', monospace;
        font-weight: 600;
        text-shadow: 0 0 8px rgba({accent_rgb}, 0.16);
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {c['cyan']};
        font-family: '{fh}', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}
    section[data-testid="stSidebar"] .stRadio > div label,
    section[data-testid="stSidebar"] .stRadio > div label p,
    section[data-testid="stSidebar"] .stRadio > div label span,
    section[data-testid="stSidebar"] .stCheckbox label,
    section[data-testid="stSidebar"] .stCheckbox label p,
    section[data-testid="stSidebar"] .stCheckbox label span {{
        color: {sidebar_text} !important;
        font-family: '{fb}', monospace;
        font-weight: 600;
        text-shadow: 0 0 8px rgba({accent_rgb}, 0.16);
    }}

    /* ===== Main Content Filter Visibility ===== */
    [data-testid="stAppViewContainer"] .stRadio > label,
    [data-testid="stAppViewContainer"] .stCheckbox > label,
    [data-testid="stAppViewContainer"] .stSelectbox > label,
    [data-testid="stAppViewContainer"] .stMultiSelect > label,
    [data-testid="stAppViewContainer"] .stDateInput > label,
    [data-testid="stAppViewContainer"] .stTimeInput > label,
    [data-testid="stAppViewContainer"] .stRadio label,
    [data-testid="stAppViewContainer"] .stRadio label p,
    [data-testid="stAppViewContainer"] .stRadio label span,
    [data-testid="stAppViewContainer"] .stCheckbox label,
    [data-testid="stAppViewContainer"] .stCheckbox label p,
    [data-testid="stAppViewContainer"] .stCheckbox label span {{
        color: {sidebar_text} !important;
        font-family: '{fb}', monospace;
        font-weight: 600;
        text-shadow: 0 0 8px rgba({accent_rgb}, 0.16);
    }}
    [data-testid="stAppViewContainer"] .stSelectbox > div > div,
    [data-testid="stAppViewContainer"] .stMultiSelect > div > div,
    [data-testid="stAppViewContainer"] .stDateInput > div > div > input,
    [data-testid="stAppViewContainer"] .stTimeInput > div > div > input {{
        border-color: rgba({accent_rgb}, 0.45);
        color: {sidebar_text};
        box-shadow: 0 0 10px rgba({accent_rgb}, 0.15);
    }}
    /* ===== Headings ===== */
    h1, h2, h3, h4 {{
        color: {c['cyan']} !important;
        font-family: '{fh}', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 3px;
    }}

    /* ===== Body Text ===== */
    p, li, span, div, td, th, label {{
        font-family: '{fb}', monospace;
    }}

    /* ===== Buttons ===== */
    .stButton > button {{
        background: linear-gradient(135deg, rgba({accent_rgb}, 0.2), rgba({accent_rgb}, 0.05));
        color: {c['cyan']};
        border: 1px solid {c['cyan']};
        font-family: '{fh}', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
        border-radius: 4px;
        transition: all 0.3s ease;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, rgba({accent_rgb}, 0.35), rgba({accent_rgb}, 0.15));
        box-shadow: 0 0 15px rgba({accent_rgb}, 0.3);
        color: #ffffff;
    }}

    /* ===== Selectbox / Inputs ===== */
    .stSelectbox > div > div,
    .stMultiSelect > div > div,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input {{
        background-color: {c['dark_bg']};
        border: 1px solid rgba({accent_rgb}, 0.3);
        color: {c['text']};
        font-family: '{fb}', monospace;
    }}

    /* ===== Radio Buttons ===== */
    .stRadio > div {{
        color: {c['text']};
    }}
    .stRadio > div label {{
        font-family: '{fb}', monospace;
        color: {c['text']};
    }}

    /* ===== Checkboxes ===== */
    .stCheckbox label {{
        color: {c['text']};
        font-family: '{fb}', monospace;
    }}

    /* ===== Expander ===== */
    .streamlit-expanderHeader {{
        color: {c['cyan']} !important;
        font-family: '{fh}', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        background-color: rgba({panel_rgb}, 0.6);
        border: 1px solid rgba({accent_rgb}, 0.2);
        border-radius: 4px;
    }}
    details[data-testid="stExpander"] {{
        border: 1px solid rgba({accent_rgb}, 0.2);
        border-radius: 4px;
        background-color: rgba({panel_rgb}, 0.6);
    }}
    details[data-testid="stExpander"] summary {{
        color: {c['cyan']} !important;
        font-family: '{fh}', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* ===== Data Tables ===== */
    .stDataFrame {{
        border: 1px solid rgba({accent_rgb}, 0.2);
        border-radius: 4px;
    }}
    [data-testid="stDataFrame"] table {{
        color: {c['text']};
        font-family: '{fb}', monospace;
    }}

    /* ===== Metric Card ===== */
    .metric-card {{
        background: {c['card_bg']};
        border-radius: 8px;
        padding: 20px 16px;
        text-align: center;
        transition: all 0.3s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
    }}
    .metric-card .metric-value {{
        font-family: '{fh}', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1.2;
    }}
    .metric-card .metric-label {{
        font-family: '{fb}', monospace;
        color: {c['text_dim']};
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 8px;
    }}

    /* ===== Info Bar ===== */
    .info-bar {{
        background: rgba({panel_rgb}, 0.7);
        border: 1px solid rgba({accent_rgb}, 0.15);
        border-radius: 4px;
        padding: 8px 16px;
        margin-bottom: 16px;
        display: flex;
        gap: 24px;
        align-items: center;
        font-family: '{fb}', monospace;
        font-size: 0.85rem;
    }}
    .info-bar .info-item {{
        color: {c['text_dim']};
    }}
    .info-bar .info-item .info-value {{
        color: {c['cyan']};
        font-weight: bold;
    }}

    /* ===== Header ===== */
    .dashboard-header {{
        text-align: center;
        padding: 4px 0 8px 0;
    }}
    .dashboard-header .title {{
        font-family: '{fh}', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: 6px;
        text-transform: uppercase;
        background: linear-gradient(90deg, {c['cyan']}, {c['green']}, {c['cyan']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .dashboard-header .subtitle {{
        font-family: '{fb}', monospace;
        color: {c['text_dim']};
        font-size: 0.85rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-top: 4px;
    }}
    .dashboard-header .header-line {{
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba({accent_rgb}, 0.3), transparent);
        margin-top: 12px;
    }}

    /* ===== Entity Header Card (drill-down) ===== */
    .entity-header {{
        background: {c['card_bg']};
        border-radius: 8px;
        padding: 20px 24px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 20px;
    }}
    .entity-header .entity-name {{
        font-family: '{fh}', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: {c['text']};
        text-transform: uppercase;
        letter-spacing: 2px;
        flex: 1;
        word-wrap: break-word;
    }}
    .entity-header .entity-score {{
        font-family: '{fh}', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
    }}
    .entity-header .entity-level {{
        font-family: '{fh}', sans-serif;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 4px 12px;
        border-radius: 4px;
        border: 1px solid;
    }}

    /* ===== Back Button ===== */
    .back-btn {{
        font-family: '{fh}', sans-serif;
        color: {c['cyan']};
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.85rem;
        cursor: pointer;
    }}

    /* ===== Session Badge ===== */
    .session-active {{
        background: rgba({green_rgb}, 0.1);
        border: 1px solid {c['green']};
        border-radius: 4px;
        padding: 8px 12px;
        text-align: center;
    }}
    .session-active .session-label {{
        font-family: '{fh}', sans-serif;
        color: {c['green']};
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}
    .session-active .session-timer {{
        font-family: '{fb}', monospace;
        color: {c['green']};
        font-size: 1.4rem;
        margin-top: 4px;
    }}

    /* ===== Streamlit Header / Top Spacing ===== */
    header {{
        visibility: visible !important;
    }}
    [data-testid="stHeader"] {{
        visibility: visible !important;
        display: block !important;
        background: transparent !important;
        border-bottom: none !important;
        box-shadow: none !important;
    }}
    [data-testid="stToolbar"] {{
        background: transparent !important;
    }}
    [data-testid="stAppViewContainer"] > .main {{
        padding-top: 0 !important;
    }}
    [data-testid="stAppViewContainer"] .block-container {{
        padding-top: 0.1rem !important;
    }}
    @media (max-width: 768px) {{
        [data-testid="stAppViewContainer"] .block-container {{
            padding-top: 0.1rem !important;
        }}
    }}

    /* ===== Sidebar Toggle Visibility ===== */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"] {{
        visibility: visible !important;
        display: flex !important;
        opacity: 1 !important;
        z-index: 10050 !important;
        pointer-events: auto !important;
        background: transparent !important;
    }}
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="collapsedControl"] button,
    button[kind="header"][aria-label="Collapse sidebar"],
    button[kind="header"][aria-label="Expand sidebar"],
    button[kind="header"][aria-label="Open sidebar"],
    button[kind="header"][aria-label="Close sidebar"],
    button[kind="header"][aria-label="Show sidebar"],
    button[kind="header"][aria-label="Show sidebar navigation"],
    button[kind="header"][aria-label="Hide sidebar navigation"],
    button[aria-label="Collapse sidebar"],
    button[aria-label="Expand sidebar"],
    button[aria-label="Open sidebar"],
    button[aria-label="Close sidebar"],
    button[aria-label="Show sidebar"],
    button[aria-label="Show sidebar navigation"],
    button[aria-label="Hide sidebar navigation"],
    [data-testid*="collapsed"] button,
    [data-testid*="Collapsed"] button {{
        background: linear-gradient(135deg, rgba({accent_rgb}, 0.3), rgba({accent_rgb}, 0.12)) !important;
        border: 1px solid rgba({accent_rgb}, 0.85) !important;
        border-radius: 999px !important;
        color: #ffffff !important;
        opacity: 1 !important;
        box-shadow: 0 0 12px rgba({accent_rgb}, 0.35) !important;
        width: 2.25rem !important;
        height: 2.25rem !important;
        transition: all 0.2s ease !important;
    }}
    button[kind="header"][aria-label="Expand sidebar"],
    button[kind="header"][aria-label="Open sidebar"],
    button[kind="header"][aria-label="Show sidebar"],
    button[kind="header"][aria-label="Show sidebar navigation"],
    button[aria-label="Expand sidebar"],
    button[aria-label="Open sidebar"],
    button[aria-label="Show sidebar"],
    button[aria-label="Show sidebar navigation"],
    [data-testid="collapsedControl"] button,
    [data-testid*="collapsed"] button,
    [data-testid*="Collapsed"] button {{
        background-color: rgba({panel_rgb}, 0.95) !important;
        background-image: linear-gradient(135deg, rgba({accent_rgb}, 0.34), rgba({accent_rgb}, 0.10)) !important;
        border-color: rgba({accent_rgb}, 0.95) !important;
    }}
    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="collapsedControl"] button:hover,
    button[kind="header"][aria-label="Collapse sidebar"]:hover,
    button[kind="header"][aria-label="Expand sidebar"]:hover,
    button[kind="header"][aria-label="Open sidebar"]:hover,
    button[kind="header"][aria-label="Close sidebar"]:hover,
    button[kind="header"][aria-label="Show sidebar"]:hover,
    button[kind="header"][aria-label="Show sidebar navigation"]:hover,
    button[kind="header"][aria-label="Hide sidebar navigation"]:hover,
    button[aria-label="Collapse sidebar"]:hover,
    button[aria-label="Expand sidebar"]:hover,
    button[aria-label="Open sidebar"]:hover,
    button[aria-label="Close sidebar"]:hover,
    button[aria-label="Show sidebar"]:hover,
    button[aria-label="Show sidebar navigation"]:hover,
    button[aria-label="Hide sidebar navigation"]:hover,
    [data-testid*="collapsed"] button:hover,
    [data-testid*="Collapsed"] button:hover {{
        background: linear-gradient(135deg, rgba({accent_rgb}, 0.45), rgba({accent_rgb}, 0.2)) !important;
        box-shadow: 0 0 16px rgba({accent_rgb}, 0.55) !important;
        transform: translateY(-1px);
    }}
    [data-testid="stSidebarCollapseButton"] button svg,
    [data-testid="collapsedControl"] button svg,
    button[kind="header"][aria-label="Collapse sidebar"] svg,
    button[kind="header"][aria-label="Expand sidebar"] svg,
    button[kind="header"][aria-label="Open sidebar"] svg,
    button[kind="header"][aria-label="Close sidebar"] svg,
    button[kind="header"][aria-label="Show sidebar"] svg,
    button[kind="header"][aria-label="Show sidebar navigation"] svg,
    button[kind="header"][aria-label="Hide sidebar navigation"] svg,
    button[aria-label="Collapse sidebar"] svg,
    button[aria-label="Expand sidebar"] svg,
    button[aria-label="Open sidebar"] svg,
    button[aria-label="Close sidebar"] svg,
    button[aria-label="Show sidebar"] svg,
    button[aria-label="Show sidebar navigation"] svg,
    button[aria-label="Hide sidebar navigation"] svg,
    [data-testid*="collapsed"] button svg,
    [data-testid*="Collapsed"] button svg,
    [data-testid="stSidebarCollapseButton"] button svg path,
    [data-testid="collapsedControl"] button svg path,
    button[kind="header"][aria-label="Collapse sidebar"] svg path,
    button[kind="header"][aria-label="Expand sidebar"] svg path,
    button[kind="header"][aria-label="Open sidebar"] svg path,
    button[kind="header"][aria-label="Close sidebar"] svg path,
    button[kind="header"][aria-label="Show sidebar"] svg path,
    button[kind="header"][aria-label="Show sidebar navigation"] svg path,
    button[kind="header"][aria-label="Hide sidebar navigation"] svg path,
    button[aria-label="Collapse sidebar"] svg path,
    button[aria-label="Expand sidebar"] svg path,
    button[aria-label="Open sidebar"] svg path,
    button[aria-label="Close sidebar"] svg path,
    button[aria-label="Show sidebar"] svg path,
    button[aria-label="Show sidebar navigation"] svg path,
    button[aria-label="Hide sidebar navigation"] svg path,
    [data-testid*="collapsed"] button svg path,
    [data-testid*="Collapsed"] button svg path {{
        fill: #ffffff !important;
        stroke: #ffffff !important;
        color: #ffffff !important;
        filter: drop-shadow(0 0 6px rgba({accent_rgb}, 0.95));
    }}
    [data-testid="stSidebarCollapseButton"] button *,
    [data-testid="collapsedControl"] button *,
    button[kind="header"][aria-label="Collapse sidebar"] *,
    button[kind="header"][aria-label="Expand sidebar"] *,
    button[kind="header"][aria-label="Open sidebar"] *,
    button[kind="header"][aria-label="Close sidebar"] *,
    button[kind="header"][aria-label="Show sidebar"] *,
    button[kind="header"][aria-label="Show sidebar navigation"] *,
    button[kind="header"][aria-label="Hide sidebar navigation"] *,
    button[aria-label="Collapse sidebar"] *,
    button[aria-label="Expand sidebar"] *,
    button[aria-label="Open sidebar"] *,
    button[aria-label="Close sidebar"] *,
    button[aria-label="Show sidebar"] *,
    button[aria-label="Show sidebar navigation"] *,
    button[aria-label="Hide sidebar navigation"] *,
    [data-testid*="collapsed"] button *,
    [data-testid*="Collapsed"] button * {{
        color: #ffffff !important;
        fill: #ffffff !important;
        stroke: #ffffff !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #ffffff !important;
    }}

    /* ===== Hide Streamlit defaults ===== */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    [data-testid="stDecoration"] {{visibility: hidden; height: 0;}}
    """


def get_plotly_layout_defaults() -> dict:
    """Default Plotly layout properties for consistent chart theming."""
    c = config.COLORS
    accent_rgb = _hex_to_rgb(c["cyan"])
    panel_rgb = _hex_to_rgb(c["panel_bg"])
    return {
        "paper_bgcolor": "rgba(10, 14, 26, 0.0)",
        "plot_bgcolor": "rgba(10, 14, 26, 0.0)",
        "font": {
            "family": f"{config.FONT_BODY}, monospace",
            "color": c["text"],
            "size": 12,
        },
        "xaxis": {
            "gridcolor": f"rgba({accent_rgb}, 0.08)",
            "linecolor": f"rgba({accent_rgb}, 0.3)",
            "zerolinecolor": f"rgba({accent_rgb}, 0.08)",
            "tickfont": {"family": f"{config.FONT_BODY}, monospace", "color": c["text"]},
        },
        "yaxis": {
            "gridcolor": f"rgba({accent_rgb}, 0.08)",
            "linecolor": f"rgba({accent_rgb}, 0.3)",
            "zerolinecolor": f"rgba({accent_rgb}, 0.08)",
            "tickfont": {"family": f"{config.FONT_BODY}, monospace", "color": c["text"]},
        },
        "legend": {
            "bgcolor": f"rgba({panel_rgb}, 0.9)",
            "bordercolor": f"rgba({accent_rgb}, 0.3)",
            "borderwidth": 1,
            "font": {"family": f"{config.FONT_BODY}, monospace", "color": c["text"]},
        },
        "margin": {"l": 10, "r": 10, "t": 40, "b": 10},
    }


def _hex_to_rgb(hex_color: str) -> str:
    """Convert '#rrggbb' hex color to 'r, g, b' string for rgba()."""
    h = hex_color.lstrip("#")
    return f"{int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}"
