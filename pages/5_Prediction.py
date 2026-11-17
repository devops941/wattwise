import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings('ignore')

import streamlit as st
import plotly.graph_objects as go

from src.household_manager import get_active_household, activate_demo, mask_consumer_name
from src.analyzer import analyze_consumption
from src.predictor import forecast_next_cycle
from src.ui_theme import apply_theme, render_sidebar_header

st.set_page_config(
    page_title="Experimental Consumption Prediction | WattWise",
    page_icon="🔮",
    layout="wide",
)

apply_theme()
render_sidebar_header()

df, meta = get_active_household()

# ── EMPTY STATE IF NO HOUSEHOLD LOADED ─────────────────────────────────────
if df is None or len(df) == 0:
    st.title("🔮 Experimental Consumption & Bill Prediction")
    st.info("ℹ️ **No Household Loaded:** Upload your own EB bills or explore the baseline academic demo dataset.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 📤 Analyze Your Household")
        st.write("Upload at least 2 TANGEDCO/TNPDCL bills to compute experimental projections.")
        st.page_link("pages/2_Upload_Bill.py", label="Upload Your EB Bills →", use_container_width=True)
    with col_b:
        st.markdown("### 📘 Explore Academic Demo")
        st.write("Inspect experimental regression and moving average models on Senthil Murugan's 5 cycles.")
        if st.button("Load Academic Demo Household", use_container_width=True, type="primary"):
            activate_demo()
            st.rerun()
    st.stop()

if len(df) < 2:
    st.title("🔮 Experimental Consumption & Bill Prediction")
    st.warning("⚠️ **Insufficient Historical Data:** At least 2 sequential billing cycles are required to compute trend and moving-average projections.")
    st.page_link("pages/2_Upload_Bill.py", label="Upload More Bills →", use_container_width=False)
    st.stop()

# ── DATA LOADED: RENDER PREDICTION ─────────────────────────────────────────
analysis = analyze_consumption(df)
forecast = forecast_next_cycle(analysis['units'], analysis['amounts'])

last_month = analysis['months'][-1] if analysis['months'] else "Last Cycle"
forecast_cycle_label = f"Next Cycle (After {last_month})"

consumer_name = meta.get('name') if meta else "Household Consumer"
masked_name = mask_consumer_name(consumer_name)

st.title("🔮 Experimental Consumption & Bill Prediction")
st.caption(f"Experimental forecasting for **{masked_name}** based on {len(df)} historical billing periods.")

st.warning(
    "⚠️ **Educational & Experimental Estimate Only:** "
    f"This projection is synthesized from {len(df)} historical bi-monthly billing cycles. "
    "In scientific time-series analytics, 24–36 continuous cycles are recommended to capture seasonal recurrence and climate oscillations. "
    "These estimations illustrate regression and moving-average mechanics and must not be treated as guaranteed utility bills."
)

st.subheader(f"Upcoming Billing Period Projections ({forecast_cycle_label})")

col_left, col_right = st.columns(2)

with col_left:
    st.metric(
        label="Linear Trend Forecast (OLS)",
        value=f"{forecast['linear']['predicted_units']} kWh",
        delta=f"Trend: {forecast['linear']['trend']} (slope = {forecast['linear']['slope']:+.1f} kWh/cycle)"
    )
    st.caption(f"Ordinary Least Squares regression (R² = {forecast['linear']['r_squared']:.2f})")

with col_right:
    st.metric(
        label=f"Moving Average Forecast ({forecast['moving_avg']['window']}-Cycle Window)",
        value=f"{forecast['moving_avg']['predicted_units']} kWh",
        delta=f"Smoothed over recent {forecast['moving_avg']['window']} cycles"
    )
    st.caption("Averages recent cycles to dampen extreme seasonal spikes")

st.divider()

# Scenario Analysis
st.subheader("Scenario-based Expenditure Estimation")
base_pred_units = forecast['moving_avg']['predicted_units']
avg_rate = analysis.get('overall_effective_rate', 6.0)
if avg_rate <= 0:
    avg_rate = 6.0

sc1, sc2, sc3 = st.columns(3)

with sc1:
    opt_units = max(0, int(round(base_pred_units * 0.90)))
    opt_amt = opt_units * (avg_rate * 0.92)
    st.info(f"🟢 **Optimistic Scenario (-10%)**\n\n**{opt_units} kWh**\n\nEstimated Bill: **₹{opt_amt:,.0f}**\n\n*Assumes active thermostat management and milder ambient weather.*")

with sc2:
    base_amt = base_pred_units * avg_rate
    st.success(f"🔵 **Base Case (Expected)**\n\n**{base_pred_units} kWh**\n\nEstimated Bill: **₹{base_amt:,.0f}**\n\n*Assumes standard historical routine under current consumption habits.*")

with sc3:
    pess_units = max(0, int(round(base_pred_units * 1.12)))
    pess_amt = pess_units * (avg_rate * 1.08)
    st.warning(f"🔴 **Pessimistic Scenario (+12%)**\n\n**{pess_units} kWh**\n\nEstimated Bill: **₹{pess_amt:,.0f}**\n\n*Assumes extended cooling runtime or progression into higher tariff tiers.*")

st.divider()

# Visual Comparison Chart
short_months = analysis['short_months']
units = analysis['units']
forecast_month = "Next Cycle (Est.)"

fig = go.Figure()

# Actual historical bars
fig.add_trace(go.Bar(
    x=short_months,
    y=units,
    name="Actual Billed Units",
    marker_color='#1565C0',
    text=[f"{u} kWh" for u in units],
    textposition='outside',
))

# Forecast markers
fig.add_trace(go.Scatter(
    x=[forecast_month],
    y=[forecast['linear']['predicted_units']],
    mode='markers+text',
    name="Linear Trend Forecast",
    marker=dict(color='#FFA000', size=14, symbol='diamond'),
    text=[f"{forecast['linear']['predicted_units']} kWh"],
    textposition='top center',
    textfont=dict(size=12, color='#FFA000', family="Arial"),
))

fig.add_trace(go.Scatter(
    x=[forecast_month],
    y=[forecast['moving_avg']['predicted_units']],
    mode='markers+text',
    name="Moving Average Forecast",
    marker=dict(color='#00897B', size=14, symbol='circle'),
    text=[f"{forecast['moving_avg']['predicted_units']} kWh"],
    textposition='bottom center',
    textfont=dict(size=12, color='#00897B', family="Arial"),
))

fig.update_layout(
    title="<b>Actual Historical Consumption vs Experimental Forecasts</b>",
    xaxis_title="Billing Cycle",
    yaxis_title="Units Consumed (kWh)",
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Plus Jakarta Sans, sans-serif", size=14),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1),
    bargap=0.35,
)
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=True, gridcolor='#EEEEEE')

st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Methodology Assumptions & Constraints")
planning_min = max(0, int(base_pred_units * 0.95))
planning_max = max(0, int(base_pred_units * 1.05))
planning_cost_min = int(planning_min * avg_rate)
planning_cost_max = int(planning_max * avg_rate)

st.markdown(
    f"""
    - **Data Granularity:** The dataset contains bi-monthly cumulative billing totals, smoothing over weekly weather fluctuations.
    - **Tariff & Arrears Separation:** Predictions forecast physical units (kWh) first; monetary bill estimates apply your effective rate (₹{avg_rate:.2f}/kWh).
    - **Statistical Minimum:** For multi-parameter seasonal time-series models (e.g. SARIMA or Holt-Winters), a minimum of 24–36 monthly cycles is mathematically necessary.
    - **Recommended Planning Budget:** For household budgeting, the expected range of **{planning_min} – {planning_max} kWh** (approx. **₹{planning_cost_min:,} – ₹{planning_cost_max:,}**) provides the most reliable guidance.
    """
)
