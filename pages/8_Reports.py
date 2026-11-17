import sys
import warnings
import zipfile
import io
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings('ignore')

import streamlit as st
import pandas as pd

from src.household_manager import get_active_household, activate_demo, mask_consumer_name, mask_connection_no
from src.analyzer import analyze_consumption
from src.report_generator import generate_pdf_report
from src.ui_theme import apply_theme, render_sidebar_header

st.set_page_config(
    page_title="Audit Reports & Exports | WattWise",
    page_icon="📋",
    layout="wide",
)

apply_theme()
render_sidebar_header()

BASE_DIR = Path(__file__).resolve().parent.parent
figures_dir = BASE_DIR / "reports" / "figures"
reports_dir = BASE_DIR / "reports"

df, meta = get_active_household()

# ── EMPTY STATE IF NO HOUSEHOLD LOADED ─────────────────────────────────────
if df is None or len(df) == 0:
    st.title("📋 Household Energy Reports & Data Exports")
    st.info("ℹ️ **No Household Loaded:** Upload your own EB bills or explore the baseline academic demo dataset.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("### 📤 Analyze Your Household")
        st.write("Upload your TANGEDCO/TNPDCL bills to generate and download a personalized PDF audit report.")
        st.page_link("pages/2_Upload_Bill.py", label="Upload Your EB Bills →", use_container_width=True)
    with col_b:
        st.markdown("### 📘 Explore Academic Demo")
        st.write("Download the verified academic audit report for consumer SENTHIL MURUGAN.")
        if st.button("Load Academic Demo Household", use_container_width=True, type="primary"):
            activate_demo()
            st.rerun()
    st.stop()

# ── DATA LOADED: RENDER REPORTS & EXPORTS ──────────────────────────────────
analysis = analyze_consumption(df)

consumer_name = meta.get('name') if meta else (df['consumer_name'].iloc[0] if 'consumer_name' in df.columns else "Household Consumer")
connection_no = meta.get('connection_no') if meta else (df['connection_no'].iloc[0] if 'connection_no' in df.columns else "N/A")
section = meta.get('section') if meta else (df['section'].iloc[0] if 'section' in df.columns else "Domestic")
tariff = meta.get('tariff_category') if meta else (df['tariff_category'].iloc[0] if 'tariff_category' in df.columns else "LT Domestic")

masked_name = mask_consumer_name(consumer_name)
masked_conn = mask_connection_no(connection_no)

st.title("📋 Household Energy Reports & Data Exports")
st.caption(f"Download complete energy audit packages and verified datasets for **{masked_name}** ({len(df)} billing cycles).")

st.divider()

# ── 1. PRIMARY PDF AUDIT REPORT DOWNLOAD CARD ──────────────────────────────
st.subheader("📑 Formal Household Energy Audit Report (PDF)")
st.markdown(
    "Generate a complete, publication-grade multi-page PDF audit report with executive metrics, "
    "meter reading progression tables, embedded trend charts, and customized energy conservation strategies."
)

try:
    consumer_info = {
        "consumer_name": consumer_name,
        "connection_no": connection_no,
        "section": section,
        "tariff_category": tariff,
    }
    pdf_bytes = generate_pdf_report(df, analysis, consumer_info)
    safe_filename_part = "".join(c for c in consumer_name if c.isalnum() or c in ("_", "-")).lower()
    if not safe_filename_part:
        safe_filename_part = "household"

    st.download_button(
        label="⬇️ Download Official Energy Audit Report (PDF)",
        data=pdf_bytes,
        file_name=f"wattwise_energy_report_{safe_filename_part}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=False,
    )
    st.caption("Includes executive summary, cycle consumption breakdown, dynamic trend charts, tariff simulation, and disclaimers.")
except Exception as e:
    st.error(f"Error generating PDF report: {e}")

st.divider()

# ── 2. SECONDARY DOWNLOADS (CSV, ARTIFACTS) ─────────────────────────────────
st.subheader("📦 Additional Data & Artifact Exports")

col1, col2, col3 = st.columns(3)

# Col 1: Cleaned Dataset CSV
with col1:
    st.markdown("#### 1. Verified Dataset (CSV)")
    st.caption("Export active billing cycles with sequenced units and quality flags.")
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Cleaned CSV",
        data=csv_bytes,
        file_name=f"wattwise_consumption_{safe_filename_part}.csv",
        mime="text/csv",
        use_container_width=True,
    )

# Col 2: EDA Charts ZIP (Demo or Saved)
with col2:
    st.markdown("#### 2. Figures Gallery (ZIP)")
    st.caption("Download high-resolution 200 DPI PNG figures for presentations and reports.")
    png_files = list(figures_dir.glob("*.png"))
    if png_files:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for png_path in sorted(png_files):
                zf.write(png_path, arcname=png_path.name)
        zip_bytes = zip_buffer.getvalue()
        st.download_button(
            label="Download All Charts (ZIP)",
            data=zip_bytes,
            file_name="wattwise_charts.zip",
            mime="application/zip",
            use_container_width=True,
        )
    else:
        st.info("Chart figures not found.")

# Col 3: Markdown Reports ZIP
with col3:
    st.markdown("#### 3. Analytical Reports (ZIP)")
    st.caption("Full technical documentation and exploratory reports in Markdown.")
    report_names = [
        "consumption_analysis.md",
        "peak_consumption_report.md",
        "prediction_report.md",
        "eda_report.md",
        "eb_extraction_report.md",
        "project_status.md",
        "final_verification_report.md",
        "final_acceptance_report.md"
    ]
    md_zip_buffer = io.BytesIO()
    found_any = False
    with zipfile.ZipFile(md_zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in report_names:
            md_path = reports_dir / name
            if md_path.exists():
                zf.write(md_path, arcname=name)
                found_any = True
    if found_any:
        md_zip_bytes = md_zip_buffer.getvalue()
        st.download_button(
            label="Download Markdown Docs (ZIP)",
            data=md_zip_bytes,
            file_name="wattwise_technical_reports.zip",
            mime="application/zip",
            use_container_width=True,
        )
    else:
        st.info("No markdown reports found.")

st.divider()

# High-Res Charts Preview
st.subheader("🖼️ High-Resolution Visualization Gallery")
chart_files = {
    "Consumption by Cycle": figures_dir / "consumption_by_cycle.png",
    "Bill Amount by Cycle": figures_dir / "bill_amount_by_cycle.png",
    "Consumption Trend": figures_dir / "consumption_trend.png",
    "Units vs Amount Comparison": figures_dir / "consumption_comparison.png",
}

tabs = st.tabs(list(chart_files.keys()))
for tab, (label, img_path) in zip(tabs, chart_files.items()):
    with tab:
        if img_path.exists():
            st.image(str(img_path), caption=f"WattWise Analysis — {label}", use_container_width=True)
        else:
            st.info(f"Figure file not found: {img_path.name}")
