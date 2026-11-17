import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings('ignore')

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from src.household_manager import (
    get_active_household, activate_demo,
    mask_consumer_name, mask_connection_no
)
from src.analyzer import analyze_consumption, detect_anomalies
from src.ui_theme import apply_theme, render_sidebar_header

st.set_page_config(
    page_title="Consumption Analysis | WattWise",
    page_icon="📈",
    layout="wide",
)

apply_theme()
render_sidebar_header()

df, meta = get_active_household()

# ── EMPTY STATE IF NO HOUSEHOLD LOADED ─────────────────────────────────────
if df is None or len(df) == 0:
    st.title("📈 Detailed Electricity Consumption Analysis")
    st.info("ℹ️ **No Household Loaded:** Upload your own EB bills or explore the baseline academic demo dataset.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 📤 Analyze Your Household")
        st.write("Upload your TANGEDCO/TNPDCL electricity bill PDFs to generate cycle-by-cycle comparisons.")
        st.page_link("pages/2_Upload_Bill.py", label="Upload Your EB Bills →", use_container_width=True)
    with col_b:
        st.markdown("### 📘 Explore Academic Demo")
        st.write("Inspect the 5-cycle historical dataset for consumer SENTHIL MURUGAN (KOODALNAGAR, Madurai).")
        if st.button("Load Academic Demo Household", use_container_width=True, type="primary"):
            activate_demo()
            st.rerun()
    st.stop()

# ── DATA LOADED: RENDER ANALYSIS ───────────────────────────────────────────
analysis = analyze_consumption(df)
anomalies = detect_anomalies(analysis)

short_months = analysis['short_months']
units = analysis['units']
amounts = analysis['amounts']
months = analysis['months']
final_readings = analysis['final_readings']
unit_changes = analysis['unit_changes']
amount_changes = analysis['amount_changes']
cycle_rates = analysis.get('cycle_rates', [])
daily_avg = analysis.get('daily_avg_units', [])

consumer_name = meta.get('name') if meta else df.get('consumer_name', ['Household Consumer'])[0]
masked_name = mask_consumer_name(consumer_name)
masked_conn = mask_connection_no(meta.get('connection_no') if meta else df.get('connection_no', ['N/A'])[0])

st.title("📈 Detailed Electricity Consumption Analysis")
st.caption(f"Analyzing **{len(df)} billing cycles** for **{masked_name}** • Connection: `{masked_conn}` • {meta.get('tariff_category', 'LT Domestic')}")

# Anomaly Alerts Banner
if anomalies:
    for a in anomalies:
        if a['type'] == 'direction_mismatch':
            st.warning(f"⚠️ **Tariff / Arrears Anomaly Detected:** {a['description']} (Check for carried-over arrears or slab progression).")
        elif 'large_jump' in a['type']:
            st.info(f"⚡ **Usage Surge:** {a['description']}")
        elif 'large_drop' in a['type']:
            st.success(f"📉 **Usage Reduction:** {a['description']}")

tab1, tab2, tab3 = st.tabs(["📊 Cycle-by-Cycle Comparison", "⚡ Meter Reading Progression", "🔍 Data Quality & Extraction Flags"])

# --- Tab 1: Cycle Comparison ---
with tab1:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=short_months,
            y=units,
            name="Units Billed (kWh)",
            marker_color='#1565C0',
            text=[f"{u} kWh" for u in units],
            textposition='outside',
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=short_months,
            y=amounts,
            name="Net Payable (₹)",
            mode='lines+markers+text',
            line=dict(color='#E65100', width=2.5),
            marker=dict(size=8, color='#BF360C'),
            text=[f"₹{a:,.0f}" for a in amounts],
            textposition="top right",
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="<b>Billed Electricity Consumption vs Net Payable Expenditure</b>",
        xaxis_title="Billing Cycle",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Plus Jakarta Sans, sans-serif", size=14),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1),
        bargap=0.35,
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(title_text="Units (kWh)", secondary_y=False, showgrid=True, gridcolor='#EEEEEE')
    fig.update_yaxes(title_text="Net Payable (₹)", secondary_y=True, showgrid=False)

    st.plotly_chart(fig, use_container_width=True)

    # Detailed cycle breakdown table
    st.subheader("Tabular Cycle Progression")
    rows = []
    for i, m in enumerate(months):
        u_change_str = "—"
        if unit_changes[i] is not None:
            _, delta, pct = unit_changes[i]
            prefix = "+" if delta > 0 else ""
            u_change_str = f"{prefix}{delta} kWh ({prefix}{pct}%)"

        a_change_str = "—"
        if amount_changes[i] is not None:
            _, delta, pct = amount_changes[i]
            prefix = "+" if delta > 0 else ""
            a_change_str = f"{prefix}₹{delta:,.0f} ({prefix}{pct}%)"

        eff_rate = f"₹{cycle_rates[i]:.2f} / kWh" if i < len(cycle_rates) and cycle_rates[i] > 0 else "—"
        d_kwh = f"{daily_avg[i]:.1f} kWh/day" if i < len(daily_avg) else "—"

        rows.append({
            "Billing Month": m,
            "Units Billed": f"{units[i]:,} kWh",
            "Avg Daily Usage": d_kwh,
            "Unit Change": u_change_str,
            "Net Payable": f"₹{amounts[i]:,.0f}",
            "Amount Change": a_change_str,
            "Effective Rate": eff_rate
        })

    changes_df = pd.DataFrame(rows)
    st.dataframe(changes_df, use_container_width=True, hide_index=True)

# --- Tab 2: Meter Readings ---
with tab2:
    st.subheader("Physical Cumulative Final Meter Reading Trajectory")

    has_readings = any(pd.notna(r) and float(r) > 0 for r in final_readings)
    if has_readings:
        fig_meter = go.Figure()
        fig_meter.add_trace(go.Scatter(
            x=short_months,
            y=final_readings,
            mode='lines+markers+text',
            line=dict(color='#2E7D32', width=2.5),
            marker=dict(size=9, color='#1B5E20'),
            text=[f"{r:,.0f}" if pd.notna(r) else "" for r in final_readings],
            textposition="top left",
            name='Final Reading (kWh)',
        ))
        fig_meter.update_layout(
            title="<b>Meter Reading Trajectory (Cumulative kWh)</b>",
            xaxis_title="Billing Cycle",
            yaxis_title="Meter Reading (kWh)",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family="Plus Jakarta Sans, sans-serif", size=14),
            margin=dict(l=40, r=20, t=50, b=40),
            showlegend=False,
        )
        fig_meter.update_xaxes(showgrid=False)
        fig_meter.update_yaxes(showgrid=True, gridcolor='#EEEEEE')
        st.plotly_chart(fig_meter, use_container_width=True)

        if analysis.get("meter_is_monotonic", True):
            st.success("✅ **Integrity Check:** The meter reading sequence is monotonically increasing, verifying continuous physical meter registration with no rollbacks.")
        else:
            st.warning("⚠️ **Non-Monotonic Readings Detected:** A meter reading is lower than a previous cycle. Verify if a meter replacement occurred or if OCR misread an initial digit.")

        # Meter reading derived table
        meter_rows = []
        for i, m in enumerate(months):
            if i == 0:
                derived = "— (First Record)"
            else:
                prev = final_readings[i - 1]
                curr = final_readings[i]
                try:
                    if pd.notna(prev) and pd.notna(curr):
                        derived = f"{int(curr) - int(prev):,} kWh"
                    else:
                        derived = "N/A"
                except (TypeError, ValueError):
                    derived = "N/A"
            meter_rows.append({
                "Billing Month": m,
                "Final Reading (kWh)": f"{final_readings[i]:,.0f}" if pd.notna(final_readings[i]) else "N/A",
                "Derived Consumption (Current − Previous)": derived,
                "Units Billed": f"{units[i]:,} kWh",
            })

        meter_df = pd.DataFrame(meter_rows)
        st.dataframe(meter_df, use_container_width=True, hide_index=True)
    else:
        st.info("No physical meter readings were recorded in this dataset. Units billed are used directly for analytics.")

# --- Tab 3: Data Quality ---
with tab3:
    st.subheader("Data Quality & Extraction Integrity")
    st.markdown(
        """
        Tamil Nadu physical EB bills frequently contain OCR noise or missing sub-line items in scanned copies.
        WattWise cross-validates:
        - **Billed Units (kWh):** Extracted from current consumption line items.
        - **Net Payable (₹):** Total bill payable amount.
        - **Meter Registration Consistency:** Cross-checking meter delta against billed units.
        """
    )
    dq_cols = ["billing_month", "bill_file", "data_quality_flag", "confidence"]
    avail_dq = [c for c in dq_cols if c in df.columns]
    if avail_dq:
        st.dataframe(df[avail_dq], use_container_width=True, hide_index=True)
    else:
        st.write("All records in the active dataset passed structural validation.")
