# ⚡ WattWise – Household Energy Consumption Intelligence & Peak-Load Discovery

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40.0-FF4B4B.svg)](https://streamlit.io/)
[![ReportLab](https://img.shields.io/badge/ReportLab-5.1.0-0D47A1.svg)](https://www.reportlab.com/)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)]()

WattWise is an end-to-end residential energy analytics platform engineered specifically for **Tamil Nadu electricity consumers (TANGEDCO / TNPDCL)**. It extracts consumption intelligence from physical and digital Low Tension (LT-1A) domestic electricity bills, identifies seasonal peak-load cycles, estimates future bills, and delivers actionable energy conservation recommendations.

---

## 🏛️ Project Architecture & Structure

```
WattWise/
├── .streamlit/
│   └── config.toml                  # Professional white & blue enterprise theme config
├── data/
│   ├── .easyocr/                    # Offline OCR models (CRAFT detection + English recognition)
│   ├── raw/
│   │   └── eb_bills/                # 5 authentic sample Tamil Nadu EB bill PDFs (Feb–Oct 2026)
│   └── processed/
│       ├── eb_consumption.csv       # Raw extracted billing data
│       └── eb_consumption_cleaned.csv# Cleaned dataset with derived units & quality flags
├── pages/
│   ├── 1_Dashboard.py               # Screen 2: Executive Energy Dashboard
│   ├── 2_Upload_Bill.py             # Screen 3 & 4: Multi-PDF Upload & Extracted Data Preview
│   ├── 3_Analysis.py                # Screen 5: Cycle-by-Cycle Consumption Analysis
│   ├── 4_Peak_Consumption.py        # Screen 6: Peak-Load Discovery & Climate Alignment
│   ├── 5_Prediction.py              # Screen 7: Experimental Forecasting (OLS & Moving Average)
│   ├── 6_Bill_Estimation.py         # Screen 8: TANGEDCO Domestic Tariff Simulator
│   ├── 7_Recommendations.py         # Screen 9: Tailored Energy-Saving Recommendations
│   └── 8_Reports.py                 # Screen 10: PDF Audit Report & Data Package Downloads
├── reports/
│   ├── figures/                     # 200 DPI publication figures
│   │   ├── consumption_by_cycle.png
│   │   ├── bill_amount_by_cycle.png
│   │   ├── consumption_trend.png
│   │   └── consumption_comparison.png
│   ├── consumption_analysis.md      # Detailed consumption patterns report
│   ├── peak_consumption_report.md   # Peak-load and seasonal swing analysis
│   ├── prediction_report.md         # Experimental forecast methodology & disclaimers
│   ├── eda_report.md                # Comprehensive exploratory data analysis
│   ├── eb_extraction_report.md      # OCR extraction and document audit report
│   ├── project_status.md            # 17-Phase comprehensive project audit matrix
│   └── development_progress.md      # Ongoing development and milestone tracking
├── src/
│   ├── analyzer.py                  # Cycle variance, anomaly detection, peak metrics
│   ├── bill_calculator.py           # TANGEDCO LT-1A slab calculator & wheeling charges
│   ├── data_processor.py            # Active session data manager & chronological sorter
│   ├── pdf_extractor.py             # Hybrid PDF text extractor & offline EasyOCR
│   ├── predictor.py                 # Linear regression & moving-average forecaster
│   ├── recommendations.py           # Prioritized energy conservation engine
│   ├── report_generator.py          # ReportLab publication-grade PDF report engine
│   └── step4_eda.py                 # Reproducible EDA and figure generation script
├── tests/
│   ├── test_all.py                  # 12 comprehensive unit and integration tests
│   └── test_pages_compilation.py    # Syntax and bytecode compilation validator
├── app.py                           # Screen 1: Modern Landing Page & Navigation Hub
├── requirements.txt                 # Runtime dependencies
└── README.md                        # Documentation
```

---

## 🚀 Key Features

### 1. Hybrid PDF Extraction & Offline OCR
- **Native PDF Parsing:** Extracts clean text from digital e-invoices downloaded from `tnpdcl.in` in milliseconds via `pdfplumber`.
- **Scanned Document OCR:** Uses PyMuPDF image rendering coupled with an offline EasyOCR engine cached locally in `data/.easyocr/` (no external network dependencies required during execution).
- **Physical Ground Truth Validation:** Validates OCR values against cumulative final meter readings (`units_derived = final_reading[i] - final_reading[i-1]`).

### 2. Multi-User Session Isolation & Batch Upload
- Support for **single and multi-file batch uploads**.
- Interactive data preview table with field validation and correction prior to session activation.
- Privacy-first architecture: consumer names and service connection numbers are automatically masked in analytical views (`SEN***` / `***0917`).
- Seamless switching between user-uploaded bills and the baseline demo dataset (Senthil Murugan, Madurai).

### 3. Consumption & Peak-Load Discovery
- **Climate Alignment:** Maps household consumption against Tamil Nadu weather patterns:
  - **Winter Baseline (Feb):** 414 kWh (₹1,263) — minimal cooling required.
  - **Summer Peak (Jun):** 911 kWh (₹3,929) — intensive air conditioning during 38°C+ heatwaves.
  - **Monsoon Dip (Aug):** 613 kWh (₹4,907) — cloud cover lowers ambient temperatures.
  - **Post-Monsoon Warmth (Oct):** 890 kWh (₹5,085) — humid warmth keeps cooling elevated.
- **Direction Mismatch Anomaly Detection:** Flags billing cycles where consumption dropped but net payable increased (e.g. August arrears or slab progression).

### 4. TANGEDCO LT-1A Tariff Simulator & "What-If" Calculator
- Implements bi-monthly domestic stepped tariff slabs with Tamil Nadu Government's **100 units free power subsidy**.
- Interactive consumption slider with quick presets (Baseline, Peak, Average, 500 kWh goal).
- "What-If" reduction calculator showing exact unit and rupee savings for thermostat adjustments or appliance upgrades.

### 5. Publication-Quality PDF Report Generation
- Powered by `reportlab` to build multi-page formal energy audit reports.
- Includes executive summary tables, meter progression charts, seasonal insights, forecast scenarios, and customized efficiency recommendations.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.12 (or >= 3.10)
- Windows / macOS / Linux

### Setup Virtual Environment
```bash
# 1. Clone the repository and enter directory
cd d:/collegeprojects/wattwise

# 2. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 💻 Running the Application

Launch the Streamlit web dashboard:
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Tests

A comprehensive automated test suite validates all modules, algorithms, and data structures:

```bash
# Run unit & integration tests
python -m unittest tests/test_all.py

# Verify compilation of all application scripts
python tests/test_pages_compilation.py
```

---

## 📊 Dataset Verification Summary

The verified baseline dataset consists of 5 authentic bi-monthly Tamil Nadu electricity bills for consumer **SENTHIL MURUGAN** (Connection `05-472-024-917`, KOODALNAGAR Section, Madurai):

| Cycle | Bill Date | Meter Reading | Units Billed | Net Payable | Quality Flag |
|---|---|---|---|---|---|
| **Feb 2026** | 20/02/2026 | 12,985 kWh | 414 kWh | ₹1,263 | OCR estimated (baseline) |
| **Apr 2026** | 20/04/2026 | 15,659 kWh | 774 kWh | ₹4,524 | OCR estimated (summer rise) |
| **Jun 2026** | 20/06/2026 | 16,570 kWh | 911 kWh | ₹3,929 | Derived from reading delta (summer peak) |
| **Aug 2026** | 21/08/2026 | 17,183 kWh | 613 kWh | ₹4,907 | Derived from reading delta (monsoon dip) |
| **Oct 2026** | 20/10/2026 | 18,073 kWh | 890 kWh | ₹5,085 | Fully confirmed: OCR == derived (890 kWh) |

- **Total Consumption:** 3,602 kWh
- **Total Expenditure:** ₹19,708.00
- **Average per Cycle:** 720.4 kWh (₹3,941.60)
- **Meter Reading Progression:** Monotonically increasing across all 5 billing cycles.

---

## 📜 Educational & Scientific Disclaimers

1. **Experimental Forecasting:** Predictions (OLS linear regression & 3-cycle moving average) are educational estimates derived from 5 historical data points. A minimum of 24–36 continuous billing cycles is standard for robust statistical time-series forecasting.
2. **Billing Totals vs Instantaneous Demand:** Standard Tamil Nadu residential energy meters record bi-monthly cumulative kWh. Instantaneous kW peak demand or appliance-level power factor cannot be inferred from bi-monthly billing totals without smart meter / IoT telemetry.
