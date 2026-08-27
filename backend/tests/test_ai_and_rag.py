import pytest
from pfcompass.ai.payload_builder import build_finding_explanation_prompt, scrub_pii
from pfcompass.ai.rag_retriever import rag_retriever


def test_pii_scrubber():
    text = "Citizen UAN 100123456789 with Aadhaar 123456789012 and PAN ABCDE1234F email test@example.com"
    scrubbed = scrub_pii(text)
    assert "100123456789" not in scrubbed
    assert "123456789012" not in scrubbed
    assert "ABCDE1234F" not in scrubbed
    assert "test@example.com" not in scrubbed
    assert "[REDACTED]" in scrubbed


def test_rag_retriever():
    chunks = rag_retriever.retrieve("full withdrawal 2 months exit", top_k=2)
    assert len(chunks) > 0
    assert "EPF" in chunks[0].doc_title or "EPFO" in chunks[0].doc_title
    assert chunks[0].scheme_reference != ""


def test_payload_builder():
    sys_prompt, user_prompt = build_finding_explanation_prompt(
        rule_id="PFH-001",
        rule_title="Inoperative Account",
        what_is_wrong="Account inoperative",
        why_it_happened="No contributions for 36 months",
        correction_path={"recommended_action": "Submit claim"},
    )
    assert "PF Compass" in sys_prompt
    assert "PFH-001" in user_prompt
    assert "JSON object matching this schema" in user_prompt
