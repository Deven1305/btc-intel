# services/seeds/walletexplorer.py
"""
WalletExplorer publishes cluster labels for exchanges and services. These
are NOT criminal addresses — they are the OPPOSITE. We load them as
'taint barriers': when criminal taint reaches a known exchange address,
propagation STOPS, because the exchange has KYC and the criminal is now
identifiable through the exchange's records (not by contaminating the
exchange's millions of innocent customers). They also serve as CLEAN
ground-truth negatives in evaluation.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

KNOWN_SERVICES = ["Binance.com", "Coinbase.com", "Kraken.com",
                  "Bitfinex.com", "Huobi.com", "OKX.com", "Bitstamp.net"]


def scrape_walletexplorer_services() -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    out: list[dict] = []
    for svc in KNOWN_SERVICES:
        try:
            resp = requests.get(f"https://www.walletexplorer.com/wallet/{svc}",
                                timeout=30, headers={"User-Agent": "btc-intel-research/0.1"})
            if resp.status_code != 200:
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.select("a[href^='/address/']"):
                addr = a.get_text(strip=True)
                if addr:
                    out.append({
                        "address": addr, "service_name": svc.replace(".com", "").replace(".net", ""),
                        "source": "WALLETEXPLORER", "label_type": "EXCHANGE",
                        "confidence": 0.85, "fetched_at": now,
                    })
        except Exception as e:
            print(f"  WalletExplorer {svc} error (non-fatal): {e}")
    return out


if __name__ == "__main__":
    labels = scrape_walletexplorer_services()
    print(f"WalletExplorer: {len(labels)} service-labelled addresses")
