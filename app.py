import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
warnings.filterwarnings('ignore')

import streamlit as st
import pandas as pd

from src.ui_theme import apply_theme, render_sidebar_header
from src.data_processor import get_dataframe_info
from src.household_manager import (
    get_active_household, activate_demo, clear_active_household,
    mask_consumer_name, mask_connection_no, list_saved_households, activate_household
)

st.set_page_config(
    page_title="WattWise | Household Energy Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global enterprise SaaS styling
apply_theme()
render_sidebar_header()

df, meta = get_active_household()

# ── HERO HEADER ────────────────────────────────────────────────────────────
st.markdown("""
<div class="ww-hero">
    <div class="ww-hero-pill">
        <span>⚡</span>
        <span>Tamil Nadu Electricity Analytics &bull; TANGEDCO LT-1A</span>
    </div>
    <div class="ww-hero-title">WattWise Energy Intelligence</div>
    <div class="ww-hero-subtitle">
        Automated consumption intelligence, cycle-by-cycle trend discovery, and certified TANGEDCO tariff simulation.
        Empowering Tamil Nadu households to analyze electricity invoices with complete privacy and zero data leakage.
    </div>
</div>
""", unsafe_allow_html=True)

# ── CASE 1: NO ACTIVE HOUSEHOLD (PUBLIC ONBOARDING STATE) ──────────────────
if df is None or meta is None:
    st.markdown("### Get Started with WattWise")
    st.caption("Select an onboarding path to begin your household energy analysis:")

    cta_col1, cta_col2 = st.columns(2)

    with cta_col1:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div class="ww-card-icon">📤</div>
                    <span class="badge badge-blue">New Household</span>
                </div>
                <div class="ww-card-title">Analyze Your Own Household</div>
                <div class="ww-card-desc">
                    Upload your own Tamil Nadu EB bill PDFs (e-invoices or scanned bills). 
                    WattWise automatically extracts meter readings, validates consumption, 
                    and generates your personalized energy audit.
                </div>
                <div style="margin-bottom: 1.2rem; font-size: 0.96rem; color: #334155; line-height: 1.68;">
                    <div>🔒 <b>100% Private:</b> Stored in your private local session.</div>
                    <div>📄 <b>Batch Upload:</b> Supports single or multi-cycle PDFs.</div>
                    <div>⚡ <b>Instant OCR:</b> Automated reading extraction & verification.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/2_Upload_Bill.py", label="Upload Your EB Bills Now →", use_container_width=True)

    with cta_col2:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div class="ww-card-icon">📘</div>
                    <span class="badge badge-green">Baseline Demo</span>
                </div>
                <div class="ww-card-title">Explore Academic Demonstration</div>
                <div class="ww-card-desc">
                    Inspect the verified research dataset of 5 authentic historical Tamil Nadu EB bills 
                    for consumer SENTHIL MURUGAN (KOODALNAGAR Section, Madurai).
                </div>
                <div style="margin-bottom: 1.2rem; font-size: 0.96rem; color: #334155; line-height: 1.68;">
                    <div>📊 <b>5 Historical Cycles:</b> Feb 2026 to Oct 2026.</div>
                    <div>🔥 <b>Peak Discovery:</b> Summer heat (911 kWh) vs Monsoon relief.</div>
                    <div>📑 <b>Audit Report:</b> Download verified publication-grade PDF.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Explore Demo Household (Senthil Murugan) →", use_container_width=True, type="primary"):
            activate_demo()
            st.rerun()

    # Saved Profiles (if any saved households exist on disk)
    saved = list_saved_households()
    if saved:
        st.divider()
        st.markdown("### 📁 Saved Household Profiles on this Device")
        s_cols = st.columns(min(len(saved), 3))
        for idx, s_meta in enumerate(saved[:3]):
            with s_cols[idx]:
                st.markdown(f"**🏠 {mask_consumer_name(s_meta['name'])}**")
                st.caption(f"Conn: `{mask_connection_no(s_meta['connection_no'])}` • {s_meta.get('cycles_count', 0)} cycles")
                if st.button(f"Open Profile", key=f"open_{s_meta['id']}", use_container_width=True):
                    activate_household(s_meta['id'])
                    st.rerun()

# ── CASE 2: HOUSEHOLD IS ACTIVE ────────────────────────────────────────────
else:
    info = get_dataframe_info(df)
    is_demo = meta.get("is_demo", False)
    
    # Active Status Bar
    bar_col1, bar_col2 = st.columns([3, 1])
    with bar_col1:
        if is_demo:
            st.markdown(
                """
                <div class="status-pill status-pill-blue">
                    <span>📘</span>
                    <span><b>Active Profile:</b> Academic Demo (SENTHIL MURUGAN &bull; 5 cycles)</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            disp_name = mask_consumer_name(meta.get('name'))
            disp_conn = mask_connection_no(meta.get('connection_no'))
            st.markdown(
                f"""
                <div class="status-pill status-pill-green">
                    <span>🟢</span>
                    <span><b>Active Profile:</b> {disp_name} &bull; Connection: {disp_conn} ({info['n_records']} cycles loaded)</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    with bar_col2:
        if is_demo:
            st.page_link("pages/2_Upload_Bill.py", label="Upload Your Own Bills ↗", use_container_width=True)
        else:
            if st.button("🔄 Switch Household", use_container_width=True):
                clear_active_household()
                st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Executive KPI Metric Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Consumption", f"{info['total_units']:,} kWh", help="Cumulative consumption across loaded cycles")
    with kpi2:
        st.metric("Total Expenditure", f"₹{info['total_amount']:,.0f}", help="Total net payable across loaded cycles")
    with kpi3:
        st.metric("Billing Cycles", f"{info['n_records']} Cycles", help="Bi-monthly billing periods analyzed")
    with kpi4:
        avg_units = round(info['total_units'] / info['n_records'], 1) if info['n_records'] > 0 else 0
        st.metric("Bi-Monthly Average", f"{avg_units:.0f} kWh", help="Bi-monthly mean consumption")

    st.divider()

    # Modern Module Navigation Cards
    st.markdown("### Household Intelligence Modules")
    st.caption("Access in-depth analytical tools calibrated for your active household:")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div class="ww-card-icon">📊</div>
                <div class="ww-card-title">Executive Dashboard</div>
                <div class="ww-card-desc">Interactive consumption trend, bill spending, and physical meter sequence.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/1_Dashboard.py", label="Open Dashboard →", use_container_width=True)

    with c2:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div class="ww-card-icon">📈</div>
                <div class="ww-card-title">Cycle Analysis</div>
                <div class="ww-card-desc">Cycle-by-cycle comparisons, unit rate progression, and anomaly alerts.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/3_Analysis.py", label="View Analysis →", use_container_width=True)

    with c3:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div class="ww-card-icon">⚡</div>
                <div class="ww-card-title">Peak-Load Discovery</div>
                <div class="ww-card-desc">Discover summer cooling peaks and seasonal weather alignments.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/4_Peak_Consumption.py", label="Discover Peaks →", use_container_width=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div class="ww-card-icon">🔮</div>
                <div class="ww-card-title">Experimental Forecast</div>
                <div class="ww-card-desc">Next-cycle predictions using linear regression & moving average models.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/5_Prediction.py", label="View Forecast →", use_container_width=True)

    with c5:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div class="ww-card-icon">💰</div>
                <div class="ww-card-title">Tariff Simulator</div>
                <div class="ww-card-desc">Simulate TANGEDCO LT-1A bills with 100 free units & What-If calculator.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/6_Bill_Estimation.py", label="Simulate Bill →", use_container_width=True)

    with c6:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div class="ww-card-icon">📑</div>
                <div class="ww-card-title">Download PDF Report</div>
                <div class="ww-card-desc">Generate a personalized formal PDF audit report for this household.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.page_link("pages/8_Reports.py", label="Download Report →", use_container_width=True)

st.divider()

# Privacy & Security Assurance
st.markdown("### Data Privacy & Security Standard")
p1, p2, p3 = st.columns(3)
with p1:
    st.markdown("##### 🔒 Private Household Workspaces")
    st.caption("Each household's bills are isolated in their own private directory. No data is mixed across users.")
with p2:
    st.markdown("##### 🛡️ Consumer Anonymization")
    st.caption("Consumer names and service numbers are masked in analytical views (`SEN***`, `***4917`).")
with p3:
    st.markdown("##### ⚙️ Local Offline Processing")
    st.caption("All PDF parsing, OCR, and calculations run locally on your machine. Documents are never transmitted to external cloud servers.")
