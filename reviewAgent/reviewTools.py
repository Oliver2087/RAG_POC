import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from extractAgent.extractionAgent import ClinicalExtract
from reviewAgent.reviewAgent import ClinicalReview
from reviewAgent.reviewPrompt import REPAIR_SYSTEM_PROMPT, REVIEW_SYSTEM_PROMPT


load_dotenv()

client = OpenAI()
MODEL_NAME = os.getenv("OPENAI_MODEL")


def review_clinical_record(
    source_text: str,
    record: ClinicalExtract,
) -> ClinicalReview:
    """
    Reviews an extracted clinical record against its source text.
    """
    if not isinstance(source_text, str):
        raise TypeError("source_text must be a string.")

    if not isinstance(record, ClinicalExtract):
        raise TypeError("record must be a ClinicalExtract.")

    source_text = source_text.strip()

    if not source_text:
        raise ValueError("Source text cannot be empty.")

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
                    "content": REVIEW_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": (
                        "ORIGINAL CLINICAL DOCUMENT:\n"
                        "---------------------------\n"
                        f"{source_text}\n\n"
                        "EXTRACTED CLINICAL RECORD:\n"
                        "--------------------------\n"
                        f"{record.model_dump_json(indent=2)}"
                    ),
                },
            ],
            text_format=ClinicalReview,
        )

    except ValidationError as error:
        raise RuntimeError(
            f"Clinical review validation failed:\n{error}"
        ) from error

    except Exception as error:
        raise RuntimeError(
            f"Clinical review request failed: {error}"
        ) from error

    review = response.output_parsed

    if review is None:
        raise RuntimeError(
            "The model returned no parsed clinical review."
        )

    return review


def repair_clinical_record(
    source_text: str,
    record: ClinicalExtract,
    review: ClinicalReview,
) -> ClinicalExtract:
    """
    Revises an extracted clinical record using review issues.
    """
    if not isinstance(source_text, str):
        raise TypeError("source_text must be a string.")

    if not isinstance(record, ClinicalExtract):
        raise TypeError("record must be a ClinicalExtract.")

    if not isinstance(review, ClinicalReview):
        raise TypeError("review must be a ClinicalReview.")

    source_text = source_text.strip()

    if not source_text:
        raise ValueError("Source text cannot be empty.")

    if review.status == "pass":
        return record

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
                    "content": REPAIR_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": (
                        "ORIGINAL CLINICAL DOCUMENT:\n"
                        "---------------------------\n"
                        f"{source_text}\n\n"
                        "EXTRACTED CLINICAL RECORD:\n"
                        "--------------------------\n"
                        f"{record.model_dump_json(indent=2)}\n\n"
                        "CLINICAL REVIEW ISSUES:\n"
                        "-----------------------\n"
                        f"{review.model_dump_json(indent=2)}"
                    ),
                },
            ],
            text_format=ClinicalExtract,
        )

    except ValidationError as error:
        raise RuntimeError(
            f"Clinical repair validation failed:\n{error}"
        ) from error

    except Exception as error:
        raise RuntimeError(
            f"Clinical repair request failed: {error}"
        ) from error

    repaired_record = response.output_parsed

    if repaired_record is None:
        raise RuntimeError(
            "The model returned no parsed repaired clinical record."
        )

    return repaired_record
