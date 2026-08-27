"""
Pydantic output schemas for structured LLM responses.
These define WHAT the LLM is allowed to produce — never eligibility decisions.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class FindingExplanation(BaseModel):
    """Citizen-friendly explanation of a PF Health finding."""
    plain_language_summary: str = Field(
        description="1-2 sentence plain language summary in simple English (not legalese)"
    )
    what_this_means_for_you: str = Field(
        description="What practical impact does this finding have on the citizen"
    )
    steps_to_fix: List[str] = Field(
        description="Ordered list of concrete steps the citizen can take to resolve this finding"
    )
    urgency_note: Optional[str] = Field(
        default=None,
        description="Time-sensitive note if action should be taken soon (e.g. account becoming inoperative soon)"
    )
    source_references: List[str] = Field(
        default_factory=list,
        description="Relevant EPFO rule references or scheme sections cited (e.g. 'EPF Scheme 1952, Para 72')"
    )


class DecisionExplanation(BaseModel):
    """Citizen-friendly explanation of a PF Decision eligibility result."""
    plain_language_summary: str = Field(
        description="Brief explanation of the eligibility outcome in plain English"
    )
    why_eligible_or_not: str = Field(
        description="Clear explanation of why the citizen is or is not eligible — grounded in rules provided"
    )
    what_happens_next: str = Field(
        description="What the citizen should do next, referencing the correct EPFO form and portal"
    )
    tax_note: Optional[str] = Field(
        default=None,
        description="Plain language tax note if payout is subject to TDS"
    )


class CaseNarrative(BaseModel):
    """AI-generated narrative for a CaseWise case status update."""
    status_summary: str = Field(
        description="1-2 sentence plain English summary of where the case currently stands"
    )
    what_is_pending: str = Field(
        description="What is the next expected action or who is responsible for the next step"
    )
    citizen_friendly_note: str = Field(
        description="An empathetic, encouraging note to the citizen about their case progress"
    )
    estimated_timeline: Optional[str] = Field(
        default=None,
        description="Approximate timeline for resolution if deterministically known (from next_action context)"
    )
