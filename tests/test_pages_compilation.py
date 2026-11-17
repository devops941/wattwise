import unittest
import py_compile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class TestPagesCompilation(unittest.TestCase):
    def test_all_python_files_compile(self):
        python_files = [
            BASE_DIR / "app.py",
            BASE_DIR / "src" / "analyzer.py",
            BASE_DIR / "src" / "bill_calculator.py",
            BASE_DIR / "src" / "data_processor.py",
            BASE_DIR / "src" / "pdf_extractor.py",
            BASE_DIR / "src" / "predictor.py",
            BASE_DIR / "src" / "recommendations.py",
            BASE_DIR / "src" / "report_generator.py",
            BASE_DIR / "src" / "step4_eda.py",
            BASE_DIR / "src" / "validator.py",
            BASE_DIR / "src" / "household_manager.py",
            BASE_DIR / "pages" / "1_Dashboard.py",
            BASE_DIR / "pages" / "2_Upload_Bill.py",
            BASE_DIR / "pages" / "3_Analysis.py",
            BASE_DIR / "pages" / "4_Peak_Consumption.py",
            BASE_DIR / "pages" / "5_Prediction.py",
            BASE_DIR / "pages" / "6_Bill_Estimation.py",
            BASE_DIR / "pages" / "7_Recommendations.py",
            BASE_DIR / "pages" / "8_Reports.py",
        ]
        
        errors = []
        for f in python_files:
            try:
                py_compile.compile(str(f), doraise=True)
            except Exception as e:
                errors.append(f"{f.name}: {e}")

        self.assertEqual(len(errors), 0, f"Compilation errors found: {errors}")

if __name__ == "__main__":
    unittest.main()
