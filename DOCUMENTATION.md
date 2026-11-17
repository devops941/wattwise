# WATTWISE AI
### Household Energy Consumption Intelligence & Peak-Load Discovery

---

### PROJECT OVERVIEW
WattWise is an intelligent, multi-household electricity analytics and peak-load discovery platform engineered for Tamil Nadu (TANGEDCO / TNPDCL) domestic consumers. It enables households to upload authentic electricity bill invoices (PDF or scanned), automatically extracts consumption data via OCR and PDF parsing, audits tariff calculations, and uncovers actionable energy-saving opportunities through interactive appliance simulations and formal PDF reporting.

---

### PROBLEM STATEMENT
Residential electricity consumers in Tamil Nadu lack visibility into their bi-monthly billing cycles, progressive telescopic tariff slabs, and cooling peak demands. High-consumption tiers past the 500 kWh threshold lead to sudden, steep electricity bills. Manual bill analysis is complex and error-prone, leaving households without clear, data-driven strategies to lower their energy costs.

---

### PROJECT OBJECTIVES
* **Digitize & Automate Bill Auditing:** Automated parsing of digital and scanned Tamil Nadu EB invoices.
* **Multi-Household Data Isolation:** Provide 100% private, isolated analytics per household without data leakage.
* **Discover Seasonal Peak-Loads:** Identify cooling demand intensity and historical consumption swings.
* **Tariff Transparency:** Verify 7-tier TANGEDCO domestic tariffs and 100 free units government subsidies.
* **Actionable Conservation:** Provide interactive appliance simulators and automated PDF audit report generation.

---

### KEY MODULES & FEATURES
* **Multi-Household Session Architecture** – Strict data isolation per household with masked consumer information.
* **Baseline Academic Demonstration** – Verified 5-cycle historical baseline dataset for Senthil Murugan (Madurai).
* **Automated Bill Extraction & OCR** – Dual-engine parser combining PyMuPDF and EasyOCR for digital/scanned PDFs.
* **Input Validation & Unit Conversion** – File integrity, duplicate cycle detection, and W / kW / kWh power vs energy converters.
* **Bi-Monthly Consumption Analytics** – Interactive trends, unit rate trajectory, and billing anomaly detection.
* **Peak-Load & Run-Rate Discovery** – Discovers summer heat surges (911 kWh) vs monsoon relief (613 kWh).
* **Experimental Predictive Forecasting** – Linear regression and moving average projections with scientific disclaimers.
* **TANGEDCO LT-1A Tariff Simulator** – 7-tier telescopic slab calculation with 100 free units subsidy and what-if calculator.
* **Interactive Appliance Savings Simulator** – Operational sliders (AC thermostat, BLDC fans, LED retrofit) computing kWh and ₹ savings.
* **Publication-Grade PDF Report Generator** – Dynamic multi-page formal audit report with embedded in-memory trend charts.

---

### TECHNOLOGY STACK
* **Frontend:** Streamlit Multi-Page App, Custom CSS Design System (Plus Jakarta Sans, Modern SaaS Theme)
* **Backend & Core Engine:** Python 3.12, PyMuPDF (`fitz`), `pdfplumber`, EasyOCR, PyTorch
* **Data Processing & Analytics:** Pandas, NumPy, Scikit-learn, SciPy
* **Visualization & Charts:** Plotly Express, Plotly Graph Objects, Matplotlib
* **Document & PDF Generation:** ReportLab, In-memory BytesIO Streaming
* **DevOps & Tooling:** Git, GitHub, Docker, Windows PowerShell

---

### PROJECT LINKS
* **GitHub Repository:** [https://github.com/devops941/wattwise](https://github.com/devops941/wattwise)
* **Live Application:** [http://localhost:8501](http://localhost:8501)
* **Domain:** Energy Analytics | Smart Grid & AI | Sustainability & Cleantech
* **Application Type:** Full-Stack Web Application / Python Analytics System
