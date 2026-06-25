# services/seeds/ofac.py
"""
Download and parse the OFAC SDN XML, extracting every confirmed crypto
address. OFAC = U.S. Treasury Office of Foreign Assets Control. The SDN
(Specially Designated Nationals) list is the authoritative source of
sanctioned addresses. Free, no API key, no signup. Updated irregularly
(sometimes multiple times a day during active enforcement, e.g. Lazarus
Group / Garantex designations).
"""
import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timezone

OFAC_URL = "https://www.treasury.gov/ofac/downloads/sdn.xml"
OFAC_NS = {"ofac": "http://tempuri.org/sdnList.xsd"}


def fetch_ofac_btc_addresses(timeout: int = 120) -> list[dict]:
    resp = requests.get(OFAC_URL, timeout=timeout)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)

    out: list[dict] = []
    for entry in root.findall(".//ofac:sdnEntry", OFAC_NS):
        last = entry.findtext("ofac:lastName", default="", namespaces=OFAC_NS) or ""
        first = entry.findtext("ofac:firstName", default="", namespaces=OFAC_NS) or ""
        entity_name = (first + " " + last).strip() or "OFAC_SDN_ENTITY"

        for feat in entry.findall(".//ofac:feature", OFAC_NS):
            ftype = feat.findtext("ofac:featureType", default="", namespaces=OFAC_NS) or ""
            if "Digital Currency Address" not in ftype:
                continue
            # Bitcoin-only: skip ETH and other 0x-prefixed chains
            if "XBT" not in ftype and "Bitcoin" not in ftype:
                continue
            value = (feat.findtext(".//ofac:value", default="", namespaces=OFAC_NS) or "").strip()
            if not value or value.startswith("0x"):
                continue
            out.append({
                "address": value,
                "entity_name": entity_name,
                "source": "OFAC_SDN",
                "confidence": 1.0,          # government ground truth
                "category": "BLACKLISTED",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            })
    return out


if __name__ == "__main__":
    seeds = fetch_ofac_btc_addresses()
    print(f"OFAC: {len(seeds)} Bitcoin addresses")
    for s in seeds[:5]:
        print(" ", s["address"], "->", s["entity_name"])
