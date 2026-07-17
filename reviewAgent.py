from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


ReviewStatus = Literal["pass", "needs_review"]


class ReviewModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class ReviewIssue(ReviewModel):
    field: str = Field(
        description=(
            "Location of the issue, such as medications[1], "
            "lab_results[3].status, or risk_flags[0]."
        )
    )
    issue: str
    suggestion: str | None = None


class ClinicalReview(ReviewModel):
    status: ReviewStatus = Field(
        description=(
            "Use pass when there are no meaningful extraction issues. "
            "Use needs_review when one or more issues are present."
        )
    )
    issues: list[ReviewIssue] = Field(default_factory=list)

    @model_validator(mode="after")
    def status_matches_issues(self) -> "ClinicalReview":
        if self.status == "pass" and self.issues:
            raise ValueError("A passing review cannot include issues.")

        if self.status == "needs_review" and not self.issues:
            raise ValueError("A review needing review must include issues.")

        return self
