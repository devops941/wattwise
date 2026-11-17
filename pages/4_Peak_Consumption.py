import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings('ignore')

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from src.household_manager import get_active_household, activate_demo, mask_consumer_name, mask_connection_no
from src.analyzer import analyze_consumption, detect_anomalies, get_peak_analysis
from src.ui_theme import apply_theme, render_sidebar_header

st.set_page_config(
    page_title="Peak Consumption Discovery | WattWise",
    page_icon="⚡",
    layout="wide",
)

apply_theme()
render_sidebar_header()

df, meta = get_active_household()

# ── EMPTY STATE IF NO HOUSEHOLD LOADED ─────────────────────────────────────
if df is None or len(df) == 0:
    st.title("⚡ Peak Consumption & Load Discovery")
    st.info("ℹ️ **No Household Loaded:** Upload your own EB bills or explore the baseline academic demo dataset.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 📤 Analyze Your Household")
        st.write("Upload your TANGEDCO/TNPDCL bills to identify peak billing cycles and seasonal load swings.")
        st.page_link("pages/2_Upload_Bill.py", label="Upload Your EB Bills →", use_container_width=True)
    with col_b:
        st.markdown("### 📘 Explore Academic Demo")
        st.write("Inspect the summer peak (911 kWh) vs monsoon dip (613 kWh) for Senthil Murugan.")
        if st.button("Load Academic Demo Household", use_container_width=True, type="primary"):
            activate_demo()
            st.rerun()
    st.stop()

# ── DATA LOADED: RENDER PEAK ANALYSIS ──────────────────────────────────────
analysis = analyze_consumption(df)
peak = get_peak_analysis(analysis)

short_months = analysis['short_months']
units = analysis['units']
amounts = analysis['amounts']
months = analysis['months']
unit_changes = analysis['unit_changes']
daily_avg = analysis.get('daily_avg_units', [])

consumer_name = meta.get('name') if meta else "Household Consumer"
masked_name = mask_consumer_name(consumer_name)
masked_conn = mask_connection_no(meta.get('connection_no') if meta else "N/A")

st.title("⚡ Peak Consumption & Load Discovery")
st.caption(f"Analyzing peak cycles for **{masked_name}** • Connection: `{masked_conn}` • Data Granularity: {peak.get('data_granularity')}")

st.info(
    "🔬 **Analytical Boundary & Scientific Scope:** This analysis is strictly grounded in actual bi-monthly billing-cycle totals. "
    "Because standard Tamil Nadu domestic meters are read bi-monthly (every 60 days), intra-day, hourly, or appliance-level peak demands "
    "cannot be measured without high-frequency smart meters and are not claimed. Peak discovery identifies cycle-level seasonal cooling demand and high-slab exposure."
)

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Peak Cycle Consumption",
        value=f"{peak['peak_units']} kWh",
        delta=f"Highest Cycle: {peak['peak_month']}",
        delta_color="inverse"
    )

with col2:
    st.metric(
        label="Lowest Baseline Cycle",
        value=f"{peak['trough_units']} kWh",
        delta=f"Baseline Cycle: {peak['trough_month']}",
    )

with col3:
    st.metric(
        label="Peak Expenditure",
        value=f"₹{peak['peak_amount']:,.0f}",
        delta=f"Month: {peak['peak_amount_month']}",
        delta_color="inverse"
    )

with col4:
    st.metric(
        label="Seasonal Variation Range",
        value=f"{peak['range_units']} kWh",
        delta=f"{peak['pct_variation']:.1f}% swing",
        delta_color="inverse"
    )

st.divider()

# Highlighted Bar Chart
peak_month = peak['peak_month']
trough_month = peak['trough_month']

bar_colors = []
for m in months:
    if m == peak_month:
        bar_colors.append('#C62828')     # red for peak
    elif m == trough_month:
        bar_colors.append('#2E7D32')     # green for trough
    else:
        bar_colors.append('#1976D2')     # primary blue for intermediate cycles

fig_peak = go.Figure()
fig_peak.add_trace(go.Bar(
    x=short_months,
    y=units,
    marker_color=bar_colors,
    text=[f"{u} kWh" for u in units],
    textposition='outside',
    name='Units (kWh)',
))
fig_peak.update_layout(
    title="<b>Cycle Consumption Spectrum — Peak (Red) | Trough (Green) | Standard (Blue)</b>",
    xaxis_title="Billing Cycle",
    yaxis_title="Units (kWh)",
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Plus Jakarta Sans, sans-serif", size=14),
    margin=dict(l=40, r=20, t=60, b=40),
    showlegend=False,
)
fig_peak.update_xaxes(showgrid=False)
fig_peak.update_yaxes(showgrid=True, gridcolor='#EEEEEE')

st.plotly_chart(fig_peak, use_container_width=True)

# Average Daily Consumption Comparison
if daily_avg:
    st.subheader("📅 Average Daily Consumption (kWh/day)")
    st.caption("Normalized daily consumption across 60-day bi-monthly billing intervals.")
    
    fig_daily = go.Figure()
    fig_daily.add_trace(go.Scatter(
        x=short_months,
        y=daily_avg,
        mode='lines+markers+text',
        line=dict(color='#6A1B9A', width=2.5),
        marker=dict(size=8, color='#4A148C'),
        text=[f"{d:.1f}" for d in daily_avg],
        textposition="top center",
        name='Daily Avg (kWh/day)'
    ))
    fig_daily.update_layout(
        title="<b>Daily Run-Rate Intensity per Billing Cycle</b>",
        xaxis_title="Billing Cycle",
        yaxis_title="kWh / Day",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Plus Jakarta Sans, sans-serif", size=14),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    fig_daily.update_xaxes(showgrid=False)
    fig_daily.update_yaxes(showgrid=True, gridcolor='#EEEEEE')
    st.plotly_chart(fig_daily, use_container_width=True)

st.divider()

# Largest Increases and Decreases
valid_changes = [(m, c, p) for entry in unit_changes if entry is not None for m, c, p in [entry]]
increases = sorted([x for x in valid_changes if x[1] > 0], key=lambda x: x[1], reverse=True)
decreases = sorted([x for x in valid_changes if x[1] < 0], key=lambda x: x[1])

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("📈 Steepest Consumption Surges")
    top_increases = increases[:2]
    if top_increases:
        for month_name, change, pct in top_increases:
            st.metric(
                label=f"Surge in {month_name}",
                value=f"+{change} kWh",
                delta=f"+{pct}% vs previous cycle",
                delta_color="inverse"
            )
    else:
        st.info("No significant increases recorded.")

with right_col:
    st.subheader("📉 Steepest Consumption Reductions")
    top_decreases = decreases[:2]
    if top_decreases:
        for month_name, change, pct in top_decreases:
            st.metric(
                label=f"Drop in {month_name}",
                value=f"{change} kWh",
                delta=f"{pct}% vs previous cycle",
            )
    else:
        st.info("No significant drops recorded.")

st.divider()

# Dynamic Climate Context
st.subheader("Tamil Nadu Climate & Seasonal Context")
st.markdown(
    f"""
    - **Observed Peak Cycle ({peak['peak_month']}):** Reached **{peak['peak_units']} kWh**, with an average daily draw of **{peak.get('peak_daily_avg', 0):.1f} kWh/day**. 
      In Tamil Nadu, peaks typically coincide with peak summer months (April–June) when ambient temperatures routinely exceed 38°C–42°C and cooling loads intensify.
    - **Observed Trough Cycle ({peak['trough_month']}):** Dropped to **{peak['trough_units']} kWh** (**{peak.get('trough_daily_avg', 0):.1f} kWh/day**), representing your household's baseline non-cooling consumption.
    - **Seasonal Swing:** Your household experienced a **{peak['pct_variation']:.1f}% consumption swing** between winter/monsoon baseline and peak cooling demand.
    """
)

# Anomaly Alerts
anomalies = detect_anomalies(analysis)
if anomalies:
    st.divider()
    st.subheader("Detected Billing Discrepancies")
    for anomaly in anomalies:
        st.warning(f"⚠️ **{anomaly['type'].replace('_', ' ').title()}:** {anomaly['description']}")
