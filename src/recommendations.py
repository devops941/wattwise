"""
WattWise Energy Recommendation Engine
Generates data-supported recommendations based on actual household billing history,
while clearly distinguishing data-backed findings from general Tamil Nadu residential best practices.
"""

def generate_recommendations(analysis: dict, anomalies: list) -> list:
    recs = []

    units = analysis.get("units", [])
    months = analysis.get("months", [])
    unit_changes = analysis.get("unit_changes", [])
    max_units = analysis.get("max_units", 0)
    max_units_month = analysis.get("max_units_month", "")
    min_units = analysis.get("min_units", 0)
    min_units_month = analysis.get("min_units_month", "")
    avg_units = analysis.get("avg_units", 0)

    # ── 1. DATA-SUPPORTED RECOMMENDATIONS ──

    # Peak cycle alert
    if max_units > 800:
        recs.append(
            {
                "priority": "High",
                "category": "Peak Consumption",
                "tag": "Data-Supported Finding",
                "title": f"Mitigate Severe Peak Usage (Air Conditioning & Cooling) ({max_units} kWh in {max_units_month})",
                "detail": (
                    f"Your highest recorded consumption was {max_units} kWh in {max_units_month}. "
                    "At this level, you cross into TANGEDCO's top slab rates (₹10.50 – ₹11.55 / unit). "
                    "While bi-monthly billing totals cannot isolate specific appliances, cooling loads "
                    "during Tamil Nadu summers are the primary historical driver of high residential demand. "
                    "Setting air conditioning thermostats to 24–26°C and ensuring clean condenser coils can reduce peak cooling energy by 15–20%."
                ),
            }
        )
    elif max_units > 500:
        recs.append(
            {
                "priority": "High",
                "category": "Tariff Optimization",
                "tag": "Data-Supported Finding",
                "title": f"Avoid the 500 kWh Tariff Threshold (Peak: {max_units} kWh)",
                "detail": (
                    f"Your peak consumption of {max_units} kWh exceeded the critical 500 kWh TANGEDCO threshold. "
                    "Under Tamil Nadu domestic tariff LT-1A, units above 500 kWh are billed at significantly higher tier rates (₹8.40+ / kWh). "
                    "Trimming just 10–15% of flexible load can pull your cycle below 500 kWh and yield disproportionate financial savings."
                ),
            }
        )

    # Spike / Jump alert
    for entry in unit_changes:
        if entry is None:
            continue
        month, change, pct = entry
        if change > 150:
            recs.append(
                {
                    "priority": "High",
                    "category": "Consumption Surge",
                    "tag": "Data-Supported Finding",
                    "title": f"Investigate Sudden Usage Surge / Spike (+{change} kWh in {month})",
                    "detail": (
                        f"Units billed surged by +{change} kWh (+{pct}%) in {month} compared to the previous cycle. "
                        "Because individual appliance sub-metering is not present, investigate operational changes during that period "
                        "(e.g., guest stays, continuous AC operation during heatwaves, water pump schedule changes, or meter read date shifts)."
                    ),
                }
            )

    # Tariff / Arrears mismatch alert
    for anomaly in anomalies:
        if anomaly.get("type") == "direction_mismatch" and "amount increased" in anomaly.get("description", "").lower():
            recs.append(
                {
                    "priority": "Medium",
                    "category": "Billing Integrity",
                    "tag": "Data-Supported Finding",
                    "title": f"Review Bill Charges & Arrears in {anomaly.get('month', 'Recent Cycle')}",
                    "detail": (
                        f"In {anomaly.get('month')}, your net payable rose despite lower unit consumption. "
                        "This pattern typically indicates carried-over arrears, delayed payment surcharges, "
                        "or annual fixed charge adjustments. Compare the itemized breakdown against your previous receipt."
                    ),
                }
            )

    # Baseline efficiency recognition
    if min_units > 0 and min_units < 500:
        recs.append(
            {
                "priority": "Low",
                "category": "Baseline Efficiency",
                "tag": "Data-Supported Finding",
                "title": f"Replicate Low-Usage Habits from {min_units_month} ({min_units} kWh)",
                "detail": (
                    f"Your consumption fell to a baseline low of {min_units} kWh in {min_units_month}. "
                    "Review whether natural cross-ventilation, lower AC runtime, or seasonal weather enabled this savings, "
                    "and replicate those operational habits in higher-load cycles."
                ),
            }
        )

    # ── 2. GENERAL TAMIL NADU EFFICIENCY BEST PRACTICES ──

    recs.append(
        {
            "priority": "Medium",
            "category": "Appliance Efficiency",
            "tag": "General Best Practice",
            "title": "Adopt 5-Star BLDC Ceiling Fans",
            "detail": (
                "Standard residential ceiling fans consume 70–80 Watts each. Replacing them with 28-Watt BLDC (brushless DC) "
                "5-star rated fans reduces fan electricity by over 60%. In a household running 3 fans for 12 hours/day, "
                "this saves ~110–130 kWh per bi-monthly billing cycle."
            ),
        }
    )

    recs.append(
        {
            "priority": "Medium",
            "category": "Solar Energy",
            "tag": "General Best Practice",
            "title": "Evaluate Rooftop Solar under PM Surya Ghar",
            "detail": (
                f"With an average consumption of {avg_units:.0f} kWh per bi-monthly cycle (~{avg_units/2:.0f} kWh/month), "
                "a 2 kW or 3 kW grid-interactive rooftop solar PV system would generate 240–360 kWh per month in Tamil Nadu's climate, "
                "potentially reducing your net payable energy charges to near zero under TANGEDCO net metering."
            ),
        }
    )

    recs.append(
        {
            "priority": "Low",
            "category": "Lighting & Standby",
            "tag": "General Best Practice",
            "title": "Eliminate Standby Phantom Loads & Upgrade to LED",
            "detail": (
                "Appliances left on standby (TVs, set-top boxes, microwave clocks, chargers) continuously consume 5–15 Watts. "
                "Using master switch power strips and replacing remaining CFL/filament lamps with 9W LEDs provides effortless baseline reductions."
            ),
        }
    )

    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    recs.sort(key=lambda r: priority_order.get(r["priority"], 99))
    return recs


def get_summary_message(analysis: dict) -> str:
    max_month = analysis.get("max_units_month", "Peak Period")
    max_units = analysis.get("max_units", 0)
    avg_units = analysis.get("avg_units", 0)

    if max_units > 800:
        context = "Summer cooling is likely your largest cost driver; focus on thermostat management and slab thresholds."
    elif avg_units > 500:
        context = "Average usage is near the 500-unit high-tariff threshold; trimming 10% can lower your slab rate."
    else:
        context = "Your consumption is moderate; small efficiency upgrades can sustain low baseline expenditure."

    return f"Highest consumption recorded in {max_month} ({max_units} kWh). {context}"
