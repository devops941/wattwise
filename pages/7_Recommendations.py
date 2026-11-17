import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings('ignore')

import streamlit as st

from src.household_manager import get_active_household, activate_demo, mask_consumer_name
from src.analyzer import analyze_consumption, detect_anomalies
from src.recommendations import generate_recommendations, get_summary_message
from src.ui_theme import apply_theme, render_sidebar_header

st.set_page_config(
    page_title="Energy Saving Recommendations | WattWise",
    page_icon="💡",
    layout="wide",
)

apply_theme()
render_sidebar_header()

df, meta = get_active_household()

# ── EMPTY STATE IF NO HOUSEHOLD LOADED ─────────────────────────────────────
if df is None or len(df) == 0:
    st.title("💡 Energy-Saving Intelligence & Recommendations")
    st.info("ℹ️ **No Household Loaded:** Upload your own EB bills or explore the baseline academic demo dataset.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 📤 Analyze Your Household")
        st.write("Upload your TANGEDCO bills to generate tailored energy reduction recommendations.")
        st.page_link("pages/2_Upload_Bill.py", label="Upload Your EB Bills →", use_container_width=True)
    with col_b:
        st.markdown("### 📘 Explore Academic Demo")
        st.write("View recommendations generated for the 5-cycle baseline demo household.")
        if st.button("Load Academic Demo Household", use_container_width=True, type="primary"):
            activate_demo()
            st.rerun()
    st.stop()

# ── DATA LOADED: RENDER RECOMMENDATIONS ────────────────────────────────────
analysis = analyze_consumption(df)
anomalies = detect_anomalies(analysis)
recs = generate_recommendations(analysis, anomalies)

consumer_name = meta.get('name') if meta else "Household Consumer"
masked_name = mask_consumer_name(consumer_name)

st.title("💡 Energy-Saving Intelligence & Recommendations")
st.caption(f"Actionable reduction strategies tailored for **{masked_name}** based on {len(df)} historical billing cycles.")

summary = get_summary_message(analysis)
st.info(f"📌 **Household Analysis Takeaway:** {summary}")

st.caption("🔬 Note: WattWise strictly differentiates **[Data-Supported Findings]** derived from your actual billing trends from **[General Efficiency Best Practices]**. Appliance-level telemetry is not available from bi-monthly utility meters.")

st.subheader("🎯 Prioritized Action Plan")

high_recs = [r for r in recs if r['priority'] == 'High']
medium_recs = [r for r in recs if r['priority'] == 'Medium']
low_recs = [r for r in recs if r['priority'] == 'Low']

tab_high, tab_med, tab_low = st.tabs([
    f"🔴 High Priority ({len(high_recs)})",
    f"🟡 Medium Priority ({len(medium_recs)})",
    f"🟢 Low Priority ({len(low_recs)})"
])

with tab_high:
    if high_recs:
        for r in high_recs:
            tag_label = r.get("tag", "Finding")
            with st.expander(f"**{r['title']}** — [{tag_label}]", expanded=True):
                st.markdown(r['detail'])
                st.caption(f"Priority: High • Category: {r['category']} • Impact: Avoids top TANGEDCO tariff tier rates (₹10.50+/kWh)")
    else:
        st.write("No high-priority alerts for this consumption range.")

with tab_med:
    if medium_recs:
        for r in medium_recs:
            tag_label = r.get("tag", "Guideline")
            with st.expander(f"**{r['title']}** — [{tag_label}]"):
                st.markdown(r['detail'])
                st.caption(f"Priority: Medium • Category: {r['category']} • Target Impact: 5-15% Bill Reduction")
    else:
        st.write("No medium-priority recommendations.")

with tab_low:
    if low_recs:
        for r in low_recs:
            tag_label = r.get("tag", "Guideline")
            with st.expander(f"**{r['title']}** — [{tag_label}]"):
                st.markdown(r['detail'])
                st.caption(f"Priority: Low • Category: {r['category']} • Target: Sustained baseline efficiency")
    else:
        st.write("No low-priority recommendations.")

st.divider()

# ── INTERACTIVE APPLIANCE SAVINGS SIMULATOR ────────────────────────────────
st.subheader("🧮 Interactive Appliance Energy Savings Simulator")
st.caption("Adjust the sliders below to calculate exact bi-monthly kilowatt-hour and rupee reductions under official TANGEDCO tariffs.")

calc_col1, calc_col2 = st.columns([3, 2])

with calc_col1:
    st.markdown("##### ⚙️ Operational & Equipment Adjustments")
    ac_hours = st.slider("❄️ Air Conditioner Daily Usage (hours/day):", min_value=0, max_value=16, value=6, step=1)
    ac_temp_shift = st.slider("🌡️ Thermostat Increase (from 20°C to 24–26°C):", min_value=0, max_value=6, value=3, step=1, help="Bureau of Energy Efficiency (BEE) benchmark: each 1°C increase saves ~6% compressor power")
    fan_replacements = st.slider("🌀 Replace traditional fans with 28W 5-Star BLDC fans:", min_value=0, max_value=6, value=2, step=1, help="Saves ~45W per fan compared to standard 75W induction motors")
    led_upgrades = st.slider("💡 Upgrade incandescent / CFL lamps to 9W LED lamps:", min_value=0, max_value=12, value=4, step=1, help="Saves ~30W per bulb running 5 hours daily")

# Computations
# AC 1.5 ton consumes ~1.5 kWh/hr. 6% per degree shift over 60 days
ac_savings_kwh = ac_hours * 1.5 * (ac_temp_shift * 0.06) * 60
# BLDC saves ~45W per fan running 10 hrs/day for 60 days = 0.045 * 10 * 60 = 27 kWh per fan
bldc_savings_kwh = fan_replacements * 27.0
# LED saves ~30W per bulb running 5 hrs/day for 60 days = 0.030 * 5 * 60 = 9 kWh per bulb
led_savings_kwh = led_upgrades * 9.0

total_saved_kwh = int(round(ac_savings_kwh + bldc_savings_kwh + led_savings_kwh))
marginal_rate = 8.40 if analysis['max_units'] > 500 else 6.30
total_rupees_saved = round(total_saved_kwh * marginal_rate, 0)
pct_saved = round((total_saved_kwh / analysis['avg_units']) * 100, 1) if analysis['avg_units'] > 0 else 0

with calc_col2:
    st.markdown("##### 💰 Estimated Savings (60-Day Cycle)")
    
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1E3A8A 0%, #1D4ED8 100%); border-radius: 16px; padding: 1.4rem; color: white; box-shadow: 0 8px 24px -4px rgba(37, 99, 235, 0.35); margin-bottom: 1rem;">
            <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #93C5FD; font-weight: 700;">Bi-Monthly Financial Relief</div>
            <div style="font-size: 2.2rem; font-weight: 800; letter-spacing: -0.03em; margin: 0.2rem 0;">₹{total_rupees_saved:,.0f}</div>
            <div style="font-size: 0.85rem; color: #DBEAFE;">Annual Cumulative Savings: <b>₹{total_rupees_saved*6:,.0f} / year</b></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric(
            label="Units Saved",
            value=f"{total_saved_kwh} kWh",
            delta=f"-{pct_saved}% of avg bill"
        )
    with m_col2:
        st.metric(
            label="Applied Tariff Slab",
            value=f"₹{marginal_rate:.2f}/kWh",
            help="TANGEDCO marginal top tier domestic tariff rate"
        )

    st.markdown(
        f"""
        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 0.85rem; font-size: 0.8rem; line-height: 1.6; color: #475569;">
            <div style="font-weight: 700; color: #0F172A; margin-bottom: 4px;">Energy Reduction Breakdown:</div>
            <div>❄️ AC Thermostat: <b>{int(round(ac_savings_kwh))} kWh</b> ({int(round(ac_savings_kwh * marginal_rate))} ₹)</div>
            <div>🌀 BLDC Ceiling Fans: <b>{int(round(bldc_savings_kwh))} kWh</b> ({int(round(bldc_savings_kwh * marginal_rate))} ₹)</div>
            <div>💡 9W LED Retrofits: <b>{int(round(led_savings_kwh))} kWh</b> ({int(round(led_savings_kwh * marginal_rate))} ₹)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

st.subheader("🌴 Climate-Smart Living in Tamil Nadu")
st.markdown(
    """
    1. **Pre-Cooling & Cross-Ventilation:** In coastal and southern Tamil Nadu (Madurai, Chennai, Trichy), open windows during early evening hours (6:00 – 7:30 PM) to purge heat, then close windows and turn on ceiling fans before considering AC.
    2. **Solar Rooftop Subsidy (PM Surya Ghar):** A 2 kW or 3 kW residential grid-tied solar system produces ~240–360 kWh/month in Tamil Nadu's high solar insolation climate, covering over 60% of domestic consumption.
    3. **Avoid the 500 kWh Cliff:** TANGEDCO bi-monthly domestic tariffs increase steeply past the 500-unit threshold. Keeping your consumption at 490 kWh instead of 510 kWh saves hundreds of rupees through lower slab classifications.
    """
)
