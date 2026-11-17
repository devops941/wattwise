import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings('ignore')

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from src.household_manager import get_active_household, mask_consumer_name
from src.analyzer import analyze_consumption
from src.bill_calculator import calculate_energy_charge, TANGEDCO_OFFICIAL_TARIFF, TN_TARIFF_2024_25
from src.ui_theme import apply_theme, render_sidebar_header

st.set_page_config(
    page_title="Electricity Bill Estimation | WattWise",
    page_icon="💰",
    layout="wide",
)

apply_theme()
render_sidebar_header()

st.title("💰 Electricity Bill Estimation & Tariff Simulator")
st.caption("Accurate bi-monthly Tamil Nadu LT Domestic electricity bill simulator based on TANGEDCO / TNERC tariff schedules.")

# Check for active household
df, meta = get_active_household()
has_household = df is not None and len(df) > 0

if has_household:
    analysis = analyze_consumption(df)
    c_name = mask_consumer_name(meta.get("name") if meta else "Household")
    st.info(f"📊 **Household Context Loaded:** Showing presets based on active profile for **{c_name}** ({len(df)} cycles).")
else:
    analysis = {}
    st.info("ℹ️ **General Mode:** Simulating standard Tamil Nadu domestic bills. (Upload your bills anytime to personalize presets).")

# ── 1. SELECT OR ENTER CONSUMPTION ─────────────────────────────────────────
st.markdown("### 1. Select or Enter Bi-Monthly Consumption")

preset_cols = st.columns(5)

if has_household:
    min_u = analysis.get("min_units", 300)
    max_u = analysis.get("max_units", 900)
    avg_u = int(round(analysis.get("avg_units", 600)))
    last_u = analysis.get("units", [avg_u])[-1]

    with preset_cols[0]:
        if st.button(f"❄️ Baseline ({min_u} kWh)", use_container_width=True):
            st.session_state['estimator_units'] = min_u
    with preset_cols[1]:
        if st.button(f"🔥 Peak ({max_u} kWh)", use_container_width=True):
            st.session_state['estimator_units'] = max_u
    with preset_cols[2]:
        if st.button(f"⚡ Recent ({last_u} kWh)", use_container_width=True):
            st.session_state['estimator_units'] = last_u
    with preset_cols[3]:
        if st.button(f"📊 Average ({avg_u} kWh)", use_container_width=True):
            st.session_state['estimator_units'] = avg_u
    with preset_cols[4]:
        if st.button("🎯 Goal (500 kWh)", use_container_width=True):
            st.session_state['estimator_units'] = 500
    default_slider_val = st.session_state.get('estimator_units', avg_u)
else:
    with preset_cols[0]:
        if st.button("200 kWh (Low)", use_container_width=True):
            st.session_state['estimator_units'] = 200
    with preset_cols[1]:
        if st.button("400 kWh (Mod)", use_container_width=True):
            st.session_state['estimator_units'] = 400
    with preset_cols[2]:
        if st.button("600 kWh (Avg)", use_container_width=True):
            st.session_state['estimator_units'] = 600
    with preset_cols[3]:
        if st.button("800 kWh (High)", use_container_width=True):
            st.session_state['estimator_units'] = 800
    with preset_cols[4]:
        if st.button("1,000 kWh (Heavy)", use_container_width=True):
            st.session_state['estimator_units'] = 1000
    default_slider_val = st.session_state.get('estimator_units', 500)

col_input1, col_input2 = st.columns([3, 2])
with col_input1:
    units_input = st.slider(
        "Units Consumed in Billing Cycle (kWh):",
        min_value=50,
        max_value=2500,
        value=default_slider_val,
        step=10,
        help="Tamil Nadu domestic billing cycles are bi-monthly (every 60 days)."
    )
with col_input2:
    tariff_choice = st.selectbox(
        "Tariff Model:",
        options=["TANGEDCO LT-1A (2024-25 Official Revised)", "Simplified 3-Slab Model"]
    )

selected_tariff = TANGEDCO_OFFICIAL_TARIFF if "TANGEDCO" in tariff_choice else TN_TARIFF_2024_25
calc_result = calculate_energy_charge(units_input, selected_tariff)

st.divider()

# ── 2. KPI CARDS ───────────────────────────────────────────────────────────
st.markdown("### 2. Bill Calculation Summary")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="Total Estimated Bill",
        value=f"₹{calc_result['estimated_total']:,.2f}",
        delta=f"₹{calc_result['estimated_total']/units_input:.2f} / kWh" if units_input > 0 else "—"
    )

with kpi2:
    st.metric(
        label="Energy Charges",
        value=f"₹{calc_result['energy_charge']:,.2f}",
        help="Sum of slab-wise charges excluding fixed & surcharge"
    )

with kpi3:
    st.metric(
        label="Free Units Benefit",
        value=f"{calc_result['free_units_applied']} kWh",
        delta="100 Units Free (TN Govt. Subsidy)"
    )

with kpi4:
    fixed_plus_surcharge = calc_result['fixed_charge'] + calc_result['wheeling_surcharge']
    st.metric(
        label="Fixed & Surcharges",
        value=f"₹{fixed_plus_surcharge:,.2f}",
        help=f"Fixed charge ₹{calc_result['fixed_charge']} + Surcharge ₹{calc_result['wheeling_surcharge']}"
    )

# ── 3. BREAKDOWN TABLE AND CHART ───────────────────────────────────────────
col_table, col_pie = st.columns([3, 2])

with col_table:
    st.markdown("#### Tariff Slab-wise Calculation")
    slab_rows = []
    
    # 0-100 free units row
    slab_rows.append({
        "Consumption Slab": "0 - 100 units (Govt Free Subsidy)",
        "Units": calc_result['free_units_applied'],
        "Rate (₹/unit)": 0.00,
        "Amount (₹)": 0.00
    })
    
    for item in calc_result['slab_breakdown']:
        slab_rows.append({
            "Consumption Slab": item['slab'],
            "Units": item['units'],
            "Rate (₹/unit)": item['rate'],
            "Amount (₹)": item['amount']
        })
    
    slab_df = pd.DataFrame(slab_rows)
    st.dataframe(slab_df, use_container_width=True, hide_index=True)
    st.caption(f"ℹ️ {calc_result['disclaimer']}")

with col_pie:
    st.markdown("#### Cost Composition")
    cost_labels = ["Energy Charge", "Fixed Charge", "Electricity Surcharge"]
    cost_vals = [
        calc_result['energy_charge'],
        calc_result['fixed_charge'],
        calc_result['wheeling_surcharge']
    ]
    fig_donut = go.Figure(data=[go.Pie(
        labels=cost_labels,
        values=cost_vals,
        hole=0.45,
        marker=dict(colors=['#1976D2', '#FFA000', '#D32F2F'])
    )])
    fig_donut.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=260,
        font=dict(family="Plus Jakarta Sans, sans-serif", size=14),
        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_donut, use_container_width=True)

st.divider()

# ── 4. WHAT-IF ENERGY SAVING SIMULATOR ─────────────────────────────────────
st.markdown("### 3. 'What-If' Bill Reduction Simulator")
st.markdown(
    "Explore how small behavioral adjustments (such as optimizing AC temperature or running ceiling fans) "
    "affect your bill and help you avoid expensive higher tariff tiers."
)

sim_cols = st.columns([3, 3])
with sim_cols[0]:
    reduction_pct = st.slider("Target Consumption Reduction (%):", min_value=5, max_value=40, value=15, step=5)

target_units = int(round(units_input * (1 - reduction_pct / 100.0)))
target_bill = calculate_energy_charge(target_units, selected_tariff)
saved_units = units_input - target_units
saved_rupees = calc_result['estimated_total'] - target_bill['estimated_total']

with sim_cols[1]:
    st.markdown("#### Projected Savings")
    sub1, sub2 = st.columns(2)
    with sub1:
        st.metric("Units Saved", f"{saved_units} kWh", delta=f"-{reduction_pct}%")
    with sub2:
        saved_pct_rupees = (saved_rupees / calc_result['estimated_total'] * 100) if calc_result['estimated_total'] > 0 else 0
        st.metric("Money Saved / Cycle", f"₹{saved_rupees:,.2f}", delta=f"-{saved_pct_rupees:.1f}%")

if units_input > 500 and target_units <= 500:
    st.success(
        f"🎉 **Super-Saver Threshold Reached!** By dropping from {units_input} kWh to {target_units} kWh, "
        f"you stay under the 500 kWh threshold, entirely dodging higher tariff slab rates (₹8.40+/unit)!"
    )

st.caption("Note: Bill estimations simulate bi-monthly domestic current consumption under active Tamil Nadu tariff schedules. Actual physical bills may also reflect arrears, meter rent, or municipal adjustments.")
