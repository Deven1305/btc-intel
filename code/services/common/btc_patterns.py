# services/common/btc_patterns.py
"""
Regex patterns for the four Bitcoin address formats. Pure string matching —
no network calls. Used by seed parsers and by anything that processes
already-acquired text (archived pages, OFAC/UN XML, etc.) to spot
address-shaped tokens before checksum validation.
"""
import re

# BECH32 (SegWit v0) and BECH32M (Taproot/SegWit v1) are case-insensitive in
# the wild but canonically lowercase — callers should normalise to lower.
BTC_PATTERNS = {
    "P2PKH":   re.compile(r"\b(1[a-km-zA-HJ-NP-Z1-9]{25,34})\b"),          # legacy '1...'
    "P2SH":    re.compile(r"\b(3[a-km-zA-HJ-NP-Z1-9]{25,34})\b"),          # script   '3...'
    "BECH32":  re.compile(r"\b(bc1q[a-z0-9]{6,87})\b", re.IGNORECASE),     # SegWit v0 'bc1q...'
    "BECH32M": re.compile(r"\b(bc1p[a-z0-9]{6,87})\b", re.IGNORECASE),     # Taproot   'bc1p...'
}


def find_candidate_addresses(text: str) -> list[tuple[str, str]]:
    """Scan arbitrary text and return (address, address_type) candidates.
    These are SHAPE matches only — always run is_valid_btc_address() on the
    result before trusting it (see btc_validate.py)."""
    out: list[tuple[str, str]] = []
    for addr_type, pattern in BTC_PATTERNS.items():
        for m in pattern.finditer(text):
            candidate = m.group(1)
            if addr_type in ("BECH32", "BECH32M"):
                candidate = candidate.lower()
            out.append((candidate, addr_type))
    return out


if __name__ == "__main__":
    sample = ("Send payment to 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa or "
               "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq for the order.")
    for addr, kind in find_candidate_addresses(sample):
        print(kind, addr)
