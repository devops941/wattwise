"""
WattWise UI Design System & Theme Engine
Enterprise-grade styling, modern typography, glassmorphism cards,
and cohesive aesthetic components for Streamlit.
"""

from pathlib import Path
import streamlit as st


def configure_sidebar_navigation():
    """Dynamically sets icons and friendly titles for Streamlit sidebar navigation."""
    try:
        from streamlit.source_util import get_pages
        pages = get_pages("app.py")
        page_config = {
            "app": ("Home", "🏠"),
            "1_Dashboard": ("Dashboard", "📊"),
            "2_Upload_Bill": ("Upload Bill", "📤"),
            "3_Analysis": ("Cycle Analysis", "📈"),
            "4_Peak_Consumption": ("Peak Discovery", "⚡"),
            "5_Prediction": ("Forecasting", "🔮"),
            "6_Bill_Estimation": ("Bill Estimation", "💰"),
            "7_Recommendations": ("Recommendations", "💡"),
            "8_Reports": ("Audit Reports", "📑"),
        }
        for p, info in pages.items():
            stem = Path(info.get("script_path", "")).stem
            for key, (friendly_title, icon) in page_config.items():
                if key == stem or key == info.get("page_name"):
                    info["page_name"] = friendly_title
                    info["icon"] = icon
    except Exception:
        pass


def apply_theme():
    """Injects modern, professional enterprise Glassmorphism CSS across the application."""
    configure_sidebar_navigation()

    st.markdown(
        """
        <style>
        /* Import High-Legibility Modern SaaS Typography */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        /* ── AMBIENT GLASSMORPHISM CANVAS ──────────────────────────────── */
        .stApp {
            background: radial-gradient(circle at 12% 15%, rgba(219, 234, 254, 0.55) 0%, transparent 45%),
                        radial-gradient(circle at 88% 22%, rgba(224, 231, 255, 0.50) 0%, transparent 45%),
                        radial-gradient(circle at 50% 80%, rgba(238, 242, 255, 0.60) 0%, transparent 55%),
                        #F8FAFC !important;
            min-height: 100vh;
        }

        /* Base Typography: Crisp, Large & Highly Readable */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            letter-spacing: -0.015em;
            font-size: 16px;
        }

        /* Prevent global font-size from overriding small text/badges/inputs in Streamlit internals */
        [class*="st-"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            letter-spacing: -0.015em;
        }

        code, pre, [class*="stCode"] {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.95rem !important;
        }

        /* Headings Hierarchy - Clean & Impactful */
        h1, [data-testid="stHeadingWithActionElements"] h1 {
            font-size: 2.35rem !important;
            font-weight: 850 !important;
            color: #0F172A !important;
            letter-spacing: -0.035em !important;
            line-height: 1.2 !important;
            margin-bottom: 0.6rem !important;
        }

        h2, [data-testid="stHeadingWithActionElements"] h2 {
            font-size: 1.70rem !important;
            font-weight: 750 !important;
            color: #0F172A !important;
            letter-spacing: -0.025em !important;
            line-height: 1.25 !important;
            margin-top: 1.2rem !important;
            margin-bottom: 0.5rem !important;
        }

        h3, [data-testid="stHeadingWithActionElements"] h3 {
            font-size: 1.40rem !important;
            font-weight: 700 !important;
            color: #1E293B !important;
            letter-spacing: -0.02em !important;
            margin-top: 1rem !important;
            margin-bottom: 0.4rem !important;
        }

        h4, [data-testid="stHeadingWithActionElements"] h4, h5 {
            font-size: 1.18rem !important;
            font-weight: 650 !important;
            color: #1E293B !important;
            letter-spacing: -0.01em !important;
        }

        /* Paragraphs & Markdown Text */
        p, div[data-testid="stMarkdownContainer"] p, .stMarkdown p {
            font-size: 1.05rem !important;
            line-height: 1.68 !important;
            color: #334155 !important;
        }

        /* Captions */
        .stCaption, [data-testid="stCaptionContainer"] {
            font-size: 0.92rem !important;
            color: #64748B !important;
            line-height: 1.55 !important;
        }

        /* Top Header & App Layout */
        .block-container {
            padding-top: 1.8rem !important;
            padding-bottom: 3.5rem !important;
            max-width: 1280px !important;
        }

        /* ── HIDE STREAMLIT CLOUD TOOLBAR, DEPLOY, FORK & STAR ICONS ──── */
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        .stDeployButton,
        #MainMenu,
        footer,
        div[data-testid="stStatusWidget"] {
            display: none !important;
            visibility: hidden !important;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
            height: 0px !important;
            min-height: 0px !important;
            padding: 0 !important;
        }

        /* Keep sidebar toggle button accessible when sidebar is closed */
        div[data-testid="stSidebarCollapsedControl"] {
            display: block !important;
            visibility: visible !important;
            position: fixed !important;
            top: 14px !important;
            left: 14px !important;
            z-index: 99999 !important;
            background: rgba(255, 255, 255, 0.85) !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 10px !important;
            border: 1px solid rgba(226, 232, 240, 0.9) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
        }

        /* ── ELECTRICITY ANIMATIONS & ENERGY GLOW ──────────────────────── */
        @keyframes electric-beam {
            0% {
                left: -100%;
                opacity: 0;
            }
            25% {
                opacity: 1;
            }
            75% {
                opacity: 1;
            }
            100% {
                left: 100%;
                opacity: 0;
            }
        }

        @keyframes electric-pulse {
            0%, 100% {
                box-shadow: 0 0 10px rgba(59, 130, 246, 0.4), 0 0 20px rgba(37, 99, 235, 0.2);
                border-color: rgba(147, 197, 253, 0.35);
            }
            50% {
                box-shadow: 0 0 22px rgba(96, 165, 250, 0.85), 0 0 38px rgba(59, 130, 246, 0.55), inset 0 0 8px rgba(147, 197, 253, 0.4);
                border-color: rgba(191, 219, 254, 0.95);
            }
        }

        @keyframes electric-bolt-glow {
            0%, 100% {
                filter: drop-shadow(0 0 3px rgba(250, 204, 21, 0.7));
                transform: scale(1);
            }
            50% {
                filter: drop-shadow(0 0 10px rgba(250, 204, 21, 1)) drop-shadow(0 0 16px rgba(251, 191, 36, 0.8));
                transform: scale(1.15);
            }
        }

        @keyframes electric-shimmer {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }

        /* ── DARK GLASSMORPHIC HERO HEADER ────────────────────────────── */
        .ww-hero {
            background: radial-gradient(120% 120% at 50% 0%, rgba(30, 58, 138, 0.95) 0%, rgba(15, 23, 42, 0.96) 75%, rgba(2, 6, 23, 0.98) 100%);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 24px;
            padding: 2.6rem 2.8rem;
            color: #FFFFFF;
            margin-bottom: 2.4rem;
            box-shadow: 0 20px 50px -15px rgba(15, 23, 42, 0.5), inset 0 1px 1px 0 rgba(255, 255, 255, 0.25);
            position: relative;
            overflow: hidden;
        }

        /* High-Voltage Scanning Electric Current along top border */
        .ww-hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 75%;
            height: 3px;
            background: linear-gradient(90deg, transparent, #38BDF8, #60A5FA, #93C5FD, #FFFFFF, #38BDF8, transparent);
            animation: electric-beam 4s cubic-bezier(0.4, 0, 0.2, 1) infinite;
            box-shadow: 0 0 14px #38BDF8, 0 0 28px #60A5FA;
            z-index: 2;
        }

        .ww-hero::after {
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 480px;
            height: 480px;
            background: radial-gradient(circle, rgba(59, 130, 246, 0.25) 0%, transparent 70%);
            pointer-events: none;
        }

        .ww-hero-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(255, 255, 255, 0.12);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.25);
            padding: 6px 16px;
            border-radius: 9999px;
            font-size: 0.84rem;
            font-weight: 700;
            color: #93C5FD;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 1.1rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            animation: electric-pulse 3.2s ease-in-out infinite;
        }

        .ww-hero-pill span:first-child {
            display: inline-block;
            animation: electric-bolt-glow 2s ease-in-out infinite;
        }

        .ww-hero-title {
            font-size: 2.55rem;
            font-weight: 900;
            line-height: 1.15;
            margin-bottom: 0.75rem;
            background: linear-gradient(135deg, #FFFFFF 15%, #BAE6FD 45%, #60A5FA 75%, #FFFFFF 100%);
            background-size: 250% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.04em;
            animation: electric-shimmer 6s ease-in-out infinite;
        }

        .ww-hero-subtitle {
            font-size: 1.10rem;
            font-weight: 450;
            color: #E2E8F0;
            line-height: 1.65;
            max-width: 900px;
            margin: 0;
        }

        /* ── FROSTED GLASS CARDS ───────────────────────────────────────── */
        .ww-glass-card, .ww-card {
            background: rgba(255, 255, 255, 0.72) !important;
            backdrop-filter: blur(18px) saturate(190%) !important;
            -webkit-backdrop-filter: blur(18px) saturate(190%) !important;
            border: 1px solid rgba(255, 255, 255, 0.85) !important;
            border-radius: 20px !important;
            padding: 1.8rem;
            box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.05),
                        0 1px 3px 0 rgba(0, 0, 0, 0.02),
                        inset 0 1px 1px 0 rgba(255, 255, 255, 0.9) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .ww-glass-card:hover, .ww-card:hover {
            background: rgba(255, 255, 255, 0.88) !important;
            border-color: rgba(59, 130, 246, 0.65) !important;
            transform: translateY(-4px) !important;
            box-shadow: 0 20px 42px -10px rgba(37, 99, 235, 0.20),
                        0 0 22px rgba(96, 165, 250, 0.22),
                        0 0 1px 1px rgba(255, 255, 255, 0.95) inset !important;
        }

        .ww-card-icon {
            width: 52px;
            height: 52px;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(239, 246, 255, 0.9) 0%, rgba(219, 234, 254, 0.8) 100%);
            color: #1D4ED8;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.6rem;
            margin-bottom: 1.1rem;
            border: 1px solid rgba(191, 219, 254, 0.9);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.10);
        }

        .ww-card-title {
            font-size: 1.25rem;
            font-weight: 750;
            color: #0F172A;
            margin-bottom: 0.45rem;
            letter-spacing: -0.02em;
        }

        .ww-card-desc {
            font-size: 0.98rem;
            color: #475569;
            line-height: 1.58;
            margin-bottom: 1.3rem;
            flex-grow: 1;
        }

        /* ── GLASS STEP CARDS (HOW IT WORKS) ───────────────────────────── */
        .ww-step-card {
            background: rgba(255, 255, 255, 0.68);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.85);
            border-radius: 18px;
            padding: 1.6rem;
            box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.04), inset 0 1px 1px rgba(255, 255, 255, 0.9);
            transition: all 0.22s ease;
            height: 100%;
        }

        .ww-step-card:hover {
            background: rgba(255, 255, 255, 0.85);
            transform: translateY(-3px);
            border-color: #60A5FA;
            box-shadow: 0 16px 32px -8px rgba(37, 99, 235, 0.14);
        }

        .ww-step-number {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: linear-gradient(135deg, #1D4ED8 0%, #3B82F6 100%);
            color: white;
            font-weight: 800;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1rem;
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);
        }

        /* ── FROSTED GLASS METRICS ─────────────────────────────────────── */
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.75) !important;
            backdrop-filter: blur(16px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
            border: 1px solid rgba(255, 255, 255, 0.85) !important;
            border-radius: 18px !important;
            padding: 1.25rem 1.4rem !important;
            box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.04),
                        inset 0 1px 1px rgba(255, 255, 255, 0.9) !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stMetric"]:hover {
            background: rgba(255, 255, 255, 0.92) !important;
            border-color: rgba(59, 130, 246, 0.45) !important;
            box-shadow: 0 12px 28px -6px rgba(37, 99, 235, 0.10) !important;
            transform: translateY(-2px) !important;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            color: #64748B !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            margin-bottom: 0.45rem !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 2.15rem !important;
            font-weight: 850 !important;
            color: #0F172A !important;
            letter-spacing: -0.035em !important;
            line-height: 1.15 !important;
        }

        [data-testid="stMetricDelta"] {
            font-size: 0.94rem !important;
            font-weight: 650 !important;
        }

        /* ── GLASS BUTTONS WITH REFLECTION ─────────────────────────────── */
        .stButton > button {
            border-radius: 12px !important;
            font-weight: 650 !important;
            font-size: 1.0rem !important;
            padding: 0.65rem 1.35rem !important;
            transition: all 0.2s ease-in-out !important;
            background: rgba(255, 255, 255, 0.75) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(203, 213, 225, 0.7) !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
        }

        .stButton > button:hover {
            border-color: #2563EB !important;
            color: #1D4ED8 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 18px rgba(37, 99, 235, 0.15) !important;
            background: rgba(255, 255, 255, 0.95) !important;
        }

        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35), inset 0 1px 1px rgba(255, 255, 255, 0.3) !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #1E40AF 0%, #1D4ED8 100%) !important;
            color: #FFFFFF !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(37, 99, 235, 0.45), inset 0 1px 1px rgba(255, 255, 255, 0.4) !important;
        }

        /* ── FROSTED GLASS FILE UPLOADER & DROPZONE REPAIR ─────────────── */
        [data-testid="stFileUploader"] {
            width: 100% !important;
            margin-bottom: 1.2rem !important;
        }

        [data-testid="stFileUploaderDropzone"] {
            background: rgba(255, 255, 255, 0.75) !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
            border: 2px dashed rgba(147, 197, 253, 0.8) !important;
            border-radius: 16px !important;
            padding: 1.8rem 1.4rem !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03), inset 0 1px 1px rgba(255, 255, 255, 0.9) !important;
            transition: all 0.2s ease-in-out !important;
        }

        [data-testid="stFileUploaderDropzone"]:hover {
            border-color: #2563EB !important;
            background: rgba(255, 255, 255, 0.92) !important;
            box-shadow: 0 8px 24px rgba(37, 99, 235, 0.12) !important;
        }

        /* Prevent text overlapping or collision in dropzone */
        [data-testid="stFileUploaderDropzone"] div[data-testid="stFileUploaderDropzoneInstructions"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: wrap !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 0.8rem !important;
            text-align: center !important;
        }

        [data-testid="stFileUploaderDropzone"] button,
        [data-testid="stFileUploaderDropzone"] button[data-testid="stBaseButton-secondary"] {
            font-size: 0.92rem !important;
            padding: 0.5rem 1.2rem !important;
            border-radius: 10px !important;
            margin: 0 !important;
            white-space: nowrap !important;
            height: auto !important;
            min-height: 38px !important;
            border: 1px solid #CBD5E1 !important;
            background: #FFFFFF !important;
            color: #1E293B !important;
            font-weight: 650 !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
        }

        [data-testid="stFileUploaderDropzone"] button:hover {
            border-color: #2563EB !important;
            color: #1D4ED8 !important;
            background: #F8FAFC !important;
        }

        [data-testid="stFileUploaderDropzone"] span {
            font-size: 0.92rem !important;
            color: #475569 !important;
            font-weight: 500 !important;
        }

        [data-testid="stFileUploaderDropzone"] small {
            font-size: 0.82rem !important;
            color: #64748B !important;
            font-weight: 500 !important;
        }

        /* ── TABS STYLING WITH FROSTED GLASS ───────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1.8rem !important;
            border-bottom: 2px solid rgba(226, 232, 240, 0.8) !important;
            padding-bottom: 0px !important;
            margin-bottom: 1.6rem !important;
            background: transparent !important;
        }

        .stTabs [data-baseweb="tab"] {
            height: auto !important;
            padding: 0.75rem 0.5rem !important;
            font-size: 1.05rem !important;
            font-weight: 650 !important;
            color: #64748B !important;
            border-bottom: 2px solid transparent !important;
            margin-bottom: -2px !important;
        }

        .stTabs [aria-selected="true"] {
            color: #1D4ED8 !important;
            border-bottom-color: #2563EB !important;
            font-weight: 750 !important;
        }

        /* ── FROSTED ALERTS & CALLOUTS ─────────────────────────────────── */
        [data-testid="stAlert"] {
            border-radius: 16px !important;
            border-width: 1px !important;
            padding: 1.0rem 1.3rem !important;
            font-size: 1.0rem !important;
            line-height: 1.62 !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03) !important;
        }

        [data-testid="stAlert"] p {
            font-size: 1.0rem !important;
            color: inherit !important;
        }

        /* Sliders & Inputs */
        .stSlider label, .stNumberInput label, .stTextInput label, .stSelectbox label {
            font-size: 1.02rem !important;
            font-weight: 650 !important;
            color: #1E293B !important;
            margin-bottom: 0.35rem !important;
        }

        /* Expanders */
        .streamlit-expanderHeader {
            border-radius: 14px !important;
            font-weight: 650 !important;
            font-size: 1.02rem !important;
            color: #1E293B !important;
            background: rgba(248, 250, 252, 0.8) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(226, 232, 240, 0.8) !important;
            padding: 0.75rem 1.0rem !important;
        }

        /* ── ENTERPRISE SIDEBAR STYLING & TOP REORDERING ────────────────── */
        [data-testid="stSidebar"] {
            background-color: rgba(255, 255, 255, 0.82) !important;
            backdrop-filter: blur(20px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
            border-right: 1px solid rgba(226, 232, 240, 0.85) !important;
            box-shadow: 2px 0 16px rgba(0, 0, 0, 0.02) !important;
        }

        /* Parent container holding stSidebarHeader, stSidebarNav, and stSidebarUserContent */
        div[data-testid="stSidebarContent"],
        section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] {
            display: flex !important;
            flex-direction: column !important;
        }

        /* Header (collapse button) at the very top */
        div[data-testid="stSidebarContent"] > div[data-testid="stSidebarHeader"] {
            order: 1 !important;
        }

        /* WattWise Brand Header sits at the TOP above navigation */
        div[data-testid="stSidebarContent"] > div[data-testid="stSidebarUserContent"] {
            order: 2 !important;
            padding-top: 0.2rem !important;
            padding-left: 0.95rem !important;
            padding-right: 0.95rem !important;
        }

        /* Navigation menu sits BELOW the brand header */
        div[data-testid="stSidebarContent"] > div[data-testid="stSidebarNav"],
        div[data-testid="stSidebarContent"] > nav[data-testid="stSidebarNav"] {
            order: 3 !important;
            padding-top: 0.2rem !important;
            padding-left: 0.95rem !important;
            padding-right: 0.95rem !important;
        }

        /* Hide the awkward default separator line */
        [data-testid="stSidebarNavSeparator"] {
            display: none !important;
        }

        /* Section header for the navigation: Crisp & Professional */
        [data-testid="stSidebarNav"]::before {
            content: "NAVIGATION MENU";
            display: block;
            font-size: 0.75rem;
            font-weight: 750;
            color: #94A3B8;
            letter-spacing: 0.08em;
            padding: 0.45rem 0.5rem 0.45rem 0.5rem;
            text-transform: uppercase;
        }

        [data-testid="stSidebarNav"] ul {
            gap: 4px !important;
            padding: 0 !important;
            list-style-type: none !important;
        }

        [data-testid="stSidebarNav"] li {
            margin-bottom: 3px !important;
        }

        /* Large, Prominent Sidebar Menu Links */
        [data-testid="stSidebarNav"] li a {
            display: flex !important;
            align-items: center !important;
            border-radius: 12px !important;
            padding: 0.65rem 0.90rem !important;
            color: #334155 !important;
            font-weight: 600 !important;
            font-size: 1.02rem !important;
            text-decoration: none !important;
            transition: all 0.15s ease-in-out !important;
            border: 1px solid transparent !important;
        }

        [data-testid="stSidebarNav"] li a:hover {
            background: rgba(241, 245, 249, 0.8) !important;
            color: #0F172A !important;
            transform: translateX(3px) !important;
            border-color: rgba(226, 232, 240, 0.8) !important;
        }

        /* Active Navigation Tab - Modern SaaS Gradient Pill */
        [data-testid="stSidebarNav"] li a[aria-current="page"] {
            background: linear-gradient(135deg, rgba(239, 246, 255, 0.95) 0%, rgba(219, 234, 254, 0.9) 100%) !important;
            color: #1D4ED8 !important;
            font-weight: 750 !important;
            border: 1px solid #BFDBFE !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
        }

        [data-testid="stSidebarNav"] li a span {
            font-size: 1.02rem !important;
            letter-spacing: -0.015em !important;
        }

        /* Custom Status Pill */
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 0.88rem;
            font-weight: 650;
            backdrop-filter: blur(8px);
        }
        .status-pill-green {
            background: rgba(236, 253, 245, 0.85);
            color: #065F46;
            border: 1px solid #A7F3D0;
        }
        .status-pill-blue {
            background: rgba(239, 246, 255, 0.85);
            color: #1E40AF;
            border: 1px solid #BFDBFE;
        }

        /* Badges */
        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .badge-blue { background: #DBEAFE; color: #1E40AF; border: 1px solid #BFDBFE; }
        .badge-green { background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; }
        .badge-amber { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_header():
    """Renders a sleek logo header at the top of the sidebar with prominent enterprise branding."""
    from src.household_manager import get_active_household, mask_consumer_name

    df, meta = get_active_household()

    with st.sidebar:
        # 1. Main Application Brand Card (Clean, Prominent and Top-Mounted)
        st.markdown(
            """
            <div style="padding: 0.3rem 0.2rem 1.0rem 0.2rem; border-bottom: 1px solid rgba(226, 232, 240, 0.8); margin-bottom: 0.8rem;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background: linear-gradient(135deg, #1D4ED8, #3B82F6); width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 850; font-size: 1.4rem; box-shadow: 0 6px 16px rgba(37,99,235,0.35);">⚡</div>
                    <div>
                        <div style="font-size: 1.35rem; font-weight: 850; color: #0F172A; letter-spacing: -0.035em; line-height: 1.15;">WattWise</div>
                        <div style="font-size: 0.78rem; color: #64748B; font-weight: 650; letter-spacing: 0.03em;">Energy Intelligence v2.1</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. Only show active household profile if bills are actually loaded;
        # When no household is selected, show NOTHING (no empty state boxes)
        if df is not None and len(df) > 0:
            is_demo = meta.get("is_demo", False) if meta else False
            raw_name = meta.get("consumer_name") or meta.get("name") or "Household" if meta else "Household"
            name = raw_name if is_demo else mask_consumer_name(raw_name)
            badge_label = "Demo" if is_demo else "Verified"
            badge_bg = "#EFF6FF" if is_demo else "#ECFDF5"
            badge_color = "#1D4ED8" if is_demo else "#059669"
            badge_border = "#BFDBFE" if is_demo else "#A7F3D0"

            st.markdown(
                f"""
                <div style="background: rgba(248, 250, 252, 0.85); backdrop-filter: blur(10px); border: 1px solid rgba(226, 232, 240, 0.9); border-radius: 12px; padding: 0.55rem 0.85rem; margin-bottom: 0.8rem; display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-size: 0.88rem; font-weight: 750; color: #0F172A; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 150px;">
                        👤 {name}
                    </span>
                    <span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border}; font-size: 0.70rem; font-weight: 750; padding: 2px 8px; border-radius: 9999px;">
                        {badge_label}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )
