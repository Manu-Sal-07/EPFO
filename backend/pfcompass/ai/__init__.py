"""
AI Layer Package — LLM provider abstraction, intent extraction, explanations, RAG retrieval.

ARCHITECTURE BOUNDARY:
- LLM is NEVER the source of truth for EPFO eligibility or rules
- Deterministic rule engine is always authoritative
- AI only: citizen-friendly explanations, intent extraction, case narratives
- All LLM calls are PII-safe (no name, UAN, PAN, Aadhaar in prompts)
"""
