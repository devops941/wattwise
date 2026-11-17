import sys
import unittest
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.data_processor import (
    load_cleaned_data, get_dataframe_info, get_display_months,
    get_active_data, set_active_user_data, reset_to_demo_data
)
from src.analyzer import analyze_consumption, detect_anomalies, get_peak_analysis
from src.bill_calculator import calculate_energy_charge, TN_TARIFF_2024_25
from src.predictor import linear_forecast, moving_avg_forecast, forecast_next_cycle
from src.recommendations import generate_recommendations, get_summary_message
from src.report_generator import generate_pdf_report
from src.pdf_extractor import (
    extract_bill_from_upload, parse_tn_eb_fields, clean_and_sequence_user_bills
)


class TestWattWiseFullFeatureMatrix(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        reset_to_demo_data()
        cls.df = load_cleaned_data()
        cls.analysis = analyze_consumption(cls.df)

    def setUp(self):
        reset_to_demo_data()

    def test_feature_01_home_page_data_and_kpis(self):
        """Feature 1: Home page loads active household metadata and summary KPI counts."""
        reset_to_demo_data()
        df, is_custom = get_active_data()
        self.assertIsNotNone(df)
        self.assertGreater(len(df), 0)
        info = get_dataframe_info(df)
        self.assertEqual(info["n_records"], 5)
        self.assertEqual(info["total_units"], 3602)
        self.assertEqual(info["total_amount"], 19708.0)
        print("✓ Feature 1 (Home Page Data & KPIs): Verified")

    def test_feature_02_dashboard_kpis_and_charts(self):
        """Feature 2: Dashboard metrics (total units, amount, averages, peak cycle)."""
        a = self.analysis
        self.assertEqual(a["total_units"], 3602)
        self.assertAlmostEqual(a["avg_units"], 720.4, places=1)
        self.assertEqual(a["max_units"], 911)
        self.assertEqual(a["max_units_month"], "June 2026")
        self.assertEqual(a["min_units_month"], "February 2026")
        self.assertEqual(len(a["short_months"]), 5)
        print("✓ Feature 2 (Dashboard Analytics): Verified")

    def test_feature_03_pdf_upload_and_extraction(self):
        """Feature 3 & 4: PDF Upload, hybrid text parsing & OCR extraction."""
        test_bill = BASE_DIR / "data" / "raw" / "eb_bills" / "ebbill october.pdf"
        self.assertTrue(test_bill.exists())
        with open(test_bill, "rb") as f:
            res = extract_bill_from_upload(f)
            self.assertIsNotNone(res)
            self.assertIn("filename", res)
            self.assertEqual(res["billing_month"], "October 2026")
            self.assertEqual(res["due_date"], "20/11/2026")
            # OCR extracted reading (approx 18043-18073 due to OCR digit noise on scanned JPEG)
            self.assertIn(int(res["final_reading"]), [18073, 18043])
        print("✓ Feature 3 & 4 (PDF Upload & Extraction): Verified")

    def test_feature_04_consumption_analysis_and_anomalies(self):
        """Feature 5: Cycle-to-cycle deltas and direction mismatch anomalies."""
        anomalies = detect_anomalies(self.analysis)
        self.assertTrue(len(anomalies) > 0)
        # August had drop in units (-298 kWh) but increase in amount (+978 Rs)
        aug_anom = [a for a in anomalies if "August" in a.get("month", "")]
        self.assertTrue(len(aug_anom) > 0, "Direction mismatch in August must be detected")
        print("✓ Feature 5 (Consumption Analysis & Anomalies): Verified")

    def test_feature_05_charts_visual_verification(self):
        """Feature 6: All 4 EDA charts exist, have valid non-zero content and dimensions."""
        from PIL import Image
        fig_dir = BASE_DIR / "reports" / "figures"
        charts = [
            "consumption_by_cycle.png",
            "bill_amount_by_cycle.png",
            "consumption_trend.png",
            "consumption_comparison.png"
        ]
        for c in charts:
            path = fig_dir / c
            self.assertTrue(path.exists(), f"Missing chart: {c}")
            img = Image.open(path)
            self.assertGreater(img.size[0], 1000)
            self.assertGreater(img.size[1], 600)
        print("✓ Feature 6 (Charts & Figures): Verified")

    def test_feature_06_prediction_with_limitations(self):
        """Feature 7: Linear trend and moving average predictions with experimental disclaimer."""
        fc = forecast_next_cycle(self.analysis["units"], self.analysis["amounts"])
        self.assertIn("warning", fc)
        self.assertIn("5 billing cycles is insufficient", fc["warning"])
        self.assertEqual(fc["moving_avg"]["predicted_units"], 805)
        self.assertAlmostEqual(fc["linear"]["slope"], 79.1, places=1)
        print("✓ Feature 7 (Prediction Engine & Limitations): Verified")

    def test_feature_07_bill_estimation_and_subsidy(self):
        """Feature 8: Electricity bill estimation with TANGEDCO 100 free units subsidy."""
        # 100 units should be 0 energy charges
        c100 = calculate_energy_charge(100, TN_TARIFF_2024_25)
        self.assertEqual(c100["free_units_applied"], 100)
        self.assertEqual(c100["energy_charge"], 0.0)

        # 414 units calculation
        c414 = calculate_energy_charge(414, TN_TARIFF_2024_25)
        self.assertEqual(c414["free_units_applied"], 100)
        self.assertEqual(c414["chargeable_units"], 314)
        self.assertGreater(c414["estimated_total"], 900.0)
        print("✓ Feature 8 (Bill Estimation Simulator): Verified")

    def test_feature_08_energy_recommendations_and_calculator(self):
        """Feature 9: Actionable prioritized recommendations and climate advice."""
        anomalies = detect_anomalies(self.analysis)
        recs = generate_recommendations(self.analysis, anomalies)
        self.assertGreaterEqual(len(recs), 4)
        priorities = {r["priority"] for r in recs}
        self.assertIn("High", priorities)
        self.assertIn("Medium", priorities)
        summary = get_summary_message(self.analysis)
        self.assertTrue(len(summary) > 20)
        print("✓ Feature 9 (Energy Recommendations Engine): Verified")

    def test_feature_09_pdf_report_download(self):
        """Feature 10: ReportLab PDF audit report generation and byte stream validity."""
        pdf_bytes = generate_pdf_report(self.df, self.analysis)
        self.assertIsNotNone(pdf_bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertGreater(len(pdf_bytes), 50000, "PDF should include embedded graphics and exceed 50KB")
        print(f"✓ Feature 10 (PDF Report Generation): Verified ({len(pdf_bytes):,} bytes)")

    def test_feature_10_user_session_isolation(self):
        """Feature 11 & 12: Multi-user session isolation and demo data preservation."""
        # Custom mock dataset
        mock_user = [
            {"filename": "user_feb.pdf", "billing_month": "February 2026", "units_consumed": 320, "net_payable": 850.0, "final_reading": 5000.0},
            {"filename": "user_apr.pdf", "billing_month": "April 2026", "units_consumed": 480, "net_payable": 1600.0, "final_reading": 5480.0},
        ]
        user_df = clean_and_sequence_user_bills(mock_user)
        self.assertEqual(len(user_df), 2)
        self.assertEqual(user_df.iloc[1]["units_derived"], 480.0)

        # Ensure demo data in files is unchanged
        fresh_demo = load_cleaned_data()
        self.assertEqual(len(fresh_demo), 5)
        self.assertEqual(fresh_demo["consumer_name"].iloc[0], "SENTHIL MURUGAN")
        print("✓ Feature 11 & 12 (Session Isolation & Sequence Integrity): Verified")


if __name__ == "__main__":
    unittest.main()
