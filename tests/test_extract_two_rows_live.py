from pathlib import Path
import json
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from extractTools import save_result
from orchestrator import process_clinical_text


DATASET_PATH = PROJECT_ROOT / "dataset" / "BHC_MIMIC-IV.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "live_two_row_review"
ROW_IDS = [2, 3]
TEXT_COLUMN = "input"


def main() -> None:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    for row_id in ROW_IDS:
        if row_id not in df.index:
            raise ValueError(f"Row {row_id} does not exist.")

        if TEXT_COLUMN not in df.columns:
            raise KeyError(
                f"Column '{TEXT_COLUMN}' was not found. "
                f"Available columns: {list(df.columns)}"
            )

        clinical_record, review, final_record = process_clinical_text(
            str(df.loc[row_id, TEXT_COLUMN])
        )

        extract_path = save_result(
            record_id=row_id,
            result=clinical_record,
            output_dir=OUTPUT_DIR,
        )
        review_path = OUTPUT_DIR / f"record_{row_id}_review.json"
        review_path.write_text(
            json.dumps(
                review.model_dump(mode="json"),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        final_path = OUTPUT_DIR / f"record_{row_id}_final.json"
        final_path.write_text(
            json.dumps(
                final_record.model_dump(mode="json"),
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        saved_paths.extend([extract_path, review_path, final_path])
        print(f"Row {row_id}")
        print(f"Summary: {clinical_record.summary}")
        print(f"Review status: {review.status}")
        print(f"Review issues: {len(review.issues)}")
        print(f"Final summary: {final_record.summary}")
        print(f"Extract saved to: {extract_path}")
        print(f"Review saved to: {review_path}")
        print(f"Final extract saved to: {final_path}")
        print()

    print("Finished extracting, reviewing, and repairing clinical records.")
    print("Saved files:")
    for path in saved_paths:
        print(f"- {path}")


if __name__ == "__main__":
    main()
