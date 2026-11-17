"""
TANGEDCO Bi-monthly Electricity Bill Calculation Engine
Calculates energy charges, slab breakdowns, and estimated totals according to
official Tamil Nadu Electricity Regulatory Commission (TNERC) domestic tariff schedules.
"""

# TANGEDCO Revised Bi-monthly Domestic Tariff 2024-25 (TNERC Tariff Order LT-1A)
TANGEDCO_OFFICIAL_TARIFF = {
    "name": "TANGEDCO LT-1A Domestic (Bi-monthly Tariff 2024-25)",
    "free_units": 100,
    "slabs": [
        {"from": 101, "to": 200, "rate": 2.35},
        {"from": 201, "to": 400, "rate": 4.70},
        {"from": 401, "to": 500, "rate": 6.30},
        {"from": 501, "to": 600, "rate": 8.40},
        {"from": 601, "to": 800, "rate": 9.45},
        {"from": 801, "to": 1000, "rate": 10.50},
        {"from": 1001, "to": None, "rate": 11.55},
    ],
    "fixed_charge": 50.0,
    "wheeling_surcharge_pct": 5.0,
    "note": "Official TNERC tariff order for bi-monthly LT-1A domestic consumer connections.",
}

# Simplified 3-slab model for reference / comparative modeling
TN_TARIFF_2024_25 = {
    "name": "TN LT-I Domestic (Approximate 2024-25)",
    "free_units": 100,
    "slabs": [
        {"from": 101, "to": 200, "rate": 2.00},
        {"from": 201, "to": 500, "rate": 3.50},
        {"from": 501, "to": None, "rate": 5.00},
    ],
    "fixed_charge": 100.0,
    "wheeling_surcharge_pct": 15.0,
    "note": "Approximate rates. Actual tariff may differ. Verify with your TANGEDCO bill.",
}

_DISCLAIMER = (
    "This is an estimated calculation using Tamil Nadu tariff schedules. "
    "Actual physical bills include municipal tax, arrears, or adjustments not reflected here."
)


def calculate_energy_charge(units: int, tariff: dict = TN_TARIFF_2024_25) -> dict:
    units = max(0, int(units))
    free_units = tariff.get("free_units", 0)
    chargeable_units = max(0, units - free_units)
    free_units_applied = min(units, free_units)

    slab_breakdown = []
    remaining = chargeable_units
    energy_charge = 0.0

    for slab in tariff["slabs"]:
        if remaining <= 0:
            break
        slab_from = slab["from"]
        slab_to = slab["to"]
        rate = slab["rate"]

        if slab_to is None:
            slab_units = remaining
        else:
            slab_capacity = slab_to - slab_from + 1
            slab_units = min(remaining, slab_capacity)

        if slab_units <= 0:
            continue

        amount = round(slab_units * rate, 2)
        energy_charge += amount
        label = (
            f"{slab_from}-{slab_to} units"
            if slab_to is not None
            else f"Above {slab_from - 1} units"
        )
        slab_breakdown.append(
            {
                "slab": label,
                "units": slab_units,
                "rate": rate,
                "amount": amount,
            }
        )
        remaining -= slab_units

    energy_charge = round(energy_charge, 2)
    fixed_charge = tariff.get("fixed_charge", 0.0)
    wheeling_pct = tariff.get("wheeling_surcharge_pct", 0.0)
    wheeling_surcharge = round(energy_charge * wheeling_pct / 100, 2)
    estimated_total = round(energy_charge + fixed_charge + wheeling_surcharge, 2)

    return {
        "units": units,
        "free_units_applied": free_units_applied,
        "chargeable_units": chargeable_units,
        "slab_breakdown": slab_breakdown,
        "energy_charge": energy_charge,
        "fixed_charge": fixed_charge,
        "wheeling_surcharge": wheeling_surcharge,
        "estimated_total": estimated_total,
        "tariff_note": tariff.get("note", ""),
        "disclaimer": _DISCLAIMER,
    }


def estimate_bill(units: int) -> dict:
    return calculate_energy_charge(units)
