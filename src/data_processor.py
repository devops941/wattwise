import pandas as pd
from pathlib import Path
from typing import Tuple, Optional, Dict, Any


def load_cleaned_data() -> pd.DataFrame:
    """Loads baseline verified Senthil Murugan dataset."""
    base_dir = Path(__file__).resolve().parent.parent
    csv_path = base_dir / "data" / "processed" / "eb_consumption_cleaned.csv"
    df = pd.read_csv(csv_path)
    for col in ("bill_date", "due_date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    df = df.sort_values("bill_date").reset_index(drop=True)
    return df


def get_active_data() -> Tuple[Optional[pd.DataFrame], bool]:
    """
    Returns (df, is_custom_user)
    - If a custom household is active: returns (df, True)
    - If demo dataset is activated: returns (demo_df, False)
    - If new session with no household loaded yet: returns (None, False)
    """
    try:
        from src.household_manager import get_active_household
        df, meta = get_active_household()
        if df is not None and meta is not None:
            is_custom = not meta.get("is_demo", False)
            return df, is_custom
    except Exception:
        pass
    return None, False


def set_active_user_data(df: pd.DataFrame):
    """Activates a custom DataFrame in the active session."""
    from src.household_manager import activate_household
    meta = {
        "id": "custom_session_household",
        "name": df["consumer_name"].iloc[0] if "consumer_name" in df.columns and len(df) > 0 else "Custom Household",
        "connection_no": df["connection_no"].iloc[0] if "connection_no" in df.columns and len(df) > 0 else "",
        "section": df["section"].iloc[0] if "section" in df.columns and len(df) > 0 else "Domestic",
        "tariff_category": df["tariff_category"].iloc[0] if "tariff_category" in df.columns and len(df) > 0 else "LT-1A Domestic",
        "cycles_count": len(df),
        "is_demo": False
    }
    activate_household("custom_session_household", df=df, meta=meta)


def reset_to_demo_data():
    """Resets session to the baseline Senthil Murugan demonstration dataset."""
    from src.household_manager import activate_demo
    activate_demo()


def get_dataframe_info(df: pd.DataFrame) -> dict:
    if df is None or len(df) == 0:
        return {
            "n_records": 0,
            "date_range_start": None,
            "date_range_end": None,
            "total_units": 0,
            "total_amount": 0.0,
            "missing_initial_readings": 0,
            "confirmed_units_count": 0,
        }
    return {
        "n_records": len(df),
        "date_range_start": df["bill_date"].min() if "bill_date" in df.columns else None,
        "date_range_end": df["bill_date"].max() if "bill_date" in df.columns else None,
        "total_units": int(df["units_best_estimate"].sum()) if "units_best_estimate" in df.columns else (
            int(df["units_consumed"].sum()) if "units_consumed" in df.columns else 0
        ),
        "total_amount": float(df["net_payable_rs"].sum()) if "net_payable_rs" in df.columns else (
            float(df["net_payable"].sum()) if "net_payable" in df.columns else 0.0
        ),
        "missing_initial_readings": int(df["initial_reading_kwh"].isna().sum()) if "initial_reading_kwh" in df.columns else 0,
        "confirmed_units_count": int(df["data_quality_flag"].str.contains("confirmed|derived", case=False, na=False).sum())
        if "data_quality_flag" in df.columns
        else 0,
    }


def get_display_months(df: pd.DataFrame) -> list:
    if df is None:
        return []
    labels = []
    for idx, row in df.iterrows():
        month_str = str(row.get("billing_month", "") or "")
        parts = month_str.split()
        if len(parts) >= 2 and len(parts[0]) >= 3:
            month_abbr = parts[0][:3].capitalize()
            year_short = parts[1][-2:]
            labels.append(f"{month_abbr} '{year_short}")
        else:
            dt = row.get("bill_date")
            if pd.notna(dt) and hasattr(dt, "strftime"):
                labels.append(dt.strftime("%b '%y"))
            elif month_str:
                labels.append(month_str)
            else:
                labels.append(f"Cycle {idx+1}")
    return labels
