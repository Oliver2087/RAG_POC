import json
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from extractionAgent import ClinicalExtract
from orchestrator import process_record


class TestWorkflow(unittest.TestCase):
    @patch("orchestrator.extract_clinical_record")
    def test_process_record_loads_cleans_extracts_and_saves(self, mock_extract):
        clinical_record = ClinicalExtract(
            document_type="clinical_note",
            diagnoses=[],
            medications=[],
            allergies=[],
            symptoms=["shortness of breath"],
            procedures=[],
            follow_up_actions=["Book routine review"],
            patient_suggestions=["Book routine review"],
            risk_flags=[],
            summary="Patient reports shortness of breath.",
        )
        mock_extract.return_value = clinical_record

        df = pd.DataFrame(
            [
                {
                    "input": (
                        " Patient reports   shortness of breath.\r\n"
                        "Book medication review. "
                    )
                }
            ]
        )

        with tempfile.TemporaryDirectory() as output_dir:
            result, output_path = process_record(
                df=df,
                row_id=0,
                text_column="input",
                output_dir=output_dir,
            )

            self.assertEqual(result, clinical_record)
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.name, "record_0.json")

            saved = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["summary"], clinical_record.summary)
            self.assertEqual(saved["symptoms"], ["shortness of breath"])
            self.assertEqual(saved["patient_suggestions"], ["Book routine review"])

        mock_extract.assert_called_once_with(
            "Patient reports shortness of breath.\nBook medication review."
        )

    def test_process_record_missing_text_column_raises(self):
        df = pd.DataFrame([{"wrong_column": "text"}])

        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaises(KeyError):
                process_record(
                    df=df,
                    row_id=0,
                    text_column="input",
                    output_dir=output_dir,
                )

    def test_process_record_empty_text_raises(self):
        df = pd.DataFrame([{"input": "   "}])

        with tempfile.TemporaryDirectory() as output_dir:
            with self.assertRaises(ValueError):
                process_record(
                    df=df,
                    row_id=0,
                    text_column="input",
                    output_dir=output_dir,
                )


if __name__ == "__main__":
    unittest.main()
