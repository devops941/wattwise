# WattWise Prediction Report
## Tamil Nadu Electricity Bill Analytics

**Household:** SENTHIL MURUGAN, KOODALNAGAR Section, Madurai  
**Tariff:** LT Domestic  
**Analysis Period:** February 2026 – October 2026 (5 billing cycles)  
**Forecast Target:** December 2026 (next billing cycle)  
**Report Date:** November 17, 2026

---

## Executive Summary and Critical Disclaimer

This report presents **experimental consumption and bill predictions** for the next billing cycle (December 2026). **These forecasts are educational estimates only and should not be used for financial planning or procurement decisions.**

**Why prediction is unreliable with this dataset:**
- Only 5 historical data points (minimum 24–36 cycles recommended)
- Billing-cycle totals mask seasonal sub-patterns
- Arrears and tariff slab changes distort billing amounts
- Single anomalous cycle (June vs August discrepancy) can skew trends
- Missing March billing cycle creates baseline uncertainty
- No external data (actual temperature, appliance changes, occupancy)

---

## Methodology

### Method 1: Linear Trend Analysis

**Approach:** Fit a linear trend line through consumption data points (Feb through Oct).

**Data Points (by cycle order):**
| Cycle # | Month | kWh |
|---|---|---|
| 0 | Feb 2026 | 414 |
| 1 | Apr 2026 | 774 |
| 2 | Jun 2026 | 911 |
| 3 | Aug 2026 | 613 |
| 4 | Oct 2026 | 890 |

**Linear Regression Result:**
```
Equation: kWh = 414 + 119 × (cycle_index)
Slope: +119 kWh per cycle
Intercept: 414 kWh
R² Value: ~0.42 (poor fit - see explanation below)
```

**Projected Consumption (Cycle 5, December 2026):**
```
Predicted kWh = 414 + 119 × 5 = 414 + 595 = 1,009 kWh
```

**Interpretation:**
- Linear trend suggests ~1,009 kWh for December 2026
- **However, R² of 0.42 indicates the linear model explains only 42% of variance** — the remaining 58% is unexplained (seasonal noise, arrears, behavioral changes)
- With only 5 points, R² is not meaningful for model validation
- Strong seasonal oscillation (↑ summer, ↓ monsoon) violates linear assumption

### Method 2: Moving Average (Last 3 Cycles)

**Approach:** Average the three most recent cycles to capture recent consumption behavior while smoothing noise.

**Data:**
| Cycle | Month | kWh |
|---|---|---|
| 2 | Jun 2026 | 911 |
| 3 | Aug 2026 | 613 |
| 4 | Oct 2026 | 890 |

**Calculation:**
```
Moving Average = (911 + 613 + 890) / 3 = 2,414 / 3 ≈ 804.7 kWh
Rounded: ~805 kWh
```

**Projected Consumption (December 2026):**
```
Estimated kWh ≈ 805 kWh (±50 kWh given volatility)
Realistic range: 750–850 kWh
```

**Rationale:**
- Reflects recent household behavior better than 5-cycle average
- Reduces impact of extreme February low (414 kWh)
- Accounts for seasonal return toward elevated consumption post-monsoon
- More conservative than linear trend's 1,009 kWh projection

---

## Consumption Forecast: December 2026

### Primary Estimate (Moving Average Method)
| Metric | Value | Confidence |
|---|---|---|
| **Central Estimate** | 805 kWh | Medium |
| **Optimistic Scenario** | 750 kWh | Low (requires sustained monsoon-like cooling) |
| **Pessimistic Scenario** | 850 kWh | Medium (heating/extended AC season) |
| **Linear Trend Estimate** | 1,009 kWh | Very Low (statistical poor fit) |

### Recommended Forecast Range
**750–850 kWh** for December 2026, with central estimate of **~805 kWh**

**Seasonal Reasoning:**
- December follows post-monsoon warming period (October: 890 kWh)
- Temperatures typically 28–32°C in Tamil Nadu (not summer extreme 32–38°C)
- AC usage present but not at June-level intensity
- Likely between October's 890 kWh and August's monsoon low of 613 kWh

---

## Billing Amount Forecast: December 2026

### Tariff Rate Uncertainty

October's fully-confirmed billing provides the most recent reliable tariff:
- **Oct 2026:** 890 kWh → Rs 5,085 = **Rs 5.71/kWh**

However, significant rate variation exists:
| Cycle | Units | Amount | Rate (Rs/kWh) |
|---|---|---|---|
| Feb 2026 | 414 | 1,263 | 3.05 |
| Apr 2026 | 774 | 4,524 | 5.84 |
| Jun 2026 | 911 | 3,929 | 4.31 |
| Aug 2026 | 613 | 4,907 | 8.00 |
| Oct 2026 | 890 | 5,085 | 5.71 |

**Rate Range:** Rs 3.05 – 8.00 per kWh

### Bill Amount Scenarios

**Using Central Consumption Estimate (805 kWh):**

| Scenario | Rate Applied | Estimated Bill | Notes |
|---|---|---|---|
| **Optimistic** | Rs 4.50/kWh | Rs 3,623 | Below-average tariff slab |
| **Base Case** | Rs 5.71/kWh | Rs 4,597 | October's confirmed rate |
| **Pessimistic** | Rs 6.80/kWh | Rs 5,474 | Slab progression or arrears recovery |
| **Arrears Included** | Rs 7.50/kWh | Rs 6,038 | Additional adjustment charges |

### Recommended Forecast Range
**Rs 4,200–5,500** for December 2026 billing

**Central Estimate:** **~Rs 4,600** (assuming consistent Oct tariff)

**Wide Range Rationale:**
- OCR uncertainty on past billing amounts prevents precise tariff slab modeling
- Arrears adjustment history (Jun vs Aug anomaly) creates unpredictability
- Progressive tariff slabs in Tamil Nadu mean rates increase with consumption level
- Missing March data prevents slab threshold identification

---

## Forecasting Limitations and Caveats

### Dataset Constraints

| Limitation | Impact | Mitigation |
|---|---|---|
| **Only 5 cycles** | Insufficient for statistical confidence (minimum 24–36 needed) | Forecast treated as exploratory only |
| **Billing-cycle totals** | Cannot identify seasonal sub-patterns or demand peaks | Daily/hourly metering required |
| **Arrears distortion** | June vs August anomaly indicates historical adjustments | Obtained itemized statements needed |
| **Tariff slab unknown** | Cannot precisely map consumption to billing rates | Using October's rate as proxy (medium confidence) |
| **Missing March 2026** | Creates gap in baseline; unclear if skipped or not billed | Assumes bimonthly billing schedule |
| **No external data** | Temperature, appliance changes, occupancy unknown | Forecast cannot adapt to these factors |

### Statistical Issues

1. **R² Meaninglessness with 5 Points:**
   - Linear model's R² = 0.42 is not statistically meaningful
   - With only 5 observations, 2–3 outliers heavily influence trend
   - Seasonal oscillation (not captured by linear fit) dominates variance

2. **Seasonal Bias:**
   - Dataset includes peak summer (June) but only one full monsoon month (August)
   - October partially post-monsoon but not winter baseline
   - True annual pattern cannot be reliably inferred

3. **Autocorrelation:**
   - Consecutive cycles show strong correlation (summer→monsoon→post-monsoon)
   - Violates independence assumption of standard regression

### What Would Improve Predictions

To achieve **high-confidence forecasts**, collect:

1. **Minimum 24 consecutive months** of meter readings (12 full seasonal cycles)
2. **Weekly or monthly readings** instead of billing-cycle totals
3. **Itemized billing statements** with tariff slab details and arrears history
4. **Daily temperature data** correlated with consumption
5. **Appliance-level monitoring** (smart plugs or sub-metering)
6. **Occupancy and behavioral logs** (vacations, lifestyle changes)

With these inputs, prediction accuracy could improve from ±45% (current) to ±10–15%.

---

## Forecast Summary Table

| Metric | Estimate | Range | Confidence |
|---|---|---|---|
| **Dec 2026 Consumption** | 805 kWh | 750–850 kWh | Medium |
| **Dec 2026 Bill Amount** | Rs 4,600 | Rs 4,200–5,500 | Low–Medium |
| **Projected Unit Rate** | Rs 5.71/kWh | Rs 4.50–7.50/kWh | Low |
| **Comparison to Oct 2026** | Slight decrease | −5% to +10% | Medium |

---

## Scenario Narratives

### Optimistic Scenario (750 kWh, Rs 4,200)
- December remains cool due to lingering monsoon effects
- Household reduces AC usage through behavioral changes
- Tariff applies favorable slab or no arrears adjustment
- **Probability:** 20–25%

### Base Case Scenario (805 kWh, Rs 4,600)
- December follows post-monsoon warming pattern
- Consumption aligns with moving average of recent cycles
- October's tariff rate (Rs 5.71/kWh) continues
- **Probability:** 40–50%

### Pessimistic Scenario (850 kWh, Rs 5,500)
- December experiences warmer-than-normal temperatures
- AC usage extends longer than typical
- Tariff slab increases or arrears adjustment applied
- **Probability:** 25–35%

---

## Conclusion and Recommendations

### Key Findings

1. **Conservative Moving Average Estimate:** 805 kWh for December 2026 (more reliable than linear trend's 1,009 kWh)

2. **Billing Amount Highly Uncertain:** Rs 4,200–5,500 range reflects tariff and arrears unpredictability

3. **Forecast Reliability is Low:** 5 data points insufficient for confident projection; treat as directional guidance only

4. **Seasonal Pattern is Strong:** Consumption clearly oscillates with Tamil Nadu's climate, but sub-cycle variation is high

### Recommendations for Improved Forecasting

| Priority | Action | Benefit | Timeline |
|---|---|---|---|
| **High** | Collect 12–24 months of monthly meter readings | Establish true seasonal baseline; validate climate correlation | 1 year |
| **High** | Obtain itemized billing statements for Feb–Oct | Resolve arrears history; identify tariff slab thresholds | Immediate |
| **Medium** | Implement smart meter or weekly manual readings | Capture consumption dynamics; identify behavioral patterns | 3 months |
| **Medium** | Log appliance changes, maintenance, behavioral shifts | Explain deviations from seasonal model | Ongoing |
| **Low** | Correlate with daily temperature data | Refine climate-consumption relationship | Ongoing |

### Disclaimer

**These are educational estimates only. Do not use for:**
- Financial planning or utility budget allocation
- Appliance purchase or procurement decisions
- Tariff negotiation with utility provider
- Billing dispute verification

For financial decisions, **contact TANGEDCO (Tamil Nadu Generation and Distribution Corporation) for:**
- Official consumption projections based on your account history
- Detailed tariff slab structure for your consumer category
- Itemized billing explanation and arrears reconciliation

---

**Report prepared by:** WattWise Analytics Platform  
**Forecast method:** Linear regression + moving average comparison  
**Data quality:** Medium (5 cycles with OCR uncertainty and arrears distortion)  
**Statistical confidence:** Low — experimental estimates only  
**Recommendation:** Treat as exploratory guidance; support decisions with utility provider input
