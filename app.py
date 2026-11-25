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
from src.bill_calculator import calculate_energy_charge, TANGEDCO_OFFICIAL_TARIFF

st.set_page_config(
    page_title="WattWise | Household Energy Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global enterprise Glassmorphism styling
apply_theme()
render_sidebar_header()

df, meta = get_active_household()

# ── HERO HEADER ────────────────────────────────────────────────────────────
st.markdown("""
<div class="ww-hero">
    <div class="ww-hero-pill">
        <span>⚡</span>
        <span>Tamil Nadu Electricity Analytics &bull; TANGEDCO LT-1A 2024-25</span>
    </div>
    <div class="ww-hero-title">WattWise Energy Intelligence</div>
    <div class="ww-hero-subtitle">
        Automated consumption intelligence, cycle-by-cycle trend discovery, and certified TANGEDCO tariff simulation.
        Empowering Tamil Nadu households to audit electricity invoices with complete privacy and zero data leakage.
    </div>
</div>
""", unsafe_allow_html=True)

# ── CASE 1: NO ACTIVE HOUSEHOLD (PUBLIC ONBOARDING & SAAS LANDING PAGE) ────
if df is None or meta is None:
    # ── 1. PRIMARY ONBOARDING CARDS ──
    st.markdown("### 🚀 Start Your Energy Audit")
    st.caption("Choose your onboarding path to analyze household consumption or inspect the verified baseline:")

    cta_col1, cta_col2 = st.columns(2)

    with cta_col1:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div class="ww-card-icon">📤</div>
                    <span class="badge badge-blue">Upload & Audit</span>
                </div>
                <div class="ww-card-title">Analyze Your Household</div>
                <div class="ww-card-desc">
                    Upload your own Tamil Nadu EB bill PDFs (e-invoices or scanned bills). 
                    WattWise automatically extracts meter readings, validates consumption, 
                    and generates your personalized energy audit.
                </div>
                <div style="margin-bottom: 1.2rem; font-size: 0.95rem; color: #334155; line-height: 1.7;">
                    <div>🔒 <b>100% Private:</b> Zero cloud uploads, processed entirely on your device.</div>
                    <div>📄 <b>Batch Upload:</b> Supports single or multi-cycle PDFs.</div>
                    <div>⚡ <b>Dual Engine:</b> Instant digital extraction with Tesseract OCR fallback.</div>
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
                <div class="ww-card-title">Explore Academic Demo</div>
                <div class="ww-card-desc">
                    Inspect the verified research dataset of 5 authentic historical Tamil Nadu EB bills 
                    for consumer SENTHIL MURUGAN (KOODALNAGAR Section, Madurai).
                </div>
                <div style="margin-bottom: 1.2rem; font-size: 0.95rem; color: #334155; line-height: 1.7;">
                    <div>📊 <b>5 Historical Cycles:</b> Feb 2026 to Oct 2026.</div>
                    <div>🔥 <b>Thermal Surge:</b> 911 kWh summer peak vs 437 kWh monsoon baseline.</div>
                    <div>📑 <b>Certified PDF:</b> Download publication-ready audit report.</div>
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
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        st.markdown("### 📁 Saved Household Profiles on this Device")
        s_cols = st.columns(min(len(saved), 3))
        for idx, s_meta in enumerate(saved[:3]):
            with s_cols[idx]:
                st.markdown(f"**🏠 {mask_consumer_name(s_meta['name'])}**")
                st.caption(f"Conn: `{mask_connection_no(s_meta['connection_no'])}` • {s_meta.get('cycles_count', 0)} cycles")
                if st.button(f"Open Profile", key=f"open_{s_meta['id']}", use_container_width=True):
                    activate_household(s_meta['id'])
                    st.rerun()

    st.divider()

    # ── 2. LIVE INTERACTIVE TANGEDCO TARIFF ESTIMATOR PREVIEW ──
    st.markdown("### ⚡ Live TANGEDCO LT-1A Tariff Estimator")
    st.caption("Experience our domestic tariff simulation engine in real-time. Adjust the slider to see slab charges and 100 free units subsidy:")

    sim_col_left, sim_col_right = st.columns([1, 2])
    with sim_col_left:
        test_units = st.slider(
            "Bi-Monthly Consumption (kWh):",
            min_value=50,
            max_value=1200,
            value=450,
            step=10,
            help="TANGEDCO domestic bills are computed on a 2-month bi-monthly cycle."
        )
        st.markdown("""
        <div style="font-size: 0.88rem; color: #64748B; background: rgba(255, 255, 255, 0.65); padding: 12px; border-radius: 12px; border: 1px solid rgba(203, 213, 225, 0.6); margin-top: 10px;">
            💡 <b>Subsidy Policy:</b> First 100 units are <b>100% Free</b> under Tamil Nadu Govt scheme. Charges apply strictly to units exceeding 100 kWh.
        </div>
        """, unsafe_allow_html=True)

    with sim_col_right:
        calc_result = calculate_energy_charge(test_units, TANGEDCO_OFFICIAL_TARIFF)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Units", f"{test_units} kWh", delta="100 Units Free", delta_color="normal")
        with m2:
            st.metric("Energy Charges", f"₹{calc_result['energy_charge']:,.2f}")
        with m3:
            st.metric("Fixed & Wheeling", f"₹{calc_result['fixed_charge'] + calc_result['wheeling_surcharge']:,.2f}")
        with m4:
            unit_rate = calc_result['estimated_total'] / test_units if test_units > 0 else 0
            st.metric("Net Payable", f"₹{calc_result['estimated_total']:,.2f}", delta=f"₹{unit_rate:.2f}/unit", delta_color="inverse")

        # Mini slab progress breakdown pill
        slabs_summary = " &bull; ".join([f"{s['slab']}: ₹{s['amount']:.0f}" for s in calc_result['slab_breakdown'][:3]])
        if len(calc_result['slab_breakdown']) > 3:
            slabs_summary += f" &bull; +{len(calc_result['slab_breakdown']) - 3} higher slabs"
        st.markdown(
            f"""
            <div style="font-size: 0.90rem; color: #1E3A8A; background: rgba(219, 234, 254, 0.6); border: 1px solid rgba(191, 219, 254, 0.8); border-radius: 10px; padding: 8px 14px; margin-top: 10px;">
                <b>Slab Distribution:</b> {slabs_summary}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # ── 3. HOW IT WORKS 3-STEP WALKTHROUGH ──
    st.markdown("### 🔄 How WattWise Works")
    st.caption("A seamless 3-step pipeline designed for speed, precision, and privacy:")

    step1, step2, step3 = st.columns(3)

    with step1:
        st.markdown("""
        <div class="ww-step-card">
            <div class="ww-step-number">1</div>
            <div style="font-size: 1.18rem; font-weight: 750; color: #0F172A; margin-bottom: 0.5rem;">Upload EB Invoices</div>
            <div style="font-size: 0.95rem; color: #475569; line-height: 1.6;">
                Feed your official Tamil Nadu digital e-receipts or scanned paper bills. Our dual-engine PDF & OCR automatically extracts dates, previous/current meter readings, and billed units without manual typing.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with step2:
        st.markdown("""
        <div class="ww-step-card">
            <div class="ww-step-number">2</div>
            <div style="font-size: 1.18rem; font-weight: 750; color: #0F172A; margin-bottom: 0.5rem;">Automated Audit & Verification</div>
            <div style="font-size: 0.95rem; color: #475569; line-height: 1.6;">
                Every cycle is cross-audited against certified TANGEDCO LT-1A tariffs. The system confirms the 100-unit government subsidy, flags consumption anomalies, and checks billing arithmetic.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with step3:
        st.markdown("""
        <div class="ww-step-card">
            <div class="ww-step-number">3</div>
            <div style="font-size: 1.18rem; font-weight: 750; color: #0F172A; margin-bottom: 0.5rem;">Actionable Intelligence & Reports</div>
            <div style="font-size: 0.95rem; color: #475569; line-height: 1.6;">
                Uncover seasonal cooling surges, forecast next-cycle expenditures with predictive models, simulate energy-saving appliance retrofits, and export publication-ready audit reports in PDF.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── 4. CORE CAPABILITIES (3x2 GLASS GRID) ──
    st.markdown("### ⚡ Platform Capabilities & Modules")
    st.caption("Comprehensive analytics suite built specifically for Tamil Nadu domestic consumers:")

    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div class="ww-card-icon">📄</div>
                <div class="ww-card-title">Dual PDF & OCR Extraction</div>
                <div class="ww-card-desc">
                    Hybrid parser capable of handling digital e-invoices, vector PDFs, and scanned physical receipts with Tesseract OCR fallback.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div class="ww-card-icon">⚖️</div>
                <div class="ww-card-title">Certified TANGEDCO LT-1A Audit</div>
                <div class="ww-card-desc">
                    Built strictly to TNERC 2024-25 domestic tariff rules with non-linear progressive slabs and 100 units free government subsidy verification.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with f3:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div class="ww-card-icon">📈</div>
                <div class="ww-card-title">Bi-Monthly Cycle Analytics</div>
                <div class="ww-card-desc">
                    In-depth breakdown of daily consumption velocity, per-unit cost shifts, seasonal variances, and cycle-over-cycle acceleration.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    f4, f5, f6 = st.columns(3)

    with f4:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div class="ww-card-icon">❄️</div>
                <div class="ww-card-title">Peak-Load & Cooling Discovery</div>
                <div class="ww-card-desc">
                    Isolate thermal cooling spikes during peak Tamil Nadu heatwaves (April–June) and benchmark monsoon baseline efficiency.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with f5:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div class="ww-card-icon">🔮</div>
                <div class="ww-card-title">Predictive Forecasting Models</div>
                <div class="ww-card-desc">
                    Ordinary Least Squares (OLS) regression and Moving Average algorithms predicting next-cycle power usage and expenditure.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with f6:
        st.markdown("""
        <div class="ww-card">
            <div>
                <div class="ww-card-icon">💡</div>
                <div class="ww-card-title">Appliance Savings Simulator</div>
                <div class="ww-card-desc">
                    Interactive what-if scenarios modeling direct ₹ savings from upgrading to 5-Star Inverter ACs, BLDC fans, and LED fixtures.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── CASE 2: HOUSEHOLD IS ACTIVE (DASHBOARD & MODULE ACCESS) ────────────────
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

# ── DATA PRIVACY & SECURITY ARCHITECTURE ──────────────────────────────────
st.markdown("### 🛡️ Enterprise Security & Data Privacy Architecture")
st.caption("Designed with zero-trust privacy principles. Your financial and consumption records remain strictly confidential:")
p1, p2, p3 = st.columns(3)
with p1:
    st.markdown("""
    <div class="ww-card" style="padding: 1.4rem;">
        <div>
            <div style="font-size: 1.3rem; margin-bottom: 0.5rem;">🔒</div>
            <div style="font-weight: 750; color: #0F172A; font-size: 1.05rem; margin-bottom: 0.35rem;">100% Client-Side Processing</div>
            <div style="font-size: 0.92rem; color: #475569; line-height: 1.6;">
                All PDF parsing, OCR, and mathematical computations run locally in memory. No bill data is uploaded to external third-party cloud servers or LLMs.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with p2:
    st.markdown("""
    <div class="ww-card" style="padding: 1.4rem;">
        <div>
            <div style="font-size: 1.3rem; margin-bottom: 0.5rem;">🛡️</div>
            <div style="font-weight: 750; color: #0F172A; font-size: 1.05rem; margin-bottom: 0.35rem;">Isolated Household Workspaces</div>
            <div style="font-size: 0.92rem; color: #475569; line-height: 1.6;">
                Each household's bills are isolated in separate storage partitions. Multiple households never cross-contaminate or mix session data.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with p3:
    st.markdown("""
    <div class="ww-card" style="padding: 1.4rem;">
        <div>
            <div style="font-size: 1.3rem; margin-bottom: 0.5rem;">👁️</div>
            <div style="font-weight: 750; color: #0F172A; font-size: 1.05rem; margin-bottom: 0.35rem;">Automated PII Anonymization</div>
            <div style="font-size: 0.92rem; color: #475569; line-height: 1.6;">
                Consumer names and service numbers are automatically masked in analytical dashboards and reports (e.g. <code>SEN***</code>, <code>***4917</code>).
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── FOOTER & PLATFORM LINKS ────────────────────────────────────────────────
st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.92rem; padding: 22px 0 10px 0; border-top: 1px solid rgba(203, 213, 225, 0.6);">
    <b>WattWise Energy Intelligence Platform</b> &bull; Built for Tamil Nadu Domestic Consumers (TANGEDCO LT-1A Tariff Order 2024-25)<br>
    <a href="https://wattwise-analytics.streamlit.app/" target="_blank" style="color: #2563EB; text-decoration: none; font-weight: 600;">Live Web App</a> &bull;
    <a href="https://github.com/devops941/wattwise" target="_blank" style="color: #2563EB; text-decoration: none; font-weight: 600;">GitHub Repository</a> &bull;
    <a href="https://github.com/devops941/wattwise/blob/main/DOCUMENTATION.md" target="_blank" style="color: #2563EB; text-decoration: none; font-weight: 600;">System Documentation</a>
</div>
""", unsafe_allow_html=True)
