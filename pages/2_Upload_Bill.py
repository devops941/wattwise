import sys
import os
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings('ignore')

import streamlit as st
import pandas as pd

from src.pdf_extractor import extract_bill_from_upload
from src.validator import (
    validate_pdf_file, validate_bill_record,
    detect_duplicates_and_inconsistencies,
    convert_power, calculate_energy_kwh, get_unit_explanation
)
from src.household_manager import (
    save_household_profile, get_active_household, activate_demo,
    clear_active_household, activate_household, list_saved_households,
    mask_consumer_name, mask_connection_no
)
from src.ui_theme import apply_theme, render_sidebar_header

st.set_page_config(
    page_title="Upload EB Bills | WattWise",
    page_icon="📤",
    layout="wide",
)

apply_theme()
render_sidebar_header()

st.title("📤 Multi-Household EB Bill Upload & Dataset Management")
st.caption("Upload one or multiple TANGEDCO / TNPDCL electricity bills (PDF) to build an isolated, verifiable household consumption dataset.")

# Privacy assurance callout
st.info(
    "🔒 **Data Privacy & Isolation:** WattWise isolates every household into its own private workspace. "
    "Consumer names and service numbers are anonymized in analytical views (`SEN***`, `***0917`). "
    "Your bills are never merged with other households."
)

# Active Household Status Banner
df, meta = get_active_household()
if df is not None and meta is not None:
    is_demo = meta.get("is_demo", False)
    col_status, col_btn = st.columns([3, 1])
    with col_status:
        if is_demo:
            st.info(f"📘 **Active Profile:** Academic Demo (`{meta.get('name')}`) — 5 billing cycles loaded.")
        else:
            m_name = mask_consumer_name(meta.get('name'))
            m_conn = mask_connection_no(meta.get('connection_no'))
            st.success(f"🟢 **Active Profile:** `{m_name}` | Connection: `{m_conn}` ({len(df)} billing cycles live).")
    with col_btn:
        if st.button("🔄 Start New / Switch Household", use_container_width=True):
            clear_active_household()
            st.session_state.pop("extracted_bills_list", None)
            st.session_state.pop("last_uploaded_count", None)
            st.rerun()

st.divider()

# Tab navigation: 1. Upload Bills, 2. Manage Saved Households, 3. Electrical Unit Reference
tab_upload, tab_saved, tab_units = st.tabs([
    "📥 Upload & Verify Bills",
    "📁 Manage Saved Households",
    "⚡ Power vs Energy Reference"
])

# ── TAB 1: UPLOAD & VERIFY BILLS ───────────────────────────────────────────
with tab_upload:
    uploaded_files = st.file_uploader(
        "Select one or multiple Tamil Nadu EB Bill PDFs:",
        type=["pdf"],
        accept_multiple_files=True,
        help="Drag and drop your bi-monthly electricity bills downloaded from tnpdcl.in or scanned invoices."
    )

    if not uploaded_files:
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown("""
            <div class="ww-card" style="padding: 1.2rem;">
                <div style="font-size: 1.15rem; margin-bottom: 0.35rem;">📄 <b>Portal Digital E-Bills</b></div>
                <div style="font-size: 0.90rem; color: #475569; line-height: 1.55;">
                    Direct instant extraction from official TNPDCL / TANGEDCO web portal download PDFs.
                </div>
            </div>
            """, unsafe_allow_html=True)
        with g2:
            st.markdown("""
            <div class="ww-card" style="padding: 1.2rem;">
                <div style="font-size: 1.15rem; margin-bottom: 0.35rem;">📷 <b>Physical Scanned Bills</b></div>
                <div style="font-size: 0.90rem; color: #475569; line-height: 1.55;">
                    Automated offline OCR extracts meter numbers, dates, and units from physical paper bills.
                </div>
            </div>
            """, unsafe_allow_html=True)
        with g3:
            st.markdown("""
            <div class="ww-card" style="padding: 1.2rem;">
                <div style="font-size: 1.15rem; margin-bottom: 0.35rem;">⚡ <b>LT-1A Domestic Audits</b></div>
                <div style="font-size: 0.90rem; color: #475569; line-height: 1.55;">
                    Full validation for bi-monthly cycles with 100 free units government subsidy audit.
                </div>
            </div>
            """, unsafe_allow_html=True)

    if uploaded_files:
        # Validate each uploaded file (size, header, empty check)
        valid_files = []
        file_errors = []
        for uf in uploaded_files:
            is_valid, err_msg = validate_pdf_file(uf, uf.name, max_size_mb=25.0)
            if is_valid:
                valid_files.append(uf)
            else:
                file_errors.append(err_msg)

        if file_errors:
            for em in file_errors:
                st.error(f"❌ {em}")

        if valid_files:
            # Check if extraction needs to run
            if "extracted_bills_list" not in st.session_state or st.session_state.get("last_uploaded_count") != len(valid_files):
                extracted_results = []
                prog = st.progress(0, text="Extracting bill data...")
                for idx, vf in enumerate(valid_files):
                    pct = int(((idx + 1) / len(valid_files)) * 100)
                    prog.progress(pct, text=f"Processing {vf.name} ({idx+1}/{len(valid_files)})...")
                    res = extract_bill_from_upload(vf)
                    extracted_results.append(res)
                prog.empty()
                st.session_state["extracted_bills_list"] = extracted_results
                st.session_state["last_uploaded_count"] = len(valid_files)

            extracted_bills = st.session_state.get("extracted_bills_list", [])

            # Check for duplicate billing cycles
            dup_check = detect_duplicates_and_inconsistencies(extracted_bills)
            if dup_check["has_duplicates"]:
                for d in dup_check["duplicates"]:
                    st.warning(f"⚠️ **Duplicate Cycle Detected:** {d['message']}")
            for w in dup_check["warnings"]:
                st.info(f"ℹ️ {w}")

            st.subheader(f"📋 Extracted Bill Preview ({len(extracted_bills)} Document{'s' if len(extracted_bills)>1 else ''})")
            
            # Summary Table
            preview_rows = []
            for i, b in enumerate(extracted_bills):
                preview_rows.append({
                    "Bill #": i + 1,
                    "File Name": b.get("filename", ""),
                    "Billing Month": b.get("billing_month") or "Needs Verification",
                    "Units (kWh)": b.get("units_consumed") if b.get("units_consumed") is not None else "Needs Input",
                    "Net Payable (₹)": f"₹{b.get('net_payable'):,.0f}" if b.get("net_payable") is not None else "N/A",
                    "Final Reading": b.get("final_reading") if b.get("final_reading") is not None else "N/A",
                    "Due Date": b.get("due_date") or "N/A",
                    "Confidence": b.get("extraction_confidence", "Medium"),
                })
            st.dataframe(pd.DataFrame(preview_rows), use_container_width=True, hide_index=True)

            st.divider()

            # Household Profile & Verification Form
            st.subheader("✏️ Household Details & Field Verification")
            st.caption("Verify and correct any extracted values before creating your household dataset.")

            with st.form("household_verification_form"):
                st.markdown("#### 1. Household Profile")
                h_col1, h_col2, h_col3, h_col4 = st.columns(4)
                
                # Pre-fill profile from first bill if available
                first_b = extracted_bills[0] if extracted_bills else {}
                default_name = str(first_b.get("consumer_name") or "User Household")
                default_conn = str(first_b.get("connection_no") or "")
                default_sec = str(first_b.get("section") or "Domestic")
                default_tariff = str(first_b.get("tariff_category") or "LT-1A Domestic")

                with h_col1:
                    f_hname = st.text_input("Household / Consumer Name", value=default_name, help="Will be masked in analytics")
                with h_col2:
                    f_conn = st.text_input("Service Connection Number", value=default_conn, help="E.g. 05-472-024-917")
                with h_col3:
                    f_sec = st.text_input("Section / Sub-station", value=default_sec)
                with h_col4:
                    f_tariff = st.selectbox("Tariff Classification", ["LT-1A Domestic", "LT-1B", "LT-2A Commercial", "Other"], index=0)

                st.markdown("#### 2. Individual Bill Verification")
                edited_bills = []
                for i, b in enumerate(extracted_bills):
                    with st.expander(f"Bill #{i+1}: {b.get('filename')} — {b.get('billing_month', 'Unspecified')}", expanded=(i==0)):
                        b1, b2, b3 = st.columns(3)
                        with b1:
                            e_month = st.text_input(f"Billing Month (#{i+1})", value=str(b.get("billing_month") or f"Cycle {i+1}"), key=f"em_{i}")
                            e_units = st.number_input(f"Units Consumed (kWh) (#{i+1})", min_value=0, max_value=15000, value=int(b.get("units_consumed") or 0), key=f"eu_{i}")
                        with b2:
                            e_amt = st.number_input(f"Net Payable (₹) (#{i+1})", min_value=0.0, max_value=250000.0, value=float(b.get("net_payable") or 0.0), step=50.0, key=f"ea_{i}")
                            e_due = st.text_input(f"Due Date (#{i+1})", value=str(b.get("due_date") or ""), key=f"ed_{i}")
                        with b3:
                            e_reading = st.number_input(f"Final Reading (kWh) (#{i+1})", min_value=0.0, max_value=500000.0, value=float(b.get("final_reading") or 0.0), key=f"er_{i}")
                            e_include = st.checkbox(f"Include in Dataset", value=True, key=f"inc_{i}", help="Uncheck to exclude this bill")

                        if e_include:
                            edited_bills.append({
                                "filename": b.get("filename"),
                                "billing_month": e_month,
                                "units_consumed": e_units if e_units > 0 else None,
                                "net_payable": e_amt if e_amt > 0 else None,
                                "due_date": e_due,
                                "final_reading": e_reading if e_reading > 0 else None,
                                "consumer_name": f_hname,
                                "connection_no": f_conn,
                                "section": f_sec,
                                "tariff_category": f_tariff,
                            })

                submit_btn = st.form_submit_button("✅ Save Household Profile & Activate Analytics", use_container_width=True, type="primary")

            if submit_btn:
                if not edited_bills:
                    st.error("❌ No bills selected for inclusion. Please keep at least one bill checked.")
                else:
                    # Validate all edited bills
                    val_errors = []
                    for idx, eb in enumerate(edited_bills):
                        is_valid, errs, warns = validate_bill_record(eb)
                        if not is_valid:
                            for e in errs:
                                val_errors.append(f"Bill #{idx+1} ({eb.get('billing_month')}): {e}")

                    if val_errors:
                        for ve in val_errors:
                            st.error(f"❌ {ve}")
                    else:
                        hid, new_df = save_household_profile(
                            household_name=f_hname,
                            connection_no=f_conn,
                            section=f_sec,
                            tariff_category=f_tariff,
                            bills_list=edited_bills,
                            raw_files=valid_files
                        )
                        st.success(f"🎉 **Household Successfully Activated!** {len(new_df)} billing cycles sequenced and stored under ID `{hid}`.")
                        st.markdown(
                            """
                            **Explore your individual household intelligence:**
                            - 👉 **[Go to Executive Dashboard](Dashboard)**
                            - 👉 **[Cycle Consumption Analysis](Analysis)**
                            - 👉 **[Peak Consumption & Load Discovery](Peak_Consumption)**
                            - 👉 **[Experimental Forecasts](Prediction)**
                            - 👉 **[Tariff & Bill Simulator](Bill_Estimation)**
                            - 👉 **[Actionable Recommendations](Recommendations)**
                            - 👉 **[Download Official PDF Audit Report](Reports)**
                            """
                        )
                        st.rerun()

    else:
        # Prompt to load sample bills or explore
        st.info("💡 **Quick Test:** Don't have bills right now? You can explore the 5 sample Tamil Nadu EB bills included with WattWise.")
        if st.button("📂 Load 5 Tamil Nadu Sample Bills (Demo Household)", use_container_width=False):
            activate_demo()
            st.success("Demo dataset loaded! Navigate to the **Dashboard** or **Analysis** pages to view insights.")
            st.rerun()

# ── TAB 2: MANAGE SAVED HOUSEHOLDS ─────────────────────────────────────────
with tab_saved:
    st.subheader("Saved Household Profiles")
    st.caption("WattWise stores created household profiles locally on this machine so you can switch between them anytime.")

    saved_profiles = list_saved_households()
    if saved_profiles:
        for p in saved_profiles:
            with st.container():
                c_info, c_action = st.columns([3, 1])
                with c_info:
                    st.markdown(f"### 🏠 {mask_consumer_name(p.get('name'))}")
                    st.caption(
                        f"ID: `{p.get('id')}` • Connection: `{mask_connection_no(p.get('connection_no'))}` • "
                        f"Section: `{p.get('section', 'Domestic')}` • Cycles: **{p.get('cycles_count', 0)}** • Created: {p.get('created_at', 'N/A')}"
                    )
                with c_action:
                    if st.button("Open This Profile", key=f"act_{p.get('id')}", use_container_width=True):
                        activate_household(p.get('id'))
                        st.rerun()
                st.divider()
    else:
        st.info("No saved household profiles found yet. Upload bills in Tab 1 to create your first household.")

    st.markdown("#### Baseline Academic Demonstration")
    st.caption("The original 5-bill dataset for consumer SENTHIL MURUGAN (KOODALNAGAR, Madurai).")
    if st.button("Open Baseline Demo Profile", use_container_width=False):
        activate_demo()
        st.rerun()

# ── TAB 3: POWER VS ENERGY UNIT REFERENCE ──────────────────────────────────
with tab_units:
    st.subheader("⚡ Electrical Unit Fundamentals & Conversions")
    st.caption("Understanding the scientific distinction between Power (Demand) and Energy (Consumption).")

    expl = get_unit_explanation()
    e_col1, e_col2 = st.columns(2)
    with e_col1:
        st.markdown(f"**Watt (W):** {expl['Watt (W)']}")
        st.markdown(f"**Kilowatt (kW):** {expl['Kilowatt (kW)']}")
    with e_col2:
        st.markdown(f"**Kilowatt-hour (kWh / Unit):** {expl['Kilowatt-hour (kWh / Unit)']}")
        st.info(f"💡 **Key Rule:** {expl['Crucial Distinction']}")

    st.divider()
    st.subheader("🧮 Interactive Power to Energy Calculator")
    st.caption("Calculate how appliance wattage and runtime translate into billed units (kWh).")

    calc1, calc2, calc3 = st.columns(3)
    with calc1:
        in_pwr = st.number_input("Appliance Power Rating:", min_value=1.0, max_value=50000.0, value=1500.0, step=50.0)
    with calc2:
        in_pwr_unit = st.selectbox("Unit:", ["Watts (W)", "Kilowatts (kW)"])
    with calc3:
        in_hrs = st.number_input("Daily Operating Hours:", min_value=0.1, max_value=24.0, value=6.0, step=0.5)

    u_symbol = "W" if "Watts" in in_pwr_unit else "KW"
    daily_kwh = calculate_energy_kwh(in_pwr, u_symbol, in_hrs)
    bimonthly_kwh = round(daily_kwh * 60, 2)
    est_bimonthly_cost = round(bimonthly_kwh * 6.30, 2)

    res1, res2, res3 = st.columns(3)
    with res1:
        st.metric("Daily Energy Usage", f"{daily_kwh} kWh / day")
    with res2:
        st.metric("Bi-Monthly Cycle Usage", f"{bimonthly_kwh} kWh / cycle", help="60 days billing cycle")
    with res3:
        st.metric("Estimated Cost (@ ₹6.30/unit)", f"₹{est_bimonthly_cost:,.2f} / cycle")
