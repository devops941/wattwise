"""
WattWise Input Validation & Unit Conversion Engine
Validates uploaded documents, checks data consistency, and provides standard
electrical unit conversion utilities (Power vs Energy).
"""

from typing import Tuple, List, Dict, Any, Optional
import io
import re
from datetime import datetime


# ── 1. FILE & DOCUMENT VALIDATION ──────────────────────────────────────────

def validate_pdf_file(file_obj: Any, filename: str, max_size_mb: float = 25.0) -> Tuple[bool, Optional[str]]:
    """
    Validates file type, size, and checks for empty or corrupted documents.
    """
    if not filename.lower().endswith(".pdf"):
        return False, f"Invalid file format for '{filename}'. Only PDF documents are supported."
    
    # Read bytes to check size and magic header
    content = None
    if hasattr(file_obj, "read"):
        content = file_obj.read()
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
    elif isinstance(file_obj, (bytes, bytearray)):
        content = bytes(file_obj)

    if content is None or len(content) == 0:
        return False, f"Document '{filename}' is empty (0 bytes)."

    size_mb = len(content) / (1024 * 1024)
    if size_mb > max_size_mb:
        return False, f"Document '{filename}' ({size_mb:.1f} MB) exceeds maximum allowed size of {max_size_mb:.0f} MB."

    # Check PDF magic bytes (%PDF)
    if not content.startswith(b"%PDF"):
        return False, f"Document '{filename}' does not have a valid PDF header (%PDF)."

    return True, None


# ── 2. RECORD-LEVEL INTEGRITY VALIDATION ────────────────────────────────────

def validate_bill_record(record: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """
    Validates an individual extracted/entered bill record.
    Returns: (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    # Check billing month
    b_month = str(record.get("billing_month") or "").strip()
    if not b_month or b_month.lower() in ("unknown", "none", "nan"):
        errors.append("Billing cycle / month is missing.")

    # Check units consumed
    units = record.get("units_consumed")
    if units is None:
        errors.append("Units consumed (kWh) is missing.")
    else:
        try:
            u_val = float(units)
            if u_val < 0:
                errors.append(f"Negative consumption ({u_val} kWh) detected. Physical electricity usage cannot be negative.")
            elif u_val == 0:
                warnings.append("Zero units recorded. If the house was unoccupied, this is valid; otherwise verify the meter.")
            elif u_val > 10000:
                warnings.append(f"Unusually high residential consumption ({u_val:,.0f} kWh). Verify whether this is commercial or typo.")
        except (ValueError, TypeError):
            errors.append(f"Invalid units value: '{units}'. Must be a numeric quantity.")

    # Check net payable amount
    amt = record.get("net_payable")
    if amt is None:
        warnings.append("Net payable amount is missing.")
    else:
        try:
            a_val = float(amt)
            if a_val < 0:
                errors.append(f"Negative bill amount (₹{a_val}). Please verify bill invoice.")
            elif a_val > 200000:
                warnings.append(f"Very high bill amount (₹{a_val:,.0f}). Confirm whether past arrears are included.")
        except (ValueError, TypeError):
            errors.append(f"Invalid net payable amount: '{amt}'. Must be numeric.")

    # Check meter reading if present
    f_read = record.get("final_reading")
    if f_read is not None:
        try:
            fr_val = float(f_read)
            if fr_val < 0:
                errors.append(f"Negative meter reading ({fr_val} kWh). Meter registers are cumulative positive values.")
        except (ValueError, TypeError):
            errors.append(f"Invalid meter reading: '{f_read}'.")

    # Check due date format if provided
    due_date = record.get("due_date")
    if due_date and str(due_date).strip():
        d_str = str(due_date).strip()
        # Common formats in TN bills: DD/MM/YYYY, DD-MM-YYYY, YYYY-MM-DD
        matched = False
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y"):
            try:
                datetime.strptime(d_str, fmt)
                matched = True
                break
            except ValueError:
                pass
        if not matched:
            warnings.append(f"Date format for due date '{d_str}' may need review (expected DD/MM/YYYY).")

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


# ── 3. DATASET-LEVEL / MULTI-BILL VALIDATION ───────────────────────────────

def detect_duplicates_and_inconsistencies(bills: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validates a list of bills for duplicate cycles, meter reading reversals, and gaps.
    """
    seen_months = {}
    duplicates = []
    warnings = []
    
    for idx, b in enumerate(bills):
        m = str(b.get("billing_month") or "").strip().lower()
        if m and m not in ("unknown", "none"):
            if m in seen_months:
                duplicates.append({
                    "month": b.get("billing_month"),
                    "indices": [seen_months[m], idx],
                    "message": f"Duplicate billing cycle '{b.get('billing_month')}' found in bills #{seen_months[m]+1} and #{idx+1}."
                })
            else:
                seen_months[m] = idx

    # Check meter reading monotonicity (if final readings are present)
    readings = []
    for idx, b in enumerate(bills):
        fr = b.get("final_reading")
        if fr is not None:
            try:
                readings.append((idx, float(fr), b.get("billing_month", f"Bill #{idx+1}")))
            except (ValueError, TypeError):
                pass

    if len(readings) >= 2:
        for i in range(1, len(readings)):
            prev_idx, prev_val, prev_m = readings[i - 1]
            curr_idx, curr_val, curr_m = readings[i]
            if curr_val < prev_val:
                warnings.append(
                    f"Meter reading decreased from {prev_val:,.0f} kWh ({prev_m}) to {curr_val:,.0f} kWh ({curr_m}). "
                    "Check for meter replacement, meter rollover, or OCR extraction error."
                )

    return {
        "has_duplicates": len(duplicates) > 0,
        "duplicates": duplicates,
        "warnings": warnings,
    }


# ── 4. ELECTRICAL UNIT CONVERSIONS (POWER VS ENERGY) ───────────────────────

def convert_power(value: float, from_unit: str, to_unit: str) -> float:
    """
    Converts instantaneous power between Watts (W) and Kilowatts (kW).
    Note: Power is instantaneous demand; Energy is Power integrated over time.
    """
    f = from_unit.strip().upper()
    t = to_unit.strip().upper()
    
    if f == t:
        return value
    if f == "W" and t == "KW":
        return value / 1000.0
    if f == "KW" and t == "W":
        return value * 1000.0
    raise ValueError(f"Unsupported power conversion from '{from_unit}' to '{to_unit}'. Supported: W, kW.")


def calculate_energy_kwh(power_val: float, power_unit: str, hours: float) -> float:
    """
    Calculates electrical energy (kWh / Units) from power demand and runtime hours.
    Formula: Energy (kWh) = Power (kW) × Time (hours)
    """
    if power_unit.strip().upper() == "W":
        power_kw = power_val / 1000.0
    elif power_unit.strip().upper() == "KW":
        power_kw = power_val
    else:
        raise ValueError(f"Unknown power unit '{power_unit}'. Use 'W' or 'kW'.")
    
    return round(power_kw * hours, 3)


def get_unit_explanation() -> Dict[str, str]:
    """
    Provides standard reference on electrical units distinguishing power and energy.
    """
    return {
        "Watt (W)": "Unit of instantaneous electrical power (rate of energy transfer). E.g. A 10W LED bulb.",
        "Kilowatt (kW)": "1,000 Watts. Typical household sanctioned load ranges from 2 kW to 5 kW.",
        "Kilowatt-hour (kWh / Unit)": "Unit of electrical ENERGY. 1 kWh = 1,000 Watts operated continuously for 1 hour. This is the unit billed by TANGEDCO.",
        "Crucial Distinction": "Power (kW) is the size of the pipe; Energy (kWh) is the volume of water consumed over time."
    }
