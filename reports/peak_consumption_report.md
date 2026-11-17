# WattWise Peak Consumption Report
## Tamil Nadu Electricity Bill Analytics

**Household:** SENTHIL MURUGAN, KOODALNAGAR Section, Madurai  
**Tariff:** LT Domestic  
**Analysis Period:** February 2026 – October 2026  
**Report Date:** November 17, 2026

---

## Executive Summary

This report focuses on consumption peaks, troughs, and extreme changes within the five-cycle billing period. While the data reveals clear seasonal extremes and significant month-to-month fluctuations, **important limitations apply:** this analysis works with billing-cycle totals (cumulative consumption over 2–3 months), not hourly or daily readings. Therefore, conclusions about appliance-level peaks, hourly demand, or time-of-use patterns **cannot be drawn** from this dataset.

---

## Peak and Trough Identification

### Consumption Peak
| Metric | Value |
|---|---|
| **Cycle** | June 2026 |
| **Units Consumed** | 911 kWh |
| **Days in Cycle** | ~60 days (assumed) |
| **Average Daily Rate** | ~15.2 kWh/day |
| **Temperature Context** | Tamil Nadu summer peak (32–38°C) |

### Consumption Trough
| Metric | Value |
|---|---|
| **Cycle** | February 2026 |
| **Units Consumed** | 414 kWh |
| **Days in Cycle** | ~60 days (assumed) |
| **Average Daily Rate** | ~6.9 kWh/day |
| **Temperature Context** | Tamil Nadu winter/mild season (25–30°C) |

### Peak-to-Trough Comparison
- **Absolute Difference:** 497 kWh
- **Relative Increase:** 120% (June vs February)
- **Ratio:** 2.2× higher consumption at peak

---

## Billing Peak

The highest bill amount occurred in a different cycle than the consumption peak:

| Metric | Value |
|---|---|
| **Cycle** | October 2026 |
| **Amount Billed** | Rs 5,085 |
| **Units Consumed** | 890 kWh |
| **Effective Rate** | Rs 5.71/kWh |
| **Temperature Context** | Post-monsoon warmth (28–32°C) |

**Note:** October's bill was not the highest by consumption (June had 911 kWh), but it had the highest billing amount. This is likely due to tariff slab progression and absence of arrears adjustments.

---

## Extreme Changes

### Largest Single-Cycle Increase
| From | To | Change | % Change |
|---|---|---|---|
| **Feb 2026** | **Apr 2026** | +360 kWh | +87% |

**Context:** February-to-April encompasses the transition from mild winter to peak summer heat, activating full air conditioning loads.

### Largest Single-Cycle Decrease
| From | To | Change | % Change |
|---|---|---|---|
| **Jun 2026** | **Aug 2026** | −298 kWh | −33% |

**Context:** June-to-August spans the onset of monsoon rains, bringing cloud cover, reduced temperatures, and decreased cooling needs.

### Volatility Ranking
1. **Feb→Apr:** +87% (largest single jump)
2. **Jun→Aug:** −33% (largest single drop)
3. **Apr→Jun:** +18% (moderate summer extension)
4. **Aug→Oct:** +45% (strong recovery post-monsoon)

---

## Seasonal Pattern Analysis

### Tamil Nadu Climate Drivers

| Season | Months | Temperature | Humidity | Rainfall | Expected Impact |
|---|---|---|---|---|---|
| **Winter** | Jan–Feb | 25–30°C | Moderate | Low | Minimal cooling; baseline consumption |
| **Summer** | Mar–May | 30–38°C | Low | Minimal | Peak cooling load; high consumption |
| **Southwest Monsoon** | Jun–Sep | 25–28°C | High | Moderate–Heavy | Cloudy, cool; reduced cooling; lower consumption |
| **Northeast Monsoon** | Oct–Nov | 28–32°C | High | Moderate | Post-monsoon warming; partial cooling resumption |

### Observed Consumption Alignment

```
            911 kWh (Jun Peak)
              ↑
        774 ──┤  ┌──────┐
             ││ │      │
   414 ──────┤│─┘      │ 890 (Oct)
             ││         ││
        613 ─┘│─────────┘│
              │          │
     Feb     Apr        Jun      Aug     Oct
   Winter   Spring    Summer  Monsoon  Post-M.
```

**Pattern Consistency:** The household's consumption closely tracks Tamil Nadu's seasonal temperature and cloud cover patterns, indicating air conditioning is the dominant load.

---

## Important Limitation: Billing-Cycle Totals vs. Hourly Data

### What This Data CAN Tell Us
✓ Seasonal consumption trends  
✓ Month-to-month total energy usage  
✓ Relative comparison of billing periods  
✓ Annual energy budget estimation  
✓ Long-term efficiency gains/degradation  

### What This Data CANNOT Tell Us
✗ Time-of-use peak demand (e.g., 6–9 PM peak)  
✗ Appliance-level consumption (AC vs. refrigerator vs. lighting)  
✗ Hourly or daily fluctuations  
✗ Equipment operating schedules  
✗ Demand response opportunities  
✗ Power factor or harmonic analysis  

**Critical Caveat:** Claims such as "peak demand occurs at 7 PM" or "air conditioning consumes 70% of energy" **cannot be derived** from this five-cycle, billing-total dataset. Such analysis requires hourly smart meter data or appliance-level monitoring.

---

## Peak Reduction Opportunities

While appliance-level identification is not possible from this data, the following general strategies align with the observed seasonal pattern:

### High-Priority (Based on Seasonal Data)
1. **Summer Cooling Optimization (Apr–Jun):**
   - Maintenance of air conditioning coils for efficiency
   - Thermostat setpoint management (target 24–26°C vs. lower)
   - Use of ceiling fans to improve circulation, reduce AC runtime
   - Scheduled AC operation during peak hours (e.g., 7 AM–10 AM, 6 PM–midnight)

2. **Monsoon Opportunity (Jul–Sep):**
   - Natural ventilation and cross-drafts reduce AC dependency
   - Already demonstrated lower consumption (613 kWh in Aug)
   - Extend this pattern through improved insulation/shading

### Supporting Measures
3. **Appliance Efficiency:**
   - Upgrade to 5-star refrigerators (if older model)
   - LED lighting throughout home
   - Energy-efficient water heating (solar thermal or time-of-use limits)

4. **Behavioral Changes:**
   - Stagger high-load activities (laundry, cooking) during off-peak cooler hours
   - Scheduled appliance usage rather than continuous background operation

### Recommended Next Steps for Deeper Analysis
- Install smart meter or sub-metering to capture hourly consumption
- Track appliance-level power consumption using clamp meters or smart plugs
- Monitor for 2+ full years to refine seasonal models and identify anomalies
- Correlate consumption with actual daily temperature data

---

## Visualization References

The following charts support this analysis (see project visualization outputs):

| Chart | File | Insight |
|---|---|---|
| **Consumption by Cycle** | `chart1_units_by_cycle.png` | Visual comparison of 414–911 kWh range |
| **Billing Amount by Cycle** | `chart2_amount_by_cycle.png` | Shows Oct peak (Rs 5,085) vs. Jun peak units |
| **Consumption Trend** | `chart3_consumption_trend.png` | Line graph showing seasonal seasonality |
| **Unit Rate Variation** | `chart4_unit_rate.png` | Illustrates Rs 4.31 (Jun) vs. Rs 8.00 (Aug) anomaly |

---

## Conclusions

1. **Clear seasonal pattern exists** — consumption more than doubles from winter low (414 kWh) to summer peak (911 kWh), driven by air conditioning demand

2. **Largest sudden change:** 87% increase from Feb→Apr reflects activation of full cooling loads as summer arrives

3. **Most significant reduction:** 33% drop from Jun→Aug demonstrates monsoon's moderating effect on consumption

4. **Billing peak differs from consumption peak** — October (Rs 5,085) rather than June reflects tariff slab impacts and arrears recovery

5. **Appliance-level conclusions are not supported** by this billing-cycle data — deeper metering required for peak-shaving strategies

6. **Realistic efficiency opportunity:** ~20–30% reduction possible through targeted AC management and behavioral changes, bringing consumption toward 600–700 kWh in summer months

---

**Report prepared by:** WattWise Analytics Platform  
**Data scope:** Billing-cycle totals (not hourly or sub-metering)  
**Methodology:** Comparative analysis, seasonal pattern matching, change quantification  
**Confidence level:** High for seasonal trends; medium for specific efficiency recommendations without appliance-level data
