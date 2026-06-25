# services/llm/ollama_backend.py
"""
Ollama local backend — the fully-offline fallback, for demoing somewhere
without reliable internet.

Model choice (verified June 2026, see README "LLM backend" section):
qwen2.5:7b. Reasoning: structured/grounded short-form writing tasks like
this brief don't need a reasoning model (which would add a slow, token-
heavy <think> block you'd have to strip out) — they need an instruction-
following model that's reliable at "use only what I gave you." Qwen2.5 7B
is a strong, well-supported instruction-following model at this size and
runs CPU-only without a dedicated GPU.

Honest speed expectation on the 24 GB laptop (Intel i7-13620H, no
dedicated GPU, CPU-only inference): expect roughly 3-6 tokens/second.
An 800-token brief therefore takes very roughly 2-4 minutes. That's slow
for a live back-and-forth, but fine for "click generate, brief appears
while you talk over it" in a demo. If a demo absolutely needs faster
generation, swap to a smaller/faster model like qwen2.5:3b or phi4-mini
at some cost to output quality — both are one `ollama pull` away because
this backend reads the model name from OLLAMA_MODEL.

Setup (see README for the full sequence):
  [Windows cmd/PowerShell] ollama pull qwen2.5:7b
  [Windows cmd/PowerShell] ollama serve     (usually auto-starts as a service after install)
"""
import json
import os
import requests

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")


def generate(system_prompt: str, computed_payload: dict, timeout: int = 300) -> str:
    user_content = "COMPUTED DATA (narrate only this):\n" + json.dumps(computed_payload, indent=2)

    resp = requests.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 800},
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


if __name__ == "__main__":
    fake_payload = {
        "address": "1ExampleAddress", "category": "WATCHLISTED", "confidence": 0.62,
        "evidence": [{"source": "DARK_WEB_PAYMENT", "lr": 50.0, "contribution": 3.91}],
        "counterfactual": "Score drops to 0.30 if DARK_WEB_PAYMENT is removed.",
    }
    from services.llm.brief import SYSTEM_PROMPT
    print(generate(SYSTEM_PROMPT, fake_payload))
