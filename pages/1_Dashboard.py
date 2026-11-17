import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings('ignore')

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.household_manager import (
    get_active_household, activate_demo, clear_active_household,
    mask_consumer_name, mask_connection_no
)
from src.analyzer import analyze_consumption
from src.ui_theme import apply_theme, render_sidebar_header

st.set_page_config(
    page_title="Executive Dashboard | WattWise",
    page_icon="📊",
    layout="wide",
)

apply_theme()
render_sidebar_header()

df, meta = get_active_household()

# ── EMPTY STATE IF NO HOUSEHOLD LOADED ──────────────────────────────────────
if df is None or meta is None or len(df) == 0:
    st.title("📊 Executive Energy Dashboard")
    st.info("👋 **No Household Selected Yet.** Upload your own Tamil Nadu EB bills or explore the baseline demo dataset.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📤 Analyze Your Household")
        st.write("Upload single or multiple EB bill PDFs to view your customized analytics.")
        st.page_link("pages/2_Upload_Bill.py", label="Go to Upload Page →", use_container_width=True)
        
    with col2:
        st.markdown("### 📘 Explore Baseline Demo")
        st.write("Inspect the verified 5-cycle dataset for SENTHIL MURUGAN (Madurai).")
        if st.button("Load Demo Household (5 Bills) →", use_container_width=True, type="primary"):
            activate_demo()
            st.rerun()
            
    st.stop()

# ── ACTIVE HOUSEHOLD DASHBOARD ──────────────────────────────────────────────
analysis = analyze_consumption(df)
short_months = analysis['short_months']
units = analysis['units']
amounts = analysis['amounts']
is_demo = meta.get('is_demo', False)

# Header Banner
head_col1, head_col2 = st.columns([3, 1])
with head_col1:
    st.title("📊 Household Energy Dashboard")
    raw_name = meta.get('name') or "Household Consumer"
    raw_conn = meta.get('connection_no') or "N/A"
    section = meta.get('section') or "Domestic"
    
    disp_name = raw_name if is_demo else mask_consumer_name(raw_name)
    disp_conn = raw_conn if is_demo else mask_connection_no(raw_conn)
    
    badge = "📘 Baseline Demo" if is_demo else "🟢 Custom Household"
    st.caption(f"**Consumer:** `{disp_name}` | **Service No:** `{disp_conn}` | **Section:** `{section}` | **Status:** {badge}")

with head_col2:
    if is_demo:
        st.page_link("pages/2_Upload_Bill.py", label="Upload Your Bills ↗", use_container_width=True)
    else:
        if st.button("🔄 Switch Household", use_container_width=True):
            clear_active_household()
            st.rerun()

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Units Consumed",
        value=f"{analysis['total_units']:,} kWh",
        help=f"Across {len(df)} billing cycles"
    )

with col2:
    st.metric(
        label="Total Amount Paid",
        value=f"₹{analysis['total_amount']:,.0f}",
        delta=f"Avg ₹{analysis['avg_amount']:,.0f} / cycle"
    )

with col3:
    st.metric(
        label="Average Consumption",
        value=f"{analysis['avg_units']:.0f} kWh",
        help="Bi-monthly household average"
    )

with col4:
    st.metric(
        label="Peak Cycle",
        value=analysis['max_units_month'],
        delta=f"{analysis['max_units']} kWh",
        help=f"Lowest was {analysis['min_units_month']} ({analysis['min_units']} kWh)"
    )

st.divider()

# Charts
left_col, right_col = st.columns([3, 2])

with left_col:
    fig_line = go.Figure()
    if len(units) > 1:
        fig_line.add_trace(go.Scatter(
            x=short_months,
            y=units,
            mode='lines+markers+text',
            name='Units (kWh)',
            text=[f"{u} kWh" for u in units],
            textposition="top center",
            line=dict(color='#1565C0', width=3),
            marker=dict(size=9, color='#0D47A1', line=dict(color='white', width=2)),
            fill='tozeroy',
            fillcolor='rgba(21, 101, 192, 0.08)',
        ))
    else:
        fig_line.add_trace(go.Bar(
            x=short_months,
            y=units,
            name='Units (kWh)',
            marker_color='#1565C0',
            text=[f"{u} kWh" for u in units],
            textposition="outside",
        ))
        
    fig_line.update_layout(
        title="<b>Bi-Monthly Electricity Consumption Trend</b>",
        xaxis_title="Billing Cycle",
        yaxis_title="Units (kWh)",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Plus Jakarta Sans, sans-serif", size=14),
        margin=dict(l=40, r=20, t=50, b=40),
        showlegend=False,
    )
    fig_line.update_xaxes(showgrid=False)
    fig_line.update_yaxes(showgrid=True, gridcolor='#EEEEEE')
    st.plotly_chart(fig_line, use_container_width=True)

with right_col:
    fig_bar = px.bar(
        x=short_months,
        y=amounts,
        color=amounts,
        color_continuous_scale='Blues',
        text=[f"₹{a:,.0f}" for a in amounts],
        labels={'x': 'Billing Cycle', 'y': 'Amount (₹)', 'color': '₹'},
        title="<b>Electricity Bill Expenditure by Cycle</b>",
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Plus Jakarta Sans, sans-serif", size=14),
        margin=dict(l=40, r=20, t=50, b=40),
        coloraxis_showscale=False,
    )
    fig_bar.update_xaxes(showgrid=False)
    fig_bar.update_yaxes(showgrid=True, gridcolor='#EEEEEE')
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# Billing Summary Table
st.subheader("Billing Cycle History")

display_cols = ['billing_month', 'units_best_estimate', 'net_payable_rs', 'final_reading_kwh', 'data_quality_flag']
available_cols = [c for c in display_cols if c in df.columns]
df_display = df[available_cols].copy()

rename_map = {
    'billing_month': 'Billing Month',
    'units_best_estimate': 'Units (kWh)',
    'net_payable_rs': 'Net Payable (₹)',
    'final_reading_kwh': 'Meter Reading (kWh)',
    'data_quality_flag': 'Data Quality / Method'
}
df_display.rename(columns={k: v for k, v in rename_map.items() if k in df_display.columns}, inplace=True)

if 'Net Payable (₹)' in df_display.columns:
    df_display['Net Payable (₹)'] = df_display['Net Payable (₹)'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "—")
if 'Meter Reading (kWh)' in df_display.columns:
    df_display['Meter Reading (kWh)'] = df_display['Meter Reading (kWh)'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "—")

st.dataframe(df_display, use_container_width=True, hide_index=True)

# Quick action pills
action_col1, action_col2, action_col3, action_col4 = st.columns(4)
with action_col1:
    st.page_link("pages/3_Analysis.py", label="Detailed Analysis →", use_container_width=True)
with action_col2:
    st.page_link("pages/4_Peak_Consumption.py", label="Peak Load Discovery →", use_container_width=True)
with action_col3:
    st.page_link("pages/6_Bill_Estimation.py", label="Tariff Simulator →", use_container_width=True)
with action_col4:
    st.page_link("pages/8_Reports.py", label="Download PDF Report →", use_container_width=True)
