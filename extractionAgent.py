from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


DiagnosisStatus = Literal[
    "active",
    "resolved",
    "historical",
    "unclear",
]

MedicationStatus = Literal[
    "started",
    "continued",
    "stopped",
    "changed",
    "unclear",
]

AllergyStatus = Literal[
    "documented",
    "none_reported",
    "not_documented",
]

LabStatus = Literal[
    "low",
    "normal",
    "high",
    "abnormal",
    "unknown",
]

RiskSeverity = Literal[
    "low",
    "medium",
    "high",
]

class ClinicalModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class Diagnosis(ClinicalModel):
    name: str

    status: DiagnosisStatus = Field(
        default="unclear",
        description=(
            "Clinical status of the diagnosis. "
            "Use active, historical, resolved or unclear."
        ),
    )

    evidence: str | None = Field(
        default=None,
        description="Short supporting text from the document."
    )


class Medication(ClinicalModel):
    name: str | None = Field(
        default=None,
        description="Medication name."
    )

    dose: str | None = Field(
        default=None,
        description="Current dose."
    )

    previous_dose: str | None = Field(
        default=None,
        description="Previous dose if status is 'changed'."
    )

    status: MedicationStatus = Field(
        default="unclear",
        description=(
            "Medication change during this admission. "
            "Use started, continued, stopped, changed or unclear."
        ),
    )


class LabResult(ClinicalModel):
    name: str
    value: str | None = None
    unit: str | None = None

    status: LabStatus = Field(
        default="unknown",
        description=(
            "Laboratory interpretation. "
            "Use unknown if the document does not explicitly indicate "
            "whether the value is normal or abnormal."
        ),
    )

    evidence: str | None = None


class Procedure(ClinicalModel):
    name: str
    details: str | None = None


class RiskFlag(ClinicalModel):
    severity: RiskSeverity = Field(
        description=(
            "Severity of the documented clinical concern. "
            "Only use high when explicitly supported by the document."
        ),
    )

    type: str

    description: str

    evidence: str | None = None


class ClinicalExtract(ClinicalModel):
    document_type: str | None = None

    diagnoses: list[Diagnosis] = Field(default_factory=list)
    medications: list[Medication] = Field(default_factory=list)
    lab_results: list[LabResult] = Field(default_factory=list)

    allergies: list[str] = Field(default_factory=list)
    allergy_status: AllergyStatus = Field(
        default="not_documented",
        description="Whether allergy information was documented."
    )

    symptoms: list[str] = Field(default_factory=list)
    procedures: list[Procedure] = Field(default_factory=list)
    follow_up_actions: list[str] = Field(default_factory=list)
    patient_suggestions: list[str] = Field(
        default_factory=list,
        description=(
            "Practical next steps that may be useful for the patient, based "
            "only on the source document. These should not introduce new "
            "diagnoses, medication changes, or treatment plans."
        ),
    )

    risk_flags: list[RiskFlag] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    summary: str = Field(
        description="A concise factual summary of the document."
    )
