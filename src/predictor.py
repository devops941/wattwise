import numpy as np


def linear_forecast(units: list, n_ahead: int = 1) -> dict:
    if len(units) < 2:
        return {
            "predicted_units": units[0] if units else 0,
            "slope": 0.0,
            "trend": "Insufficient Data",
            "r_squared": 0.0,
            "method": "Linear Trend (OLS)",
        }

    x = np.arange(len(units), dtype=float)
    y = np.array(units, dtype=float)
    coeffs = np.polyfit(x, y, 1)
    slope = float(coeffs[0])
    intercept = float(coeffs[1])

    predicted = slope * (len(units) - 1 + n_ahead) + intercept

    y_pred = np.polyval(coeffs, x)
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r_squared = round(1 - ss_res / ss_tot, 4) if ss_tot != 0 else 0.0

    if abs(slope) < 5:
        trend = "Stable"
    elif slope > 0:
        trend = "Increasing"
    else:
        trend = "Decreasing"

    return {
        "predicted_units": max(0, int(round(predicted))),
        "slope": round(slope, 4),
        "trend": trend,
        "r_squared": r_squared,
        "method": "Linear Trend (OLS)",
    }


def moving_avg_forecast(units: list, window: int = 3) -> dict:
    if not units:
        return {"predicted_units": 0, "window": 0, "method": "Moving Average"}
    effective_window = min(window, len(units))
    last_values = units[-effective_window:]
    predicted = sum(last_values) / len(last_values)
    return {
        "predicted_units": max(0, int(round(predicted))),
        "window": effective_window,
        "method": f"Moving Average (window={effective_window})",
    }


def forecast_next_cycle(units: list, amounts: list) -> dict:
    linear = linear_forecast(units)
    ma = moving_avg_forecast(units)

    avg_units = sum(units) / len(units) if units else 1
    avg_amount = sum(amounts) / len(amounts) if amounts else 0
    rate_per_unit = avg_amount / avg_units if avg_units != 0 else 0

    estimated_amount_linear = round(linear["predicted_units"] * rate_per_unit, 2)
    estimated_amount_ma = round(ma["predicted_units"] * rate_per_unit, 2)

    return {
        "linear": linear,
        "moving_avg": ma,
        "estimated_amount_linear": estimated_amount_linear,
        "estimated_amount_ma": estimated_amount_ma,
        "data_points": len(units),
        "warning": (
            f"Experimental estimate only. {len(units)} billing cycles is insufficient "
            "for high-confidence statistical time-series forecasting (minimum 24-36 cycles recommended)."
        ),
    }
