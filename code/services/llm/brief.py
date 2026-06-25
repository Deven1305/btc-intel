# services/llm/brief.py
"""
Pluggable investigation-brief narration layer. Replaces the Claude-API-only
Section 10 from the original design with a backend-agnostic abstraction:
generate_brief(decision, backend="gemini"|"ollama"|"huggingface").

Grounded prompting design (unchanged from the original Claude version,
identical across all three backends): the model receives ONLY the evidence
BTC-Intel already computed — the evidence list, the score, the category,
and the counterfactual. Its job is to NARRATE those findings in clear
English for a compliance officer, NOT to invent new ones. The system
prompt forbids the model from adding any risk factor that was not computed
by the deterministic pipeline. The engine decides; the model describes.

Switch backends with one config value (BTC_LLM_BACKEND env var, or the
dashboard sidebar toggle) — no code changes needed.
"""
import json
import os

SYSTEM_PROMPT = """You are a blockchain forensics analyst writing a compliance brief.

STRICT RULES:
- You will be given COMPUTED intelligence about one Bitcoin address: its category,
  confidence score, a list of evidence items (each with a source name and detail),
  and a counterfactual.
- Every statement you write MUST be grounded in a specific evidence item provided.
  Cite the evidence source name (e.g. "OFAC_SDN", "DARK_WEB_PAYMENT") for each claim.
- DO NOT invent, infer, or speculate about any risk factor not present in the data.
- DO NOT assign your own score or change the category. Report what was computed.
- If the evidence is thin, say so plainly. Do not embellish.

Write exactly these sections:
1. VERDICT (1 sentence): the category and confidence.
2. KEY EVIDENCE (bullets): each evidence item, in plain language, with its source name.
3. WHAT WOULD CHANGE THIS (1 sentence): restate the provided counterfactual.
4. RECOMMENDED ACTION (1 sentence): derive ONLY from the category:
   BLACKLISTED -> "Block all transactions; escalate to compliance."
   WATCHLISTED -> "Flag for manual review; request source-of-funds."
   PRE_CRIME_WATCHLIST -> "Do not transact; monitor for first activity."
   CLEAN -> "No action required."
Keep each section to 2-3 sentences."""


def _computed_payload(decision) -> dict:
    return {
        "address": decision.address,
        "category": decision.category,
        "confidence": decision.final_score,
        "evidence": decision.evidence,
        "counterfactual": decision.counterfactual,
        "contradictions": decision.contradictions,
    }


def generate_brief(decision, backend: str | None = None) -> str:
    """backend: 'gemini' (default, free tier) | 'ollama' (fully offline) |
    'huggingface' (free hosted inference, if configured). Falls back to the
    BTC_LLM_BACKEND env var, then 'gemini', if not specified."""
    backend = backend or os.getenv("BTC_LLM_BACKEND", "gemini")
    payload = _computed_payload(decision)

    if backend == "gemini":
        from services.llm.gemini_backend import generate as _gen
    elif backend == "ollama":
        from services.llm.ollama_backend import generate as _gen
    elif backend == "huggingface":
        from services.llm.huggingface_backend import generate as _gen
    else:
        raise ValueError(f"Unknown LLM backend: {backend!r}")

    return _gen(SYSTEM_PROMPT, payload)


if __name__ == "__main__":
    from services.risk.engine import RiskDecision
    fake = RiskDecision(
        address="1ExampleAddress", category="WATCHLISTED", final_score=0.62,
        evidence=[{"source": "DARK_WEB_PAYMENT", "lr": 50.0, "contribution": 3.91}],
        counterfactual="Score drops to 0.30 if DARK_WEB_PAYMENT is removed.",
    )
    print(generate_brief(fake, backend=os.getenv("BTC_LLM_BACKEND", "gemini")))
