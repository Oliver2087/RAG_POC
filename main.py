import argparse
import json
from pathlib import Path

import pandas as pd

from extractTools import save_result
from orchestrator import process_clinical_text


def parse_row_ids(value: str) -> list[int]:
    row_ids: list[int] = []

    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        row_ids.append(int(part))

    if not row_ids:
        raise argparse.ArgumentTypeError("At least one row id is required.")

    return row_ids


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def process_dataset(
    dataset_path: Path,
    text_column: str,
    row_ids: list[int],
    output_dir: Path,
) -> list[Path]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")

    df = pd.read_csv(dataset_path)

    if text_column not in df.columns:
        raise KeyError(
            f"Column '{text_column}' was not found. "
            f"Available columns: {list(df.columns)}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: list[Path] = []

    for row_id in row_ids:
        if row_id not in df.index:
            raise ValueError(f"Row {row_id} does not exist.")

        source_text = str(df.loc[row_id, text_column])
        clinical_record, review, final_record = process_clinical_text(source_text)

        extract_path = save_result(
            record_id=row_id,
            result=clinical_record,
            output_dir=output_dir,
        )

        review_path = output_dir / f"record_{row_id}_review.json"
        write_json(review_path, review.model_dump(mode="json"))

        final_path = output_dir / f"record_{row_id}_final.json"
        write_json(final_path, final_record.model_dump(mode="json"))

        saved_paths.extend([extract_path, review_path, final_path])

        print(f"Row {row_id}")
        print(f"Review status: {review.status}")
        print(f"Review issues: {len(review.issues)}")
        print(f"Extract saved to: {extract_path}")
        print(f"Review saved to: {review_path}")
        print(f"Final extract saved to: {final_path}")
        print()

    return saved_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run clinical extraction, review, and repair over selected dataset rows."
        )
    )
    parser.add_argument(
        "dataset",
        type=Path,
        help="Path to a CSV dataset containing clinical text.",
    )
    parser.add_argument(
        "--text-column",
        default="input",
        help="CSV column containing the clinical text.",
    )
    parser.add_argument(
        "--rows",
        type=parse_row_ids,
        default=[0, 1],
        help="Comma-separated row indexes to process, for example 0,1,2.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs") / "prototype",
        help="Directory for JSON outputs.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    saved_paths = process_dataset(
        dataset_path=args.dataset,
        text_column=args.text_column,
        row_ids=args.rows,
        output_dir=args.output_dir,
    )

    print("Finished extracting, reviewing, and repairing clinical records.")
    print("Saved files:")
    for path in saved_paths:
        print(f"- {path}")


if __name__ == "__main__":
    main()
