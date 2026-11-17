import unittest
import shutil
from pathlib import Path
import pandas as pd

from src.validator import (
    validate_pdf_file, validate_bill_record,
    detect_duplicates_and_inconsistencies,
    convert_power, calculate_energy_kwh, get_unit_explanation
)
from src.household_manager import (
    save_household_profile, get_household_dir, load_household_data,
    load_household_meta, activate_household, activate_demo, clear_active_household,
    get_active_household, mask_consumer_name, mask_connection_no, list_saved_households,
    HOUSEHOLDS_DIR
)
from src.analyzer import analyze_consumption, get_peak_analysis, detect_anomalies
from src.predictor import forecast_next_cycle
from src.bill_calculator import calculate_energy_charge, TANGEDCO_OFFICIAL_TARIFF, TN_TARIFF_2024_25
from src.recommendations import generate_recommendations, get_summary_message
from src.report_generator import generate_pdf_report


class TestMultiHouseholdAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_hh_id = None

    @classmethod
    def tearDownClass(cls):
        # Clean up test household folder if created
        if cls.test_hh_id:
            h_dir = get_household_dir(cls.test_hh_id)
            if h_dir.exists():
                shutil.rmtree(h_dir, ignore_errors=True)

    def test_01_public_landing_empty_state(self):
        """Verify new visitor starts with no active household (Module 1)."""
        clear_active_household()
        df, meta = get_active_household()
        self.assertIsNone(df, "New session must not pre-load any user's data")
        self.assertIsNone(meta, "New session must have no active metadata")

    def test_02_validation_and_unit_conversion(self):
        """Verify validation engine and electrical unit conversions (Module 3)."""
        # File validation
        is_val, err = validate_pdf_file(b"NOT_A_PDF", "sample.txt")
        self.assertFalse(is_val)
        self.assertIn("Invalid file format", err)

        is_val, err = validate_pdf_file(b"", "empty.pdf")
        self.assertFalse(is_val)
        self.assertIn("empty", err)

        is_val, err = validate_pdf_file(b"%PDF-1.4 sample content", "valid.pdf")
        self.assertTrue(is_val)
        self.assertIsNone(err)

        # Record validation
        rec_invalid = {"billing_month": "Feb 2026", "units_consumed": -50, "net_payable": 500}
        is_val, errs, warns = validate_bill_record(rec_invalid)
        self.assertFalse(is_val)
        self.assertTrue(any("Negative consumption" in e for e in errs))

        rec_valid = {"billing_month": "Feb 2026", "units_consumed": 450, "net_payable": 2100.0}
        is_val, errs, warns = validate_bill_record(rec_valid)
        self.assertTrue(is_val)
        self.assertEqual(len(errs), 0)

        # Duplicate billing cycle detection
        bills = [
            {"billing_month": "June 2026", "units_consumed": 600},
            {"billing_month": "June 2026", "units_consumed": 650},
        ]
        dup_res = detect_duplicates_and_inconsistencies(bills)
        self.assertTrue(dup_res["has_duplicates"])
        self.assertEqual(len(dup_res["duplicates"]), 1)

        # Electrical Unit conversions
        self.assertEqual(convert_power(1500, "W", "kW"), 1.5)
        self.assertEqual(convert_power(2.5, "kW", "W"), 2500.0)
        # 1.5 kW for 6 hours = 9.0 kWh
        self.assertEqual(calculate_energy_kwh(1500, "W", 6.0), 9.0)
        self.assertEqual(calculate_energy_kwh(1.5, "kW", 6.0), 9.0)

    def test_03_create_isolated_new_household(self):
        """Verify creating a new independent household profile (Modules 2 & 5)."""
        new_bills = [
            {
                "billing_month": "February 2026",
                "units_consumed": 380,
                "net_payable": 1650.0,
                "final_reading": 11500.0,
                "due_date": "20/03/2026",
            },
            {
                "billing_month": "April 2026",
                "units_consumed": 620,
                "net_payable": 3450.0,
                "final_reading": 12120.0,
                "due_date": "20/05/2026",
            },
            {
                "billing_month": "June 2026",
                "units_consumed": 840,
                "net_payable": 5200.0,
                "final_reading": 12960.0,
                "due_date": "20/07/2026",
            },
        ]

        hh_id, df = save_household_profile(
            household_name="Karthik Residence",
            connection_no="07-210-098-112",
            section="VELACHERY",
            tariff_category="LT-1A Domestic",
            bills_list=new_bills
        )
        self.__class__.test_hh_id = hh_id

        # Check directory existence
        h_dir = get_household_dir(hh_id)
        self.assertTrue(h_dir.exists(), "Household folder must be created in data/households/")
        self.assertTrue((h_dir / "meta.json").exists())
        self.assertTrue((h_dir / "consumption.csv").exists())

        # Check metadata
        meta = load_household_meta(hh_id)
        self.assertEqual(meta["name"], "Karthik Residence")
        self.assertEqual(meta["connection_no"], "07-210-098-112")
        self.assertEqual(meta["section"], "VELACHERY")
        self.assertFalse(meta["is_demo"])
        self.assertEqual(meta["cycles_count"], 3)

        # Check active session
        active_df, active_meta = get_active_household()
        self.assertIsNotNone(active_df)
        self.assertEqual(len(active_df), 3)
        self.assertEqual(active_meta["id"], hh_id)

    def test_04_privacy_and_consumer_masking(self):
        """Verify privacy masking for names and connections (Module 15)."""
        self.assertEqual(mask_consumer_name("Karthik Residence"), "Kar***")
        self.assertEqual(mask_consumer_name("SENTHIL MURUGAN"), "SEN***")
        self.assertEqual(mask_connection_no("07-210-098-112"), "***8112")
        self.assertEqual(mask_connection_no("05-472-024-917"), "***4917")

    def test_05_domain_calculations_and_trends(self):
        """Verify domain calculation engine and comparisons (Modules 6 & 7)."""
        h_df = load_household_data(self.test_hh_id)
        self.assertIsNotNone(h_df)
        analysis = analyze_consumption(h_df)

        # Units: [380, 620, 840] -> Total = 1840 kWh
        self.assertEqual(analysis["total_units"], 1840)
        self.assertEqual(analysis["avg_units"], round(1840 / 3, 1))
        self.assertEqual(analysis["max_units"], 840)
        self.assertEqual(analysis["max_units_month"], "June 2026")
        self.assertEqual(analysis["min_units"], 380)
        self.assertEqual(analysis["min_units_month"], "February 2026")

        # Amounts: [1650, 3450, 5200] -> Total = 10300
        self.assertEqual(analysis["total_amount"], 10300.0)
        self.assertEqual(analysis["avg_amount"], round(10300.0 / 3, 2))

        # Effective rate
        self.assertAlmostEqual(analysis["overall_effective_rate"], round(10300 / 1840, 2), places=2)

        # Progression changes
        # Cycle 2: 620 - 380 = +240 kWh (+63.2%)
        ch2 = analysis["unit_changes"][1]
        self.assertEqual(ch2[1], 240)
        self.assertAlmostEqual(ch2[2], 63.2, places=1)

        # Meter monotonicity
        self.assertTrue(analysis["meter_is_monotonic"])

    def test_06_peak_consumption_discovery(self):
        """Verify peak load discovery on available granularity (Module 8)."""
        h_df = load_household_data(self.test_hh_id)
        analysis = analyze_consumption(h_df)
        peak = get_peak_analysis(analysis)

        self.assertEqual(peak["peak_month"], "June 2026")
        self.assertEqual(peak["peak_units"], 840)
        self.assertEqual(peak["trough_month"], "February 2026")
        self.assertEqual(peak["trough_units"], 380)
        self.assertEqual(peak["range_units"], 460)
        self.assertAlmostEqual(peak["pct_variation"], round((460 / 380) * 100, 1), places=1)
        self.assertIn("Bi-monthly", peak["data_granularity"])

    def test_07_experimental_prediction(self):
        """Verify experimental forecast and uncertainty warnings (Module 9)."""
        h_df = load_household_data(self.test_hh_id)
        analysis = analyze_consumption(h_df)
        forecast = forecast_next_cycle(analysis["units"], analysis["amounts"])

        self.assertIn("linear", forecast)
        self.assertIn("moving_avg", forecast)
        self.assertGreater(forecast["linear"]["predicted_units"], 0)
        self.assertGreater(forecast["moving_avg"]["predicted_units"], 0)
        self.assertIn("insufficient", forecast["warning"].lower())

    def test_08_bill_estimation_tangedco_tariff(self):
        """Verify TANGEDCO LT-1A domestic tariff calculation (Module 10)."""
        # For 500 units under LT-1A:
        # 0-100: 0.00
        # 101-200 (100 units @ 2.35) = 235.0
        # 201-400 (200 units @ 4.70) = 940.0
        # 401-500 (100 units @ 6.30) = 630.0
        # Energy charge = 1805.00
        # Fixed charge = 50.0
        # Surcharge (5% of 1805) = 90.25
        # Total = 1945.25
        calc = calculate_energy_charge(500, TANGEDCO_OFFICIAL_TARIFF)
        self.assertEqual(calc["free_units_applied"], 100)
        self.assertEqual(calc["chargeable_units"], 400)
        self.assertAlmostEqual(calc["energy_charge"], 1805.00, places=2)
        self.assertAlmostEqual(calc["estimated_total"], 1945.25, places=2)

    def test_09_recommendations(self):
        """Verify data-supported recommendations generation (Module 11)."""
        h_df = load_household_data(self.test_hh_id)
        analysis = analyze_consumption(h_df)
        anomalies = detect_anomalies(analysis)
        recs = generate_recommendations(analysis, anomalies)

        self.assertGreater(len(recs), 0)
        # Check that tags are present
        tags = [r.get("tag") for r in recs]
        self.assertTrue(any("Data-Supported" in t for t in tags if t))
        self.assertTrue(any("General" in t for t in tags if t))

        summary = get_summary_message(analysis)
        self.assertIn("June 2026", summary)

    def test_10_dynamic_pdf_report_generation(self):
        """Verify dynamic PDF audit report generation for this household (Module 13)."""
        h_df = load_household_data(self.test_hh_id)
        analysis = analyze_consumption(h_df)
        consumer_info = {
            "consumer_name": "Karthik Residence",
            "connection_no": "07-210-098-112",
            "section": "VELACHERY",
            "tariff_category": "LT-1A Domestic",
        }

        pdf_bytes = generate_pdf_report(h_df, analysis, consumer_info)
        self.assertIsNotNone(pdf_bytes)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"), "Must be a valid PDF document")

    def test_11_dataset_isolation_and_switching(self):
        """Verify strict multi-household data isolation (Modules 2 & 15)."""
        # 1. Switch to demo
        activate_demo()
        demo_df, demo_meta = get_active_household()
        self.assertTrue(demo_meta["is_demo"])
        self.assertEqual(len(demo_df), 5)
        self.assertEqual(demo_meta["name"], "SENTHIL MURUGAN")

        # 2. Switch back to custom household
        activate_household(self.test_hh_id)
        c_df, c_meta = get_active_household()
        self.assertFalse(c_meta["is_demo"])
        self.assertEqual(len(c_df), 3)
        self.assertEqual(c_meta["name"], "Karthik Residence")
        self.assertEqual(c_meta["connection_no"], "07-210-098-112")

        # 3. Ensure demo data was NOT modified by custom household
        demo_meta_disk = load_household_meta("demo_senthil_murugan")
        self.assertEqual(demo_meta_disk["cycles_count"], 5)
        self.assertEqual(demo_meta_disk["name"], "SENTHIL MURUGAN")

        # 4. Clear household (logout / reset)
        clear_active_household()
        df_none, meta_none = get_active_household()
        self.assertIsNone(df_none)
        self.assertIsNone(meta_none)


if __name__ == "__main__":
    unittest.main()
