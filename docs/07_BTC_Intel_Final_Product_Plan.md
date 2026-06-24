# BTC-Intel: Final Product Implementation Plan
## From Working POC → Production-Grade Bitcoin Wallet Intelligence
### College Server Setup · Every POC Component Made Complete · No ClearTrace

> **What this document is:** How to take every piece of the POC and make it
> production-grade. Same core goal: "Is this Bitcoin wallet criminal?"
> Same 5-phase architecture. Everything here is about making each POC component
> better, faster, more accurate, and legally defensible at scale.
>
> **ClearTrace is NOT here.** It was removed. The only reference to ClearTrace
> concepts in this system is the grounded LLM prompting design (their idea of
> "Claude narrates computed findings, never invents them") — which we use for
> the investigation brief generator. Nothing else from ClearTrace is needed.

---

## Table of Contents

**Part 1 — Your Setup Questions Answered in Full**
1. [VM Safety: Full Production Setup on College Server](#1-vm-safety-full-production-setup)
2. [HTML Storage: Where It Lives and How Long](#2-html-storage)
3. [College Server: What to Install, How to Configure](#3-college-server-setup)

**Part 2 — Every POC Component Made Production-Grade**
4. [Phase 1 → Production: Seed Collection](#4-phase-1--production-seed-collection)
5. [Phase 2 → Production: Dark Web Crawler](#5-phase-2--production-dark-web-crawler)
6. [Phase 3 → Production: Blockchain Graph](#6-phase-3--production-blockchain-graph)
7. [Phase 4 → Production: Cross-Reference + Risk Engine](#7-phase-4--production-risk-engine)
8. [Phase 5 → Production: PRE_CRIME Watchlist](#8-phase-5--production-pre_crime-watchlist)

**Part 3 — Production-Only Features**
9. [Calibrated Likelihood Ratios (Not Guesses)](#9-calibrated-likelihood-ratios)
10. [Analyst Feedback Loop](#10-analyst-feedback-loop)
11. [Model Drift Detection + Auto-Retrain](#11-model-drift-detection)
12. [Production API Layer](#12-production-api-layer)
13. [Audit Log and Legal Compliance](#13-audit-log-and-legal-compliance)
14. [Production Dashboard](#14-production-dashboard)
15. [All 21 Issues: POC vs Final Product Comparison](#15-all-21-issues-poc-vs-final-product)
16. [16-Week Production Roadmap](#16-16-week-production-roadmap)

---

## Part 1 — Your Setup Questions Answered in Full

---

## 1. VM Safety: Full Production Setup

### Why a VM Is Mandatory (Not Optional)

The college server is your production machine. It hosts your database, your API,
your dashboard. You cannot afford to compromise it.

Dark web pages can contain:
- JavaScript exploits targeting the browser/headless renderer
- Malformed data designed to crash Python parsers
- Auto-download triggers for malicious files
- Fingerprinting scripts that attempt to identify your real IP

**The VM is a blast shield.** If a malicious page exploits the crawler, it damages
the VM — not the server running your database and API.

Think of it like this:
```
College Server (your valuable production environment)
    └── KVM Hypervisor (the wall between VM and server)
            └── Crawler VM (expendable — can be destroyed and restored in 2 minutes)
                    └── Tor daemon (all Tor traffic stays here)
                    └── Splash renderer (renders JavaScript here, not on the server)
                    └── Python crawler (runs here, writes only to MinIO via network)
```

The VM can be wiped and restored from a snapshot in under 2 minutes.
The server is never directly exposed to dark web content.

### Production VM Configuration

```bash
# ── On the college server (host machine) ────────────────────────────────────

# Install KVM (free, open-source hypervisor — the industry standard)
sudo apt install -y qemu-kvm libvirt-daemon-system virtinst bridge-utils

# Create the crawler VM
# RAM: 4GB (enough for Tor + Splash + Python)
# Disk: 50GB (temp files only — all real data goes to MinIO on host)
# CPU: 2 cores
virt-install \
  --name btcintel-crawler \
  --ram 4096 \
  --vcpus 2 \
  --disk path=/var/lib/libvirt/images/btcintel-crawler.qcow2,size=50 \
  --os-variant ubuntu22.04 \
  --network network=default \
  --graphics none \
  --console pty,target_type=serial \
  --location 'http://archive.ubuntu.com/ubuntu/dists/jammy/main/installer-amd64/'

# Take a clean snapshot BEFORE installing anything
# (This is your restore point if the VM is ever compromised)
virsh snapshot-create-as btcintel-crawler clean_base_$(date +%Y%m%d)

# ── Inside the crawler VM (SSH in) ──────────────────────────────────────────
# Install Tor
sudo apt install -y tor
# Verify Tor is routing correctly
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
# Expected: {"IsTor":true,"IP":"..."}

# Install Splash (JavaScript renderer that routes through Tor)
sudo apt install -y docker.io
sudo docker run -d \
  --name splash \
  -p 8050:8050 \
  scrapinghub/splash \
  --max-timeout 90 \
  --slots 4          # 4 concurrent renders
# Note: configure Splash to use Tor SOCKS5 in production

# Take a post-install snapshot (before any crawling begins)
# Run this on the HOST:
virsh snapshot-create-as btcintel-crawler post_install_$(date +%Y%m%d)
```

### Network Isolation (Production)

In production, the crawler VM should be on a network segment that can ONLY
reach the MinIO port on the college server — nothing else.

```bash
# On the college server, create an isolated network for the crawler VM
# The VM can reach the server's MinIO (port 9000) but nothing else on the internet
# This prevents the crawler from being used as a pivot point if compromised

# Create isolated bridge network
sudo brctl addbr btcintel-isolated
sudo ip addr add 192.168.100.1/24 dev btcintel-isolated
sudo ip link set btcintel-isolated up

# Firewall rules: VM can only reach MinIO on the host (192.168.100.1:9000)
# and Tor exits (Tor handles its own routing)
sudo iptables -A FORWARD -i btcintel-isolated -d 192.168.100.1 -p tcp --dport 9000 -j ACCEPT
sudo iptables -A FORWARD -i btcintel-isolated -j DROP
```

### Daily Crawler Routine (Production)

```bash
# Run this script at the start of each crawl session
# It snapshots the VM, runs the crawl, then verifies the VM is clean

#!/bin/bash
# scripts/daily_crawl.sh

echo "Taking pre-crawl snapshot..."
virsh snapshot-create-as btcintel-crawler "pre_crawl_$(date +%Y%m%d_%H%M)"

echo "Starting crawler (inside VM)..."
ssh crawler-vm "cd /opt/btcintel && python crawler.py --max-pages 3000"

echo "Verifying VM integrity..."
# Check that no unexpected processes are running
ssh crawler-vm "ps aux | grep -v 'python\|tor\|splash\|sshd\|init'" 

echo "Crawl session complete. VM remains snapshotted for forensics if needed."
```

---

## 2. HTML Storage

### Where It Goes and Why

```
Dark web page fetched by crawler (inside VM)
    ↓
[Never saved to VM disk permanently]
    ↓
Gzip compressed (reduces 10MB HTML to ~1MB)
    ↓
SHA-256 hash computed (deduplication key + tamper detection)
    ↓
Written to MinIO on college server via local network
    Path: btc-intel-pages/pages/YYYY/MM/DD/<sha256>.html.gz
    ↓
Only the extracted metadata (addresses, context, PGP keys) written to PostgreSQL
```

### MinIO Storage Layout

```
MinIO Bucket: btc-intel-pages
├── pages/
│   ├── 2024/03/15/
│   │   ├── a1b2c3d4...sha256.html.gz   (raw HTML, gzip compressed)
│   │   ├── e5f6g7h8...sha256.html.gz
│   │   └── ...
│   └── 2024/03/16/
│       └── ...
└── metadata/
    └── (archive index — kept permanently)

Retention policy:
  pages/      → 90-day auto-delete (MinIO lifecycle policy)
  metadata/   → kept forever (it's tiny: just keys and hashes)
```

### Why 90-Day Deletion of Raw HTML

Three reasons:

**1. Legal (GDPR Article 5(1)(e)):** Data minimisation principle — don't keep data
longer than necessary. Raw HTML may contain personal data (PGP UIDs, usernames).
After extracting what we need, the raw HTML has no research value.

**2. Storage (Issue #19 fix):** At 3,000 pages/day × 1MB compressed = 3GB/day.
Over 90 days = 270GB. This is manageable on a college server.
If you keep forever: 270GB × 4 years = 1TB of raw HTML. Not sustainable.

**3. Safety:** In the unlikely event of a server compromise, old raw dark web HTML
could be a liability. 90-day rolling window limits exposure.

### Setting Up MinIO Lifecycle Policy

```bash
# On college server — configure 90-day auto-delete for raw pages
# Uses MinIO Client (mc)

# Install mc
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc && sudo mv mc /usr/local/bin/

# Connect to local MinIO
mc alias set local http://localhost:9000 btcintel your_strong_password

# Create bucket
mc mb local/btc-intel-pages

# Set lifecycle: delete pages/ objects after 90 days
mc ilm rule add \
  --expire-days 90 \
  --prefix "pages/" \
  local/btc-intel-pages

# Verify
mc ilm rule ls local/btc-intel-pages
# Expected: Rule for pages/ expires in 90 days
```

### Is the Data Safe?

Yes, for three reasons:

**1. It never leaves campus:** MinIO runs on the college server. No data goes to AWS,
Google, or any cloud provider. The only external connection is the BigQuery queries
(which send Bitcoin addresses to Google for querying — these are already public
blockchain data, not dark web content).

**2. The raw HTML stays in one controlled location:** MinIO access requires credentials.
Only the crawler VM (which has MinIO credentials in its config) and the extraction
service (which runs on the server) can read it.

**3. Encryption at rest:** MinIO supports AES-256 encryption.

```bash
# Enable encryption for the bucket
mc encrypt set sse-s3 local/btc-intel-pages
```

---

## 3. College Server Setup

### What to Install (One-Time Setup)

```
College Server Hardware Recommended for Final Product:
CPU:  8 cores (4 for DB/API, 2 for Bitcoin node, 2 for VM hypervisor)
RAM:  32GB (16GB for Neo4j + PostgreSQL, 8GB for VM, 8GB for services)
SSD:  2TB NVMe (620GB Bitcoin full node + 500GB Neo4j + 500GB PostgreSQL + overhead)
NET:  Campus LAN (100Mbps is fine — blockchain sync uses internet initially)
```

```bash
# ── Complete college server setup (Ubuntu 22.04 LTS) ───────────────────────

# System updates
sudo apt update && sudo apt upgrade -y

# ── Databases ─────────────────────────────────────────────────────────────
# PostgreSQL 16
sudo apt install -y postgresql-16 postgresql-client-16
sudo -u postgres psql -c "CREATE USER btcintel WITH PASSWORD 'your_strong_password';"
sudo -u postgres psql -c "CREATE DATABASE btcintel OWNER btcintel;"

# Neo4j Community 5.x (free)
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update && sudo apt install -y neo4j
# Configure Neo4j heap (allocate 8GB for production)
sudo sed -i 's/#server.memory.heap.initial_size=/server.memory.heap.initial_size=4G/' \
    /etc/neo4j/neo4j.conf
sudo sed -i 's/#server.memory.heap.max_size=/server.memory.heap.max_size=8G/' \
    /etc/neo4j/neo4j.conf
sudo systemctl enable neo4j && sudo systemctl start neo4j

# Redis (caching)
sudo apt install -y redis-server
sudo systemctl enable redis && sudo systemctl start redis

# ── Object Storage ─────────────────────────────────────────────────────────
# MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio && sudo mv minio /usr/local/bin/
sudo mkdir -p /data/minio
# Create systemd service for MinIO
sudo tee /etc/systemd/system/minio.service << 'EOF'
[Unit]
Description=MinIO Object Storage
After=network.target

[Service]
User=minio-user
ExecStart=/usr/local/bin/minio server /data/minio --console-address ":9001"
Environment=MINIO_ROOT_USER=btcintel
Environment=MINIO_ROOT_PASSWORD=your_strong_password
Restart=always

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl enable minio && sudo systemctl start minio

# ── Python Environment ─────────────────────────────────────────────────────
sudo apt install -y python3.11 python3.11-venv python3.11-dev
cd /opt && sudo git clone <your-repo> btcintel
cd btcintel && python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# ── Bitcoin Full Node (Final Product — takes 7 days to sync) ──────────────
# For POC: skip this step (use BigQuery free tier instead)
# For Final Product: install Bitcoin Core
sudo add-apt-repository ppa:bitcoin/bitcoin
sudo apt update && sudo apt install -y bitcoind
# Configure bitcoin.conf for ElectrumX
cat > /home/$(whoami)/.bitcoin/bitcoin.conf << 'EOF'
txindex=1
server=1
rpcuser=btcintel
rpcpassword=your_rpc_password
zmqpubrawblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28333
# Start sync (will take 5-7 days, 620GB download)
EOF
bitcoind -daemon
# Track sync progress:
bitcoin-cli getblockchaininfo | grep verificationprogress

# ── ElectrumX (address indexer for Bitcoin Core) ──────────────────────────
pip install aiohttp pylru plyvel
git clone https://github.com/spesmilo/electrumx.git /opt/electrumx
# Configure and start ElectrumX after Bitcoin Core is synced

# ── KVM for Crawler VM ────────────────────────────────────────────────────
sudo apt install -y qemu-kvm libvirt-daemon-system virtinst bridge-utils
# (Create crawler VM as described in Section 1)

# ── Firewall Configuration ────────────────────────────────────────────────
sudo ufw enable
sudo ufw allow from <campus_subnet> to any port 8501  # Streamlit dashboard
sudo ufw allow from <campus_subnet> to any port 8000  # FastAPI
sudo ufw allow from 192.168.100.0/24 to any port 9000  # MinIO (crawler VM only)
sudo ufw deny 7687   # Neo4j: internal only (no external access)
sudo ufw deny 5432   # PostgreSQL: internal only
sudo ufw deny 6379   # Redis: internal only
```

---

## Part 2 — Every POC Component Made Production-Grade

---

## 4. Phase 1 → Production: Seed Collection

### What the POC Did
- Downloaded OFAC and UN lists manually
- Static seed set loaded once at startup
- No detection of new additions

### What Production Adds

**Auto-refresh with change detection:**

The problem with loading OFAC once: OFAC adds new addresses irregularly. During
active enforcement (Lazarus Group, Garantex seizures), OFAC updates the same day.
If you loaded the list at 8am and OFAC added 50 addresses at 2pm, you'll miss those
addresses for the rest of the day.

**Solution: HTTP ETag checking every 4 hours**

```python
# services/seed_collector/production_collector.py

import requests, hashlib, json
from datetime import datetime
import psycopg2

class AutoRefreshingSeedCollector:
    """
    Checks OFAC and UN lists every 4 hours using HTTP ETags.
    ETag = a server-provided hash of the file's current content.
    If the ETag hasn't changed, the file hasn't changed → skip download.
    If the ETag changed → download and process the new file.

    This means: most checks download nothing (just a tiny HEAD request).
    But when OFAC adds new addresses, we pick them up within 4 hours.
    Compare to POC: POC might go days without picking up new OFAC additions.
    """

    OFAC_URL = "https://www.treasury.gov/ofac/downloads/sdn.xml"
    UN_URL   = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"

    def __init__(self, db_conn):
        self.db = db_conn
        self._etags = {}  # Track last seen ETag per URL

    def check_and_update(self, url: str, source_name: str) -> int:
        """
        Returns number of new addresses added (0 if no update).
        """
        # Check if file has changed via ETag
        head = requests.head(url, timeout=30)
        current_etag = head.headers.get('ETag', head.headers.get('Last-Modified', ''))

        if self._etags.get(url) == current_etag and current_etag:
            return 0  # No change — skip download entirely

        # File changed — download and process
        print(f"Updating {source_name}...")
        resp = requests.get(url, timeout=120)
        new_addresses = self._parse_xml(resp.content, source_name)

        # Compare with current database to find truly new addresses
        existing = set(row[0] for row in
                       self.db.execute("SELECT address FROM seed_addresses").fetchall())
        truly_new = [a for a in new_addresses if a['address'] not in existing]

        if truly_new:
            self.db.executemany("""
                INSERT INTO seed_addresses (address, entity_name, source, confidence, fetched_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (address) DO NOTHING
            """, [(a['address'], a['entity'], a['source'], a['confidence'],
                   datetime.utcnow()) for a in truly_new])
            self.db.commit()
            print(f"  {source_name}: {len(truly_new)} new addresses added")

            # IMPORTANT: Re-run risk assessment for all addresses connected to new seeds
            # (An address that was WATCHLISTED may now be BLACKLISTED if a new OFAC seed
            #  is 1 hop away from it)
            self._trigger_downstream_reassessment(truly_new)

        self._etags[url] = current_etag
        return len(truly_new)

    def _trigger_downstream_reassessment(self, new_seeds: list[dict]):
        """
        When new OFAC seeds arrive, find all addresses within 3 hops in Neo4j
        and queue them for re-evaluation.
        This is what keeps the database current — new sanctions propagate
        outward through the graph automatically.
        """
        for seed in new_seeds:
            # Add to reassessment queue (processed by the risk engine background job)
            self.db.execute("""
                INSERT INTO reassessment_queue (address, reason, queued_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT DO NOTHING
            """, (seed['address'], f"NEW_SEED_{seed['source']}"))
```

**Extended source list for production:**

POC uses: OFAC + UN + Chainabuse + MistTrack (100/day free)

Production adds:
```python
PRODUCTION_SOURCES = {
    'OFAC_SDN':      {'url': 'treasury.gov/ofac/downloads/sdn.xml',
                       'cost': 'FREE', 'confidence': 1.0, 'refresh_hours': 4},
    'UN_SANCTIONS':  {'url': 'scsanctions.un.org/resources/xml/en/consolidated.xml',
                       'cost': 'FREE', 'confidence': 1.0, 'refresh_hours': 24},
    'CHAINABUSE':    {'url': 'api.chainabuse.com/v0/reports',
                       'cost': 'FREE_100/day', 'confidence': 0.6, 'refresh_hours': 24},
    'MISTTRACK':     {'url': 'misttrack.io/api',
                       'cost': 'FREE_100/day', 'confidence': 0.8, 'refresh_hours': 24},
    'CRYPTOSCAMDB':  {'url': 'github.com/cryptoscamdb',
                       'cost': 'FREE_OPEN_SOURCE', 'confidence': 0.7, 'refresh_hours': 24},
    'SLOWMIST':      {'url': 'github.com/slowmist/blockchain-blacklist',
                       'cost': 'FREE_OPEN_SOURCE', 'confidence': 0.75, 'refresh_hours': 24},
    'CDA':           {'url': 'cryptodefendersalliance.com',
                       'cost': 'FREE_OPEN_SOURCE', 'confidence': 0.7, 'refresh_hours': 12},
    # Future paid sources (when budget allows):
    # 'CHAINALYSIS_SANCTIONS': free sanctions API (contact for access)
    # 'TRM_LABS':              paid, best for law enforcement integration
}
```

---

## 5. Phase 2 → Production: Dark Web Crawler

### What the POC Did
- Single set of 6 Tor instances
- Pre-crawled DUTA-10K dataset for testing
- No recrawl scheduling
- Manual queue management

### What Production Adds

**Problem 1 — Freshness (Issue #7)**

Criminal markets change payment addresses frequently (some change daily to evade
detection). A payment address crawled 2 weeks ago may already be replaced.

**Solution: Domain-specific recrawl schedule**

```python
# services/dark_web/recrawl_scheduler.py

RECRAWL_SCHEDULE = {
    'ACTIVE_MARKET':    3,   # days — markets change addresses frequently
    'FORUM':            7,   # days — forums change less often
    'PASTE_SITE':       1,   # days — paste sites are very ephemeral
    'STATIC_INFO':      14,  # days — static information sites rarely change
    'DEAD':             30,  # days — retry dead sites once a month
}

def get_domains_needing_recrawl(db_conn) -> list[dict]:
    """
    Returns domains whose content may have changed since last crawl.
    Prioritizes high-value domains (more wallet addresses found historically).
    """
    return db_conn.execute("""
        SELECT domain, domain_type, last_crawled_at,
               wallet_addresses_found_total,
               EXTRACT(EPOCH FROM (NOW() - last_crawled_at)) / 86400 AS days_since_crawl
        FROM crawled_domains
        WHERE EXTRACT(EPOCH FROM (NOW() - last_crawled_at)) / 86400 >=
              CASE domain_type
                WHEN 'ACTIVE_MARKET' THEN 3
                WHEN 'FORUM' THEN 7
                WHEN 'PASTE_SITE' THEN 1
                ELSE 14
              END
        ORDER BY wallet_addresses_found_total DESC  -- High-value domains first
        LIMIT 1000
    """).fetchall()
```

**Problem 2 — Context Improvement (Issue #18 — Attribution Risk)**

The POC classifies context with a simple keyword counter.
Production adds sentence-boundary context windows:

```python
# services/dark_web/context_extractor.py

from nltk.tokenize import sent_tokenize

def get_payment_context_window(full_text: str,
                                addr_position: int) -> tuple[str, float]:
    """
    POC used fixed 500-char window.
    Problem: if the address is at the top of a long page, the payment context
    sentence might be 600 chars away — missed by fixed window.

    Production uses sentence boundaries:
    1. Find the sentence containing the address
    2. Expand to the 3 nearest sentences in both directions
    3. Score based on payment keywords in those sentences

    Example:
    Page text: "... Welcome to DarkShop. We sell [long description] ...
                Payment: Send exactly 0.05 BTC to 1ABC... within 24 hours. ..."

    Fixed window (500 chars back): might miss "Payment: Send exactly..."
    Sentence-boundary window: catches "Payment: Send exactly 0.05 BTC to 1ABC..."
    correctly as PAYMENT context with high confidence.
    """
    # Find the sentence containing the address
    sentences = sent_tokenize(full_text)
    addr_sentence_idx = None
    pos = 0
    for i, sent in enumerate(sentences):
        if pos <= addr_position <= pos + len(sent):
            addr_sentence_idx = i
            break
        pos += len(sent) + 1

    if addr_sentence_idx is None:
        # Fallback to fixed window
        start = max(0, addr_position - 250)
        end   = min(len(full_text), addr_position + 250)
        return full_text[start:end], 0.30

    # Take 3 sentences before and after
    window_start = max(0, addr_sentence_idx - 3)
    window_end   = min(len(sentences), addr_sentence_idx + 4)
    context = ' '.join(sentences[window_start:window_end])

    # Score the context
    ctx_l = context.lower()
    VICTIM_KWS  = ['scam', 'scammer', 'stolen', 'fraud', 'victim', 'warning']
    PAYMENT_KWS = ['send', 'pay', 'payment', 'btc', 'bitcoin', 'deposit',
                   'transfer', 'price', 'address', 'wallet', 'escrow']
    if any(kw in ctx_l for kw in VICTIM_KWS):
        return context, 0.05   # Victim context — low confidence

    hits = sum(1 for kw in PAYMENT_KWS if kw in ctx_l)
    confidence = min(0.95, 0.40 + 0.08 * hits)
    return context, confidence
```

**Problem 3 — Image-Based Addresses (Issue #14)**

Some dark web markets post Bitcoin addresses as images (to defeat text-based crawlers).

```python
# services/dark_web/image_ocr.py

import pytesseract
from PIL import Image
from io import BytesIO
import requests, re

BTC_RE = re.compile(
    r'\b(1[a-km-zA-HJ-NP-Z1-9]{25,34}|3[a-km-zA-HJ-NP-Z1-9]{25,34}|'
    r'bc1[qp][a-z0-9]{6,87})\b',
    re.IGNORECASE
)

def extract_addresses_from_image(img_url: str,
                                   tor_proxies: dict) -> list[str]:
    """
    Download an image from a dark web page and OCR it for Bitcoin addresses.

    Only applied to images < 2MB (larger = unlikely to contain text addresses,
    more likely to be product photos — waste of compute).

    QR code detection also runs (pyzbar library) — some markets post QR codes
    of their payment address instead of the text address.
    """
    try:
        resp = requests.get(img_url, proxies=tor_proxies, timeout=30)
        if len(resp.content) > 2 * 1024 * 1024:  # 2MB limit
            return []

        img = Image.open(BytesIO(resp.content))

        # Method 1: OCR text
        ocr_text = pytesseract.image_to_string(img)
        addresses = BTC_RE.findall(ocr_text)

        # Method 2: QR code detection
        try:
            from pyzbar.pyzbar import decode as decode_qr
            for qr in decode_qr(img):
                qr_data = qr.data.decode('utf-8')
                if qr_data.startswith('bitcoin:'):
                    qr_data = qr_data[8:].split('?')[0]  # Strip bitcoin: prefix
                addr_matches = BTC_RE.findall(qr_data)
                addresses.extend(addr_matches)
        except Exception:
            pass

        return list(set(addresses))

    except Exception:
        return []
```

---

## 6. Phase 3 → Production: Blockchain Graph

### What the POC Did
- BigQuery for all blockchain data (free tier)
- Batch processing only
- No real-time new block monitoring

### What Production Adds: Bitcoin Full Node + Real-Time Monitoring

**Why switch from BigQuery to your own Bitcoin node?**

Example: An exchange is about to process a withdrawal to address `1ABC...`
If you check BigQuery: data has a 24-hour lag. You see yesterday's transactions.
If you check your own Bitcoin node: data is 10 minutes old (one block).

For real-time deposit/withdrawal screening, you need your own node.

**Important:** For the POC, BigQuery is completely sufficient and free.
The full node is a Final Product upgrade — plan 7 days for initial sync.

```python
# services/blockchain/realtime_monitor.py

import zmq
import bitcoin.rpc as bitcoin_rpc
from datetime import datetime

class RealTimeBlockMonitor:
    """
    Listens to Bitcoin Core's ZMQ stream for every new transaction
    that appears in the mempool (before it's mined) AND every new block.

    Why ZMQ?
    ZMQ is a message queue. Bitcoin Core PUSHES notifications to us the
    moment something happens. We don't need to poll (ask repeatedly).

    Mempool monitoring: catches transactions the moment they are broadcast
    (before they are confirmed in a block). For exchange screening,
    this means you can flag a suspicious deposit before it confirms.

    Configuration (in bitcoin.conf on the college server):
    zmqpubrawblock=tcp://127.0.0.1:28332
    zmqpubrawtx=tcp://127.0.0.1:28333
    """

    def __init__(self, rpc_url: str = "http://btcintel:password@127.0.0.1:8332"):
        self.rpc      = bitcoin_rpc.RawProxy(service_url=rpc_url)
        self.zmq_ctx  = zmq.Context()

    def monitor_mempool(self, risk_engine, db_conn):
        """
        Watch for new transactions. When one involves a known-bad address,
        flag it immediately — before it confirms in a block.
        """
        sock = self.zmq_ctx.socket(zmq.SUB)
        sock.connect("tcp://127.0.0.1:28333")  # ZMQ raw tx stream
        sock.setsockopt_string(zmq.SUBSCRIBE, "rawtx")

        print("🔴 Monitoring Bitcoin mempool for suspicious addresses...")

        while True:
            _, raw_tx, _ = sock.recv_multipart()
            txid = raw_tx[:32].hex()

            try:
                tx = self.rpc.decoderawtransaction(raw_tx.hex())
            except Exception:
                continue

            # Check all addresses in this transaction
            all_addresses = []
            for inp in tx.get('vin', []):
                if inp.get('prevout', {}).get('scriptPubKey', {}).get('address'):
                    all_addresses.append(inp['prevout']['scriptPubKey']['address'])
            for out in tx.get('vout', []):
                if out.get('scriptPubKey', {}).get('address'):
                    all_addresses.append(out['scriptPubKey']['address'])

            for addr in all_addresses:
                # Fast path: check Redis cache first (sub-millisecond)
                cached = db_conn.redis.get(f"risk:{addr}")
                if cached:
                    decision = json.loads(cached)
                    if decision['category'] in ('BLACKLISTED', 'WATCHLISTED',
                                                 'PRE_CRIME_WATCHLIST'):
                        print(f"🚨 ALERT: {decision['category']} address {addr} "
                              f"in mempool tx {txid}")
                        self._emit_alert(addr, txid, decision, db_conn)
                else:
                    # Full risk assessment (runs async to not block monitoring)
                    # Queue for background processing
                    db_conn.execute(
                        "INSERT INTO screening_queue (address, txid, queued_at) "
                        "VALUES (%s, %s, NOW()) ON CONFLICT DO NOTHING",
                        (addr, txid)
                    )

    def _emit_alert(self, address: str, txid: str,
                     decision: dict, db_conn):
        """
        Alert when a suspicious address appears in the mempool.
        In production: sends webhook to registered systems.
        For college server demo: logs to PostgreSQL alerts table.
        """
        db_conn.execute("""
            INSERT INTO realtime_alerts
                (address, txid, category, confidence, alert_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (address, txid, decision['category'], decision['confidence']))
        db_conn.commit()
```

### CoinJoin Detection Improvement (Production)

The POC used a single CoinJoin detection rule.
Production uses protocol-specific detection:

```python
# services/blockchain/coinjoin_detector.py

def detect_coinjoin_protocol(tx: dict) -> tuple[bool, str]:
    """
    Identify which CoinJoin protocol (if any) this transaction uses.
    Different protocols need different handling.

    Wasabi 1.x: Fixed denomination outputs (0.1 BTC)
    Wasabi 2.0: >= 20 inputs, variable amounts
    Whirlpool:  Exactly 5 equal outputs
    JoinMarket: >= 3 inputs, maker-taker signature structure
    Generic:    40%+ equal outputs, 5+ outputs

    Why this matters:
    - Generic CoinJoin: skip CIO, do NOT propagate taint through it
    - Wasabi mixer: the coordinator address receives a fee — that fee address
      CAN be used as evidence of the coordinator's cluster
    - Whirlpool: 5 equal outputs means taint is evenly distributed (20% each)
    """
    inputs  = tx.get('vin', [])
    outputs = tx.get('vout', [])
    values  = [o.get('value', 0) for o in outputs]

    if not values:
        return False, 'NOT_COINJOIN'

    from collections import Counter
    most_common_count = Counter(values).most_common(1)[0][1]
    equal_fraction    = most_common_count / len(values)
    n_inputs          = len(inputs)
    n_outputs         = len(outputs)

    # Whirlpool: exactly 5 equal outputs
    if n_outputs == 5 and equal_fraction == 1.0:
        return True, 'WHIRLPOOL'

    # Wasabi 2.0: many inputs, variable amounts
    if n_inputs >= 20 and n_outputs >= 10:
        return True, 'WASABI_2'

    # Wasabi 1.x: 0.1 BTC denomination
    if any(abs(v - 0.1) < 0.0001 for v in values) and equal_fraction >= 0.30:
        return True, 'WASABI_1'

    # Generic CoinJoin
    if n_outputs >= 5 and equal_fraction >= 0.40:
        return True, 'GENERIC_COINJOIN'

    return False, 'NOT_COINJOIN'
```

---

## 7. Phase 4 → Production: Cross-Reference + Risk Engine

### What the POC Did
- Hardcoded likelihood ratios (expert guesses)
- No feedback mechanism to correct false positives
- Single static risk assessment per address

### What Production Adds: Calibrated LRs + Feedback Loop

**The most important production upgrade:** Calibrated likelihood ratios.

Here is why hardcoded LRs are dangerous in production:

```
POC guess: DARK_WEB_PAYMENT LR = 50
(meaning: 50x more likely to be criminal if found in DW payment context)

After measuring on real data:
Of 1,000 addresses found in DW payment contexts:
- 720 were later confirmed criminal (OFAC, law enforcement)
- 280 were either victims, test wallets, or legitimate

Measured LR = 720/1000 ÷ 0.001 (prior) = 720

POC guess was 50. Real value is 720. That's 14x wrong.
A wallet that scored 0.45 (WATCHLISTED) with the guessed LR
would score 0.94 (BLACKLISTED) with the calibrated LR.

Real consequence: wallets being under-flagged (missed criminals)
because the LR was set 14x too conservative.
```

See Section 9 for the full calibration methodology.

---

## 8. Phase 5 → Production: PRE_CRIME Watchlist

### What the POC Did
- BigQuery polling every 6 hours to detect first transactions
- Manual check of watchlist status

### What Production Adds: Real-Time Monitoring via ElectrumX

**The difference between polling and real-time:**

```
POC (BigQuery polling every 6 hours):
Day 1 10am: Address enters PRE_CRIME_WATCHLIST
Day 1 10am - 4pm: Address makes first criminal transaction
Day 1 4pm: BigQuery poll detects it (6 hours later)
→ 6 hours of missed detection window

Production (ElectrumX real-time subscription):
Day 1 10am: Address enters PRE_CRIME_WATCHLIST
             ElectrumX subscription created immediately
Day 1 11am: Address makes first transaction
             ElectrumX notifies BTC-Intel within seconds
→ Minutes of detection window (not 6 hours)
```

```python
# services/watchlist/electrumx_monitor.py

import asyncio
import aiohttp, json

class ElectrumXPreCrimeMonitor:
    """
    Subscribe to ElectrumX address notifications for all PRE_CRIME_WATCHLIST addresses.
    When any of them receives a first transaction, immediately trigger full risk assessment.

    ElectrumX is the address indexer that runs on top of Bitcoin Core.
    It provides an API to subscribe to any Bitcoin address and receive
    real-time notifications when that address is used in a transaction.

    Install ElectrumX: github.com/spesmilo/electrumx
    (Requires Bitcoin Core full node to be running and synced first)
    """

    ELECTRUMX_URL = "ws://localhost:50001"  # Local ElectrumX WebSocket

    async def monitor_watchlist(self, db_conn, risk_engine):
        """
        Load all ACTIVE watchlist entries and subscribe to each address.
        This runs as a long-running background task on the college server.
        """
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(self.ELECTRUMX_URL) as ws:

                # Load all active watchlist addresses
                watched = db_conn.execute(
                    "SELECT address FROM pre_crime_watchlist "
                    "WHERE monitoring_status = 'ACTIVE'"
                ).fetchall()

                # Subscribe to all of them
                for row in watched:
                    addr = row[0]
                    await ws.send_json({
                        "id": addr,
                        "method": "blockchain.address.subscribe",
                        "params": [addr]
                    })

                print(f"⚡ Subscribed to {len(watched)} PRE_CRIME_WATCHLIST addresses")

                # Listen for notifications
                async for msg in ws:
                    data = json.loads(msg.data)

                    # ElectrumX sends a notification when the status of a
                    # subscribed address changes (i.e., new transaction)
                    if data.get('method') == 'blockchain.address.subscribe':
                        address = data['params'][0]
                        status  = data['params'][1]

                        if status is not None:  # None = no history; not-None = has tx
                            print(f"🚨 PRE_CRIME → TRIGGERED: {address}")
                            await self._process_first_transaction(
                                address, db_conn, risk_engine
                            )

    async def _process_first_transaction(self, address: str,
                                          db_conn, risk_engine):
        """
        When a PRE_CRIME_WATCHLIST address gets its first transaction:
        1. Update status to TRIGGERED
        2. Run full risk engine with combined DW + blockchain evidence
        3. Store result in risk_decisions
        4. Emit alert if result is BLACKLISTED or WATCHLISTED
        """
        db_conn.execute("""
            UPDATE pre_crime_watchlist
            SET monitoring_status = 'TRIGGERED',
                first_tx_at = NOW()
            WHERE address = %s
        """, (address,))
        db_conn.commit()

        # Run full risk assessment now that on-chain data exists
        dw_record = db_conn.execute(
            "SELECT * FROM pre_crime_watchlist WHERE address = %s", (address,)
        ).fetchone()

        signals = {
            'dark_web_payment_confidence': dw_record['dw_confidence'],
            'pre_crime_watchlist':         False,  # Now has history
            'taint_hop1':                  0.0,    # Will be updated by graph expansion
        }

        decision = risk_engine.classify(address, signals)

        # Store decision
        db_conn.execute("""
            INSERT INTO risk_decisions (address, category, confidence, evidence,
                                        counterfactual, assessed_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            ON CONFLICT (address) DO UPDATE
            SET category = EXCLUDED.category,
                confidence = EXCLUDED.confidence,
                last_updated = NOW()
        """, (address, decision.category, decision.confidence,
              json.dumps(decision.evidence), decision.counterfactual))
        db_conn.commit()

        print(f"  Reclassified {address}: PRE_CRIME → {decision.category} "
              f"(confidence: {decision.confidence:.1%})")
```

---

## Part 3 — Production-Only Features

---

## 9. Calibrated Likelihood Ratios

### Why This Is the Most Important Production Upgrade

In the POC, we guessed likelihood ratios based on intuition.
In production, every LR is measured from data.

**How to calibrate:**

You need:
- **Positive examples:** Confirmed criminal addresses (OFAC, UN, law enforcement confirmed)
- **Negative examples:** Confirmed clean addresses (exchange hot wallets from WalletExplorer)
- **For each:** Whether each signal was present or absent

```python
# services/risk_engine/lr_calibrator.py

import numpy as np

def calibrate_lr(signal_name: str,
                  positives: list[bool],   # Was signal present for confirmed criminals?
                  negatives: list[bool],   # Was signal present for confirmed clean?
                  ) -> dict:
    """
    Empirically measure the likelihood ratio for a signal.

    Example: DARK_WEB_PAYMENT signal
    Positives: 800 confirmed criminal addresses
               720 had dark web payment context → 90% rate
    Negatives: 5000 confirmed exchange addresses
               8 appeared in dark web payment context → 0.16% rate

    LR = 0.90 / 0.0016 = 562.5

    Compare to our POC guess of LR = 50.
    The measured value is 11x higher.
    This matters enormously for borderline cases.

    Laplace smoothing (+1) prevents division by zero for rare signals.
    """
    n_pos = len(positives)
    n_neg = len(negatives)
    p_pos = (sum(positives) + 1) / (n_pos + 2)  # P(signal | criminal)
    p_neg = (sum(negatives) + 1) / (n_neg + 2)  # P(signal | clean)
    lr    = p_pos / p_neg

    return {
        'signal':       signal_name,
        'lr':           round(lr, 2),
        'log_lr':       round(np.log(lr), 4),
        'p_criminal':   round(p_pos, 4),
        'p_clean':      round(p_neg, 6),
        'n_positive':   n_pos,
        'n_negative':   n_neg,
        'note':         f"Based on {n_pos} criminal and {n_neg} clean examples",
        'calibrated_at': datetime.now().isoformat(),
    }

# Example calibration run (use after collecting evaluation dataset)
def calibrate_all_signals(confirmed_criminals: list[str],
                           confirmed_clean: list[str],
                           db_conn) -> dict:
    """
    Runs calibration for all signals using the confirmed address sets.
    Store results in database; risk engine loads from there.
    """
    signals_to_calibrate = [
        'dark_web_payment_confidence',
        'taint_hop1', 'taint_hop2', 'taint_hop3',
        'community_report', 'pgp_criminal_link',
        'behavioral_anomaly'
    ]
    calibrated = {}
    for signal in signals_to_calibrate:
        # Get signal presence for each confirmed criminal
        pos = [bool(db_conn.execute(
            "SELECT 1 FROM dark_web_records WHERE address = %s AND context_type = 'PAYMENT'",
            (addr,)).fetchone()) for addr in confirmed_criminals]
        # Get signal presence for each confirmed clean address
        neg = [bool(db_conn.execute(
            "SELECT 1 FROM dark_web_records WHERE address = %s AND context_type = 'PAYMENT'",
            (addr,)).fetchone()) for addr in confirmed_clean]
        result = calibrate_lr(signal, pos, neg)
        calibrated[signal] = result
        print(f"  {signal}: LR = {result['lr']:.1f} "
              f"(p_criminal={result['p_criminal']:.2%}, p_clean={result['p_clean']:.4%})")
    return calibrated
```

---

## 10. Analyst Feedback Loop

### Why the POC Has None and Production Must Have One

The POC produces risk decisions. An analyst reviews them. If the analyst finds
a false positive (innocent wallet incorrectly flagged), they manually ignore it.
Next week, the same pattern triggers the same false positive again. No learning.

**The feedback loop prevents false positive accumulation:**

```python
# services/feedback/feedback_processor.py

def process_analyst_feedback(address: str,
                               verdict: str,  # CONFIRMED_CRIMINAL or CONFIRMED_INNOCENT
                               analyst_id: str,
                               notes: str,
                               db_conn):
    """
    When an analyst reviews a flagged wallet and gives feedback:
    1. Record the feedback immutably (audit log)
    2. If CONFIRMED_INNOCENT: retroactively un-taint downstream addresses
    3. If CONFIRMED_CRIMINAL: retroactively strengthen downstream taint
    4. Add as training example for next LR calibration run

    Example of why retroactive correction matters:
    Wallet A was incorrectly flagged as criminal.
    Wallets B, C, D are within 2 hops of A and received taint from A.
    B, C, D are WATCHLISTED because of their proximity to A.
    When analyst confirms A is innocent:
    → A's score set to CLEAN
    → B, C, D's taint is recomputed WITHOUT A's contribution
    → B, C, D may drop below WATCHLISTED threshold
    → B, C, D automatically reclassified to CLEAN

    Without this: innocent wallets B, C, D remain WATCHLISTED forever.
    """

    # 1. Immutable audit record (for legal accountability)
    db_conn.execute("""
        INSERT INTO audit_log (action, actor, resource, details, timestamp)
        VALUES ('ANALYST_FEEDBACK', %s, %s, %s, NOW())
    """, (analyst_id, address,
          json.dumps({'verdict': verdict, 'notes': notes})))

    if verdict == 'CONFIRMED_INNOCENT':
        # 2. Update address to CLEAN
        db_conn.execute("""
            UPDATE risk_decisions
            SET category = 'CLEAN', confidence = 0.02,
                analyst_override = true, override_by = %s
            WHERE address = %s
        """, (analyst_id, address))

        # 3. Find addresses within 2 hops that received taint from this address
        downstream = find_downstream_taint_recipients(address, max_hops=2, db_conn=db_conn)
        corrected  = 0
        for downstream_addr in downstream:
            new_score = recompute_taint_excluding(downstream_addr, address, db_conn)
            if new_score < 0.35:  # Below WATCHLISTED threshold
                db_conn.execute("""
                    UPDATE risk_decisions
                    SET category = 'CLEAN', confidence = %s,
                        retroactive_correction = true
                    WHERE address = %s
                """, (new_score, downstream_addr))
                corrected += 1

        print(f"✅ Feedback processed: {address} → CLEAN, "
              f"{corrected} downstream addresses corrected")

    elif verdict == 'CONFIRMED_CRIMINAL':
        # Strengthen signal for downstream addresses
        db_conn.execute("""
            UPDATE risk_decisions
            SET category = 'BLACKLISTED', confidence = 0.98,
                analyst_override = true
            WHERE address = %s
        """, (address,))

    db_conn.commit()
```

---

## 11. Model Drift Detection

### The Problem: Your Risk Scores Go Stale Without Noticing

Criminal patterns evolve. If you calibrated your likelihood ratios in January
and it's now September, the real-world accuracy of your scores may have degraded.

Example of drift:
- January: 90% of addresses in DW payment context are criminal → LR = 720
- September: Criminals started using throwaway addresses more → only 60% are criminal → LR = 480
- Your LR is still set to 720 → you're over-flagging

```python
# services/monitoring/drift_detector.py

class LRDriftDetector:
    """
    Monitors whether likelihood ratios are still accurate by comparing
    the predicted positive rate to the observed positive rate on
    analyst-reviewed cases.

    Requires: Analyst feedback data (Section 10) to compute observed rates.
    More feedback = more accurate drift detection.
    """

    def compute_drift(self, signal: str, current_lr: float,
                       db_conn) -> dict:
        """
        Compare the current LR to what it would be if recalibrated today
        using the last 90 days of analyst-confirmed cases.
        """
        # Get cases where signal was present + analyst confirmed criminal
        confirmed_pos = db_conn.execute("""
            SELECT COUNT(*) FROM risk_decisions rd
            JOIN analyst_feedback af ON rd.address = af.address
            WHERE af.verdict = 'CONFIRMED_CRIMINAL'
              AND rd.evidence @> '[{"source": "DARK_WEB_PAYMENT"}]'
              AND af.created_at > NOW() - INTERVAL '90 days'
        """).fetchone()[0]

        total_pos = db_conn.execute("""
            SELECT COUNT(*) FROM risk_decisions rd
            WHERE rd.evidence @> '[{"source": "DARK_WEB_PAYMENT"}]'
              AND rd.assessed_at > NOW() - INTERVAL '90 days'
        """).fetchone()[0]

        if total_pos < 20:
            return {'status': 'INSUFFICIENT_DATA', 'min_required': 20}

        observed_precision = confirmed_pos / total_pos
        expected_precision = 1 - (1 / current_lr)  # Simplified

        drift_ratio = observed_precision / max(expected_precision, 0.001)

        return {
            'signal':             signal,
            'current_lr':         current_lr,
            'observed_precision': round(observed_precision, 4),
            'expected_precision': round(expected_precision, 4),
            'drift_ratio':        round(drift_ratio, 3),
            'status': (
                'RETRAIN_NOW'  if drift_ratio < 0.5 else  # Accuracy halved
                'DRIFT_WARNING' if drift_ratio < 0.75 else  # 25% degradation
                'STABLE'
            )
        }
```

---

## 12. Production API Layer

### From Dashboard-Only to Queryable API

The POC serves results through Streamlit. In production, other systems
(exchanges, compliance tools, other researchers) need to query your risk scores.

```python
# services/api/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt

app = FastAPI(
    title="BTC-Intel Risk API",
    description="Bitcoin wallet risk assessment — BLACKLISTED / WATCHLISTED / CLEAN",
    version="2.0.0"
)
security = HTTPBearer()

@app.get("/v2/wallet/{address}")
async def assess_wallet(
    address: str,
    token:   str = Depends(security)
) -> dict:
    """
    Assess the risk of a single Bitcoin wallet address.

    Returns: category, confidence, evidence chain, investigation brief.
    Latency target: < 200ms for cached results (Redis), < 5s for new assessment.

    Rate limit: 1000 requests/day per API key (free tier).
    """
    # Validate address format first (quick fail)
    if not is_valid_btc_address(address):
        raise HTTPException(400, "Invalid Bitcoin address format")

    # Check Redis cache (sub-millisecond for already-assessed addresses)
    import redis
    r = redis.Redis(host='localhost', port=6379)
    cached = r.get(f"risk:{address}")
    if cached:
        return json.loads(cached)

    # Full assessment pipeline
    result = await run_full_assessment(address)

    # Cache for 5 minutes (balance between freshness and performance)
    r.setex(f"risk:{address}", 300, json.dumps(result))

    return result

@app.post("/v2/wallet/batch")
async def assess_batch(
    addresses: list[str],
    token: str = Depends(security)
) -> list[dict]:
    """
    Assess up to 1000 addresses in one request.
    Used by exchanges for bulk deposit screening.
    All addresses processed in parallel.
    """
    if len(addresses) > 1000:
        raise HTTPException(400, "Maximum 1000 addresses per batch request")

    # Process in parallel using asyncio
    import asyncio
    results = await asyncio.gather(*[run_full_assessment(a) for a in addresses])
    return results

@app.get("/v2/watchlist/pre_crime")
async def get_pre_crime_watchlist(token: str = Depends(security)) -> list[dict]:
    """
    Returns all addresses currently on the PRE_CRIME_WATCHLIST.
    These are addresses found on dark web with ZERO on-chain history.
    """
    return db.execute("""
        SELECT address, onion_domain, page_topic, dw_confidence,
               first_seen_dw, monitoring_status
        FROM pre_crime_watchlist
        WHERE monitoring_status = 'ACTIVE'
        ORDER BY dw_confidence DESC
    """).fetchall()
```

---

## 13. Audit Log and Legal Compliance

### Why an Immutable Audit Log Is Mandatory

If your system incorrectly flags an innocent person's wallet and they complain:
- Without audit log: you cannot prove what evidence led to the decision
- With audit log: you can show exactly what was computed, when, by which version

```sql
-- Immutable audit log
-- Once written, NO UPDATE or DELETE is ever allowed (enforced by database permissions)

CREATE TABLE audit_log (
    id           BIGSERIAL PRIMARY KEY,
    action       TEXT NOT NULL,       -- WALLET_ASSESSED / FEEDBACK / SEED_UPDATED
    address      TEXT,
    result_hash  TEXT,                -- SHA-256 of the full result (tamper detection)
    actor        TEXT NOT NULL,       -- 'SYSTEM' or analyst_id
    details      JSONB,
    timestamp    TIMESTAMPTZ DEFAULT NOW()
);

-- Remove UPDATE and DELETE from the application user (immutable by design)
REVOKE UPDATE, DELETE ON audit_log FROM btcintel_app;

-- Application code creates the hash:
def log_assessment(address, decision, db_conn):
    result_hash = hashlib.sha256(
        json.dumps({
            'address':    address,
            'category':   decision.category,
            'confidence': decision.confidence,
            'timestamp':  datetime.utcnow().isoformat()
        }, sort_keys=True).encode()
    ).hexdigest()

    db_conn.execute("""
        INSERT INTO audit_log (action, address, result_hash, actor, details)
        VALUES ('WALLET_ASSESSED', %s, %s, 'SYSTEM', %s)
    """, (address, result_hash, json.dumps(decision.evidence)))
```

---

## 14. Production Dashboard

### What Changes from Streamlit POC to Production React

```
POC (Streamlit):                     Production (React + TypeScript):
──────────────────────────────────   ─────────────────────────────────────────
Rerenders entire page on each click  Component-level updates (faster)
Single user at a time                Multi-analyst concurrent workspace
No role-based access                 Analyst / Researcher / Admin roles
No SLA tracking                      60-day PMLA deadline tracker per alert
No audit log viewer                  Full audit log explorer with tamper detection
No PRE_CRIME live feed               Real-time PRE_CRIME_WATCHLIST with ElectrumX events
Works fine for POC demo              Required for institutional deployment
```

**Key production-only dashboard features:**

```
1. Alert Queue with SLA
   Each BLACKLISTED/WATCHLISTED address has a review deadline.
   Colour coding: green (time remaining), yellow (<7 days), red (overdue).

2. PRE_CRIME Live Feed
   WebSocket connection shows new PRE_CRIME_WATCHLIST entries in real-time.
   "New address found on abc.onion/drugs — DRUG, confidence 0.82"

3. Evidence Timeline
   For each address: timeline of when each evidence signal was first seen.
   "Dark web first seen: March 10 → First transaction: March 13 → OFAC confirmed: April 2"
   Shows the PRE_CRIME detection advantage clearly (3 days earlier than OFAC).

4. Audit Log Explorer
   Searchable, filterable audit trail.
   Tamper detection: each row shows ✅ (hash valid) or ❌ (hash mismatch — alert).
```

---

## 15. All 21 Issues: POC vs Final Product Comparison

| # | Issue | POC Solution | Final Product Upgrade |
|---|-------|-------------|----------------------|
| 1 | Seed Management | 6 sources, static load | Auto-refresh with ETag, 8+ sources, downstream re-evaluation on new seeds |
| 2 | URL Structure | Depth=3 limit, category/listing classification | URL priority scoring based on historical wallet yield per domain |
| 3 | Link Discovery | Extract all `<a href="*.onion">` | Domain reputation scoring, high-yield domains prioritised |
| 4 | Deduplication | SHA-256 hash in Redis | Content-hash + URL-normalisation; cross-session dedup in PostgreSQL |
| 5 | Crawl Depth | Hard max=3 | Adaptive depth based on content value (pages with wallets get deeper crawl) |
| 6 | Infinite Expansion | 500 pages/domain/cycle cap | Global priority queue, completed domains excluded automatically |
| 7 | Recrawling | DUTA-10K static sample | Domain-type schedule (markets=3d, forums=7d, paste=1d) |
| 8 | Dead Services | 60s timeout, mark DEAD | Exponential backoff, 30-day retry, health score per domain |
| 9 | Response Speed | 6 Tor instances, 30s rate limit | Auto-scale workers based on queue depth |
| 10 | Auth Walls | Unauthenticated only (~8%) | Supplement with DUTA-10K, Gwern archives, research partnerships |
| 11 | JavaScript | Splash renderer | Splash with automatic fallback to raw HTML for static pages |
| 12 | HTML Complexity | BeautifulSoup4 with permissive parser | Sentence-boundary context windows, not fixed char windows |
| 13 | Content Types | MIME check, PDF + image | OCR images <2MB, QR code detection, PDF full text extraction |
| 14 | Image Data | Tesseract OCR | QR code detection via pyzbar, higher OCR accuracy with preprocessing |
| 15 | Video Content | Skipped (documented) | Future: keyframe OCR (not in v1) |
| 16 | Search Quality | Domain reputation filter | Domain yield scoring, low-yield domains deprioritised automatically |
| 17 | Fake/Invalid | Base58Check validation | Validation + BigQuery existence check (phantom address filter) |
| 18 | Attribution Risk | 3-state + confidence scores | Calibrated LRs, exculpatory signals, victim-context protection |
| 19 | Storage Explosion | 90-day MinIO lifecycle | MinIO + tiered storage (hot SSD for <30d, cold HDD for 30-90d) |
| 20 | Malicious Content | VM blast shield, snapshot daily | Network-isolated VM, automatic post-crawl integrity check |
| 21 | Legal/Ethical | IRB documentation, passive-only | Full GDPR compliance layer, data retention policy, research ethics framework |

---

## 16. 16-Week Production Roadmap

| Weeks | What Gets Built | What Changes From POC | Demo Milestone |
|-------|----------------|----------------------|----------------|
| 1–2 | College server full setup: PostgreSQL, Neo4j, MinIO, Redis, KVM | POC ran on laptop; now runs on dedicated always-on server | Server accessible at college server IP |
| 3–4 | Auto-refreshing seed collector (ETag-based). Extended source list (8 sources). | POC loaded seeds once; production auto-updates every 4 hours | Seeds update automatically when OFAC publishes new designations |
| 5–6 | Bitcoin full node setup + initial sync (takes 7 days). ElectrumX address indexer. | POC used BigQuery; production uses own full node for real-time | Real-time mempool monitoring live |
| 7 | Sentence-boundary context extraction. Protocol-specific CoinJoin detection. Image OCR. | POC used fixed-char windows; production uses sentence boundaries | Improved address extraction accuracy measurable on DUTA-10K |
| 8 | PRE_CRIME watchlist with ElectrumX real-time subscription. | POC polled BigQuery every 6 hours; production gets notified in seconds | PRE_CRIME → TRIGGERED detection latency: minutes not hours |
| 9 | Calibrated likelihood ratios (measured from OFAC + WalletExplorer dataset). | POC used guessed LRs; production uses measured LRs | Risk score distribution comparison: before/after calibration |
| 10 | Analyst feedback loop. Retroactive correction cascade. | POC had no feedback; production corrects downstream from false positives | False positive correction working end-to-end |
| 11 | LR drift detection. Quarterly recalibration trigger. | POC had static LRs; production detects when they go stale | Drift report showing signal accuracy over time |
| 12 | Production FastAPI. Redis caching. Batch endpoint (1000 addr/request). | POC had Streamlit only; production has REST API | API accepting external queries from other systems |
| 13 | Domain recrawl scheduler. Dead service handling. URL priority scoring. | POC had static queue; production has intelligent priority queue | Crawler efficiency metrics (yield per domain) |
| 14 | Audit log with tamper detection. GDPR data retention enforcement. | POC had no audit trail; production has immutable signed log | Compliance documentation ready for review |
| 15 | React production dashboard. Role-based access. SLA tracker. PRE_CRIME live feed. | POC used Streamlit; production uses React + TypeScript | Full multi-user analyst workspace functional |
| 16 | Load testing. Security hardening. Documentation. Research paper evaluation data. | Final polish | System ready for research paper evaluation and institutional demo |

---

*This document is the complete specification for taking BTC-Intel from a working POC
to a production-grade Bitcoin wallet intelligence system. Every section builds directly
on the POC. The core goal never changes: "Is this Bitcoin wallet criminal, and why?"*
