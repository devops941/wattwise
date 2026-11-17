import sys
import unittest
from pathlib import Path
import pandas as pd
import numpy as np

# Add repo root to sys.path
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
    parse_tn_eb_fields, clean_and_sequence_user_bills
)


class TestWattWiseCore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = load_cleaned_data()
        cls.analysis = analyze_consumption(cls.df)

    def test_01_data_loading_and_cleaning(self):
        """Verify the 5 actual Tamil Nadu EB billing records and columns."""
        df = self.df
        self.assertEqual(len(df), 5, "Dataset must contain exactly 5 billing cycles")
        expected_cols = [
            "bill_file", "billing_month", "bill_date", "final_reading_kwh",
            "units_best_estimate", "net_payable_rs", "data_quality_flag"
        ]
        for col in expected_cols:
            self.assertIn(col, df.columns, f"Column {col} missing from cleaned data")

        # Verify exact totals
        self.assertEqual(int(df["units_best_estimate"].sum()), 3602, "Total units must be 3602 kWh")
        self.assertEqual(float(df["net_payable_rs"].sum()), 19708.0, "Total amount must be ₹19,708.00")

        # Sequence integrity
        readings = df["final_reading_kwh"].tolist()
        for i in range(1, len(readings)):
            self.assertGreater(readings[i], readings[i - 1], "Final readings must be strictly increasing")

    def test_02_data_processor_helpers(self):
        """Test dataframe info and display month formatters."""
        info = get_dataframe_info(self.df)
        self.assertEqual(info["n_records"], 5)
        self.assertEqual(info["total_units"], 3602)
        self.assertEqual(info["total_amount"], 19708.0)

        display_months = get_display_months(self.df)
        self.assertEqual(len(display_months), 5)
        self.assertTrue(any("Feb" in m for m in display_months))
        self.assertTrue(any("Oct" in m for m in display_months))

    def test_03_consumption_analyzer(self):
        """Verify cycle analytics, averages, and peak-trough discovery."""
        res = self.analysis
        self.assertEqual(res["total_units"], 3602)
        self.assertAlmostEqual(res["avg_units"], 720.4, places=1)
        self.assertEqual(res["max_units"], 911)
        self.assertEqual(res["max_units_month"], "June 2026")
        self.assertEqual(res["min_units"], 414)
        self.assertEqual(res["min_units_month"], "February 2026")

        self.assertEqual(res["max_amount"], 5085.0)
        self.assertEqual(res["max_amount_month"], "October 2026")
        self.assertEqual(res["min_amount"], 1263.0)
        self.assertEqual(res["min_amount_month"], "February 2026")

    def test_04_anomaly_detection(self):
        """Verify detection of direction mismatch (August: units down, amount up)."""
        anomalies = detect_anomalies(self.analysis)
        self.assertIsInstance(anomalies, list)
        self.assertTrue(len(anomalies) > 0, "Must detect at least 1 billing anomaly")
        
        # Verify direction mismatch detected for August
        mismatch_found = any(
            a["type"] == "direction_mismatch" and "August" in a["month"]
            for a in anomalies
        )
        self.assertTrue(mismatch_found, "Must detect August direction mismatch anomaly")

    def test_05_peak_analysis(self):
        """Verify peak and trough metrics calculation."""
        peak = get_peak_analysis(self.analysis)
        self.assertEqual(peak["peak_month"], "June 2026")
        self.assertEqual(peak["peak_units"], 911)
        self.assertEqual(peak["trough_month"], "February 2026")
        self.assertEqual(peak["trough_units"], 414)
        self.assertEqual(peak["range_units"], 497)
        self.assertGreater(peak["pct_variation"], 100.0)

    def test_06_bill_calculator(self):
        """Verify TANGEDCO LT domestic tariff slab calculations and free units."""
        # Test 1: Under 100 units should have 0 energy charges (100 free units)
        calc_100 = calculate_energy_charge(100, TN_TARIFF_2024_25)
        self.assertEqual(calc_100["free_units_applied"], 100)
        self.assertEqual(calc_100["chargeable_units"], 0)
        self.assertEqual(calc_100["energy_charge"], 0.0)

        # Test 2: 400 units
        calc_400 = calculate_energy_charge(400, TN_TARIFF_2024_25)
        self.assertEqual(calc_400["chargeable_units"], 300)
        # 101-200 (100 units @ 2.0 = 200), 201-500 (200 units @ 3.5 = 700) -> Energy charge 900
        self.assertEqual(calc_400["energy_charge"], 900.0)
        self.assertGreater(calc_400["estimated_total"], 900.0)

    def test_07_prediction_engine(self):
        """Verify linear regression, moving average, and small-data disclaimer."""
        units = self.analysis["units"]
        amounts = self.analysis["amounts"]
        
        lin = linear_forecast(units)
        self.assertIn("predicted_units", lin)
        self.assertIn("slope", lin)
        self.assertEqual(lin["trend"], "Increasing")

        ma = moving_avg_forecast(units, window=3)
        self.assertIn("predicted_units", ma)
        # Last 3 cycles: Jun (911), Aug (613), Oct (890) -> avg ~ 804.67 -> 805
        self.assertEqual(ma["predicted_units"], 805)

        fc = forecast_next_cycle(units, amounts)
        self.assertIn("warning", fc)
        self.assertIn("insufficient", fc["warning"].lower())

    def test_08_recommendation_engine(self):
        """Verify tailored energy recommendations."""
        anomalies = detect_anomalies(self.analysis)
        recs = generate_recommendations(self.analysis, anomalies)
        self.assertIsInstance(recs, list)
        self.assertTrue(len(recs) >= 4)

        priorities = [r["priority"] for r in recs]
        self.assertIn("High", priorities)
        self.assertIn("Medium", priorities)

        summary = get_summary_message(self.analysis)
        self.assertIn("June 2026", summary)

    def test_09_pdf_report_generation(self):
        """Verify ReportLab PDF generation builds a valid, non-empty PDF document."""
        pdf_bytes = generate_pdf_report(self.df, self.analysis)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 10000, "PDF size must be > 10 KB")
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"), "File must start with standard PDF header")

    def test_10_field_parsing_regex(self):
        """Verify parsing of Tamil Nadu EB bill text patterns."""
        sample_text = (
            "Tax Invoice for LT Current Consumption Charges for the Month of October_2026\n"
            "Section: KOODALNAGAR Service Conn No: 05-472-024-917\n"
            "Name: SENTHIL MURUGAN\n"
            "20/11/2026 Due Date\n"
            "REAdING 18073.0\n"
            "Pay This Bill Online Rs-5,085\n"
            "Units Consumed: 890\n"
        )
        parsed = parse_tn_eb_fields(sample_text)
        self.assertEqual(parsed.get("billing_month"), "October 2026")
        self.assertEqual(parsed.get("net_payable"), 5085.0)
        self.assertEqual(parsed.get("due_date"), "20/11/2026")

    def test_11_user_bill_sequencer(self):
        """Verify clean_and_sequence_user_bills processes uploaded bill dictionaries."""
        mock_user_bills = [
            {"filename": "bill1.pdf", "billing_month": "January 2026", "bill_date": "2026-01-20", "final_reading": 10000.0, "units_consumed": 300, "net_payable": 800.0},
            {"filename": "bill2.pdf", "billing_month": "March 2026", "bill_date": "2026-03-20", "final_reading": 10450.0, "units_consumed": 450, "net_payable": 1400.0},
        ]
        user_df = clean_and_sequence_user_bills(mock_user_bills)
        self.assertEqual(len(user_df), 2)
        self.assertEqual(user_df.iloc[1]["units_derived"], 450.0)
        self.assertEqual(user_df.iloc[1]["units_best_estimate"], 450)

    def test_12_session_isolation(self):
        """Verify session data isolation between demo and custom user."""
        reset_to_demo_data()
        df_demo, is_custom = get_active_data()
        self.assertFalse(is_custom)
        self.assertEqual(len(df_demo), 5)

        mock_df = pd.DataFrame({
            "billing_month": ["Jan 2026"],
            "units_best_estimate": [500],
            "net_payable_rs": [1500.0],
            "consumer_name": ["TEST CONSUMER"],
            "connection_no": ["01-111-222-333"],
            "section": ["TEST SECTION"],
            "tariff_category": ["LT Domestic"]
        })
        set_active_user_data(mock_df)
        df_custom, is_custom2 = get_active_data()
        self.assertTrue(is_custom2)
        self.assertEqual(len(df_custom), 1)

        reset_to_demo_data()
        df_demo2, is_custom3 = get_active_data()
        self.assertFalse(is_custom3)
        self.assertEqual(len(df_demo2), 5)


if __name__ == "__main__":
    unittest.main()
