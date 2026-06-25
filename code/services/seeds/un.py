# services/seeds/un.py
"""
UN Security Council Consolidated Sanctions List. International coverage
beyond the US-centric OFAC list. The UN XML embeds crypto identifiers
inside free-text NOTE fields rather than structured features, so we scan
NOTE text for address-shaped tokens and checksum-validate them.
"""
import re
import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timezone
from services.common.btc_validate import is_valid_btc_address

UN_URL = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"
ADDR_RE = re.compile(
    r"\b(?:1[a-km-zA-HJ-NP-Z1-9]{25,34}"
    r"|3[a-km-zA-HJ-NP-Z1-9]{25,34}"
    r"|bc1[a-z0-9]{6,87})\b",
    re.IGNORECASE,
)


def fetch_un_btc_addresses(timeout: int = 120) -> list[dict]:
    resp = requests.get(UN_URL, timeout=timeout)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    now = datetime.now(timezone.utc).isoformat()

    out: list[dict] = []
    # UN schema uses INDIVIDUAL and ENTITY nodes; we scan both, namespace-agnostic.
    for node in root.iter():
        tag = node.tag.split("}")[-1]
        if tag not in ("INDIVIDUAL", "ENTITY"):
            continue
        name_parts = [c.text for c in node.iter()
                      if c.tag.split("}")[-1] in ("FIRST_NAME", "SECOND_NAME") and c.text]
        entity_name = " ".join(name_parts).strip() or "UN_ENTITY"
        for c in node.iter():
            if c.tag.split("}")[-1] != "NOTE" or not c.text:
                continue
            for cand in ADDR_RE.findall(c.text):
                cand = cand.lower() if cand.lower().startswith("bc1") else cand
                if is_valid_btc_address(cand):
                    out.append({
                        "address": cand, "entity_name": entity_name,
                        "source": "UN_SANCTIONS", "confidence": 1.0,
                        "category": "BLACKLISTED", "fetched_at": now,
                    })
    # de-dup within this source
    seen, uniq = set(), []
    for r in out:
        if r["address"] not in seen:
            seen.add(r["address"]); uniq.append(r)
    return uniq


if __name__ == "__main__":
    seeds = fetch_un_btc_addresses()
    print(f"UN: {len(seeds)} Bitcoin addresses")
    for s in seeds[:5]:
        print(" ", s["address"], "->", s["entity_name"])
