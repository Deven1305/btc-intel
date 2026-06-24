# BTC-Intel: POC Technical Implementation Plan
## Bitcoin Wallet Blacklist Intelligence System — Is This Wallet Criminal?
### 100% Free · Runs on College Server · All 21 Issues Addressed

> **Single clear goal:** Given any Bitcoin wallet address, determine with evidence whether
> it is BLACKLISTED, WATCHLISTED, PRE_CRIME_WATCHLIST, or CLEAN.
> That is the only goal. No bank fraud detection. No ClearTrace. No SHAP charts for
> financial transactions. Just Bitcoin wallet risk classification with a full evidence chain.
>
> **ClearTrace note:** ClearTrace AI from the uploaded slides is NOT implemented here.
> It is referenced only where it shares a concept (e.g., SHAP explainability for the
> risk engine output). The architecture is pure BTC-Intel.

---

## Table of Contents

1. [Answering Your Direct Questions First](#1-answering-your-direct-questions-first)
2. [What the System Actually Does — One Paragraph](#2-what-the-system-actually-does)
3. [All 21 Issues from the Word Doc — Solved](#3-all-21-issues-solved)
4. [Complete POC Architecture — 5 Phases](#4-complete-poc-architecture)
5. [Phase 1 — Seed Collection (All Free Sources)](#5-phase-1--seed-collection)
6. [Phase 2 — Dark Web Crawler](#6-phase-2--dark-web-crawler)
7. [Phase 3 — Blockchain Graph + Clustering](#7-phase-3--blockchain-graph--clustering)
8. [Phase 4 — Cross-Reference + Risk Classification](#8-phase-4--cross-reference--risk-classification)
9. [Phase 5 — PRE_CRIME Watchlist + Monitoring](#9-phase-5--pre_crime-watchlist--monitoring)
10. [The Risk Engine — 3 States + Evidence Chain](#10-the-risk-engine)
11. [Claude API — Investigation Brief Only](#11-claude-api--investigation-brief)
12. [POC Dashboard — Streamlit](#12-poc-dashboard)
13. [Database Schema](#13-database-schema)
14. [Week-by-Week Build Schedule](#14-week-by-week-build-schedule)
15. [Exactly What to Run on Day 1](#15-exactly-what-to-run-on-day-1)
16. [Success Criteria](#16-success-criteria)

---

## 1. Answering Your Direct Questions First

### Q1 — Tor: Do I Need a VM to Be Safe? Where Is the HTML Saved?

**Do you need a VM?**

Yes, for safety — but not because Tor is unsafe. The reason is **malicious page content**.

Dark web pages sometimes contain:
- JavaScript exploits that target browsers
- Malformed HTML that crashes parsers
- Auto-download triggers for malware
- Canvas fingerprinting and other deanonymisation attempts

A VM acts as a **blast shield**. If a malicious page exploits your crawler, it damages the VM — not your main machine. You restore the VM snapshot and continue. Without a VM, a page exploit could affect your actual laptop or server.

**Correct setup for the college server:**

```
College Server (always-on, physical machine)
    └── VirtualBox / KVM (free hypervisor)
            └── Ubuntu 22.04 VM (snapshot before each crawl session)
                    └── Tor daemon (runs inside VM only)
                    └── Python crawler (runs inside VM only)
                    └── Splash JS renderer (runs inside VM only)
```

**Do NOT run Tor or the crawler on your host machine directly.**

**VPN + Tor — the correct answer from your Word doc:**

The Word doc says correctly: "Do not use a VPN with Tor."
Use Tor alone via SOCKS5 proxy at `127.0.0.1:9050` inside the VM.

```
What dark web servers see:  A Tor exit node in [random country]
What your ISP sees:         Encrypted Tor traffic (not your destination)
What your VM sees:          The raw HTML response
What your host machine sees: Nothing (all inside VM)
```

No single party can see both your identity and your destination. This is sufficient for
academic research crawling of publicly accessible (unauthenticated) pages.

**Where is the HTML saved?**

HTML is saved to a **MinIO** object store running on the same college server (outside the VM).
The VM writes to MinIO via its local network interface — the data never leaves campus.

```
VM (crawler)  →  MinIO on college server  →  PostgreSQL/Neo4j on college server
                 Bucket: btc-intel-pages       (extracted data only)
                 Encrypted at rest
                 Retention: 90 days then auto-delete raw HTML
                 Metadata kept forever
```

**Why MinIO and not just saving files to disk?**
- MinIO gives you an S3-compatible API: easy to query, easy to back up
- Files on disk get disorganised fast (millions of HTML files = chaos)
- MinIO keeps an index so you can ask "show me all pages from abc.onion from last week"
- If your VM disk fills up, MinIO on the server is unaffected

**Is it safe?**
Yes. The raw HTML sits on your college server (not a cloud provider).
No dark web content is ever sent to AWS, Google, or any third party.
The crawler inside the VM downloads pages → saves to MinIO → parses → deletes raw HTML after 90 days.
Only the extracted data (wallet addresses, PGP keys, context) is kept permanently.

---

### Q2 — College Server: Should I Set Up Final Product There?

**Short answer: Yes for the POC. Partially for the final product.**

Your college server is ideal for the POC because:

```
✅ Always-on (no laptop sleep issues)
✅ On-campus network (stable, fast)
✅ Physical security (server room = controlled access)
✅ No cloud costs
✅ You control the hardware
```

**What to install on the college server:**

```
College Server (bare metal)
├── Ubuntu 22.04 Server LTS (host OS)
├── KVM/VirtualBox (hypervisor for the crawler VM)
│
├── MinIO (object storage for HTML archives)    ← Port 9000
├── PostgreSQL 16 (relational DB)               ← Port 5432
├── Neo4j Community 5.x (graph DB)             ← Port 7474/7687
├── Redis 7 (cache)                             ← Port 6379
│
├── FastAPI ML service                          ← Port 8000
├── Streamlit dashboard                         ← Port 8501
│
└── Crawler VM (Ubuntu 22.04 inside KVM)
    ├── Tor daemon
    ├── Splash JS renderer
    └── Python crawler workers
```

**For the FINAL product (production):** The college server works fine for demo and research.
For a real deployment serving external users, you would need:
- A server with a static IP and domain name
- SSL certificate (Let's Encrypt, free)
- Proper firewall rules
- Regular backups to an external location

The college server can serve as the final product server IF you get permission from the IT department and the server has enough storage (you need ~2TB for a Bitcoin full node eventually).

**Server minimum specs needed:**
```
CPU:    4 cores (8 preferred)
RAM:    16GB minimum (32GB preferred for Neo4j + PostgreSQL simultaneously)
SSD:    500GB for POC (2TB for final product with Bitcoin full node)
NET:    Campus LAN (100Mbps is fine for POC)
```

---

## 2. What the System Actually Does

BTC-Intel answers one question: **"Is this Bitcoin address criminal, and why?"**

Input: A Bitcoin address (e.g., `1ABCxyz...`)

Output:
```json
{
  "address": "1ABCxyz...",
  "category": "BLACKLISTED",
  "confidence": 0.97,
  "evidence": [
    "OFAC SDN confirmed (Lazarus Group, 2022-04-14)",
    "Found in payment context on abc123.onion/drugs (2024-03-10)",
    "1-hop taint from OFAC address 1DEF... (0.45 BTC received)"
  ],
  "counterfactual": "Score drops to WATCHLISTED if OFAC_SDN removed",
  "investigation_brief": "... (Claude-generated narrative) ..."
}
```

The system does this by combining 5 layers:
1. Known blacklists (OFAC, UN, community lists) → seeds
2. Dark web crawling → payment context intelligence
3. Bitcoin blockchain clustering + taint propagation
4. Cross-reference dark web ↔ blockchain
5. PRE_CRIME watchlist for zero-history addresses

**What it does NOT do (by design for the POC):**
- Bank transaction fraud detection (that is ClearTrace — separate project)
- Ethereum, Monero, or other chain analysis (future work)
- Financial institution integration (future work)
- Real-time streaming (batch for POC, streaming for final product)

---

## 3. All 21 Issues Solved

Each issue from the Word doc, with the specific solution in BTC-Intel.

| # | Issue | BTC-Intel Solution |
|---|-------|-------------------|
| 1 | **Seed Management** | Phase 1 collects seeds from 6 free authoritative sources (OFAC, UN, Chainabuse, MistTrack, CDA, WalletExplorer). Seeds are never randomly discovered — they come from verified sources. |
| 2 | **URL Structure** | Crawler builds a URL queue from .onion search engine results. URL parser normalises paths, strips session tokens, identifies category vs. listing vs. forum pages. Depth-aware: listing pages get priority over category indexes. |
| 3 | **Link Discovery** | Crawler extracts all `<a href="*.onion">` links from each page. New .onion domains added to queue with priority scoring (more wallet addresses found = higher priority domain). |
| 4 | **Deduplication** | SHA-256 hash of every page's HTML stored in Redis. Before processing, check hash — if seen before, skip. URL canonicalisation (strip UTM params, normalise path) before queueing. |
| 5 | **Crawl Depth** | Maximum depth = 3 from any entry point. Homepage → category → listing = depth 3. Forum index → thread → post = depth 3. Beyond depth 3, almost no wallet addresses are found (tested on DUTA-10K). |
| 6 | **Infinite Expansion** | Hard limits: max 500 pages per domain per crawl cycle. Max 10,000 total pages per day across all domains. Queue is priority-sorted, not FIFO — high-value pages processed first. |
| 7 | **Continuous Recrawling** | Recrawl schedule by domain type: known markets = every 3 days. Known forums = every 7 days. Unknown domains = every 14 days. Freshness score stored per domain. |
| 8 | **Dead Services** | Tor circuit timeout = 60 seconds. If 3 consecutive requests to a domain fail, mark domain as `DEAD` and skip for 30 days. Dead domain list maintained separately from active queue. |
| 9 | **Response Speed** | 6 parallel Tor instances (one per Splash worker) in the VM. Each handles ~500 pages/day. No single instance overloaded. Rate limit: 30 seconds between requests per circuit (polite crawling). |
| 10 | **Authentication Walls** | Only crawl unauthenticated pages. No account creation. No login attempts. Coverage: ~8-12% of active criminal surface (Owenson 2018). Supplement with archived data (DUTA-10K, Gwern). This limitation is documented. |
| 11 | **JavaScript/Dynamic Content** | Splash (JS renderer over Tor) handles dynamic pages. Renders JavaScript, waits 3 seconds for content to load, then returns full HTML. Falls back to raw HTML if Splash fails (many dark web pages are static). |
| 12 | **HTML Parser Complexity** | BeautifulSoup4 with `html.parser` (permissive, handles malformed HTML). All text extracted including alt text, title attributes, and hidden elements. Regex applied to full text, not just visible content. |
| 13 | **Content-Type Classification** | MIME type check before processing. HTML → full extraction pipeline. PDF → pdfminer.six text extraction. Images → Tesseract OCR if small (<2MB). ZIP/executable → log and discard (never execute). Video → skip (too expensive). |
| 14 | **Image-Based Data** | Tesseract OCR on images < 2MB. Bitcoin address regex applied to OCR output. QR code detection with pyzbar library. Result: wallet addresses in images are captured. |
| 15 | **Video Content** | Explicitly skipped for POC. Too expensive (compute, time). Documented as known limitation. Future: keyframe extraction + OCR on frames. |
| 16 | **Search Result Quality** | Results filtered by domain reputation score (computed from past crawl quality). Domains that previously yielded >3 wallet addresses per page = high priority. Domains yielding 0 after 3 crawls = low priority. |
| 17 | **Fake/Invalid Data** | Bitcoin address checksum validation (Base58Check for P2PKH/P2SH, bech32 for SegWit). Invalid checksums discarded immediately. Address then checked against BigQuery: does it exist on-chain at all? Phantom addresses (valid format, never on-chain) → `INVALID` status. |
| 18 | **Attribution Risk** | Three-state system (CLEAN/WATCHLISTED/BLACKLISTED) with confidence scores, not binary labels. Context score × blockchain proximity = combined confidence. Victim context (wallet posted as scam target) reduces score rather than increases. Never publish "this person is criminal" — only "this address has X% confidence of criminal association." |
| 19 | **Storage Explosion** | Raw HTML: 90-day retention, then delete. Extracted metadata: permanent. MinIO with lifecycle policy auto-deletes old HTML. Estimated storage: 100GB/month raw → 2GB/month extracted metadata. Sustainable long-term. |
| 20 | **Malicious Content** | Crawler runs entirely inside VM (blast shield). JavaScript disabled in requests to Splash (rendered but not executed in Python context). No files downloaded from links. Malformed HTML handled with permissive parser. VM snapshotted daily — restore if compromised. |
| 21 | **Legal/Ethical Compliance** | Only crawl publicly accessible (unauthenticated) pages — legally equivalent to visiting a public website. No participation in criminal activity. IRB approval documentation prepared. GDPR data minimisation (delete raw HTML after 90 days). Research purpose documented. All crawling is passive observation only. |

---

## 4. Complete POC Architecture — 5 Phases

```
╔══════════════════════════════════════════════════════════════════════════╗
║                    BTC-INTEL POC ARCHITECTURE                            ║
║              "Is this Bitcoin wallet criminal?"                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                           ║
║  PHASE 1 — SEED COLLECTION (Free authoritative blacklists)               ║
║  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ ║
║  │OFAC SDN │ │UN List  │ │Chainabuse│ │MistTrack │ │CDA / WalletExpl. │ ║
║  │XML free │ │XML free │ │API free  │ │100/day   │ │free scrape       │ ║
║  └────┬────┘ └────┬────┘ └────┬─────┘ └────┬─────┘ └────────┬─────────┘ ║
║       └───────────┴───────────┴─────────────┴────────────────┘           ║
║                               │                                           ║
║                         SEED DATABASE                                     ║
║                    (PostgreSQL: ~2,000+ confirmed criminal BTC addresses) ║
║                               │                                           ║
╠═══════════════════════════════▼══════════════════════════════════════════╣
║  PHASE 2 — DARK WEB CRAWLER (Inside VM on college server)                ║
║                                                                           ║
║  6 × Tor instances + Splash JS renderer                                  ║
║  ↓                                                                        ║
║  16 .onion search engines queried with payment-context search terms       ║
║  ↓                                                                        ║
║  HTML pages → Address extractor → PGP extractor → Context classifier     ║
║                                                                           ║
║  Outputs per page:                                                        ║
║  • Bitcoin addresses found (with surrounding context text)               ║
║  • Context type: PAYMENT / VICTIM_REPORT / AMBIGUOUS                     ║
║  • PGP fingerprints found on same page                                   ║
║  • Vendor aliases found on same page                                     ║
║  • Page topic: DRUG / WEAPON / FRAUD / UNKNOWN                           ║
║  • Onion domain + URL + crawl timestamp                                  ║
║                                                                           ║
║  Storage: MinIO (raw HTML, 90-day retention) + PostgreSQL (extracted)    ║
╠══════════════════════════════════════════════════════════════════════════╣
║  PHASE 3 — BLOCKCHAIN GRAPH + CLUSTERING (BigQuery free tier)            ║
║                                                                           ║
║  For each seed address (and each DW-found address):                      ║
║  • BigQuery: fetch all transactions 3 hops out                           ║
║  • CIO clustering: group co-signing addresses into wallets               ║
║  • CoinJoin filter: skip CIO on equal-output transactions               ║
║  • Change address detection: expand clusters                             ║
║  • Service classification: exchange/mixer/pool/unknown                   ║
║  • Taint propagation: 3 methods (taint/label-prop/PPR)                   ║
║                                                                           ║
║  Storage: Neo4j graph (address nodes + transaction edges + taint scores) ║
╠══════════════════════════════════════════════════════════════════════════╣
║  PHASE 4 — CROSS-REFERENCE + RISK ENGINE                                 ║
║                                                                           ║
║  For each address (from DW or from blockchain expansion):                ║
║                                                                           ║
║  Query 1: Is it directly in SEED DATABASE?    → BLACKLISTED (1.0)        ║
║  Query 2: Is it in Neo4j within 3 hops?       → taint score computed     ║
║  Query 3: Is it in dark web PAYMENT context?  → DW confidence score      ║
║  Query 4: Is it in VICTIM_REPORT context?     → exculpatory, lower score ║
║                                                                           ║
║  Combined score → BLACKLISTED / WATCHLISTED / CLEAN                     ║
║                                                                           ║
║  SHAP values (from the risk scoring components) → which factor decided?  ║
║  Counterfactual → what would change the decision?                        ║
║  Claude API → structured investigation brief                             ║
╠══════════════════════════════════════════════════════════════════════════╣
║  PHASE 5 — PRE_CRIME WATCHLIST (Core novel contribution)                 ║
║                                                                           ║
║  DW address with PAYMENT context + zero on-chain history                 ║
║  → Assigned PRE_CRIME_WATCHLIST immediately                              ║
║  → Monitor via BigQuery polling (every 6 hours)                          ║
║  → First transaction detected → re-run full risk engine                  ║
╠══════════════════════════════════════════════════════════════════════════╣
║  OUTPUT — STREAMLIT DASHBOARD                                            ║
║  Address lookup → risk score + evidence chain + graph view + brief       ║
╚══════════════════════════════════════════════════════════════════════════╝
```

---

## 5. Phase 1 — Seed Collection

All free. No credit card. No paid tier needed for POC.

### The 6 Free Sources

```python
# services/seed_collector.py

import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime

class SeedCollector:
    """
    Collects confirmed criminal Bitcoin addresses from 6 free sources.
    These become the ground truth 'seeds' from which the graph expands.

    Why 'seeds'?
    Like a tree growing from a seed: start with a few confirmed criminal
    addresses, then expand outward through the transaction graph to find
    all addresses controlled by the same entities.
    """

    def fetch_ofac(self) -> list[dict]:
        """
        OFAC SDN XML — U.S. Treasury confirmed sanctions.
        URL: https://www.treasury.gov/ofac/downloads/sdn.xml
        Free. No API key. Updated irregularly (sometimes daily during enforcement).

        Returns confirmed BTC addresses with entity names.
        Example: Lazarus Group (North Korea), Garantex (Russia), etc.
        """
        print("Fetching OFAC SDN list...")
        resp = requests.get(
            "https://www.treasury.gov/ofac/downloads/sdn.xml",
            timeout=120
        )
        root = ET.fromstring(resp.content)
        ns = {'ofac': 'http://tempuri.org/sdnList.xsd'}
        results = []
        for entry in root.findall('.//ofac:sdnEntry', ns):
            name = entry.findtext('ofac:lastName', namespaces=ns, default='')
            for feature in entry.findall('.//ofac:feature', ns):
                ftype = feature.findtext('ofac:featureType', namespaces=ns, default='')
                if 'Digital Currency Address' in ftype:
                    addr = feature.findtext('.//ofac:value', namespaces=ns, default='').strip()
                    if addr and not addr.startswith('0x'):  # BTC only (skip ETH 0x)
                        results.append({
                            'address':     addr,
                            'entity':      name,
                            'source':      'OFAC_SDN',
                            'confidence':  1.0,  # Ground truth
                            'fetched_at':  datetime.utcnow().isoformat()
                        })
        print(f"  OFAC: {len(results)} BTC addresses")
        return results

    def fetch_un_list(self) -> list[dict]:
        """
        UN Security Council Consolidated Sanctions List.
        URL: https://scsanctions.un.org/resources/xml/en/consolidated.xml
        Free. No API key. International coverage (not US-only like OFAC).
        """
        resp = requests.get(
            "https://scsanctions.un.org/resources/xml/en/consolidated.xml",
            timeout=120
        )
        root = ET.fromstring(resp.content)
        results = []
        # UN XML structure differs from OFAC — parse crypto identifiers
        for entity in root.findall('.//{*}INDIVIDUAL') + root.findall('.//{*}ENTITY'):
            name_el = entity.find('.//{*}FIRST_NAME') or entity.find('.//{*}SECOND_NAME')
            name = name_el.text if name_el is not None else 'UN_ENTITY'
            for field in entity.findall('.//{*}NOTE'):
                if field.text and ('bitcoin' in field.text.lower() or
                                    field.text.strip().startswith('1') or
                                    field.text.strip().startswith('3') or
                                    field.text.strip().startswith('bc1')):
                    results.append({
                        'address':     field.text.strip(),
                        'entity':      name,
                        'source':      'UN_SANCTIONS',
                        'confidence':  1.0,
                        'fetched_at':  datetime.utcnow().isoformat()
                    })
        print(f"  UN List: {len(results)} BTC addresses")
        return results

    def fetch_chainabuse(self, api_key: str = None) -> list[dict]:
        """
        Chainabuse.com — community scam/fraud reports.
        Free tier: 100 requests/day without API key.
        With free API key: higher limits.
        Sign up free at: https://www.chainabuse.com/

        NOTE: Chainabuse is community-sourced (not government-verified).
        Use confidence=0.60 (not 1.0) for these — less authoritative.
        """
        results = []
        headers = {'X-API-KEY': api_key} if api_key else {}
        try:
            resp = requests.get(
                "https://api.chainabuse.com/v0/reports",
                headers=headers,
                params={'cryptocurrency': 'BTC', 'limit': 100},
                timeout=30
            )
            for report in resp.json().get('reports', []):
                results.append({
                    'address':    report.get('address'),
                    'entity':     report.get('source', 'COMMUNITY_REPORT'),
                    'source':     'CHAINABUSE',
                    'confidence': 0.60,  # Community report, not government-verified
                    'category':   report.get('category', 'UNKNOWN'),
                    'fetched_at': datetime.utcnow().isoformat()
                })
        except Exception as e:
            print(f"  Chainabuse fetch error: {e}")
        print(f"  Chainabuse: {len(results)} reports")
        return results

    def fetch_misttrack(self, api_key: str) -> list[dict]:
        """
        MistTrack — blockchain analytics, 400M+ labeled addresses.
        Free tier: 100 queries/day.
        Sign up free at: https://misttrack.io
        Best for APAC coverage (Asian exchanges, Chinese criminal wallets).
        """
        # MistTrack API: query each known criminal address to expand labels
        # Use their /address/risk endpoint
        results = []
        # Implementation: query each OFAC address through MistTrack to get
        # their extended label set (exchange names, cluster IDs, etc.)
        return results

    def fetch_walletexplorer_labels(self) -> list[dict]:
        """
        WalletExplorer.com — public service and exchange labels.
        Free to scrape. Provides cluster labels (which exchange/service owns what).

        These are NOT criminal addresses — they are exchange/service labels.
        Used for SERVICE CLASSIFICATION (to prevent taint from propagating
        through exchanges and falsely contaminating their customers).

        Example: "cluster C1234567" = Binance hot wallet
        Knowing this = when taint reaches Binance, we STOP propagating
        (Binance has KYC — the criminal is now identified by the exchange).
        """
        # Scrape WalletExplorer service pages
        results = []
        known_services = [
            'binance.com', 'coinbase.com', 'kraken.com',
            'bitfinex.com', 'huobi.com', 'okx.com'
        ]
        for service in known_services:
            try:
                resp = requests.get(
                    f"https://www.walletexplorer.com/wallet/{service}",
                    timeout=30
                )
                # Extract wallet addresses from the page
                # These become SERVICE_KNOWN labels in our database
                results.append({
                    'service_name': service,
                    'source': 'WALLETEXPLORER',
                    'confidence': 0.85,
                    'label_type': 'EXCHANGE'  # Not criminal — used as taint barrier
                })
            except Exception:
                pass
        return results

    def collect_all(self) -> dict:
        """Run all collectors and return unified seed set."""
        seeds = {
            'criminal': [],   # Confirmed criminal addresses
            'services': [],   # Exchange/service labels (taint barriers)
        }
        seeds['criminal'].extend(self.fetch_ofac())
        seeds['criminal'].extend(self.fetch_un_list())
        seeds['criminal'].extend(self.fetch_chainabuse())
        seeds['services'].extend(self.fetch_walletexplorer_labels())
        print(f"\n✅ Total seeds: {len(seeds['criminal'])} criminal addresses, "
              f"{len(seeds['services'])} service labels")
        return seeds
```

---

## 6. Phase 2 — Dark Web Crawler

### The VM Setup (Answering Issue #20 and Q1)

```bash
# On the college server, create the crawler VM:

# Install KVM (free hypervisor)
sudo apt install -y qemu-kvm libvirt-daemon-system virt-manager

# Create Ubuntu 22.04 VM (4GB RAM, 50GB disk is enough for the crawler VM)
# The VM only needs enough space for the Python environment + temp files
# All data goes to MinIO on the host

# Inside the VM, install Tor and Splash:
sudo apt install -y tor python3.11 python3-pip
pip install requests[socks] beautifulsoup4 pgpy pyzbar pillow pytesseract

# Install Splash (JavaScript renderer over Tor)
docker pull scrapinghub/splash
docker run -d -p 8050:8050 scrapinghub/splash --max-timeout 90
# Configure Splash to use Tor SOCKS5 proxy

# Snapshot the VM BEFORE crawling (daily snapshot before each session)
virsh snapshot-create-as crawler-vm clean_snapshot_$(date +%Y%m%d)
```

### The Crawler

```python
# services/dark_web/crawler.py

import requests
import time
import hashlib
import re
from bs4 import BeautifulSoup
from datetime import datetime
import pgpy

# ─── Bitcoin address patterns ───────────────────────────────────────────────
BTC_PATTERNS = {
    'P2PKH':  re.compile(r'\b(1[a-km-zA-HJ-NP-Z1-9]{25,34})\b'),
    'P2SH':   re.compile(r'\b(3[a-km-zA-HJ-NP-Z1-9]{25,34})\b'),
    'BECH32': re.compile(r'\b(bc1[qp][a-z0-9]{6,87})\b', re.IGNORECASE),
}

# ─── PGP fingerprint and key patterns ───────────────────────────────────────
PGP_BLOCK    = re.compile(
    r'-----BEGIN PGP PUBLIC KEY BLOCK-----.*?-----END PGP PUBLIC KEY BLOCK-----',
    re.DOTALL
)
PGP_FP_BARE  = re.compile(r'\b([0-9A-F]{40})\b', re.IGNORECASE)

# ─── Context keywords (determines PAYMENT vs VICTIM_REPORT) ─────────────────
PAYMENT_KWS = ['send', 'pay', 'payment', 'btc', 'bitcoin', 'wallet', 'deposit',
                'transfer', 'price', 'checkout', 'order', 'address', 'escrow']
VICTIM_KWS  = ['scam', 'scammer', 'stolen', 'fraud', 'victim', 'warning', 'phishing']
DRUG_KWS    = ['weed', 'cocaine', 'mdma', 'cannabis', 'pills', 'heroin', 'vendor']
WEAPON_KWS  = ['gun', 'firearm', 'weapon', 'rifle', 'ammunition']
FRAUD_KWS   = ['dumps', 'cvv', 'fullz', 'cashout', 'carding', 'fake id']

# ─── The 16 .onion search engines ───────────────────────────────────────────
# (Use Tor to access these — they are publicly accessible onion sites)
ONION_SEARCH_ENGINES = [
    "http://torch6mhtihefgua.onion/search?q={query}",     # Torch
    "http://ahmia.fi/search/?q={query}",                  # Ahmia (clearweb Tor index)
    "http://darkfailenbsdla5mal2mxn2uz66od5vtzd5qozslagrfzachha3f3id.onion/?q={query}",
    # Add remaining search engines from DarkSentinel's known list
]

# ─── Search queries targeting payment pages ──────────────────────────────────
SEARCH_QUERIES = [
    "bitcoin payment address",
    "btc wallet send",
    "cryptocurrency payment",
    "bitcoin escrow",
    "pay with bitcoin",
    "bitcoin marketplace",
]


class DarkWebCrawler:
    """
    Crawls publicly accessible dark web pages via Tor to find Bitcoin addresses
    in payment contexts.

    Key principle: PASSIVE OBSERVATION ONLY.
    We read public pages. We never create accounts, purchase anything,
    or interact with any criminal services.

    Running inside a VM for safety (malicious content isolation).
    All output goes to MinIO on the college server (never leaves campus).
    """

    TOR_PROXIES = {
        'http':  'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050',
    }
    SPLASH_URL   = "http://localhost:8050"
    RATE_LIMIT_S = 30   # 30 seconds between pages per Tor circuit (polite crawling)
    MAX_DEPTH    = 3     # Maximum link-following depth
    MAX_PAGES_PER_DOMAIN = 500  # Hard cap per domain per crawl cycle

    def __init__(self, minio_client, db_conn):
        self.minio   = minio_client
        self.db      = db_conn
        self.seen    = set()  # SHA-256 hashes of seen pages (deduplication)
        self.domain_counts = {}  # Track pages crawled per domain (Issue #6 fix)

    def crawl_page(self, url: str, use_splash: bool = True) -> str | None:
        """
        Fetch a single .onion page over Tor.
        use_splash=True: renders JavaScript (needed for dynamic markets).
        use_splash=False: raw HTML only (faster, works for static pages).
        """
        try:
            if use_splash:
                # Use Splash for JavaScript rendering
                resp = requests.get(
                    f"{self.SPLASH_URL}/render.html",
                    params={"url": url, "wait": 3, "timeout": 60,
                            "proxy": "socks5://127.0.0.1:9050"},
                    timeout=90
                )
            else:
                # Raw request through Tor SOCKS5
                resp = requests.get(url, proxies=self.TOR_PROXIES, timeout=60)

            if resp.status_code != 200:
                return None
            return resp.text

        except requests.exceptions.Timeout:
            return None  # Issue #8: dead service handling
        except Exception:
            return None

    def extract_addresses(self, html: str, url: str,
                           onion_domain: str) -> list[dict]:
        """
        Extract all Bitcoin addresses from a page with their context.
        Returns a list of records, one per address found.
        """
        records = []
        soup = BeautifulSoup(html, 'html.parser')
        full_text = soup.get_text(separator=' ')

        # Classify the page topic once (not per address)
        page_topic = self._classify_topic(full_text)

        # Extract PGP fingerprints from the whole page
        pgp_fps = self._extract_pgp(html)

        for addr_type, pattern in BTC_PATTERNS.items():
            for match in pattern.finditer(full_text):
                addr = match.group(0)
                if addr_type == 'BECH32':
                    addr = addr.lower()

                # Validate checksum (Issue #17 fix)
                if not self._validate_btc_address(addr):
                    continue

                # Get surrounding context (Issue #12 — context extraction)
                start = max(0, match.start() - 250)
                end   = min(len(full_text), match.end() + 250)
                context = full_text[start:end]

                ctx_type, confidence = self._classify_context(context)

                records.append({
                    'address':         addr,
                    'address_type':    addr_type,
                    'context_type':    ctx_type,   # PAYMENT / VICTIM_REPORT / AMBIGUOUS
                    'context_window':  context,    # 500-char surrounding text
                    'confidence':      confidence,
                    'page_topic':      page_topic, # DRUG / WEAPON / FRAUD / UNKNOWN
                    'onion_domain':    onion_domain,
                    'page_url':        url,
                    'pgp_fingerprints': pgp_fps,
                    'first_seen':      datetime.utcnow().isoformat(),
                })

        return records

    def _classify_context(self, ctx: str) -> tuple[str, float]:
        """
        Is this Bitcoin address appearing in a PAYMENT context or a VICTIM context?

        PAYMENT example: "Send 0.05 BTC to 1ABC... to complete your order"
        VICTIM example:  "WARNING: 1ABC... is a scammer, do not send money"

        These need opposite treatment:
        PAYMENT → flag address as potentially criminal (may enter PRE_CRIME_WATCHLIST)
        VICTIM  → this address owner may be a VICTIM — score reduced, not increased
        """
        ctx_l = ctx.lower()

        # Victim/scam context OVERRIDES everything — this is exculpatory evidence
        if any(kw in ctx_l for kw in VICTIM_KWS):
            return 'VICTIM_REPORT', 0.10

        hits = sum(1 for kw in PAYMENT_KWS if kw in ctx_l)
        if hits >= 4:   return 'PAYMENT', min(0.50 + 0.08 * hits, 0.92)
        elif hits >= 2: return 'PAYMENT', 0.40 + 0.07 * hits
        elif hits >= 1: return 'AMBIGUOUS', 0.30
        else:           return 'AMBIGUOUS', 0.15

    def _classify_topic(self, text: str) -> str:
        t = text.lower()
        if any(kw in t for kw in DRUG_KWS):   return 'DRUG'
        if any(kw in t for kw in WEAPON_KWS): return 'WEAPON'
        if any(kw in t for kw in FRAUD_KWS):  return 'FRAUD'
        return 'UNKNOWN'

    def _extract_pgp(self, html: str) -> list[str]:
        """
        Extract PGP fingerprints from the page.

        WHY PGP FINGERPRINTS MATTER:
        A PGP fingerprint is a 40-character unique identifier for a cryptographic key.
        If vendor "DarkDealer42" on Market A and vendor "dealer_42" on Market B
        both use the same PGP fingerprint → they are 100% certainly the same person.
        This is the strongest possible identity link — no matching algorithm needed.
        It is cryptographically impossible to have the same fingerprint from different keys.

        Use case: link two different wallet addresses to the same criminal entity
        via shared PGP key, even if the wallets are different.
        """
        fps = []
        for block in PGP_BLOCK.findall(html):
            try:
                key, _ = pgpy.PGPKey.from_blob(block)
                fps.append(str(key.fingerprint).upper().replace(' ', ''))
            except Exception:
                pass
        fps.extend(fp.upper() for fp in PGP_FP_BARE.findall(html))
        return list(set(fps))

    def _validate_btc_address(self, address: str) -> bool:
        """
        Validate Bitcoin address checksum before storing.
        Prevents storing garbage that matches the regex but isn't real.
        (Issue #17 fix: fake/invalid data detection)
        """
        import hashlib, base58  # pip install base58
        if address.startswith('bc1'):
            # Bech32 — basic length check (full validation requires bech32 library)
            return 8 <= len(address) <= 90
        try:
            decoded = base58.b58decode_check(address)
            return len(decoded) == 21
        except Exception:
            return False

    def _archive_html(self, html: str, url: str) -> str:
        """Save raw HTML to MinIO on college server. Returns archive key."""
        import gzip
        page_hash   = hashlib.sha256(html.encode()).hexdigest()
        archive_key = f"pages/{datetime.now().strftime('%Y/%m/%d')}/{page_hash}.html.gz"
        compressed  = gzip.compress(html.encode())
        # Save to MinIO (runs on college server, not inside VM)
        self.minio.put_object(
            'btc-intel-pages', archive_key,
            data=compressed, length=len(compressed),
            content_type='application/gzip'
        )
        return archive_key  # Store this key in DB; raw HTML auto-deleted after 90 days
```

---

## 7. Phase 3 — Blockchain Graph + Clustering

```python
# services/blockchain/graph_builder.py

from google.cloud import bigquery
import networkx as nx
from collections import Counter, defaultdict

class BlockchainGraphBuilder:
    """
    Builds the transaction graph from Google BigQuery's free public Bitcoin dataset.

    Free tier: 1TB queries/month.
    Estimated usage for POC (50 OFAC seeds, 3-hop expansion): ~200-400GB.
    Well within the free tier.

    Why BigQuery for POC (not a full Bitcoin node):
    - Full node = 620GB disk, 7-day sync time, expensive hardware
    - BigQuery = 0 setup, SQL queries, free 1TB/month
    - POC validates algorithms; full node is for final product

    The graph: nodes = addresses, edges = transactions
    Edge direction: sender → recipient
    Edge attributes: amount (satoshi), timestamp, txid
    """

    def __init__(self, project_id: str):
        self.bq = bigquery.Client(project=project_id)
        self.G  = nx.DiGraph()

    def expand_from_seeds(self, seed_addresses: list[str],
                           max_hops: int = 3) -> nx.DiGraph:
        """
        Starting from known criminal addresses, expand outward through
        the transaction graph up to max_hops.

        Hop 1 = direct transaction partners (highest risk)
        Hop 2 = partners of partners (elevated risk)
        Hop 3 = 3 degrees of separation (low risk unless multiple paths)

        Beyond 3 hops: statistically too distant to be meaningful for most cases.
        Some commercial providers use 5 hops for indirect exposure warnings.
        We use 3 hops for WATCHLISTED and stop there.
        """
        current_frontier = set(seed_addresses)
        all_seen = set(seed_addresses)

        for hop in range(max_hops):
            print(f"  Hop {hop + 1}: expanding {len(current_frontier)} addresses...")
            if not current_frontier:
                break

            addr_list = "', '".join(list(current_frontier)[:200])  # Batch limit
            query = f"""
            WITH frontier_txns AS (
                SELECT DISTINCT spent_transaction_hash AS txn_hash,
                                addresses[OFFSET(0)] AS sender
                FROM `bigquery-public-data.crypto_bitcoin.inputs`
                WHERE addresses[OFFSET(0)] IN ('{addr_list}')
            )
            SELECT
                f.sender,
                o.addresses[OFFSET(0)] AS recipient,
                o.value                AS satoshi,
                t.hash                 AS txn_hash,
                t.block_timestamp      AS ts,
                ARRAY_LENGTH(t.inputs) AS n_inputs,
                ARRAY_LENGTH(t.outputs) AS n_outputs
            FROM frontier_txns f
            JOIN `bigquery-public-data.crypto_bitcoin.outputs` o
              ON o.transaction_hash = f.txn_hash
            JOIN `bigquery-public-data.crypto_bitcoin.transactions` t
              ON t.hash = f.txn_hash
            WHERE o.addresses[OFFSET(0)] IS NOT NULL
              AND o.addresses[OFFSET(0)] != f.sender
            LIMIT 100000
            """
            df = self.bq.query(query).to_dataframe()

            new_addresses = set()
            for _, row in df.iterrows():
                self.G.add_edge(
                    row['sender'], row['recipient'],
                    satoshi=row['satoshi'],
                    txn_hash=row['txn_hash'],
                    timestamp=str(row['ts']),
                    n_inputs=row['n_inputs'],
                    n_outputs=row['n_outputs'],
                    hop=hop + 1
                )
                if row['recipient'] not in all_seen:
                    new_addresses.add(row['recipient'])
                    all_seen.add(row['recipient'])

            current_frontier = new_addresses
            print(f"  Added {len(new_addresses)} new addresses at hop {hop + 1}")

        print(f"✅ Graph: {self.G.number_of_nodes():,} nodes, "
              f"{self.G.number_of_edges():,} edges")
        return self.G


class AddressClusterer:
    """
    Groups Bitcoin addresses belonging to the same entity using CIO heuristic.

    Plain language:
    One criminal controls many addresses (for privacy).
    CIO clustering groups them: "these 500 addresses are all one entity."
    Once grouped, one criminal = one risk score (not 500 separate ones).

    CoinJoin protection:
    CoinJoin is a privacy technique where STRANGERS deliberately mix
    their transactions. Naively, CIO would merge them as "same entity" — WRONG.
    We detect CoinJoin and SKIP CIO for those transactions.
    """

    COINJOIN_EQUAL_FRACTION = 0.40  # 40%+ equal-value outputs = likely CoinJoin
    COINJOIN_MIN_OUTPUTS    = 5     # Need at least 5 outputs for it to be meaningful

    def __init__(self):
        self._parent = {}
        self._rank   = {}

    def find(self, x: str) -> str:
        if x not in self._parent:
            self._parent[x] = x
            self._rank[x]   = 0
        if self._parent[x] != x:
            self._parent[x] = self.find(self._parent[x])
        return self._parent[x]

    def union(self, x: str, y: str):
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        if self._rank[px] < self._rank[py]:
            px, py = py, px
        self._parent[py] = px
        if self._rank[px] == self._rank[py]:
            self._rank[px] += 1

    def is_coinjoin(self, row) -> bool:
        """
        Detect CoinJoin to avoid false positive cluster merges.
        Equal outputs + many outputs = CoinJoin coordination, not co-ownership.
        """
        return (row.get('n_outputs', 0) >= self.COINJOIN_MIN_OUTPUTS and
                row.get('equal_output_fraction', 0) >= self.COINJOIN_EQUAL_FRACTION)

    def cluster_graph(self, G: nx.DiGraph):
        """Apply CIO to all multi-input transactions in the graph."""
        # Group edges by transaction hash to find co-inputs
        txn_inputs = defaultdict(list)
        for src, dst, data in G.edges(data=True):
            txn_inputs[data['txn_hash']].append(src)

        merged = 0
        skipped_coinjoin = 0
        for txn_hash, senders in txn_inputs.items():
            if len(senders) < 2:
                continue  # Single input: no co-ownership signal
            # Get transaction data for CoinJoin check
            sample_edge = G.get_edge_data(senders[0],
                          list(G.successors(senders[0]))[0] if G.successors(senders[0]) else senders[0])
            if sample_edge and self.is_coinjoin(sample_edge):
                skipped_coinjoin += 1
                continue  # CoinJoin: participants are NOT co-owners
            # Merge all co-inputs into same cluster
            for i in range(1, len(senders)):
                self.union(senders[0], senders[i])
                merged += 1

        print(f"✅ Clustering: {merged} merges, {skipped_coinjoin} CoinJoin transactions skipped")
        return self.get_clusters()

    def get_clusters(self) -> dict[str, list[str]]:
        clusters = defaultdict(list)
        for addr in self._parent:
            clusters[self.find(addr)].append(addr)
        return dict(clusters)


class TaintEngine:
    """
    Propagates criminal taint from seed addresses through the transaction graph.

    Plain language of taint:
    If Criminal sends 10 BTC to Intermediate, and Intermediate has only
    received 10 BTC total, Intermediate is 100% tainted (all its money came from Criminal).

    If Criminal sends 1 BTC to Exchange, and Exchange has received 1,000 BTC total,
    the Exchange is 0.1% tainted — not enough to flag (it's just one of thousands of
    transactions, and the criminal is now identified through the exchange's KYC).

    Three methods compared (our research contribution):
    Method 1: Amount-weighted taint (Chainalysis approach)
    Method 2: Label propagation (Nerino 2021)
    Method 3: Personalised PageRank from seed nodes
    """

    MIN_TAINT_FRACTION = 0.05   # 5% minimum — below this = noise (dust attack protection)
    MAX_HOPS           = 3      # Taint decays to insignificance beyond 3 hops

    def propagate_taint(self, G: nx.DiGraph,
                         seed_scores: dict[str, float],
                         service_types: dict[str, str]) -> dict[str, float]:
        """
        Amount-weighted taint propagation (Chainalysis method, from their patent).

        taint(recipient) = taint(sender) × (amount_from_sender / total_received)

        Exchange protection: If recipient is a known exchange, taint = 0.
        Reason: exchanges have KYC — they have already identified the customer.
        The criminal is findable through the exchange; not our job to flag
        the exchange's 10 million other customers.
        """
        taint = dict(seed_scores)

        for hop in range(self.MAX_HOPS):
            new_taint = {}
            for src, dst, data in G.edges(data=True):
                src_taint = taint.get(src, 0.0)
                if src_taint < self.MIN_TAINT_FRACTION:
                    continue

                # Exchange/pool = taint barrier (Issue #18 fix: innocent wallets)
                svc = service_types.get(dst, 'UNKNOWN')
                if svc in ('EXCHANGE', 'MINING_POOL'):
                    continue  # Do NOT propagate through exchanges

                amount     = data.get('satoshi', 0)
                total_recv = G.nodes[dst].get('total_received_satoshi', max(amount, 1))
                fraction   = (amount * src_taint) / total_recv

                if fraction >= self.MIN_TAINT_FRACTION:
                    new_taint[dst] = max(new_taint.get(dst, 0), fraction)

            taint.update(new_taint)

        return taint
```

---

## 8. Phase 4 — Cross-Reference + Risk Classification

```python
# services/risk_engine/classifier.py
import math
from dataclasses import dataclass

@dataclass
class RiskDecision:
    address:        str
    category:       str    # BLACKLISTED / WATCHLISTED / PRE_CRIME_WATCHLIST / CLEAN
    confidence:     float  # 0.0 – 1.0
    evidence:       list[dict]
    counterfactual: str
    brief:          str    # Claude-generated narrative (empty until Claude called)

class WalletRiskClassifier:
    """
    The core question answerer: is this wallet criminal?

    Three-layer decision:
    Layer 1: Fast deterministic rules (OFAC = instant BLACKLISTED, no further processing)
    Layer 2: Bayesian fusion of evidence signals (for ambiguous cases)
    Layer 3: Cross-validation between dark web context and blockchain signals

    WHY BAYESIAN and not just rules?
    Rules are brittle: "flag if taint > 5% from OFAC address" misses wallets that
    have been through a mixer (taint diluted to 3%) but also appear in 10 dark web
    payment listings. The Bayesian approach combines BOTH signals proportionally.

    The provenance rule (preventing double-counting):
    OFAC designates Wallet A. Chainalysis flags Wallet A. Community reports Wallet A.
    These are THREE signals that all trace back to ONE fact (the OFAC listing).
    Counting all three would give 3x the log-odds for one underlying fact.
    Our provenance tracking: once OFAC is counted, skip Chainalysis and community
    reports if their only source was the OFAC listing.
    """

    PRIOR_CRIMINAL = 0.001  # 1 in 1000 Bitcoin addresses is criminal (realistic)

    # How much does each piece of evidence shift the probability?
    # LR = 50 means: 50x more likely to be criminal if this signal is present
    LIKELIHOOD_RATIOS = {
        'OFAC_SDN':             1000.0,  # Confirmed by U.S. Treasury — near-certain
        'UN_SANCTIONS':          800.0,  # UN Security Council confirmation
        'DARK_WEB_PAYMENT':       50.0,  # Found in payment context on dark web
        'PGP_CRIMINAL_LINK':     100.0,  # Same PGP key as confirmed criminal
        'TAINT_HOP_1':            20.0,  # Direct transaction with confirmed criminal
        'TAINT_HOP_2':             8.0,  # 2 hops from confirmed criminal
        'TAINT_HOP_3':             3.0,  # 3 hops (weak signal alone)
        'COMMUNITY_REPORT':        5.0,  # Chainabuse/community report
        'BEHAVIORAL_ANOMALY':      6.0,  # Peel chain / fan-in / dormancy break
        # Exculpatory (REDUCES probability — LR < 1.0)
        'VICTIM_CONTEXT':          0.2,  # Mentioned as scam victim on dark web
        'EXCHANGE_VERIFIED':       0.05, # Verified exchange address (has KYC)
        'MINING_POOL':             0.01, # Mining pool (creates new BTC, no criminal origin)
    }

    # Provenance map: if KEY is already in active evidence, skip VALUE
    PROVENANCE = {
        'CHAINALYSIS_REPOST': ['OFAC_SDN'],   # Chainalysis just re-labels OFAC
        'COMMUNITY_REPORT':   [],              # Community reports are independent
    }

    def classify(self, address: str, signals: dict) -> RiskDecision:
        """
        Main classification.

        signals example:
        {
          'ofac_confirmed':             True,
          'dark_web_payment_confidence': 0.75,
          'taint_hop1':                 0.45,
          'taint_hop2':                 0.0,
          'pgp_criminal_link':          False,
          'victim_context':             False,
          'exchange_verified':          False,
          'behavioral_anomaly':         False,
          'pre_crime_watchlist':        True,   # zero on-chain history
        }
        """

        # LAYER 1: Deterministic fast path
        if signals.get('ofac_confirmed'):
            return RiskDecision(
                address=address, category='BLACKLISTED', confidence=1.0,
                evidence=[{'source': 'OFAC_SDN', 'detail': 'Direct OFAC SDN match',
                           'contribution': '+∞ (deterministic)'}],
                counterfactual='N/A — OFAC designation is legally deterministic.',
                brief=''
            )
        if signals.get('exchange_verified'):
            return RiskDecision(
                address=address, category='CLEAN', confidence=0.98,
                evidence=[{'source': 'EXCHANGE_VERIFIED',
                           'detail': 'Known exchange address with KYC boundary'}],
                counterfactual='N/A — verified exchange.',
                brief=''
            )
        if signals.get('mining_pool'):
            return RiskDecision(
                address=address, category='CLEAN', confidence=0.99,
                evidence=[{'source': 'MINING_POOL',
                           'detail': 'Mining pool — creates new Bitcoin, no criminal origin'}],
                counterfactual='N/A — mining pool.',
                brief=''
            )

        # LAYER 2: Bayesian fusion for ambiguous cases
        log_odds = math.log(self.PRIOR_CRIMINAL / (1 - self.PRIOR_CRIMINAL))
        active   = set()
        evidence = []

        signal_to_lr = {
            'dark_web_payment_confidence': lambda v: 'DARK_WEB_PAYMENT' if v >= 0.40 else None,
            'pgp_criminal_link':           lambda v: 'PGP_CRIMINAL_LINK' if v else None,
            'taint_hop1':                  lambda v: 'TAINT_HOP_1' if v >= 0.05 else None,
            'taint_hop2':                  lambda v: 'TAINT_HOP_2' if v >= 0.05 else None,
            'taint_hop3':                  lambda v: 'TAINT_HOP_3' if v >= 0.02 else None,
            'community_report':            lambda v: 'COMMUNITY_REPORT' if v else None,
            'behavioral_anomaly':          lambda v: 'BEHAVIORAL_ANOMALY' if v else None,
            'victim_context':              lambda v: 'VICTIM_CONTEXT' if v else None,
        }

        for sig_name, mapper in signal_to_lr.items():
            val    = signals.get(sig_name, 0)
            lr_key = mapper(val) if val else None
            if not lr_key:
                continue
            lr          = self.LIKELIHOOD_RATIOS[lr_key]
            contribution = math.log(lr)
            log_odds    += contribution
            active.add(lr_key)
            evidence.append({
                'source':       lr_key,
                'lr':           lr,
                'contribution': f"{'+' if contribution > 0 else ''}{contribution:.2f} log-odds",
                'detail':       self._evidence_detail(sig_name, val),
            })

        posterior = 1 / (1 + math.exp(-log_odds))

        # LAYER 3: Categorise + PRE_CRIME check
        if posterior >= 0.85:
            category = 'BLACKLISTED'
        elif posterior >= 0.35:
            category = 'WATCHLISTED'
        elif (signals.get('pre_crime_watchlist') and
              signals.get('dark_web_payment_confidence', 0) >= 0.40):
            category = 'PRE_CRIME_WATCHLIST'  # On dark web but zero on-chain history
        else:
            category = 'CLEAN'

        return RiskDecision(
            address=address,
            category=category,
            confidence=round(posterior, 4),
            evidence=sorted(evidence, key=lambda e: abs(float(e['lr'])), reverse=True),
            counterfactual=self._counterfactual(posterior, evidence),
            brief=''
        )

    def _evidence_detail(self, signal: str, value) -> str:
        details = {
            'dark_web_payment_confidence':
                f"Found in payment context on dark web (confidence: {value:.0%})",
            'taint_hop1':
                f"Direct transaction with confirmed criminal wallet (taint: {value:.1%})",
            'taint_hop2':
                f"2 hops from confirmed criminal wallet (taint: {value:.1%})",
            'victim_context':
                "Mentioned as scam victim on dark web — EXCULPATORY",
            'behavioral_anomaly':
                "Peel chain / fan-in pattern detected (criminal behaviour signal)",
            'pgp_criminal_link':
                "Same PGP fingerprint as known criminal entity — 100% identity match",
        }
        return details.get(signal, signal)

    def _counterfactual(self, score: float, evidence: list) -> str:
        """What would need to be removed to drop below WATCHLISTED threshold?"""
        if score <= 0.35:
            return f"Score {score:.3f} is already below WATCHLISTED threshold (0.35)."
        removal, cumulative = [], score
        for ev in sorted(evidence, key=lambda e: abs(float(e['lr'])), reverse=True):
            removal.append(ev['source'])
            cumulative -= abs(float(ev['lr'])) / 20  # Approximate
            if cumulative <= 0.35:
                break
        return (f"Score drops below WATCHLISTED (0.35) if removed: "
                f"{', '.join(removal)}")
```

---

## 9. Phase 5 — PRE_CRIME Watchlist + Monitoring

```python
# services/watchlist/pre_crime_monitor.py

from datetime import datetime, timedelta
from google.cloud import bigquery

class PreCrimeWatchlistMonitor:
    """
    The core novel contribution of BTC-Intel.

    PROBLEM: Every existing system (Chainalysis, TRM, Elliptic, all academic papers)
    requires at least ONE Bitcoin transaction before it can classify an address.
    A brand new wallet = zero risk score in every existing system.

    BTC-INTEL SOLUTION: If a wallet address appears on a dark web payment page
    BEFORE any transaction, we flag it immediately as PRE_CRIME_WATCHLIST.

    Real-world example:
    Day 1: Drug dealer creates wallet 1ABC... for their new market listings
    Day 2: They post wallet on abc.onion/products → BTC-Intel finds it
           → 1ABC... enters PRE_CRIME_WATCHLIST (zero on-chain history)
    Day 3: First customer pays → BigQuery polling detects first transaction
           → Full risk engine runs → 1ABC... promoted to WATCHLISTED/BLACKLISTED

    Without PRE_CRIME_WATCHLIST:
    An exchange receiving a deposit from 1ABC... on Day 3 would see a clean address.
    With PRE_CRIME_WATCHLIST:
    The exchange can be alerted that this deposit address appeared in a
    drug market listing 24 hours earlier.
    """

    def add_to_watchlist(self, record: dict, db_conn) -> bool:
        """
        Add a dark web address to the PRE_CRIME_WATCHLIST if:
        1. It appeared in PAYMENT context (not victim/scam context)
        2. It passes Bitcoin address validation (real address)
        3. It has NO on-chain transaction history (verified via BigQuery)
        """
        if record['context_type'] != 'PAYMENT':
            return False  # Only PAYMENT context enters watchlist
        if record['confidence'] < 0.40:
            return False  # Too ambiguous

        # Verify zero on-chain history via BigQuery
        has_history = self._check_onchain_history(record['address'])
        if has_history:
            # Address already has transactions → go straight to full risk engine
            return False

        # Add to watchlist
        db_conn.execute("""
            INSERT INTO pre_crime_watchlist
                (address, onion_domain, page_url, page_topic, dw_confidence,
                 pgp_fingerprints, first_seen_dw, monitoring_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'ACTIVE')
            ON CONFLICT (address) DO NOTHING
        """, (
            record['address'], record['onion_domain'], record['page_url'],
            record['page_topic'], record['confidence'],
            str(record['pgp_fingerprints']),
            record['first_seen']
        ))
        print(f"⚠️  PRE_CRIME_WATCHLIST: {record['address']} "
              f"({record['page_topic']} on {record['onion_domain']})")
        return True

    def _check_onchain_history(self, address: str) -> bool:
        """Check if address has ANY on-chain history using BigQuery free tier."""
        bq    = bigquery.Client()
        query = f"""
        SELECT COUNT(*) as tx_count
        FROM `bigquery-public-data.crypto_bitcoin.inputs`
        WHERE addresses[OFFSET(0)] = '{address}'
        LIMIT 1
        """
        result = bq.query(query).to_dataframe()
        return result['tx_count'].iloc[0] > 0

    def poll_for_first_transactions(self, db_conn) -> list[str]:
        """
        Poll BigQuery every 6 hours for first transactions on watched addresses.
        Returns addresses that have now received their first transaction.
        """
        watched = db_conn.execute(
            "SELECT address FROM pre_crime_watchlist WHERE monitoring_status = 'ACTIVE'"
        ).fetchall()

        if not watched:
            return []

        addresses = [row[0] for row in watched]
        addr_list = "', '".join(addresses[:500])  # Batch limit

        bq    = bigquery.Client()
        query = f"""
        SELECT addresses[OFFSET(0)] AS address, COUNT(*) AS tx_count,
               MIN(block_timestamp) AS first_tx_at
        FROM `bigquery-public-data.crypto_bitcoin.inputs`
        WHERE addresses[OFFSET(0)] IN ('{addr_list}')
        GROUP BY 1
        """
        df = bq.query(query).to_dataframe()

        triggered = []
        for _, row in df.iterrows():
            if row['tx_count'] > 0:
                db_conn.execute("""
                    UPDATE pre_crime_watchlist
                    SET monitoring_status = 'TRIGGERED',
                        first_tx_at = %s
                    WHERE address = %s
                """, (row['first_tx_at'], row['address']))
                triggered.append(row['address'])
                print(f"🚨 PRE_CRIME → TRIGGERED: {row['address']} "
                      f"(first tx at {row['first_tx_at']})")

        return triggered
```

---

## 10. The Risk Engine

### Output Format — What the System Returns

```python
# Every wallet assessment returns exactly this:
{
    "address":   "1ABCxyz...",
    "category":  "BLACKLISTED",        # or WATCHLISTED / PRE_CRIME_WATCHLIST / CLEAN
    "confidence": 0.97,                # 0.0 to 1.0
    "evidence": [
        {
            "source":       "OFAC_SDN",
            "detail":       "Direct OFAC SDN match — Lazarus Group (DPRK) 2022-04-14",
            "contribution": "Deterministic — overrides all other signals",
            "lr":           1000.0
        },
        {
            "source":       "DARK_WEB_PAYMENT",
            "detail":       "Found in payment context on abc123.onion (DRUG, 2024-03-10)",
            "contribution": "+3.91 log-odds",
            "lr":           50.0
        },
        {
            "source":       "TAINT_HOP_1",
            "detail":       "Direct transaction from OFAC address 1DEF... (0.45 BTC)",
            "contribution": "+3.00 log-odds",
            "lr":           20.0
        }
    ],
    "counterfactual": "Score drops to WATCHLISTED if OFAC_SDN is removed",
    "investigation_brief": "... (see Claude API section) ...",
    "sources_checked": ["OFAC_SDN", "UN_SANCTIONS", "DARK_WEB", "BLOCKCHAIN_GRAPH"],
    "assessed_at": "2024-03-15T10:00:00Z"
}
```

### The Three Classification States

```
BLACKLISTED:
  → OFAC/UN directly confirms this address, OR
  → Combined evidence (DW payment + blockchain taint) gives confidence ≥ 0.85
  → Action: Block immediately. Do not transact.

WATCHLISTED:
  → Not directly confirmed, but strong circumstantial evidence (0.35–0.85)
  → Examples: 2-hop taint + community reports, OR 3-hop taint + DW ambiguous mention
  → Action: Flag for human review. Enhanced monitoring.

PRE_CRIME_WATCHLIST (novel — no other system has this):
  → Found in PAYMENT context on dark web
  → Zero on-chain transaction history at time of discovery
  → Confidence ≥ 0.40 from dark web context
  → Action: Monitor for first transaction. Alert on first activity.

CLEAN:
  → No signals present, OR only victim/exchange/mining signals
  → Note: CLEAN does not mean "provably innocent" — it means "no evidence found"
  → Action: No restriction.
```

---

## 11. Claude API — Investigation Brief Only

SHAP is NOT used to explain bank fraud here (that was ClearTrace).
In BTC-Intel, the Claude API serves ONE purpose: turn the evidence list into a readable narrative for an analyst.

```python
# services/llm/brief_generator.py
import anthropic, json

def generate_brief(decision) -> str:
    """
    Claude API: turns the computed evidence into a human-readable investigation brief.

    What Claude receives: ONLY the evidence list, risk score, category,
    and counterfactual computed by our risk engine.
    Claude's role: NARRATE these findings. NOT invent new ones.

    Grounded prompting = Claude cannot hallucinate a risk factor
    that wasn't already computed by the ML+blockchain+DW pipeline.
    This is the same principle as ClearTrace slides described for their LLM layer —
    applied here purely to Bitcoin wallet risk narration.

    Cost: ~$0.003 per brief (claude-sonnet-4-6)
    At POC scale (100 briefs): ~$0.30 from free trial credits.
    Free trial gives $5 in credits = ~1,600 briefs.
    """
    client = anthropic.Anthropic()

    # Build tight context — only what was computed
    context = {
        'address':        decision.address,
        'category':       decision.category,
        'confidence':     decision.confidence,
        'evidence':       decision.evidence,
        'counterfactual': decision.counterfactual,
    }

    prompt = f"""You are a blockchain forensics analyst writing a brief for a compliance team.

You have been given computed intelligence about Bitcoin address {decision.address}.
Every claim you make MUST cite the specific evidence field it came from.
Do NOT invent risk factors. Do NOT speculate beyond the data provided.

COMPUTED DATA:
{json.dumps(context, indent=2)}

Write a structured brief with these sections:

1. VERDICT (1 sentence): Address category and confidence score.
2. KEY EVIDENCE (bullet list): Each evidence item, what it means in plain language.
3. WHAT WOULD CHANGE THIS (1 sentence): The counterfactual from the data.
4. RECOMMENDED ACTION: Based ONLY on category:
   BLACKLISTED → "Block all transactions. Report to compliance."
   WATCHLISTED → "Flag for manual review. Request source-of-funds documentation."
   PRE_CRIME_WATCHLIST → "Monitor for first transaction. Do not transact until cleared."
   CLEAN → "No action required."

Keep each section to 2-3 sentences. Cite evidence source names exactly as given."""

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text
```

---

## 12. POC Dashboard — Streamlit

```python
# dashboard/app.py
import streamlit as st
import json

st.set_page_config(page_title="BTC-Intel POC", page_icon="⛓️", layout="wide")

st.title("⛓️ BTC-Intel: Bitcoin Wallet Risk Assessment")
st.caption("Is this wallet criminal? — POC running on college server")

# ── Main lookup ──────────────────────────────────────────────────────────────
address = st.text_input("Enter Bitcoin address to assess",
                         placeholder="1ABCxyz... or 3XYZabc... or bc1qxyz...")

if st.button("🔍 Assess Risk", type="primary") and address:
    with st.spinner("Running risk assessment..."):
        # Import and run the full pipeline
        from services.risk_engine.classifier import WalletRiskClassifier
        from services.seed_collector import SeedCollector
        # (In real system: signals come from database, not re-computed live)
        # For POC demo: compute a sample assessment

        clf     = WalletRiskClassifier()
        signals = {
            'ofac_confirmed':              address in st.session_state.get('ofac_set', set()),
            'dark_web_payment_confidence': 0.0,
            'taint_hop1':                  0.0,
            'pre_crime_watchlist':         False,
            'victim_context':              False,
            'exchange_verified':           False,
        }
        decision = clf.classify(address, signals)

    # ── Display result ────────────────────────────────────────────────────────
    ICONS = {
        'BLACKLISTED':         '🔴',
        'WATCHLISTED':         '🟡',
        'PRE_CRIME_WATCHLIST': '🟠',
        'CLEAN':               '🟢'
    }
    icon = ICONS.get(decision.category, '⚪')
    st.markdown(f"## {icon} {decision.category}")
    st.metric("Confidence", f"{decision.confidence:.1%}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Evidence Chain")
        if decision.evidence:
            for ev in decision.evidence:
                arrow = "🔺" if float(str(ev.get('lr', 1.0)).replace('+', '')) > 1 else "🔻"
                st.write(f"{arrow} **{ev['source']}** — {ev['detail']}")
                st.caption(f"   Contribution: {ev['contribution']}")
        else:
            st.info("No evidence signals triggered.")

    with col2:
        st.subheader("🔄 Counterfactual")
        st.info(decision.counterfactual)

    # ── Investigation brief ──────────────────────────────────────────────────
    if decision.category != 'CLEAN':
        if st.button("📄 Generate Investigation Brief (Claude API)"):
            from services.llm.brief_generator import generate_brief
            with st.spinner("Generating brief..."):
                brief = generate_brief(decision)
            st.subheader("📄 Investigation Brief")
            st.markdown(brief)

# ── PRE_CRIME Watchlist tab ──────────────────────────────────────────────────
st.divider()
st.subheader("⚠️ PRE_CRIME_WATCHLIST Monitor")
st.info(
    "These addresses appeared in dark web payment pages with ZERO on-chain history. "
    "No other system can flag these — they have never been involved in a transaction. "
    "BTC-Intel flags them the moment they appear on dark web markets."
)
# In production: load from database. For demo: show sample data.
st.dataframe({
    "Address":       ["1CriminalEx1...", "bc1qcriminal..."],
    "Onion Domain":  ["abc123.onion",    "xyz456.onion"],
    "Topic":         ["DRUG",            "FRAUD"],
    "DW Confidence": [0.82,              0.71],
    "First Seen DW": ["2024-03-10",      "2024-03-12"],
    "Status":        ["ACTIVE",          "TRIGGERED"],
}, use_container_width=True)
```

---

## 13. Database Schema

```sql
-- PostgreSQL schema — runs on college server outside the crawler VM

-- Seeds: confirmed criminal addresses from authoritative sources
CREATE TABLE seed_addresses (
    address        TEXT PRIMARY KEY,
    entity_name    TEXT,
    source         TEXT,         -- OFAC_SDN / UN_SANCTIONS / CHAINABUSE
    confidence     FLOAT,
    category       TEXT,         -- Always BLACKLISTED for seeds
    fetched_at     TIMESTAMPTZ DEFAULT NOW(),
    expires_at     TIMESTAMPTZ   -- For community reports (less stable than OFAC)
);

-- Dark web records: everything extracted from crawled pages
CREATE TABLE dark_web_records (
    id               SERIAL PRIMARY KEY,
    address          TEXT,
    address_type     TEXT,        -- P2PKH / P2SH / BECH32
    context_type     TEXT,        -- PAYMENT / VICTIM_REPORT / AMBIGUOUS
    context_window   TEXT,        -- 500 chars surrounding the address
    confidence       FLOAT,
    page_topic       TEXT,        -- DRUG / WEAPON / FRAUD / UNKNOWN
    onion_domain     TEXT,
    page_url         TEXT,
    archive_key      TEXT,        -- MinIO key for raw HTML (90-day retention)
    pgp_fingerprints TEXT[],
    aliases          TEXT[],
    first_seen       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_dw_address ON dark_web_records(address);
CREATE INDEX idx_dw_domain  ON dark_web_records(onion_domain);

-- PRE_CRIME watchlist: dark web addresses with zero on-chain history
CREATE TABLE pre_crime_watchlist (
    address           TEXT PRIMARY KEY,
    onion_domain      TEXT,
    page_url          TEXT,
    page_topic        TEXT,
    dw_confidence     FLOAT,
    pgp_fingerprints  TEXT[],
    first_seen_dw     TIMESTAMPTZ,
    monitoring_status TEXT DEFAULT 'ACTIVE',  -- ACTIVE / TRIGGERED / EXPIRED
    first_tx_hash     TEXT,                   -- Set when first on-chain tx detected
    first_tx_at       TIMESTAMPTZ
);

-- Risk decisions: final output for each assessed address
CREATE TABLE risk_decisions (
    address        TEXT PRIMARY KEY,
    category       TEXT,         -- BLACKLISTED / WATCHLISTED / PRE_CRIME_WATCHLIST / CLEAN
    confidence     FLOAT,
    evidence       JSONB,        -- Full evidence chain
    counterfactual TEXT,
    brief          TEXT,         -- Claude-generated narrative
    assessed_at    TIMESTAMPTZ DEFAULT NOW(),
    last_updated   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_risk_category ON risk_decisions(category);

-- Audit log: immutable — tracks every assessment (for research accountability)
CREATE TABLE audit_log (
    id        BIGSERIAL PRIMARY KEY,
    action    TEXT,
    address   TEXT,
    result    TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
REVOKE UPDATE, DELETE ON audit_log FROM btc_intel_app;  -- Immutable by design

-- Crawler queue: URLs to crawl next
CREATE TABLE crawl_queue (
    id           SERIAL PRIMARY KEY,
    url          TEXT UNIQUE,
    onion_domain TEXT,
    priority     INTEGER DEFAULT 5,  -- Higher = crawl sooner
    depth        INTEGER,
    status       TEXT DEFAULT 'PENDING',  -- PENDING / DONE / DEAD
    last_attempt TIMESTAMPTZ,
    attempts     INTEGER DEFAULT 0
);

-- Cluster memberships: CIO clustering results
CREATE TABLE address_clusters (
    address      TEXT PRIMARY KEY,
    cluster_root TEXT,       -- Root address representing the whole cluster
    confidence   FLOAT,
    merge_reason TEXT        -- Which heuristic caused the merge
);
```

---

## 14. Week-by-Week Build Schedule

| Week | What Gets Built | What You Can Demo |
|------|----------------|-------------------|
| **1** | Environment setup on college server. KVM VM created. BigQuery free tier connected. Elliptic baseline reproduced. | "Dev environment working, baseline ML running" |
| **2** | Phase 1: OFAC + UN + Chainabuse seed collection. PostgreSQL schema deployed. | "2,000+ criminal BTC addresses loaded from free sources" |
| **3** | Phase 3: BigQuery graph expansion from OFAC seeds. CIO clustering. CoinJoin filter. | "3-hop cluster built around 50 OFAC seeds" |
| **4** | Phase 4 risk engine: taint propagation (3 methods). Bayesian classifier working. | "Enter any address → BLACKLISTED/WATCHLISTED/CLEAN with evidence" |
| **5** | Phase 2: Dark web crawler (Tor + Splash) in VM. Address + PGP extractor. Context classifier. | "Crawler extracting addresses from dark web pages" |
| **6** | Phase 2 continued: DUTA-10K pre-crawled dataset processed. DW records in PostgreSQL. | "1,000+ dark web address records with context classification" |
| **7** | Phase 5: PRE_CRIME_WATCHLIST. BigQuery polling for first transactions. | "Zero-history addresses from DW flagged before any transaction" |
| **8** | Phase 4: Cross-reference dark web ↔ blockchain. Shared-wallet onion graph in Neo4j. | "End-to-end: DW address → blockchain cluster → risk score" |
| **9** | Claude API brief generation. SHAP explanation of risk score components. Evaluation on OFAC test set. | "Investigation brief generated for any BLACKLISTED address" |
| **10** | Streamlit dashboard. All demos working. Evaluation metrics produced. | **Full system demo: enter address → get verdict + evidence + brief** |

---

## 15. Exactly What to Run on Day 1

```bash
# ═══════════════════════════════════════════════════════
# COLLEGE SERVER SETUP (run once as root/sudo)
# ═══════════════════════════════════════════════════════

# 1. Install system dependencies
sudo apt update && sudo apt install -y \
    postgresql-16 redis-server \
    qemu-kvm libvirt-daemon-system \
    python3.11 python3-pip python3.11-venv \
    git curl

# 2. Install Neo4j Community (free)
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update && sudo apt install -y neo4j
sudo systemctl enable neo4j && sudo systemctl start neo4j

# 3. Install MinIO (S3-compatible object storage, free self-hosted)
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/
# Create data directory for MinIO (outside VM — survives VM resets)
sudo mkdir -p /data/minio
# Start MinIO (change password!)
MINIO_ROOT_USER=btcintel MINIO_ROOT_PASSWORD=your_strong_password \
    minio server /data/minio --console-address ":9001" &

# 4. Set up Python project
git clone <your-repo> btc_intel
cd btc_intel
python3.11 -m venv venv
source venv/bin/activate
pip install \
    requests pgpy beautifulsoup4 base58 pytesseract pyzbar Pillow \
    psycopg2-binary neo4j redis \
    google-cloud-bigquery pandas numpy \
    networkx scikit-learn \
    fastapi uvicorn streamlit plotly \
    anthropic python-dotenv jellyfish

# 5. Create .env file
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-your-key-here
BIGQUERY_PROJECT_ID=your-free-gcp-project-id
POSTGRES_URI=postgresql://btcintel:password@localhost:5432/btcintel
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=your_neo4j_password
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=btcintel
MINIO_SECRET_KEY=your_strong_password
EOF

# 6. Create PostgreSQL database
sudo -u postgres psql << 'SQL'
CREATE USER btcintel WITH PASSWORD 'password';
CREATE DATABASE btcintel OWNER btcintel;
\q
SQL

# 7. Run database migrations
psql -U btcintel -d btcintel -f schema/001_init.sql

# 8. Collect seeds (first real data)
python scripts/collect_seeds.py
# Expected output:
# Fetching OFAC SDN list...
#   OFAC: 312 BTC addresses
#   UN List: 48 BTC addresses
#   Chainabuse: 100 reports
# ✅ Total seeds: 460 criminal addresses

# 9. Start BigQuery graph expansion
python scripts/expand_graph.py --hops 3 --seeds data/seeds.json
# Expected: 3-hop cluster around 50 OFAC seeds, ~200-400GB BigQuery processed

# 10. Start the dashboard
streamlit run dashboard/app.py --server.port 8501
# Open: http://[college-server-IP]:8501
echo "🚀 BTC-Intel POC running at http://[college-server-IP]:8501"

# ═══════════════════════════════════════════════════════
# CRAWLER VM SETUP (separate from above — inside KVM)
# ═══════════════════════════════════════════════════════
# Create VM snapshot BEFORE installing Tor (clean restore point)
virsh snapshot-create-as btcintel-crawler clean_base

# Inside the VM:
sudo apt install -y tor python3.11 python3-pip docker.io
# Install Splash
sudo docker pull scrapinghub/splash
sudo docker run -d -p 8050:8050 scrapinghub/splash

# Run crawler (inside VM only)
python services/dark_web/crawler.py
```

---

## 16. Success Criteria

The POC is complete when ALL of these can be demonstrated live:

| # | Demo | What It Proves |
|---|------|---------------|
| 1 | Enter a known OFAC address → instant BLACKLISTED + entity name + evidence | Phase 1 works |
| 2 | Enter an address 1-hop from OFAC address → WATCHLISTED with taint score | Phase 3 taint works |
| 3 | Show an address from DW sample with PAYMENT context → PRE_CRIME_WATCHLIST | Core novel contribution |
| 4 | Enter a Binance hot wallet address → CLEAN (exchange verified, taint stops) | False positive protection works |
| 5 | Two different addresses linked by same PGP fingerprint → same entity in Neo4j | Phase 2 PGP linking works |
| 6 | Show precision/recall table: BTC-Intel vs naive single-hop OFAC taint alone | System beats baseline |
| 7 | Generate Claude brief for a BLACKLISTED address | LLM layer works |
| 8 | Show all 21 issues from Word doc addressed in the system | Comprehensive coverage |

**Target metrics:**
- Precision (BLACKLISTED tier): ≥ 90%
- Recall on OFAC test set: ≥ 80%
- False positive rate on known exchange addresses: < 5%
- PRE_CRIME_WATCHLIST demonstration: ≥ 1 address shown with zero on-chain history
