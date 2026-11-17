import pandas as pd
from src.data_processor import get_display_months


def analyze_consumption(df: pd.DataFrame) -> dict:
    months = df["billing_month"].tolist()
    short_months = get_display_months(df)
    
    # Support both column naming conventions (clean dataset vs raw upload)
    u_col = "units_best_estimate" if "units_best_estimate" in df.columns else "units_consumed"
    a_col = "net_payable_rs" if "net_payable_rs" in df.columns else "net_payable"
    r_col = "final_reading_kwh" if "final_reading_kwh" in df.columns else "final_reading"

    units = [int(u) if pd.notna(u) else 0 for u in df[u_col]]
    amounts = [float(a) if pd.notna(a) else 0.0 for a in df[a_col]]
    final_readings = df[r_col].tolist() if r_col in df.columns else [None] * len(units)

    n_cycles = len(units)
    total_units = sum(units)
    avg_units = round(total_units / n_cycles, 1) if n_cycles > 0 else 0.0
    
    # Bi-monthly cycles each cover ~2 calendar months
    avg_monthly_units = round(total_units / (n_cycles * 2), 1) if n_cycles > 0 else 0.0

    max_units = max(units) if units else 0
    max_units_month = months[units.index(max_units)] if units else ""
    min_units = min(units) if units else 0
    min_units_month = months[units.index(min_units)] if units else ""

    total_amount = sum(amounts)
    avg_amount = round(total_amount / n_cycles, 2) if n_cycles > 0 else 0.0
    max_amount = max(amounts) if amounts else 0.0
    max_amount_month = months[amounts.index(max_amount)] if amounts else ""
    min_amount = min(amounts) if amounts else 0.0
    min_amount_month = months[amounts.index(min_amount)] if amounts else ""

    unit_changes = [None]
    for i in range(1, n_cycles):
        change = units[i] - units[i - 1]
        pct = round((change / units[i - 1]) * 100, 1) if units[i - 1] != 0 else 0.0
        unit_changes.append((months[i], change, pct))

    amount_changes = [None]
    for i in range(1, n_cycles):
        change = amounts[i] - amounts[i - 1]
        pct = round((change / amounts[i - 1]) * 100, 1) if amounts[i - 1] != 0 else 0.0
        amount_changes.append((months[i], change, pct))

    # Cost per unit (effective rate)
    overall_effective_rate = round(total_amount / total_units, 2) if total_units > 0 else 0.0
    cycle_rates = [
        round(amounts[i] / units[i], 2) if units[i] > 0 else 0.0
        for i in range(n_cycles)
    ]

    # Daily consumption (kWh/day)
    # If billing_days is present in df, use it; otherwise standard 60-day bi-monthly assumption
    daily_avg_units = []
    for i in range(n_cycles):
        days = 60
        if "billing_days" in df.columns and pd.notna(df["billing_days"].iloc[i]):
            try:
                days = max(1, int(df["billing_days"].iloc[i]))
            except (ValueError, TypeError):
                days = 60
        daily_avg_units.append(round(units[i] / days, 2) if days > 0 else 0.0)

    # Meter reading sequence monotonicity check
    valid_readings = [float(r) for r in final_readings if pd.notna(r)]
    meter_is_monotonic = True
    if len(valid_readings) >= 2:
        meter_is_monotonic = all(valid_readings[i] >= valid_readings[i - 1] for i in range(1, len(valid_readings)))

    return {
        "months": months,
        "short_months": short_months,
        "units": units,
        "amounts": amounts,
        "total_units": total_units,
        "avg_units": avg_units,
        "avg_monthly_units": avg_monthly_units,
        "max_units": max_units,
        "max_units_month": max_units_month,
        "min_units": min_units,
        "min_units_month": min_units_month,
        "total_amount": total_amount,
        "avg_amount": avg_amount,
        "max_amount": max_amount,
        "max_amount_month": max_amount_month,
        "min_amount": min_amount,
        "min_amount_month": min_amount_month,
        "unit_changes": unit_changes,
        "amount_changes": amount_changes,
        "final_readings": final_readings,
        "overall_effective_rate": overall_effective_rate,
        "cycle_rates": cycle_rates,
        "daily_avg_units": daily_avg_units,
        "meter_is_monotonic": meter_is_monotonic,
    }


def detect_anomalies(analysis: dict) -> list:
    anomalies = []
    units = analysis["units"]
    amounts = analysis["amounts"]
    months = analysis["months"]
    unit_changes = analysis["unit_changes"]

    for i in range(1, len(units)):
        unit_went_up = units[i] > units[i - 1]
        amount_went_up = amounts[i] > amounts[i - 1]
        if unit_went_up != amount_went_up:
            direction = (
                "Units increased but amount decreased"
                if unit_went_up
                else "Amount increased but units decreased"
            )
            anomalies.append(
                {
                    "type": "direction_mismatch",
                    "month": months[i],
                    "description": f"{direction} in {months[i]}.",
                }
            )

    for entry in unit_changes:
        if entry is None:
            continue
        month, change, _ = entry
        if abs(change) > 200:
            direction = "jump" if change > 0 else "drop"
            anomalies.append(
                {
                    "type": f"large_{direction}",
                    "month": month,
                    "description": f"Single-cycle unit {direction} of {abs(change)} kWh detected in {month}.",
                }
            )

    return anomalies


def get_peak_analysis(analysis: dict) -> dict:
    units = analysis["units"]
    months = analysis["months"]
    amounts = analysis["amounts"]
    daily_avg = analysis.get("daily_avg_units", [])

    if not units:
        return {
            "peak_month": "",
            "peak_units": 0,
            "trough_month": "",
            "trough_units": 0,
            "peak_amount_month": "",
            "peak_amount": 0.0,
            "range_units": 0,
            "pct_variation": 0.0,
            "peak_daily_avg": 0.0,
            "trough_daily_avg": 0.0,
        }

    peak_idx = units.index(max(units))
    trough_idx = units.index(min(units))
    peak_amt_idx = amounts.index(max(amounts))
    range_units = max(units) - min(units)
    pct_variation = round((range_units / min(units)) * 100, 1) if min(units) != 0 else 0.0

    return {
        "peak_month": months[peak_idx],
        "peak_units": units[peak_idx],
        "trough_month": months[trough_idx],
        "trough_units": units[trough_idx],
        "peak_amount_month": months[peak_amt_idx],
        "peak_amount": amounts[peak_amt_idx],
        "range_units": range_units,
        "pct_variation": pct_variation,
        "peak_daily_avg": daily_avg[peak_idx] if peak_idx < len(daily_avg) else 0.0,
        "trough_daily_avg": daily_avg[trough_idx] if trough_idx < len(daily_avg) else 0.0,
        "data_granularity": "Bi-monthly billing cycle totals (TANGEDCO domestic LT-1A)",
    }
