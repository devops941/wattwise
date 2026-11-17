import os
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
from src.pdf_extractor import parse_tn_eb_fields, clean_and_sequence_user_bills


class TestWattWiseFinalAudit(unittest.TestCase):

    def setUp(self):
        self.df = load_cleaned_data()
        self.analysis = analyze_consumption(self.df)

    def test_01_preservation_of_actual_eb_bills(self):
        """Verify the 5 original EB bills exist and match expected file names."""
        bill_dir = BASE_DIR / "data" / "raw" / "eb_bills"
        expected_bills = [
            "ebbill april.pdf", "ebbill august.pdf", "ebbill feb.pdf",
            "ebbill october.pdf", "ebebill june.pdf"
        ]
        for b in expected_bills:
            p = bill_dir / b
            self.assertTrue(p.exists(), f"Missing original bill: {b}")
            self.assertGreater(p.stat().st_size, 100000, f"Bill file appears corrupt or truncated: {b}")

    def test_02_cleaned_csv_integrity(self):
        """Verify processed CSV records, values, and absence of invented data."""
        df = self.df
        self.assertEqual(len(df), 5)
        # Check units sequence
        self.assertEqual(df["units_best_estimate"].tolist(), [414, 774, 911, 613, 890])
        # Check amounts sequence
        self.assertEqual(df["net_payable_rs"].tolist(), [1263.0, 4524.0, 3929.0, 4907.0, 5085.0])
        # Check final readings
        self.assertEqual(df["final_reading_kwh"].tolist(), [12985.0, 15659.0, 16570.0, 17183.0, 18073.0])
        # Check monotonic increase
        self.assertTrue((df["final_reading_kwh"].diff().dropna() > 0).all())

    def test_03_eda_visualizations_exist_and_valid(self):
        """Verify the 4 required EDA charts exist, have valid sizes, and non-empty content."""
        fig_dir = BASE_DIR / "reports" / "figures"
        required_figs = [
            "consumption_by_cycle.png",
            "bill_amount_by_cycle.png",
            "consumption_trend.png",
            "consumption_comparison.png"
        ]
        for f in required_figs:
            p = fig_dir / f
            self.assertTrue(p.exists(), f"Missing required figure: {f}")
            self.assertGreater(p.stat().st_size, 20000, f"Figure too small / invalid: {f}")

    def test_04_consumption_and_peak_analysis(self):
        """Verify core analytical calculations."""
        a = self.analysis
        self.assertEqual(a["total_units"], 3602)
        self.assertAlmostEqual(a["avg_units"], 720.4, places=1)
        self.assertEqual(a["total_amount"], 19708.0)
        self.assertAlmostEqual(a["avg_amount"], 3941.60, places=2)

        peak = get_peak_analysis(a)
        self.assertEqual(peak["peak_month"], "June 2026")
        self.assertEqual(peak["peak_units"], 911)
        self.assertEqual(peak["trough_month"], "February 2026")
        self.assertEqual(peak["trough_units"], 414)
        self.assertEqual(peak["peak_amount_month"], "October 2026")
        self.assertEqual(peak["peak_amount"], 5085.0)

    def test_05_prediction_limitations_and_scenarios(self):
        """Verify forecast functions include warnings and calculate regression correctly."""
        fc = forecast_next_cycle(self.analysis["units"], self.analysis["amounts"])
        self.assertIn("warning", fc)
        self.assertIn("insufficient", fc["warning"].lower())
        self.assertEqual(fc["data_points"], 5)
        # OLS slope on [414, 774, 911, 613, 890] is exactly 79.1 kWh/cycle
        self.assertAlmostEqual(fc["linear"]["slope"], 79.1, places=1)
        # 3-cycle MA is 805
        self.assertEqual(fc["moving_avg"]["predicted_units"], 805)

    def test_06_bill_estimation_logic(self):
        """Verify TANGEDCO tariff calculation and free units."""
        calc = calculate_energy_charge(500, TN_TARIFF_2024_25)
        self.assertEqual(calc["free_units_applied"], 100)
        self.assertEqual(calc["chargeable_units"], 400)
        self.assertGreater(calc["estimated_total"], 0)
        self.assertIn("disclaimer", calc)

    def test_07_recommendations_customization(self):
        """Verify recommendations engine responds to actual data patterns."""
        anomalies = detect_anomalies(self.analysis)
        recs = generate_recommendations(self.analysis, anomalies)
        titles = [r["title"] for r in recs]
        self.assertTrue(any("Air Conditioning" in t for t in titles))
        self.assertTrue(any("Spike" in t for t in titles))
        self.assertTrue(any("Arrears" in t for t in titles))

    def test_08_pdf_report_generation(self):
        """Verify PDF report builds completely and contains standard PDF header."""
        pdf_bytes = generate_pdf_report(self.df, self.analysis)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
        self.assertGreater(len(pdf_bytes), 50000, "PDF size must be > 50 KB")

    def test_09_user_session_isolation(self):
        """Verify user data isolation logic."""
        reset_to_demo_data()
        demo_df, is_custom = get_active_data()
        self.assertFalse(is_custom)
        self.assertEqual(len(demo_df), 5)
        self.assertEqual(demo_df["consumer_name"].iloc[0], "SENTHIL MURUGAN")

    def test_10_field_parsing_robustness(self):
        """Verify robust parsing of Tamil Nadu EB bills."""
        sample_text = (
            "Month of October_2026\n"
            "05-472-024-917\n"
            "SENTHIL MURUGAN\n"
            "Due Date: 20/11/2026\n"
            "Net Payable: Rs 5,085.00\n"
            "Final Reading: 18073\n"
            "Units Consumed: 890\n"
        )
        parsed = parse_tn_eb_fields(sample_text)
        self.assertEqual(parsed["billing_month"], "October 2026")
        self.assertEqual(parsed["net_payable"], 5085.0)
        self.assertEqual(parsed["units_consumed"], 890)
        self.assertEqual(parsed["final_reading"], 18073.0)


if __name__ == "__main__":
    unittest.main()
