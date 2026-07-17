import json
import os
import re
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from extractAgent.extractionAgent import ClinicalExtract
from extractAgent.extractPrompt import EXTRACT_SYSTEM_PROMPT

load_dotenv()

client = OpenAI()
MODEL_NAME = os.getenv("OPENAI_MODEL")


def load_record(df: pd.DataFrame, row_id: int) -> dict[str, Any]:
    """
    Loads one dataset row by DataFrame index.

    Raises:
        TypeError: If df is not a DataFrame.
        ValueError: If the row does not exist or the index is duplicated.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    if row_id not in df.index:
        raise ValueError(f"Row {row_id} does not exist.")

    row = df.loc[row_id]

    if isinstance(row, pd.DataFrame):
        raise ValueError(
            f"Index {row_id} is duplicated. Reset the DataFrame index first."
        )

    return row.to_dict()


def clean_clinical_text(text: Any) -> str:
    """
    Cleans clinical text while preserving medically meaningful punctuation.

    Preserves:
    - Decimal points: 7.2
    - Slashes: 120/80
    - Percentages: 95%
    - Hyphens: follow-up
    - Colons: Diagnosis:
    - Parentheses and measurement symbols
    """
    if text is None or pd.isna(text):
        return ""

    if not isinstance(text, str):
        text = str(text)

    # Remove null bytes and non-printing control characters.
    text = text.replace("\x00", " ")
    text = re.sub(r"[\x01-\x08\x0B\x0C\x0E-\x1F\x7F]", " ", text)

    # Normalise line endings.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Replace repeated horizontal whitespace but preserve line breaks.
    text = re.sub(r"[ \t]+", " ", text)

    # Remove whitespace around line breaks.
    text = re.sub(r" *\n *", "\n", text)

    # Limit excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_clinical_record(text: str) -> ClinicalExtract:
    """
    Extracts and validates a ClinicalRecord from clinical text.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string.")

    text = text.strip()

    if not text:
        raise ValueError(
            "Cannot extract a clinical record from empty text."
        )

    if not MODEL_NAME:
        raise RuntimeError(
            "OPENAI_MODEL is not configured. Add it to your .env file."
        )

    try:
        response = client.responses.parse(
            model=MODEL_NAME,
            input=[
                {
                    "role": "system",
                    "content": EXTRACT_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": (
                        "Extract a structured clinical record from this "
                        "document:\n\n"
                        f"{text}"
                    ),
                },
            ],
            text_format=ClinicalExtract,
        )

        result = response.output_parsed

        if result is None:
            raise ValueError(
                "The model returned no parsed clinical record."
            )

        return result

    except ValidationError as error:
        raise RuntimeError(
            f"Clinical record validation failed:\n{error}"
        ) from error

    except Exception as error:
        raise RuntimeError(
            f"Clinical extraction request failed: {error}"
        ) from error


def parse_clinical_record(record_dict: dict[str, Any]) -> ClinicalExtract:
    """
    Validates and converts an extraction dictionary into ClinicalRecord.
    """
    if not isinstance(record_dict, dict):
        raise TypeError("record_dict must be a dictionary.")

    try:
        return ClinicalExtract.model_validate(record_dict)
    except ValidationError as error:
        raise ValueError(
            f"Clinical record validation failed:\n{error}"
        ) from error


def save_result(
    record_id: int,
    result: ClinicalExtract,
    output_dir: str | Path = "outputs",
) -> Path:
    """
    Saves a validated ClinicalRecord as JSON.
    """
    output_directory = Path(output_dir)
    output_directory.mkdir(parents=True, exist_ok=True)

    output_path = output_directory / f"record_{record_id}.json"

    try:
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(
                result.model_dump(mode="json"),
                file,
                indent=2,
                ensure_ascii=False,
            )
    except OSError as error:
        raise OSError(
            f"Could not save result to {output_path}: {error}"
        ) from error

    return output_path
