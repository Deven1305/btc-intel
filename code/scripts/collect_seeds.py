# scripts/collect_seeds.py
"""
[Anaconda Prompt] python scripts/collect_seeds.py

Runs on the Windows host. Pulls every legitimately-public seed source:
OFAC SDN, UN Sanctions, Chainabuse, CryptoScamDB, SlowMist, plus
WalletExplorer service labels (taint barriers, not criminals). None of
this touches Tor or the dark web — it's all open HTTPS endpoints.
"""
import os
import psycopg2
from services.seeds.ofac import fetch_ofac_btc_addresses
from services.seeds.ofac_mirror import fetch_ofac_mirror
from services.seeds.un import fetch_un_btc_addresses
from services.seeds.chainabuse import fetch_chainabuse
from services.seeds.cryptoscamdb import fetch_cryptoscamdb
from services.seeds.slowmist import fetch_slowmist
from services.seeds.walletexplorer import scrape_walletexplorer_services
from services.seeds.store import store_criminal_seeds, store_service_labels


def main():
    conn = psycopg2.connect(os.environ["POSTGRES_URI"])

    try:
        ofac = fetch_ofac_btc_addresses()
    except Exception:
        print("  OFAC XML parse failed; using 0xB10C mirror")
        ofac = fetch_ofac_mirror()

    try:
        un = fetch_un_btc_addresses()
    except Exception as e:
        print(f"  UN sanctions fetch failed (non-fatal): {e}")
        un = []

    criminal = (
        ofac
        + un
        + fetch_chainabuse(os.getenv("CHAINABUSE_KEY"))
        + fetch_cryptoscamdb()
        + fetch_slowmist()
    )
    services = scrape_walletexplorer_services()

    n_crim = store_criminal_seeds(conn, criminal)
    n_svc = store_service_labels(conn, services)
    print(f"\n[OK] Stored {n_crim} criminal seeds, {n_svc} service labels")
    # Typical day:
    #   OFAC: ~700-800 BTC addresses
    #   UN:   ~30-60 BTC addresses
    #   Chainabuse: ~100 reports
    #   CryptoScamDB / SlowMist: varies, usually hundreds combined
    #   -> ~1,000+ criminal seeds; hundreds of service labels


if __name__ == "__main__":
    main()
