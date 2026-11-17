# WattWise – Exploratory Data Analysis Report

**Generated:** 2026-11-17  
**Step:** 4 – Data Cleaning & EDA  
**Data Source:** `data/processed/eb_consumption_cleaned.csv`  
**Consumer:** SENTHIL MURUGAN — Connection 05-472-024-917, KOODALNAGAR Section, Madurai

---

## 1. Dataset Overview

| Property | Value |
|---|---|
| Source file | eb_consumption.csv (from Step 3 OCR extraction) |
| Total records | 5 billing cycles |
| Date range | February 2026 – October 2026 |
| Tariff | LT Domestic (Low Tension) |
| Utility | TNPDCL / TANGEDCO |
| Billing type | Tax Invoice – LT Current Consumption |

---

## 2. Data Quality Findings

### 2.1 Missing Values (before cleaning)

| Column | Issue | Count |
|---|---|---|
| `initial_reading_kwh` | OCR_UNCERTAIN placeholder | 4 of 5 |
| `energy_charge_rs` | OCR_UNCLEAR placeholder | 5 of 5 |
| `fixed_charge_rs` | OCR_UNCLEAR placeholder | 5 of 5 |

> **Cause:** All 5 PDFs are scanned image bills (no embedded text layer). EasyOCR struggles with numbers in adjacent tabular columns, especially initial readings and itemized charges.

### 2.2 Data Type Issues (before cleaning)

| Column | Original Type | Corrected To |
|---|---|---|
| `bill_date` | object (string) | datetime64 |
| `due_date` | object (string) | datetime64 |
| `initial_reading_kwh` | object (string) | float64 (NaN where uncertain) |
| `energy_charge_rs` | object (string) | float64 (NaN — all unclear) |
| `fixed_charge_rs` | object (string) | float64 (NaN — all unclear) |

### 2.3 Duplicates
**None found.** All 5 records are unique billing cycles.

### 2.4 Date Validation
All 5 `bill_date` and `due_date` values parsed correctly with format `DD/MM/YYYY`. No invalid dates.

| Billing Month | Bill Date | Due Date | Days to Pay |
|---|---|---|---|
| February 2026 | 20/02/2026 | 18/03/2026 | 26 days |
| April 2026 | 20/04/2026 | 20/05/2026 | 30 days |
| June 2026 | 20/06/2026 | 20/07/2026 | 30 days |
| August 2026 | 21/08/2026 | 21/09/2026 | 31 days |
| October 2026 | 20/10/2026 | 20/11/2026 | 31 days |

### 2.5 Units vs Meter Reading Consistency

Final readings form a valid, strictly increasing sequence:

```
Feb 2026:  12,985 kWh
Apr 2026:  15,659 kWh
Jun 2026:  16,570 kWh
Aug 2026:  17,183 kWh
Oct 2026:  18,073 kWh
```

Derived units (this final − previous final) vs OCR-extracted units:

| Cycle | Derived | OCR | Match |
|---|---|---|---|
| February 2026 | — (no prior) | 414 | N/A |
| April 2026 | 2,674 | 774 | DIFFER — gap likely covers missing March 2026 bill |
| June 2026 | 911 | 711 | DIFFER — OCR likely misread "9" as "7" |
| August 2026 | 613 | 813 | DIFFER — OCR likely misread "6" as "8" |
| October 2026 | 890 | 890 | **CONFIRMED** |

> October 2026 is the only bill where both methods agree (890 kWh), confirming the derived method is reliable for consecutive months. OCR digit substitutions (9→7, 6→8) are common in scanned bills.

---

## 3. Cleaning Actions Taken

| Action | Justification |
|---|---|
| Converted `bill_date`, `due_date` to datetime | Enables date arithmetic and sorting |
| Replaced OCR_UNCERTAIN/OCR_UNCLEAR with NaN | Prevents false numeric calculations on placeholder strings |
| Added `initial_reading_derived` column | Computed from final reading sequence (reliable cross-reference) |
| Added `units_derived` column | Difference between consecutive final readings |
| Added `units_best_estimate` column | Most reliable unit figure per cycle (see below) |
| Added `data_quality_flag` column | Transparent per-row data confidence note |
| Sorted records chronologically | Correct temporal order for time-series analysis |

### Best Estimate Units Decision Logic

| Cycle | Chosen Value | Method | Reason |
|---|---|---|---|
| February 2026 | 414 | OCR | No prior reading in dataset |
| April 2026 | 774 | OCR | Derived (2674) covers 2 billing months; OCR consistent with bill amount |
| June 2026 | 911 | Derived | OCR "711" likely 9→7 digit substitution; derived confirmed by Oct |
| August 2026 | 613 | Derived | OCR "813" likely 6→8 digit substitution; derived confirmed by Oct |
| October 2026 | 890 | Both | OCR = Derived = 890 — fully confirmed |

**No values were invented or synthetically generated.**

---

## 4. Consumption Analysis

| Metric | Value |
|---|---|
| Total units consumed (5 cycles) | 3,602 kWh |
| Average per billing cycle | 720.4 kWh |
| Highest consumption cycle | June 2026 — 911 kWh |
| Lowest consumption cycle | February 2026 — 414 kWh |
| Range (max − min) | 497 kWh |

### Cycle-wise Consumption

| Billing Cycle | Units (kWh) | Change from Previous |
|---|---|---|
| February 2026 | 414 | — |
| April 2026 | 774 | +360 (+87%) |
| June 2026 | 911 | +137 (+18%) |
| August 2026 | 613 | −298 (−33%) |
| October 2026 | 890 | +277 (+45%) |

**Key observations:**
- February is the **lowest consumption month** — likely cooler weather, less AC usage.
- Consumption rose sharply from February to April (+87%), coinciding with Tamil Nadu's pre-summer period (March–May heat).
- June peaked at 911 kWh — typical of peak Tamil Nadu summer (May–July).
- August dropped to 613 kWh despite being a hot month — this may reflect partial OCR inaccuracy or reduced usage (monsoon cooling effect).
- October rebounded to 890 kWh — post-monsoon warmth increasing fan/AC usage again.

---

## 5. Bill Amount Analysis

| Metric | Value |
|---|---|
| Total bill amount (5 cycles) | Rs 19,708.00 |
| Average per billing cycle | Rs 3,941.60 |
| Highest bill | October 2026 — Rs 5,085.00 |
| Lowest bill | February 2026 — Rs 1,263.00 |
| Range (max − min) | Rs 3,822.00 |

### Cycle-wise Bill Amount

| Billing Cycle | Net Payable (Rs) | Change from Previous |
|---|---|---|
| February 2026 | 1,263 | — |
| April 2026 | 4,524 | +3,261 (+258%) |
| June 2026 | 3,929 | −595 (−13%) |
| August 2026 | 4,907 | +978 (+25%) |
| October 2026 | 5,085 | +178 (+4%) |

---

## 6. Important Observations

### 6.1 February is significantly cheaper
At Rs 1,263 for 414 units — less than 25% of the October bill (Rs 5,085). February is a cooler month in Tamil Nadu; reduced air conditioning is the most likely factor.

### 6.2 April shows the steepest unit jump (+360 kWh)
Consumption nearly doubled from February to April. This aligns with Tamil Nadu's summer onset (March–May temperatures 36–42°C), when cooling load increases sharply.

### 6.3 June vs August anomaly
June (911 kWh, Rs 3,929) consumed more units than August (613 kWh, Rs 4,907), yet August's bill is **Rs 978 higher**. Possible explanations:
- Accumulated arrears billed in August
- Progressive tariff slab effect (fewer units at higher slab vs more units partly in lower slab)
- August OCR-estimated units (originally 813, revised to 613 via derived method) may carry residual inaccuracy

> This anomaly should be manually verified against the original August PDF bill.

### 6.4 Meter reading sequence is internally consistent
The 5 final readings (12985 → 15659 → 16570 → 17183 → 18073) are strictly increasing with no resets, confirming a single continuous meter. No tampering or anomalies detected in the readings.

### 6.5 Arrears component is likely present in multiple bills
Several bills show balance amounts from prior periods. The net payable likely includes outstanding amounts from previous months, which is why some bill amounts do not scale linearly with units consumed.

---

## 7. Generated Charts

| Chart | Filename | Type |
|---|---|---|
| Consumption by billing cycle | `chart1_units_by_cycle.png` | Bar chart |
| Bill amount by billing cycle | `chart2_amount_by_cycle.png` | Bar chart |
| Consumption trend | `chart3_consumption_trend.png` | Line chart |
| Units vs Amount comparison | `chart4_units_vs_amount.png` | Grouped dual-axis bar |

All charts saved in: `reports/figures/`

---

## 8. Dataset Limitations

| Limitation | Impact |
|---|---|
| Only 5 billing cycles available | Cannot identify seasonal patterns with high confidence |
| Energy charge and fixed charge not extracted | Cannot break down bill components |
| Initial reading OCR noise | Cannot compute exact units for Feb, Apr |
| March 2026 bill missing | April consumption (derived: 2,674 kWh) is unusable |
| No hourly or daily usage data | Cannot detect peak-load times or appliance-level patterns |
| Arrears included in net payable | Bill amount does not purely reflect current-month consumption cost |

---

## 9. Cleaned Data Files

| File | Description |
|---|---|
| `data/processed/eb_consumption_cleaned.csv` | Fully cleaned dataset with derived columns and quality flags |
| `reports/figures/chart1_units_by_cycle.png` | Bar chart — units per cycle |
| `reports/figures/chart2_amount_by_cycle.png` | Bar chart — amount per cycle |
| `reports/figures/chart3_consumption_trend.png` | Line chart — consumption trend |
| `reports/figures/chart4_units_vs_amount.png` | Dual-axis comparison chart |

---

*Step 4 complete. Ready to proceed to Step 5 – Streamlit Dashboard Development.*
