import os
import json
import shutil
import re
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List
import pandas as pd
from datetime import datetime

from src.pdf_extractor import clean_and_sequence_user_bills

BASE_DIR = Path(__file__).resolve().parent.parent
HOUSEHOLDS_DIR = BASE_DIR / "data" / "households"
HOUSEHOLDS_DIR.mkdir(parents=True, exist_ok=True)


def mask_consumer_name(name: Optional[str]) -> str:
    if not name:
        return "Household Consumer"
    name = str(name).strip()
    if len(name) <= 3:
        return name + "***"
    return name[:3] + "***"


def mask_connection_no(conn_no: Optional[str]) -> str:
    if not conn_no:
        return "N/A"
    clean = re.sub(r"[^\w]", "", str(conn_no))
    if len(clean) <= 4:
        return "***" + clean
    return "***" + clean[-4:]


def sanitize_id(val: str) -> str:
    cleaned = re.sub(r"[^\w\-]", "_", str(val).strip().lower())
    return cleaned[:32] if cleaned else "household"


def get_household_dir(household_id: str) -> Path:
    return HOUSEHOLDS_DIR / sanitize_id(household_id)


def load_household_meta(household_id: str) -> Optional[Dict[str, Any]]:
    h_dir = get_household_dir(household_id)
    meta_path = h_dir / "meta.json"
    if meta_path.exists():
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def load_household_data(household_id: str) -> Optional[pd.DataFrame]:
    h_dir = get_household_dir(household_id)
    csv_path = h_dir / "consumption.csv"
    if csv_path.exists():
        try:
            df = pd.read_csv(csv_path)
            for col in ("bill_date", "due_date"):
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
            df = df.sort_values("bill_date").reset_index(drop=True)
            return df
        except Exception:
            return None
    return None


def save_household_profile(
    household_name: str,
    connection_no: str,
    section: str,
    tariff_category: str,
    bills_list: List[Dict[str, Any]],
    raw_files: Optional[List[Any]] = None
) -> Tuple[str, pd.DataFrame]:
    """
    Creates an isolated household profile with clean sequenced dataset and metadata.
    """
    # Generate unique ID based on connection no or timestamp
    base_tag = sanitize_id(connection_no) if connection_no and len(connection_no) >= 5 else "hh"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    household_id = f"{base_tag}_{timestamp}"
    
    h_dir = get_household_dir(household_id)
    h_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean and sequence the uploaded bills
    df = clean_and_sequence_user_bills(bills_list)
    df["consumer_name"] = household_name
    df["connection_no"] = connection_no
    df["section"] = section
    df["tariff_category"] = tariff_category
    
    # Save CSV
    csv_path = h_dir / "consumption.csv"
    df.to_csv(csv_path, index=False)
    
    # Save raw uploaded PDFs securely in private household folder
    if raw_files:
        bills_dir = h_dir / "bills"
        bills_dir.mkdir(parents=True, exist_ok=True)
        for rf in raw_files:
            try:
                fname = getattr(rf, "name", "bill.pdf")
                safe_fname = re.sub(r"[^\w\.\-]", "_", fname)
                content = rf.read() if hasattr(rf, "read") else None
                if content:
                    (bills_dir / safe_fname).write_bytes(content)
                if hasattr(rf, "seek"):
                    rf.seek(0)
            except Exception:
                pass

    # Save meta.json
    meta = {
        "id": household_id,
        "name": household_name,
        "connection_no": connection_no,
        "section": section,
        "tariff_category": tariff_category,
        "cycles_count": len(df),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_demo": False
    }
    with open(h_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        
    # Activate in current session
    activate_household(household_id, df, meta)
    
    return household_id, df


def activate_household(household_id: str, df: Optional[pd.DataFrame] = None, meta: Optional[Dict[str, Any]] = None):
    try:
        import streamlit as st
        st.session_state["active_household_id"] = household_id
        if df is not None:
            st.session_state["active_household_df"] = df
        else:
            st.session_state["active_household_df"] = load_household_data(household_id)
            
        if meta is not None:
            st.session_state["active_household_meta"] = meta
        else:
            st.session_state["active_household_meta"] = load_household_meta(household_id)
    except Exception:
        pass


def activate_demo():
    """Activates the baseline Senthil Murugan demo household."""
    try:
        import streamlit as st
        st.session_state["active_household_id"] = "demo_senthil_murugan"
        st.session_state["active_household_df"] = load_household_data("demo_senthil_murugan")
        st.session_state["active_household_meta"] = load_household_meta("demo_senthil_murugan")
    except Exception:
        pass


def clear_active_household():
    """Resets session to no household loaded (new user state)."""
    try:
        import streamlit as st
        st.session_state["active_household_id"] = None
        st.session_state["active_household_df"] = None
        st.session_state["active_household_meta"] = None
    except Exception:
        pass


def get_active_household() -> Tuple[Optional[pd.DataFrame], Optional[Dict[str, Any]]]:
    """
    Returns (df, meta) for the active household.
    If no household is active (new visitor), returns (None, None).
    """
    try:
        import streamlit as st
        hid = st.session_state.get("active_household_id")
        if not hid:
            return None, None
            
        # Check cache in session_state
        df = st.session_state.get("active_household_df")
        meta = st.session_state.get("active_household_meta")
        if df is not None and meta is not None:
            return df, meta
            
        # Load from disk
        df = load_household_data(hid)
        meta = load_household_meta(hid)
        if df is not None and meta is not None:
            st.session_state["active_household_df"] = df
            st.session_state["active_household_meta"] = meta
            return df, meta
    except Exception:
        pass
    return None, None


def list_saved_households() -> List[Dict[str, Any]]:
    """Lists all saved household profiles (excluding demo)."""
    profiles = []
    if not HOUSEHOLDS_DIR.exists():
        return profiles
        
    for p in HOUSEHOLDS_DIR.iterdir():
        if p.is_dir() and p.name != "demo_senthil_murugan":
            meta = load_household_meta(p.name)
            if meta:
                profiles.append(meta)
    # Sort newest first
    profiles.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return profiles
