import unittest
import re

class TestRegexExtraction(unittest.TestCase):
    def test_regex_patterns(self):
        text = """
        O3-E . S4L HGL Tax Involce forLT Current Consumption Charges fortho Month of October_2026 Gcdcc KCODALNGAR 
        Scralc Conncc conjui (05-172-024-917 Ction CT Non CT Flaceo ELFFI Tamahacu NamelAddress & CST of tha Consumer
        No2 Fcquar seNTHIL MuRUGAN LOTAO - TSrO LAASRI KARFAGA
        Pay This Bill By Online in ECcci Rs-5,085 - 94987 44487 htps: } WwW_tncbnct org 20/11/2026 Duc Datc
        REAdING 18043.0 171e3 0 lol 203 205
        Nat Pirablo 5,085.00
        """
        
        m_month = re.search(r"Month\s+(?:of|fortho\s+Month\s+of|:)?\s*([A-Za-z]+)[\s_]+(\d{4})", text, re.IGNORECASE)
        self.assertIsNotNone(m_month)
        self.assertEqual(m_month.group(1), "October")
        self.assertEqual(m_month.group(2), "2026")

        m_amt = re.search(r"Rs[\s\.\-_]*(\d[\d,]+(?:\.\d{1,2})?)", text, re.IGNORECASE)
        self.assertIsNotNone(m_amt)
        self.assertEqual(float(m_amt.group(1).replace(",", "")), 5085.0)

        m_due = re.search(r"(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\s*(?:Duc\s*Datc|Due\s*Date)", text, re.IGNORECASE)
        self.assertIsNotNone(m_due)
        self.assertEqual(m_due.group(1), "20/11/2026")

        m_reading = re.search(r"REAdING\s*(\d{4,6}(?:\.\d)?)", text, re.IGNORECASE)
        self.assertIsNotNone(m_reading)
        self.assertEqual(float(m_reading.group(1)), 18043.0)

if __name__ == "__main__":
    unittest.main()
