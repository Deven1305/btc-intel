# services/content/context.py
"""
Classify the context window around an already-extracted Bitcoin address as
PAYMENT, VICTIM_REPORT, or AMBIGUOUS, and classify the page topic. Pure
keyword/text classification — operates on text you already have, fetches
nothing.

Why context flips the meaning: the SAME address can mean opposite things
depending on the surrounding words. "Send BTC to 1ABC..." is a PAYMENT
context (inculpatory — it's the criminal's collection address).
"WARNING: 1ABC... is a scammer, do not send money" is a VICTIM_REPORT
context (exculpatory — it may belong to a victim, or be quoted by one).
Getting this backwards would flag victims as criminals, so the classifier
checks exculpatory (victim) keywords FIRST — they override everything.
"""
PAYMENT_KWS = ["send", "pay", "payment", "btc", "bitcoin", "wallet", "deposit",
               "transfer", "price", "checkout", "order", "address", "escrow"]
VICTIM_KWS  = ["scam", "scammer", "stolen", "fraud", "victim", "warning",
               "phishing", "reported", "hacked"]
DRUG_KWS    = ["weed", "cocaine", "mdma", "cannabis", "pills", "heroin", "vendor", "gram"]
WEAPON_KWS  = ["gun", "firearm", "weapon", "rifle", "ammunition", "glock"]
FRAUD_KWS   = ["dumps", "cvv", "fullz", "cashout", "carding", "fake id", "paypal"]


def classify_context(context: str) -> tuple[str, float]:
    """Returns (context_type, confidence). Victim keywords override (exculpatory)."""
    c = context.lower()
    if any(kw in c for kw in VICTIM_KWS):
        return "VICTIM_REPORT", 0.10              # exculpatory: low criminal confidence
    hits = sum(1 for kw in PAYMENT_KWS if kw in c)
    if hits >= 4:
        return "PAYMENT", min(0.50 + 0.08 * hits, 0.92)
    if hits >= 2:
        return "PAYMENT", 0.40 + 0.07 * hits
    if hits >= 1:
        return "AMBIGUOUS", 0.30
    return "AMBIGUOUS", 0.15


def classify_topic(text: str) -> str:
    t = text.lower()
    if any(kw in t for kw in DRUG_KWS):   return "DRUG"
    if any(kw in t for kw in WEAPON_KWS): return "WEAPON"
    if any(kw in t for kw in FRAUD_KWS):  return "FRAUD"
    return "UNKNOWN"


if __name__ == "__main__":
    print(classify_context("Please send your bitcoin payment to complete checkout"))
    print(classify_context("WARNING: this address is a known scammer, reported by victims"))
