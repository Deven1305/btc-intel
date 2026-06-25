# services/llm/huggingface_backend.py
"""
Hugging Face free hosted-inference backend — a real, currently-live third
option (verified June 2026, see README "LLM backend" section).

Hugging Face's "Inference Providers" router (https://router.huggingface.co/v1)
exposes an OpenAI-compatible chat-completions endpoint that routes to
partner providers (Together AI, Groq, Cerebras, and others) using a single
free Hugging Face access token — no credit card required to generate a
token or use the free quota.

Honesty about limits: Hugging Face does NOT publish a fixed free-tier
number for this router the way Gemini does. It's described as rate-limited
and shared, varying by model popularity and current load. Treat it as a
backup option for occasional briefs, not as the primary demo path — Gemini
(free, with documented per-minute/per-day numbers) or Ollama (fully
offline, no limits at all) are better defaults; this exists as the third
pluggable option your prompt asked for, in case you want a no-local-GPU,
no-Google-account alternative.

Setup:
  1. Create a free token at https://huggingface.co/settings/tokens
     (fine-grained token, "Make calls to Inference Providers" permission).
  2. pip install openai   (the official OpenAI client works against HF's
     OpenAI-compatible endpoint — no separate HF-specific SDK required for
     this call shape)
  3. Set HF_TOKEN in your .env.
"""
import json
import os

HF_MODEL = os.getenv("HF_MODEL", "moonshotai/Kimi-K2-Instruct-0905")


def generate(system_prompt: str, computed_payload: dict) -> str:
    from openai import OpenAI

    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_TOKEN"],
    )
    user_content = "COMPUTED DATA (narrate only this):\n" + json.dumps(computed_payload, indent=2)

    completion = client.chat.completions.create(
        model=HF_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        max_tokens=800,
        temperature=0.2,
    )
    return completion.choices[0].message.content


if __name__ == "__main__":
    fake_payload = {
        "address": "1ExampleAddress", "category": "WATCHLISTED", "confidence": 0.62,
        "evidence": [{"source": "DARK_WEB_PAYMENT", "lr": 50.0, "contribution": 3.91}],
        "counterfactual": "Score drops to 0.30 if DARK_WEB_PAYMENT is removed.",
    }
    from services.llm.brief import SYSTEM_PROMPT
    print(generate(SYSTEM_PROMPT, fake_payload))
