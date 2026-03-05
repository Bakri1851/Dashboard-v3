# theme.py — Sci-fi neon theme CSS generation
import functools

import config


@functools.lru_cache(maxsize=1)
def get_google_fonts_import() -> str:
    """HTML style block importing Orbitron and Share Tech Mono from Google Fonts."""
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');
    </style>
    """


@functools.lru_cache(maxsize=1)
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
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
        gap: 0.35rem;
    }}
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        margin: 0.2rem 0 0.3rem 0 !important;
        line-height: 1.2;
    }}
    section[data-testid="stSidebar"] [data-testid="stButton"] {{
        margin: 0.1rem 0 !important;
    }}
    section[data-testid="stSidebar"] hr {{
        margin: 0.45rem 0 !important;
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

    /* ===== Sidebar Session Blocks ===== */
    section[data-testid="stSidebar"] .lab-code-card {{
        background: rgba({accent_rgb}, 0.08);
        border: 1px solid {c['cyan']};
        border-radius: 8px;
        padding: 12px;
        margin-top: 8px;
        margin-bottom: 4px;
        text-align: center;
        display: block;
        position: relative;
        z-index: 1;
    }}
    section[data-testid="stSidebar"] .lab-code-label {{
        font-family: '{fb}', monospace;
        color: {c['text_dim']};
        font-size: 0.65rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }}
    section[data-testid="stSidebar"] .lab-code-value {{
        font-family: '{fh}', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: {c['cyan']};
        letter-spacing: 6px;
        line-height: 1.2;
        text-shadow: 0 0 16px rgba({accent_rgb}, 0.5);
        white-space: nowrap;
    }}
    section[data-testid="stSidebar"] .session-action-gap {{
        display: block;
        height: 0.35rem;
    }}
    @media (max-width: 1200px) {{
        section[data-testid="stSidebar"] .lab-code-value {{
            font-size: 1.5rem;
            letter-spacing: 4px;
        }}
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

    /* ===== View Transition (smooth re-render) ===== */
    section.main > div {{
        animation: fadeIn 0.15s ease-in;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0.6; }}
        to   {{ opacity: 1.0; }}
    }}
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


@functools.lru_cache(maxsize=1)
def get_mobile_css() -> str:
    """Mobile-optimized CSS for lab_app.py. Designed for 375px+ phone screens."""
    c = config.COLORS
    fh = config.FONT_HEADING
    fb = config.FONT_BODY
    accent_rgb = _hex_to_rgb(c["cyan"])
    panel_rgb = _hex_to_rgb(c["panel_bg"])

    return f"""
    /* ===== Mobile Reset ===== */
    .stApp {{
        background: linear-gradient(180deg, {c['dark_bg']} 0%, {c['panel_bg']} 100%);
        color: {c['text']};
        font-family: '{fb}', monospace;
    }}
    [data-testid="stAppViewContainer"] .block-container {{
        max-width: 480px;
        margin: 0 auto;
        padding: 0.75rem 1rem 3rem 1rem !important;
    }}

    /* Hide sidebar on mobile */
    section[data-testid="stSidebar"] {{ display: none !important; }}
    [data-testid="collapsedControl"] {{ display: none !important; }}
    [data-testid="stSidebarCollapseButton"] {{ display: none !important; }}

    /* ===== Headings ===== */
    h1, h2, h3, h4 {{
        color: {c['cyan']} !important;
        font-family: '{fh}', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0.5rem 0 0.25rem 0 !important;
    }}

    /* ===== Body Text ===== */
    p, li, span, div, td, th, label {{
        font-family: '{fb}', monospace;
    }}

    /* ===== Full-width large buttons ===== */
    .stButton > button {{
        background: linear-gradient(135deg, rgba({accent_rgb}, 0.2), rgba({accent_rgb}, 0.05));
        color: {c['cyan']};
        border: 1px solid {c['cyan']};
        font-family: '{fh}', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
        border-radius: 8px;
        min-height: 52px;
        font-size: 0.9rem;
        width: 100%;
    }}
    .stButton > button:hover {{
        background: rgba({accent_rgb}, 0.3);
        box-shadow: 0 0 18px rgba({accent_rgb}, 0.4);
        color: #ffffff;
    }}

    /* ===== Inputs ===== */
    .stTextInput > div > div > input {{
        background-color: {c['dark_bg']};
        border: 1px solid rgba({accent_rgb}, 0.45);
        color: {c['text']};
        font-family: '{fb}', monospace;
        font-size: 1.05rem;
        min-height: 48px;
        border-radius: 6px;
    }}
    .stTextInput > label {{
        color: {c['text']} !important;
        font-family: '{fb}', monospace !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    /* ===== Session Code Display ===== */
    .lab-code-display {{
        background: rgba({accent_rgb}, 0.08);
        border: 2px solid {c['cyan']};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 12px 0;
        box-shadow: 0 0 24px rgba({accent_rgb}, 0.2);
    }}
    .lab-code-display .code-label {{
        font-family: '{fb}', monospace;
        color: {c['text_dim']};
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 3px;
    }}
    .lab-code-display .code-value {{
        font-family: '{fh}', sans-serif;
        font-size: 2.6rem;
        font-weight: 700;
        color: {c['cyan']};
        letter-spacing: 8px;
        text-shadow: 0 0 20px rgba({accent_rgb}, 0.6);
        margin-top: 6px;
    }}

    /* ===== Assistant Session Status Strip ===== */
    .assistant-session-strip {{
        background: rgba({accent_rgb}, 0.08);
        border: 1px solid rgba({accent_rgb}, 0.45);
        border-radius: 10px;
        padding: 10px 12px;
        margin: 8px 0 12px 0;
    }}
    .assistant-session-strip-label {{
        font-family: '{fb}', monospace;
        color: {c['text_dim']};
        font-size: 0.66rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    .assistant-session-strip-meta {{
        display: flex;
        justify-content: space-between;
        gap: 10px;
        flex-wrap: wrap;
        font-family: '{fb}', monospace;
        font-size: 0.78rem;
        color: {c['text']};
    }}

    /* ===== Student Card (assigned view) ===== */
    .student-card {{
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
    }}
    .student-card .card-label {{
        font-family: '{fb}', monospace;
        color: {c['text_dim']};
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-bottom: 6px;
    }}
    .student-card .student-id {{
        font-family: '{fh}', sans-serif;
        color: {c['text']};
        font-size: 1.05rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        word-break: break-all;
    }}
    .student-card .score-value {{
        font-family: '{fh}', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        margin-top: 8px;
        line-height: 1.1;
    }}

    /* ===== Struggle Badge ===== */
    .struggle-badge {{
        display: inline-block;
        padding: 5px 14px;
        border-radius: 20px;
        font-family: '{fh}', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 1px solid;
        margin-top: 8px;
    }}

    /* ===== Student List Item (unassigned view) ===== */
    .student-list-item {{
        background: rgba({panel_rgb}, 0.7);
        border-radius: 8px;
        padding: 12px 14px;
        margin: 6px 0;
        border-left: 3px solid;
    }}

    /* ===== Section Label ===== */
    .section-label {{
        font-family: '{fb}', monospace;
        color: {c['cyan']};
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin: 16px 0 8px 0;
    }}

    /* ===== Status message ===== */
    .status-ended {{
        text-align: center;
        padding: 48px 0;
    }}

    /* ===== Divider ===== */
    hr {{
        border-color: rgba({accent_rgb}, 0.15) !important;
        margin: 12px 0 !important;
    }}

    /* ===== Alert/Info boxes ===== */
    [data-testid="stAlert"] {{
        border-radius: 8px;
        font-family: '{fb}', monospace;
    }}


    /* ===== Hide Streamlit defaults ===== */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    [data-testid="stDecoration"] {{visibility: hidden; height: 0;}}
    [data-testid="stHeader"] {{
        background: transparent !important;
        border-bottom: none !important;
        box-shadow: none !important;
    }}
    [data-testid="stToolbar"] {{ background: transparent !important; }}
    """


def _hex_to_rgb(hex_color: str) -> str:
    """Convert '#rrggbb' hex color to 'r, g, b' string for rgba()."""
    h = hex_color.lstrip("#")
    return f"{int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}"
