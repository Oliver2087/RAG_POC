    
import pandas as pd
from pathlib import Path

from extractAgent.extractionAgent import ClinicalExtract
from reviewAgent.reviewAgent import ClinicalReview
from extractAgent.extractTools import load_record, clean_clinical_text, extract_clinical_record, save_result
from reviewAgent.reviewTools import repair_clinical_record, review_clinical_record



def process_record(
    df:     pd.DataFrame,
    row_id: int,
    text_column: str,
    output_dir: str | Path = "outputs",
) -> tuple[ClinicalExtract, Path]:
    """
    Runs one dataset record through the complete processing pipeline.

    Pipeline:
        load → select text → clean → extract → validate → save
    """
    row = load_record(df, row_id)

    if text_column not in row:
        raise KeyError(
            f"Column '{text_column}' was not found. "
            f"Available columns: {list(row.keys())}"
        )

    raw_text = row[text_column]
    cleaned_text = clean_clinical_text(raw_text)

    if not cleaned_text:
        raise ValueError(
            f"Row {row_id} contains no usable text in '{text_column}'."
        )

    clinical_record = extract_clinical_record(cleaned_text)

    output_path = save_result(
        record_id=row_id,
        result=clinical_record,
        output_dir=output_dir,
    )

    return clinical_record, output_path

def process_clinical_text(
    text: str,
) -> tuple[ClinicalExtract, ClinicalReview, ClinicalExtract]:
    cleaned_text = clean_clinical_text(text)

    if not cleaned_text:
        raise ValueError("No usable clinical text was provided.")

    record = extract_clinical_record(cleaned_text)
    review = review_clinical_record(
        source_text=cleaned_text,
        record=record,
    )
    final_record = repair_clinical_record(
        source_text=cleaned_text,
        record=record,
        review=review,
    )

    return record, review, final_record
