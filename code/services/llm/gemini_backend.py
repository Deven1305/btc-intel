# services/llm/gemini_backend.py
"""
Google Gemini API backend — the free-tier default for brief narration.

Current as of June 2026 (see README "LLM backend" section for sourcing):
  - Pro models (Gemini 2.5 Pro / 3.x Pro) were removed from the Gemini API
    free tier on April 1, 2026 and are now paid-only.
  - Flash and Flash-Lite remain free. gemini-2.5-flash is the current
    stable Flash-tier model recommended for this kind of short, grounded
    structured-writing task; it is NOT a preview model, so it's the safer
    default for something you'll demo on a specific day.
  - Free-tier limits for gemini-2.5-flash (subject to change without
    notice — re-check ai.google.dev/gemini-api/docs/rate-limits before a
    demo): roughly 10 requests/minute, 250,000 tokens/minute, 250-1,500
    requests/day depending on the live quota Google shows for your
    project. A demo generating 50-100 briefs in a single sitting is
    comfortably inside the daily limit as long as you don't burst past
    ~10 requests in any one minute — space brief-generation clicks out a
    little if you're clicking fast.
  - No credit card needed for the free tier itself.

pip install google-genai
Get a free API key at https://aistudio.google.com/apikey (no card required).
"""
import json
import os

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def generate(system_prompt: str, computed_payload: dict) -> str:
    from google import genai

    api_key = os.environ["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)

    user_content = "COMPUTED DATA (narrate only this):\n" + json.dumps(computed_payload, indent=2)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_content,
        config={
            "system_instruction": system_prompt,
            "max_output_tokens": 800,
            "temperature": 0.2,
        },
    )
    return response.text


if __name__ == "__main__":
    fake_payload = {
        "address": "1ExampleAddress", "category": "WATCHLISTED", "confidence": 0.62,
        "evidence": [{"source": "DARK_WEB_PAYMENT", "lr": 50.0, "contribution": 3.91}],
        "counterfactual": "Score drops to 0.30 if DARK_WEB_PAYMENT is removed.",
    }
    from services.llm.brief import SYSTEM_PROMPT
    print(generate(SYSTEM_PROMPT, fake_payload))
