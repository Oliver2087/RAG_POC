# RAG POC

This is a proof-of-concept pipeline for turning unstructured clinical notes into
validated structured JSON. Despite the repository name, the current prototype is
not a retrieval system yet; it is an extraction, review, and repair workflow.

## Approach

The pipeline reads a CSV row containing clinical text, cleans the text, and asks
an OpenAI model to produce a `ClinicalExtract` object. A second review pass
compares that JSON against the original source. If the review returns
`needs_review`, a repair pass receives the source text, original extraction, and
review issues, then returns a corrected final record.

```text
clinical text -> extract JSON -> review JSON -> repair if needed -> final JSON
```

Run the prototype with:

```powershell
.\venv\Scripts\python.exe main.py .\dataset\BHC_MIMIC-IV.csv --text-column input --rows 0,1,2,3 --output-dir .\outputs\prototype
```

## Models And Tools

- OpenAI Responses API with structured parsing
- Pydantic schemas for validated extraction and review outputs
- pandas for reading CSV input
- python-dotenv for loading `OPENAI_API_KEY` and `OPENAI_MODEL`

The main schemas live in `extractAgent/` and `reviewAgent/`. The CLI entrypoint
is `main.py`.

## Assumptions

- Input data is a CSV with one text column, defaulting to `input`.
- The model should extract only information supported by the source document.
- Patient suggestions must be practical and source-supported, not new medical
advice.
- Lab interpretations should be conservative when the source does not clearly
state normality or abnormality.
- Final outputs are prototype artifacts and still require human clinical review.

## Example

Input:

```text
Discharge Instructions: You were admitted with abdominal fullness and pain from
ascites. You had a diagnostic and therapeutic paracentesis with 4.3 L removed.
Your spironolactone was discontinued because your potassium was high. Your lasix
was increased to 40mg daily.
```

Output excerpt:

```json
{
  "diagnoses": [
    {
      "name": "Ascites",
      "status": "active",
      "evidence": "admitted with abdominal fullness and pain from ascites"
    }
  ],
  "medications": [
    {
      "name": "Furosemide",
      "dose": "40 mg daily",
      "previous_dose": null,
      "status": "changed"
    },
    {
      "name": "Spironolactone",
      "dose": null,
      "previous_dose": null,
      "status": "stopped"
    }
  ],
  "procedures": [
    {
      "name": "Paracentesis",
      "details": "4.3 L removed"
    }
  ],
  "patient_suggestions": [
    "Follow documented discharge instructions and planned follow-up."
  ],
  "summary": "Patient admitted with ascites-related abdominal fullness and pain; paracentesis removed 4.3 L, spironolactone was stopped, and furosemide was increased."
}
```

Do not commit `.env`, datasets, or generated outputs. This project is not a
clinical decision system.
