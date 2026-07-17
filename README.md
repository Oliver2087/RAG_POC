# RAG POC

A proof-of-concept AI pipeline for extracting structured clinical information
from unstructured healthcare documents.

The prototype reads clinical text from a CSV dataset, extracts a structured
clinical record, reviews the extraction for meaningful issues, and optionally
repairs the record when the review finds problems.

## Workflow

```text
CSV row
-> clean clinical text
-> extract ClinicalExtract
-> review ClinicalReview
-> repair ClinicalExtract if review needs_review
-> save JSON outputs
```

## Project Structure

```text
extractionAgent.py      Pydantic schema for extracted clinical records
extractPrompt.py        Extraction prompt
extractTools.py         Loading, cleaning, extraction, and save helpers
reviewAgent.py          Pydantic schema for review output
reviewPrompt.py         Review and repair prompts
reviewTools.py          Review and repair API calls
orchestrator.py         End-to-end pipeline functions
main.py                 CLI entrypoint for processing dataset rows
run_prototype.ps1       Example script for the local dataset
tests/                  Live/manual test scripts
test_workflow.py        Unit tests for the local workflow
```

## Setup

Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=your_model_here
```

Example model values depend on your OpenAI account access.

## Usage

Run the prototype against a CSV dataset:

```powershell
.\venv\Scripts\python.exe main.py .\dataset\BHC_MIMIC-IV.csv --text-column input --rows 0,1,2,3 --output-dir .\outputs\prototype
```

Or use the included local runner:

```powershell
.\run_prototype.ps1
```

The CSV must contain a text column. By default, the prototype expects the column
to be named `input`.

## Outputs

For each processed row, the pipeline writes:

```text
record_<row_id>.json          Original extracted clinical record
record_<row_id>_review.json   Review result
record_<row_id>_final.json    Final record after repair, or unchanged if review passed
```

The extracted record includes:

- diagnoses
- medications
- laboratory results
- allergies
- symptoms
- procedures
- follow-up actions
- patient suggestions
- risk flags
- warnings
- summary

## Tests

Run the unit tests:

```powershell
.\venv\Scripts\python.exe -m unittest test_workflow.py
```

Live API test scripts are in `tests/`. They call the OpenAI API and may incur
costs:

```powershell
.\venv\Scripts\python.exe tests\test_openai_live.py
.\venv\Scripts\python.exe tests\test_extract_two_rows_live.py
```

## Data And Safety Notes

The repository intentionally ignores:

- `.env`
- `venv/`
- `dataset/`
- `outputs/`

Do not commit API keys, real patient data, or generated clinical outputs unless
they are explicitly safe to share.

This project is a prototype for structured extraction and quality control. It
does not provide medical advice and should not be used for clinical decisions
without appropriate validation and human review.
