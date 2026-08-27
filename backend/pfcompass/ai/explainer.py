import json
import logging
from typing import Any, Dict, Optional

from pfcompass.ai.output_schemas import CaseNarrative, DecisionExplanation, FindingExplanation
from pfcompass.ai.payload_builder import (
    build_case_narrative_prompt,
    build_decision_explanation_prompt,
    build_finding_explanation_prompt,
)
from pfcompass.ai.providers import llm
from pfcompass.ai.rag_retriever import rag_retriever

logger = logging.getLogger(__name__)


def _clean_json_str(text: str) -> str:
    """Extract raw JSON substring from LLM text output."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


class AIExplainer:
    """
    AI Explanation Engine — Generates citizen-friendly explanations using Groq LLM + RAG.
    Enforces deterministic rule boundaries and safe fallback parsing.
    """

    async def explain_finding(
        self,
        rule_id: str,
        rule_title: str,
        what_is_wrong: str,
        why_it_happened: str,
        correction_path: Dict[str, Any],
    ) -> FindingExplanation:
        # Retrieve relevant RAG context
        query = f"{rule_id} {rule_title} {what_is_wrong} {why_it_happened}"
        chunks = rag_retriever.retrieve(query, top_k=2)
        rag_context = "\n\n".join([f"[{c.scheme_reference}] {c.content}" for c in chunks])

        sys_prompt, user_prompt = build_finding_explanation_prompt(
            rule_id=rule_id,
            rule_title=rule_title,
            what_is_wrong=what_is_wrong,
            why_it_happened=why_it_happened,
            correction_path=correction_path,
            rag_context=rag_context,
        )

        try:
            raw_resp = await llm().complete(sys_prompt, user_prompt, max_tokens=600, temperature=0.2)
            json_str = _clean_json_str(raw_resp)
            data = json.loads(json_str)
            return FindingExplanation(**data)
        except Exception as e:
            logger.warning(f"AI finding explanation fallback used: {e}")
            # Deterministic fallback explanation
            return FindingExplanation(
                plain_language_summary=f"Issue detected: {what_is_wrong}",
                what_this_means_for_you=why_it_happened,
                steps_to_fix=[
                    correction_path.get("recommended_action", "Check EPFO Member Portal to resolve issue.")
                ],
                urgency_note="Please address this issue to avoid delay in future claim processing.",
                source_references=[c.scheme_reference for c in chunks],
            )

    async def explain_decision(
        self,
        claim_type: str,
        form_number: str,
        eligibility_status: str,
        why_it_happened: str,
        recommended_action: str,
        tax_note: Optional[str] = None,
    ) -> DecisionExplanation:
        query = f"{claim_type} {form_number} {eligibility_status} {why_it_happened}"
        chunks = rag_retriever.retrieve(query, top_k=2)
        rag_context = "\n\n".join([f"[{c.scheme_reference}] {c.content}" for c in chunks])

        sys_prompt, user_prompt = build_decision_explanation_prompt(
            claim_type=claim_type,
            form_number=form_number,
            eligibility_status=eligibility_status,
            why_it_happened=why_it_happened,
            recommended_action=recommended_action,
            tax_note=tax_note,
            rag_context=rag_context,
        )

        try:
            raw_resp = await llm().complete(sys_prompt, user_prompt, max_tokens=500, temperature=0.2)
            json_str = _clean_json_str(raw_resp)
            data = json.loads(json_str)
            return DecisionExplanation(**data)
        except Exception as e:
            logger.warning(f"AI decision explanation fallback used: {e}")
            return DecisionExplanation(
                plain_language_summary=f"Your claim status for {form_number} ({claim_type}) is {eligibility_status}.",
                why_eligible_or_not=why_it_happened,
                what_happens_next=recommended_action,
                tax_note=tax_note,
            )

    async def explain_case_narrative(
        self,
        case_type: str,
        current_status: str,
        last_event_description: str,
        next_action_title: Optional[str] = None,
        next_action_description: Optional[str] = None,
    ) -> CaseNarrative:
        query = f"{case_type} {current_status} {last_event_description}"
        chunks = rag_retriever.retrieve(query, top_k=1)
        rag_context = "\n\n".join([f"[{c.scheme_reference}] {c.content}" for c in chunks])

        sys_prompt, user_prompt = build_case_narrative_prompt(
            case_type=case_type,
            current_status=current_status,
            last_event_description=last_event_description,
            next_action_title=next_action_title,
            next_action_description=next_action_description,
            rag_context=rag_context,
        )

        try:
            raw_resp = await llm().complete(sys_prompt, user_prompt, max_tokens=400, temperature=0.3)
            json_str = _clean_json_str(raw_resp)
            data = json.loads(json_str)
            return CaseNarrative(**data)
        except Exception as e:
            logger.warning(f"AI case narrative fallback used: {e}")
            return CaseNarrative(
                status_summary=f"Case status is currently {current_status}. Last update: {last_event_description}.",
                what_is_pending=next_action_description or "Awaiting next processing step.",
                citizen_friendly_note="Your case is active in the CaseWise tracking timeline.",
                estimated_timeline="7-14 business days",
            )


# Global singleton instance
ai_explainer = AIExplainer()
