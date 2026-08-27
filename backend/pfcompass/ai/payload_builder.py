"""
PII-Safe Payload Builder.

CRITICAL: All prompts sent to the LLM MUST go through this builder.
It strips any citizen-identifying information (name, UAN, PAN, Aadhaar, mobile, email)
before constructing prompts.

The LLM receives only anonymous, rule-based context.
"""
import re
from typing import Any, Dict, List, Optional


# Patterns that identify PII we must never send to external LLMs
_PII_PATTERNS = [
    re.compile(r"\b\d{12}\b"),          # Aadhaar (12 digits)
    re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),  # PAN Card
    re.compile(r"\b\d{10,12}\b"),        # UAN / mobile (10-12 digits)
    re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),  # Email
    re.compile(r"\b[6-9]\d{9}\b"),       # Indian mobile
]


def scrub_pii(text: str) -> str:
    """Replace any detected PII patterns with [REDACTED]."""
    for pattern in _PII_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def build_finding_explanation_prompt(
    rule_id: str,
    rule_title: str,
    what_is_wrong: str,
    why_it_happened: str,
    correction_path: Dict[str, Any],
    rag_context: Optional[str] = None,
) -> tuple[str, str]:
    """
    Build a PII-safe (system_prompt, user_prompt) pair for explaining a PF Health finding.
    Returns: (system_prompt, user_prompt)
    """
    system_prompt = """You are PF Compass, a helpful, empathetic guide for Indian EPFO citizens.
Your role is to explain PF (Provident Fund) health issues in simple, clear language that any citizen can understand.

STRICT RULES:
1. You MUST NOT make up eligibility decisions — only explain what the rule engine found
2. You MUST NOT promise specific rupee amounts or guarantee outcomes
3. You MUST cite EPFO scheme rules/paragraphs when available
4. Use simple, reassuring language — citizens are often worried about their PF
5. If RAG context is provided, use it to ground your explanation
6. Always end with an actionable next step
7. Respond in JSON matching the FindingExplanation schema exactly"""

    rag_section = ""
    if rag_context:
        rag_section = f"\n\nRelevant EPFO Knowledge:\n---\n{scrub_pii(rag_context)}\n---"

    user_prompt = f"""A citizen's PF account has the following issue detected by our rule engine.

Rule ID: {rule_id}
Rule Title: {rule_title}
What Is Wrong: {scrub_pii(what_is_wrong)}
Why It Happened: {scrub_pii(why_it_happened)}
Correction Required: {scrub_pii(str(correction_path))}
{rag_section}

Please explain this issue to the citizen in simple English.

Respond with a JSON object matching this schema EXACTLY:
{{
  "plain_language_summary": "...",
  "what_this_means_for_you": "...",
  "steps_to_fix": ["step 1", "step 2", ...],
  "urgency_note": null or "...",
  "source_references": ["EPF Scheme 1952, Para XX", ...]
}}"""

    return system_prompt, user_prompt


def build_decision_explanation_prompt(
    claim_type: str,
    form_number: str,
    eligibility_status: str,
    why_it_happened: str,
    recommended_action: str,
    tax_note: Optional[str] = None,
    rag_context: Optional[str] = None,
) -> tuple[str, str]:
    """
    Build a PII-safe (system_prompt, user_prompt) for explaining an eligibility decision.
    """
    system_prompt = """You are PF Compass, an expert guide for EPFO citizens in India.
Your role is to explain PF withdrawal/transfer/pension eligibility decisions in simple, plain language.

STRICT RULES:
1. The eligibility decision is already determined by the rule engine — do NOT override it
2. Your job is ONLY to explain in simple language WHY the citizen is eligible or not
3. Always mention the correct EPFO form number for next steps
4. Be empathetic — citizens often depend on this money
5. Respond in JSON matching the DecisionExplanation schema exactly"""

    rag_section = ""
    if rag_context:
        rag_section = f"\n\nRelevant EPFO Rules:\n---\n{scrub_pii(rag_context)}\n---"

    user_prompt = f"""The rule engine has evaluated a citizen's PF claim.

Claim Type: {claim_type}
Form Number: {form_number}
Eligibility Status: {eligibility_status}
Reason: {scrub_pii(why_it_happened)}
Recommended Action: {scrub_pii(recommended_action)}
Tax Note: {scrub_pii(tax_note) if tax_note else "No TDS applicable"}
{rag_section}

Explain this decision to the citizen clearly and empathetically.

Respond with a JSON object matching this schema EXACTLY:
{{
  "plain_language_summary": "...",
  "why_eligible_or_not": "...",
  "what_happens_next": "...",
  "tax_note": null or "..."
}}"""

    return system_prompt, user_prompt


def build_case_narrative_prompt(
    case_type: str,
    current_status: str,
    last_event_description: str,
    next_action_title: Optional[str],
    next_action_description: Optional[str],
    rag_context: Optional[str] = None,
) -> tuple[str, str]:
    """
    Build a PII-safe (system_prompt, user_prompt) for generating a CaseWise case narrative.
    """
    system_prompt = """You are PF Compass, a helpful EPFO case status narrator.
Your role is to explain where a citizen's PF claim/correction case currently stands in simple, empathetic language.

STRICT RULES:
1. Do NOT invent timeline or processing duration information unless provided
2. Use reassuring, professional tone — citizens are often anxious about their cases
3. Clearly state what the citizen needs to do next (if anything) vs what is pending with EPFO
4. Respond in JSON matching the CaseNarrative schema exactly"""

    rag_section = ""
    if rag_context:
        rag_section = f"\n\nRelevant EPFO Process Information:\n---\n{scrub_pii(rag_context)}\n---"

    user_prompt = f"""A citizen's EPFO case has the following status.

Case Type: {case_type}
Current Status: {current_status}
Last Event: {scrub_pii(last_event_description)}
Next Required Action: {next_action_title or 'Awaiting EPFO processing'}
Action Details: {scrub_pii(next_action_description or 'No immediate action required from citizen')}
{rag_section}

Narrate this case status to the citizen in a clear, empathetic way.

Respond with a JSON object matching this schema EXACTLY:
{{
  "status_summary": "...",
  "what_is_pending": "...",
  "citizen_friendly_note": "...",
  "estimated_timeline": null or "..."
}}"""

    return system_prompt, user_prompt
