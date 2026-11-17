import unittest
from pathlib import Path
from src.pdf_extractor import extract_bill_from_upload, clean_and_sequence_user_bills

BASE_DIR = Path(__file__).resolve().parent.parent

class TestExtractionAudit(unittest.TestCase):
    def test_actual_5_eb_bills_extraction(self):
        bills_dir = BASE_DIR / "data" / "raw" / "eb_bills"
        pdf_files = list(bills_dir.glob("*.pdf"))
        self.assertEqual(len(pdf_files), 5, "Expected 5 actual EB bills in data/raw/eb_bills")

        extracted_data = []
        for p in sorted(pdf_files):
            with open(p, "rb") as f:
                res = extract_bill_from_upload(f)
                extracted_data.append(res)
                self.assertIsNotNone(res.get("filename"))

        cleaned_df = clean_and_sequence_user_bills(extracted_data)
        self.assertEqual(len(cleaned_df), 5, "Expected 5 sequenced records")
        self.assertTrue("units_best_estimate" in cleaned_df.columns)
        self.assertTrue("net_payable_rs" in cleaned_df.columns)

if __name__ == "__main__":
    unittest.main()
