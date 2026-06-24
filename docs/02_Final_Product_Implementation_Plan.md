# BTC-Intel: Final Product Implementation Plan
## Production-Grade Architecture — Layer-Wise Specification
### With Full Architectural Justification and Alternative Analysis

> **Document Purpose:** This is the second implementation plan. It covers the Final Product — a production-grade, scalable, legally defensible threat intelligence system. It assumes the POC has validated the core algorithms. Every layer here is significantly more robust than the POC equivalent. This plan is written for engineering teams, not just researchers.

---

## Table of Contents

1. [Product Vision and Non-Negotiable Requirements](#1-product-vision)
2. [Final Architecture Overview](#2-final-architecture-overview)
3. [Layer 1 — Acquisition Layer (Production)](#3-layer-1--acquisition-layer)
4. [Layer 2 — Extraction & Normalisation Layer](#4-layer-2--extraction--normalisation-layer)
5. [Layer 3 — Entity Resolution Layer](#5-layer-3--entity-resolution-layer)
6. [Layer 4 — Blockchain Intelligence Layer](#6-layer-4--blockchain-intelligence-layer)
7. [Layer 5 — Service Recognition Layer (Production)](#7-layer-5--service-recognition-layer)
8. [Layer 6 — Behavior Analysis Layer](#8-layer-6--behavior-analysis-layer)
9. [Layer 7 — Multi-Evidence Risk Engine (Production)](#9-layer-7--multi-evidence-risk-engine)
10. [Layer 8 — Explainability Engine](#10-layer-8--explainability-engine)
11. [Layer 9 — Analyst Feedback Layer](#11-layer-9--analyst-feedback-layer)
12. [Layer 10 — API & Integration Layer](#12-layer-10--api--integration-layer)
13. [Layer 11 — Threat Intelligence Dashboard (Production)](#13-layer-11--threat-intelligence-dashboard)
14. [Infrastructure: Justified Technology Choices](#14-infrastructure-justified-technology-choices)
15. [Complete Database Schema (Production)](#15-complete-database-schema-production)
16. [Security, Compliance & Legal Framework](#16-security-compliance--legal-framework)
17. [Model Versioning & Drift Management](#17-model-versioning--drift-management)
18. [Production Build Roadmap (16 Weeks Post-POC)](#18-production-build-roadmap)
19. [Operational Runbook: What Happens When Things Break](#19-operational-runbook)

---

## 1. Product Vision and Non-Negotiable Requirements

The Final Product is a production-grade cryptocurrency threat intelligence platform designed for use by:
- Financial institutions performing KYC/AML screening
- Law enforcement intelligence units
- Cryptocurrency exchanges performing deposit screening
- Compliance teams requiring blockchain transaction risk assessment

**Non-Negotiable Requirements (must meet all of these to be production-grade):**

| Requirement | Target | Why Non-Negotiable |
|-------------|--------|--------------------|
| Risk score latency (single address lookup) | < 200ms P99 | Real-time deposit screening use case |
| Batch processing throughput | ≥ 10,000 addresses/hour | Exchange bulk screening |
| System uptime | 99.5% (allowing ~44 hours downtime/year) | 24/7 enforcement operations |
| False positive rate (BLACKLISTED tier) | < 2% | Legal defensibility — wrongful accusation risk |
| Evidence chain completeness | 100% | Every score must be explainable |
| Analyst feedback integration | < 1 minute retroactive correction | Prevents systematic false positive propagation |
| Data retention compliance | Configurable per jurisdiction (30/90 days) | GDPR Article 5(1)(e) |
| Audit log | Immutable, cryptographically signed | Legal chain of custody |

**The difference from the POC:**
The POC proves algorithms work. The Final Product guarantees they work at scale, correctly, consistently, with legal defensibility, and without catastrophic false positives under adversarial conditions.

---

## 2. Final Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ACQUISITION LAYER (PRODUCTION)                    │
│                                                                       │
│  ┌──────────────────────────┐  ┌──────────────────────────────────┐  │
│  │   TOR CRAWLER CLUSTER    │  │   BLOCKCHAIN NODE CLUSTER        │  │
│  │   6 × Tor instances      │  │   Bitcoin Core (full, non-pruned)│  │
│  │   JavaScript rendering   │  │   ElectrumX address indexer      │  │
│  │   15,000–25,000 pgs/day  │  │   Blockchair Pro API (burst)     │  │
│  │   MinIO page archive     │  │   Mempool.space (real-time)      │  │
│  └──────────────────────────┘  └──────────────────────────────────┘  │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │   INTELLIGENCE FEEDS                                             │  │
│  │   OFAC SDN XML (auto-refresh)  │  Chainabuse API               │  │
│  │   Crystal Blockchain (trial)   │  Community reporting API       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────────────┘
                               │  Kafka message bus
┌──────────────────────────────▼───────────────────────────────────────┐
│                    EXTRACTION & NORMALISATION LAYER                   │
│  BTC Extractor (4-stage: structural→regex→NER→context)               │
│  PGP Extractor (pgpy, fingerprint normalisation)                     │
│  Alias Extractor (NER: fine-tuned spaCy on dark web corpus)          │
│  PDF Extractor (pdfminer.six → pdf2image+Tesseract fallback)         │
│  Amount Parser (BTC/mBTC/μBTC/satoshi normalisation)                 │
│  Topic Classifier (LDA on dark web content)                          │
│  Context Window Classifier (sentence-boundary sliding window)        │
└─────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                    ENTITY RESOLUTION LAYER                            │
│  Probabilistic entity resolution (4-signal: wallet+PGP+alias+domain) │
│  Jaro-Winkler alias fuzzy matching (threshold 0.85)                  │
│  Trigram cosine similarity (longer handles)                          │
│  PGP fingerprint normalisation (40-char hex, collision detection)    │
│  Neo4j entity graph (confidence-weighted edges)                      │
│  Temporal entity tracking (split/merge events over time)             │
└─────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                    BLOCKCHAIN INTELLIGENCE LAYER                      │
│  CIO Clustering (CoinJoin filter + LN filter + Taproot gap flag)     │
│  Change Address Heuristics (script-type + optimal-change combined)   │
│  Address Reuse Detection (5th heuristic, 100% precision, low recall) │
│  Multi-heuristic Weighted Voting (Delgado 2021 weights, recalibrated)│
│  UTXO-level analysis (finer-grained than address-level)              │
│  Cross-chain Bridge Detection (WBTC contract addresses flagged)      │
│  Temporal Cluster Tracking (merge/split events logged)               │
└─────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                    SERVICE RECOGNITION LAYER                          │
│  [MUST RUN BEFORE RISK PROPAGATION]                                  │
│  ExchangeDetector  │  MixerDetector  │  PoolDetector                │
│  MarketDetector    │  LightningDetector  │  MerchantDetector         │
│  Feedback loop: misclassified services trigger CIO partial reversal  │
└─────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                    BEHAVIOR ANALYSIS LAYER                            │
│  Static features (Peled 2021, 40+ features)                          │
│  Temporal rolling-window features (7/30/90/365 days)                 │
│  Temporal delta features (volume acceleration, dormancy break)       │
│  Money flow fingerprint (64-dim vector, Sayadi 2023)                 │
│  Isolation Forest anomaly detection (trained on clean population)    │
│  Behavioral similarity search (cosine distance vs known criminals)   │
│  Model versioning with drift detection                               │
└─────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                    THREE-LAYER RISK ENGINE                            │
│  Layer 1: Rule-based fast path (deterministic cases)                 │
│  Layer 2: Provenance-aware Bayesian fusion (ambiguous cases)         │
│  Layer 3: Isolation Forest anomaly (novel pattern detection)         │
│  → CLEAN / WATCHLISTED / BLACKLISTED / PRE_CRIME_WATCHLIST           │
│  Output: RiskDecision with full evidence chain                       │
└─────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                    EXPLAINABILITY ENGINE                              │
│  SHAP values (ML layer)                                              │
│  Counterfactual generator (rule + Bayesian layers)                   │
│  Evidence ranking (contribution-sorted)                              │
│  Contradiction detector                                              │
│  Analyst-readable narrative generation                               │
└─────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                    ANALYST FEEDBACK LAYER                             │
│  Binary feedback API (CONFIRMED_CRIMINAL/CONFIRMED_INNOCENT)         │
│  Retroactive taint correction (within 2-hop propagation)             │
│  Downstream re-evaluation trigger                                    │
│  False positive catalogue and pattern detection                      │
│  Active learning queue (FP patterns feed classifier retraining)      │
└─────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                    API & INTEGRATION LAYER                            │
│  FastAPI REST (address lookup, batch screening, watchlist mgmt)      │
│  gRPC (high-throughput exchange integration)                         │
│  Webhook notifications (PRE_CRIME_WATCHLIST triggers)                │
│  STIX 2.1 export (standard threat intelligence format)               │
│  Rate limiting + authentication (JWT + API keys)                     │
└─────────────────────────────┬───────────────────────────────────────┘
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                    THREAT INTELLIGENCE DASHBOARD                      │
│  React + TypeScript (production frontend)                            │
│  Neo4j Bloom (graph visualisation)                                   │
│  Timeline view (temporal analysis)                                   │
│  Evidence chain navigator                                            │
│  Analyst workspace (feedback, case management)                       │
│  Audit log viewer                                                    │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Layer 1 — Acquisition Layer (Production)

### 3.1 Tor Crawler Cluster

**Why a cluster and NOT a single crawler:**
A single Tor instance can crawl approximately 2,000–4,000 pages/day with proper rate limiting. To reach the 15,000–25,000 pages/day target without aggressive scraping that would get BTC-Intel's exit node IP blocked, you need 6 independent Tor instances, each with a separate Tor circuit and identity.

**Why 6 instances specifically:**
- Tor circuit establishment: ~3–5 seconds per circuit
- Average page load time (onion): ~4–8 seconds  
- 6 instances × 2,000 pages/day = 12,000 pages minimum, up to 25,000 with efficient scheduling
- Each instance runs on a separate VM to avoid shared circuit fingerprinting

**Why NOT ScrapingBee, Bright Data, or commercial proxies:**
- Commercial proxy services log requests — legally problematic for law enforcement intelligence work
- Tor provides circuit isolation that protects the operator's identity in jurisdictions where dark web research is legally sensitive
- Reproducibility: a research paper describing "we used a commercial proxy" cannot be independently validated

**Why JavaScript rendering is required in production (but not POC):**
Many modern dark web markets use JavaScript-rendered React or Angular frontends. Without JS rendering, your crawler sees an empty shell and misses all product listings. In the POC, we used pre-crawled archives (which already captured rendered content). In production, you need Splash (Tor-compatible Selenium alternative) or Playwright with a Tor proxy.

```yaml
# Docker Compose: Tor Crawler Production Configuration
services:
  tor_1:
    image: dperson/torproxy
    ports: ["9050:9050", "9051:9051"]
    environment:
      TOR_MaxCircuitDirtiness: "600"
      TOR_NewCircuitPeriod: "30"

  splash_1:
    image: scrapinghub/splash
    command: --proxy-host tor_1 --proxy-port 8118 --max-timeout 90
    depends_on: [tor_1]

  crawler_worker_1:
    build: ./crawler
    environment:
      SPLASH_URL: http://splash_1:8050
      KAFKA_BOOTSTRAP: kafka:9092
      MINIO_ENDPOINT: minio:9000
    depends_on: [splash_1, kafka, minio]
    deploy:
      resources:
        limits:
          memory: 2G
```

**Why MinIO for page archive and NOT S3 directly:**
- MinIO is S3-compatible but self-hosted, which keeps crawled dark web content on your own infrastructure
- Storing dark web page content on AWS S3 creates a third-party data dependency that has GDPR implications (data processing agreement required) and law enforcement disclosure risk
- MinIO can be encrypted at rest with customer-managed keys, which is required for handling potential PII (PGP keys, aliases)

---

### 3.2 Bitcoin Full Node (Production)

**Why a Bitcoin full node and NOT BigQuery (which was fine for POC):**
- BigQuery has a ~24-hour lag — unacceptable for real-time deposit screening
- BigQuery costs scale with query volume; at production query rates, BigQuery costs $5,000+/month
- A Bitcoin full node with ElectrumX provides real-time access with no external dependency and no per-query cost after setup
- For a production system, blockchain data is core infrastructure — it should not depend on a Google service availability

**Why ElectrumX alongside the full node:**
Bitcoin Core's RPC (`bitcoin-cli`) queries by TXID or block hash. To query by address ("give me all transactions for address 1ABC..."), you need an address indexer. ElectrumX is the standard production choice: it maintains a full address-to-transaction index, requires ~350GB of additional storage, and handles unlimited concurrent address queries.

**Why NOT a pruned node:**
A pruned node cannot answer historical queries. If a criminal address was active in 2016 and your clustering needs to trace its full history, a pruned node covering only the last 6 months of blocks cannot provide it. Historical completeness is non-negotiable for a clustering system.

**Hardware specification for production Bitcoin node:**

```
CPU:  8 cores (blockchain sync is I/O bound, not CPU bound)
RAM:  32GB (16GB for Bitcoin Core dbcache, 16GB for ElectrumX)
SSD:  2TB NVMe (620GB Bitcoin blockchain + 350GB ElectrumX index + headroom)
NET:  100Mbps sustained (initial sync requires significant bandwidth)
OS:   Ubuntu 22.04 LTS
```

---

### 3.3 Intelligence Feed Integration

**OFAC SDN XML (Auto-Refresh):**
The OFAC SDN list is updated irregularly. Production systems must check for updates at least twice daily (OFAC has updated multiple times in a single day during active enforcement periods). Use an HTTP ETag/Last-Modified check to detect updates without downloading the full ~40MB XML on every check.

**Chainabuse API:**
Used as corroborating evidence only, not primary signal. Rate limit: 100 requests/day on free tier; sufficient for enriching flagged addresses but not for bulk screening. Upgrade to paid tier for production if needed.

**Why NOT Chainalysis/TRM API as primary source:**
At production scale, Chainalysis API pricing is $50,000+/year. For a system building its own intelligence (which is BTC-Intel's value proposition), paying Chainalysis to be your primary data source negates the purpose of building BTC-Intel. Use commercial APIs for validation/corroboration only.

---

## 4. Layer 2 — Extraction & Normalisation Layer

### 4.1 Production Extraction Pipeline

**Why Kafka between acquisition and extraction:**
- The crawler cluster produces pages at 10–20 pages/second at peak
- The extraction pipeline (NER + PDF + OCR) processes at ~2–5 pages/second per worker
- Without a message queue, the crawler overwhelms the extraction pipeline
- Kafka provides durable buffering, horizontal scaling of extractors, and replay capability if an extractor crashes mid-batch

**Why NOT RabbitMQ:**
Kafka retains messages with configurable retention (we use 7 days). If an extractor worker crashes, it can replay from the Kafka offset. RabbitMQ deletes messages on acknowledgment — a crashed worker loses the un-ACK'd messages. For a data pipeline where dark web content is ephemeral (pages change or disappear), retention-based replay is critical.

**Why spaCy fine-tuned on dark web corpus and NOT standard spaCy:**
Standard spaCy is trained on news and legal text. Dark web text uses drug slang ("g" for gram, "lb" for pound), coded language, heavy abbreviations ("WW shipping"), PGP-formatted blocks embedded in prose, and non-standard punctuation. Standard spaCy has ~40% recall on dark web alias extraction vs. ~75% for a fine-tuned version (based on the Peled 2021 supplementary data). The fine-tuning cost is 200–500 labeled examples (1–2 days of annotation) — worth the precision gain.

**The sliding context window (production improvement over POC):**
The POC uses a fixed 150-character window around each extracted address. The production system uses sentence-boundary detection (NLTK `sent_tokenize`) to find the nearest payment-context sentence, regardless of character distance. This correctly handles listings where the address appears at the bottom of a long product description, far from the "payment instructions" text that classifies it as a payment context.

```python
def get_payment_context_window(html: str, addr_position: int,
                                max_sentences: int = 5) -> tuple[str, str]:
    """
    Find the nearest payment-context sentence to the address.
    Uses sentence boundary detection rather than fixed character window.
    Returns: (context_text, classification_basis_sentence)
    """
    from nltk.tokenize import sent_tokenize

    # Extract text around address (±2000 chars for sentence detection)
    surrounding = html[max(0, addr_position - 2000): addr_position + 2000]
    sentences   = sent_tokenize(surrounding)

    # Find address-containing sentence
    addr_sentence_idx = None
    for i, sent in enumerate(sentences):
        if addr_position - max(0, addr_position - 2000) in range(
            surrounding.find(sent), surrounding.find(sent) + len(sent)
        ):
            addr_sentence_idx = i
            break

    if addr_sentence_idx is None:
        # Fallback to fixed window
        return html[max(0, addr_position - 250): addr_position + 250], 'FIXED_WINDOW_FALLBACK'

    # Take up to max_sentences before and after the address sentence
    window_start = max(0, addr_sentence_idx - max_sentences)
    window_end   = min(len(sentences), addr_sentence_idx + max_sentences)
    context_text = ' '.join(sentences[window_start:window_end])

    # Find the most payment-relevant sentence in the window
    payment_scores = []
    for s in sentences[window_start:window_end]:
        score = sum(1 for kw in PAYMENT_CONTEXT_KEYWORDS['high'] if kw in s.lower())
        payment_scores.append((score, s))

    best_sentence = max(payment_scores, key=lambda x: x[0])[1] if payment_scores else ''
    return context_text, best_sentence
```

### 4.2 Amount Normalisation (Production-Only Feature)

This is absent from the POC and adds significant research value:

```python
AMOUNT_PATTERNS = {
    # All normalise to satoshi (smallest Bitcoin unit)
    r'(\d+\.?\d*)\s*BTC':     lambda x: int(float(x) * 1e8),
    r'(\d+\.?\d*)\s*mBTC':    lambda x: int(float(x) * 1e5),
    r'(\d+\.?\d*)\s*μBTC':    lambda x: int(float(x) * 100),
    r'(\d+\.?\d*)\s*bits?':   lambda x: int(float(x) * 100),
    r'(\d+\.?\d*)\s*sat':     lambda x: int(float(x)),
    r'(\d+\.?\d*)\s*satoshi': lambda x: int(float(x)),
}

def parse_amount_to_satoshi(text: str) -> int | None:
    """
    Extract and normalise Bitcoin amount from dark web listing text.
    Returns amount in satoshi, or None if no recognisable amount found.
    """
    import re
    for pattern, converter in AMOUNT_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return converter(match.group(1))
            except (ValueError, OverflowError):
                continue
    return None
```

**Why amount parsing matters for production:**
If a dark web listing says "price: 0.234 BTC" and the first on-chain transaction to that address is exactly 0.234 BTC within 24 hours of the listing, this is extremely strong corroborating evidence of a completed transaction. This cross-validation capability is not available in any academic paper or commercial tool — it is a novel production feature that strengthens evidence confidence significantly.

---

## 5. Layer 3 — Entity Resolution Layer

### 5.1 Probabilistic Entity Resolution (Four-Signal)

**Why probabilistic and NOT deterministic (binary) entity resolution:**
Deterministic resolution (merge if PGP key matches) is binary — either they're the same entity or they're not. This fails when evidence is partial: a vendor reuses an alias with a typo, or their PGP key changes between markets. Probabilistic resolution assigns a confidence score to every potential entity merge, keeping "possibly same entity" links as tentative rather than forcing a binary decision.

**The four evidence signals and their confidence weights:**

| Signal | Weight | Why | Failure Mode |
|--------|--------|-----|-------------|
| Exact PGP fingerprint match (40-char) | 0.95 | Cryptographically unique | Key sharing/vouching — two entities can share a key |
| Exact Bitcoin address match | 1.0 | Addresses are unique | Address reuse may be unintentional (copy-paste) |
| Alias exact match | 0.70 | Stable pseudonyms | Common aliases ("admin", "vendor1") have many collisions |
| Alias fuzzy match (JW ≥ 0.90) | 0.60 | Typo/variation variants | Coincidental similarity |
| Domain co-occurrence | 0.40 | Same operator may run multiple sites | Domain sharing ≠ same operator (reseller/mirror) |
| PGP UID match (name in key) | 0.50 | Claimed identity | Self-asserted, easily faked |

**Why Jaro-Winkler for alias matching and NOT Levenshtein:**
Jaro-Winkler gives higher weight to common prefixes, which matches how dark web vendors create alias variations ("DarkVendor", "DarkVendor_v2", "DarkVendor_official"). Levenshtein treats all character positions equally, which overweights suffix differences. For a 0.85 threshold, Jaro-Winkler correctly links "DarkVendor" and "DarkVendorv2" as the same entity while keeping "DarkVendor" and "DarkBuyer" as different.

**Why NOT deep learning for entity resolution (in production v1):**
Deep learning entity resolution models (e.g., DeepMatcher) require substantial labeled training data ("these two entities are the same person / different persons"). We do not have this training data in labeled form. The probabilistic rule-based approach works at 70–80% precision for the aliases we care about (dark web vendor identities) without training data. Deep learning is deferred to production v2 after we have accumulated analyst-verified entity pairs as training data.

### 5.2 Temporal Entity Tracking

**Why this is necessary but absent in the POC:**
Dark web entities are not static. A vendor's private key gets sold (cluster split: one cluster becomes two entities). Two markets merge operations (cluster merge: two clusters become one entity). A vendor gets arrested and their infrastructure is taken over by a successor (entity discontinuity).

Production requires tracking these changes:

```python
@dataclass
class EntityEvent:
    event_type:    str           # MERGE | SPLIT | KEY_ROTATION | MARKET_TAKEOVER
    entity_ids:    list[str]     # Entities involved
    evidence:      dict          # What triggered this event
    confidence:    float         # How confident are we this event occurred?
    timestamp:     datetime

def detect_cluster_split(before_cluster: set, after_cluster: set,
                          transaction_graph) -> list[EntityEvent]:
    """
    Detect when a cluster splits: addresses that were co-owned before
    no longer appear in the same transactions.
    This can indicate a private key sale or operational split.
    """
    addresses_removed = before_cluster - after_cluster
    addresses_added   = after_cluster - before_cluster

    if not addresses_removed:
        return []

    # Check if removed addresses now appear in a different cluster's transactions
    new_cluster_roots = set()
    for addr in addresses_removed:
        new_root = find_cluster_root(addr, transaction_graph)
        if new_root != find_cluster_root(next(iter(before_cluster)), transaction_graph):
            new_cluster_roots.add(new_root)

    if new_cluster_roots:
        return [EntityEvent(
            event_type = 'SPLIT',
            entity_ids = [find_entity_for_cluster(before_cluster)] +
                          [find_entity_for_cluster({r}) for r in new_cluster_roots],
            evidence   = {'removed_addresses': list(addresses_removed),
                          'new_clusters': list(new_cluster_roots)},
            confidence = 0.75,
            timestamp  = datetime.utcnow(),
        )]
    return []
```

---

## 6. Layer 4 — Blockchain Intelligence Layer

### 6.1 UTXO-Level Analysis (Production Upgrade over POC)

**Why UTXO-level and NOT just address-level:**
The POC clusters at the address level. Production must cluster at the UTXO (Unspent Transaction Output) level, because a UTXO can be controlled by a different entity than the address's historical owner if the private key was sold.

Example: Address `1ABC...` was used by Criminal A until 2021, then the private key was sold to Criminal B. The address's UTXOs from 2021 onward belong to Criminal B, but address-level analysis would attribute everything to Criminal A's cluster.

UTXO-level analysis tracks which specific UTXOs are spent together, not just which addresses — a more precise signal for CIO clustering.

### 6.2 Multi-Heuristic Weighted Voting (Production)

```python
class ProductionClusterer:
    """
    Implements Delgado 2021 multi-heuristic voting with:
    1. CIO (weight 0.40, reduced from 0.50 for 2024 data — CoinJoin prevalence)
    2. Script-type change address (weight 0.30)
    3. Optimal change (weight 0.20)
    4. Address reuse (weight 0.10 — 100% precision, very low recall)
    
    Why these weights for 2024:
    Delgado 2021 calibrated on data through ~2020. CoinJoin adoption grew
    significantly in 2021–2024 (Wasabi 2.0, Whirlpool). CIO weight reduced
    from 0.50 to 0.40 to account for higher false positive rate from CoinJoin.
    Recalibration on 2024 data is a research contribution (Paper 1.3 gap).
    
    Confidence threshold for automatic merge:  0.65
    Confidence threshold for tentative merge:  0.40 (goes to WATCHLISTED cluster)
    Below 0.40:                                no merge
    """
    WEIGHTS = {
        'CIO':          0.40,
        'SCRIPT_CHANGE': 0.30,
        'OPTIMAL_CHANGE': 0.20,
        'ADDR_REUSE':   0.10,
    }
    AUTO_MERGE_THRESHOLD     = 0.65
    TENTATIVE_MERGE_THRESHOLD = 0.40

    def vote_merge(self, addr_a: str, addr_b: str,
                   heuristic_results: dict) -> tuple[str, float]:
        """
        Returns: (decision, confidence)
        decision: 'MERGE' | 'TENTATIVE_MERGE' | 'NO_MERGE'
        """
        weighted_vote = sum(
            self.WEIGHTS[h] for h, fired in heuristic_results.items() if fired
        )
        if weighted_vote >= self.AUTO_MERGE_THRESHOLD:
            return 'MERGE', weighted_vote
        elif weighted_vote >= self.TENTATIVE_MERGE_THRESHOLD:
            return 'TENTATIVE_MERGE', weighted_vote
        else:
            return 'NO_MERGE', weighted_vote
```

### 6.3 Cross-Chain Bridge Detection

**Why necessary in production:**
Criminals increasingly bridge Bitcoin → Ethereum (via WBTC) or Bitcoin → Monero (atomic swaps) to escape blockchain analysis. Production systems must detect when funds enter a cross-chain bridge and emit a "monitoring ends" signal rather than silently failing to track the funds.

**Known Bitcoin cross-chain bridge addresses (maintained list):**
- WBTC custodian addresses: publicly known (BitGo, Kyber, etc.)
- RenBridge gateway addresses: publicly known
- THORChain Bitcoin vault addresses: published on-chain

```python
KNOWN_BRIDGE_ADDRESSES = {
    'WBTC_BITGO':      ['3BitGoAddresses...'],
    'RENBRIDGE':       ['3RenProtocolGateway...'],
    'THORCHAIN':       ['bc1qTHORVault...'],
}

def detect_bridge_exit(transaction, known_bridges: dict) -> dict | None:
    """
    If any output address is a known cross-chain bridge,
    emit a CROSS_CHAIN_EXIT event — monitoring cannot continue beyond this point.
    """
    for output in transaction.outputs:
        for bridge_name, bridge_addrs in known_bridges.items():
            if output['address'] in bridge_addrs:
                return {
                    'event_type':   'CROSS_CHAIN_EXIT',
                    'bridge':       bridge_name,
                    'amount_sat':   output['value'],
                    'txid':         transaction.txid,
                    'monitoring':   'ENDED',
                    'reason':       f'Funds entered {bridge_name} — cross-chain tracking not implemented'
                }
    return None
```

---

## 7. Layer 5 — Service Recognition Layer (Production)

### Full Classification Taxonomy

**Production adds two service types not in the POC: Lightning Network nodes and merchants.**

**Why Lightning Network node detection is critical:**
Lightning Network has 60,000+ nodes and growing. LN channel funding transactions look like 2-of-2 multisig criminal setups to a naive CIO clusterer. Production must detect LN channel opens and: (a) skip CIO for the channel participants, and (b) track LN payment channels as a separate graph structure. LN payments are off-chain and completely invisible on the main blockchain — when funds are committed to LN, your tracking of those specific UTXOs ends until they are settled on-chain.

**The feedback loop to clustering (production-only):**
If service recognition classifies a cluster as a CoinJoin coordinator after it has already been CIO-merged, the production system must partially reverse the CIO merges for that cluster — the participants in the CoinJoin are not co-owned with the coordinator. This retroactive correction is architecturally expensive but necessary for precision. The POC does not implement this; production must.

```python
class ServiceRecognitionWithFeedback:
    """
    Production service recognition includes a feedback mechanism to clustering.
    """

    def classify_and_feedback(self, cluster_root: str, cluster: set,
                               clusterer: ProductionClusterer,
                               transaction_db) -> dict:
        classification = self.classify(cluster_root, cluster)

        # Feedback to clustering for CoinJoin coordinators
        if classification['service_type'] == 'COINJOIN_COORDINATOR':
            # Find all CoinJoin transactions in this cluster's history
            coinjoin_txns = [
                tx for tx in transaction_db.get_cluster_transactions(cluster)
                if clusterer.is_coinjoin(tx)
            ]
            # For each CoinJoin, the inputs are NOT co-owned with the coordinator
            for tx in coinjoin_txns:
                participant_addrs = [inp['address'] for inp in tx.inputs
                                     if inp['address'] not in cluster]
                for addr in participant_addrs:
                    # Remove incorrectly merged participants from coordinator cluster
                    clusterer.remove_from_cluster(addr, cluster_root)
                    # Log this as a correction event
                    db.log_cluster_correction(addr, cluster_root,
                                              'COINJOIN_PARTICIPANT_REMOVAL')

        return classification
```

---

## 8. Layer 6 — Behavior Analysis Layer

### 8.1 Temporal Rolling Window Features (Production)

**Why 4 time windows (7/30/90/365 days) and NOT just one:**
Criminal wallet lifecycle phases (pre-crime, active crime, evasion, exit — per Chen 2023) operate on different timescales. A dormancy break (criminal inactive for 300+ days, suddenly active) is only detectable if you have the 365-day window showing the dormancy and the 7-day window showing the new activity. A single static snapshot misses this entirely.

```python
def compute_all_temporal_features(address: str, transaction_db) -> dict:
    """
    Compute complete temporal feature set across 4 rolling windows.
    Returns 200+ dimensional feature vector.
    """
    features = {}

    for window_days in [7, 30, 90, 365]:
        stats = transaction_db.get_stats(address, days=window_days)
        features.update({
            f'tx_count_{window_days}d':           stats.tx_count,
            f'volume_btc_{window_days}d':         stats.total_volume_btc,
            f'distinct_senders_{window_days}d':   stats.distinct_senders,
            f'distinct_recipients_{window_days}d':stats.distinct_recipients,
            f'avg_tx_value_{window_days}d':       stats.avg_tx_value,
            f'peel_chain_length_{window_days}d':  stats.max_peel_chain_length,
            f'consolidation_ratio_{window_days}d': stats.consolidation_fraction,
        })

    # Temporal delta features — the novel contribution
    features['volume_acceleration'] = (
        features['volume_btc_7d'] - features['volume_btc_30d'] / 4.3
    )  # Positive = recent spike vs 30-day average
    features['sender_growth_rate']  = (
        features['distinct_senders_7d'] / max(features['distinct_senders_90d'] / 13, 0.001)
    )  # Recent sender growth vs 90-day baseline
    features['dormancy_break_score'] = (
        1.0 if features['tx_count_7d'] > 5 and features['tx_count_365d'] < 3
        else 0.0
    )  # Active in last week but barely active in last year
    features['activity_concentration'] = (
        features['tx_count_7d'] / max(features['tx_count_365d'], 1)
    )  # High = burst activity (criminal pattern)

    # Off-chain/on-chain temporal gap (novel feature — requires DW data)
    dw_record = transaction_db.get_dark_web_record(address)
    if dw_record and features.get('first_tx_date'):
        features['dw_to_first_tx_days'] = (
            features['first_tx_date'] - dw_record.first_seen_dw
        ).days  # Time from DW listing to first on-chain transaction
    else:
        features['dw_to_first_tx_days'] = None

    return features
```

### 8.2 Behavioral Fingerprint Library (Production)

In production, maintain a library of behavioral fingerprints for all OFAC-confirmed clusters. New addresses are compared against this library to find behavioral matches even without a direct taint link.

```python
class FingerprintLibrary:
    """
    Stores and queries 64-dimensional behavioral fingerprints.
    Uses FAISS (Facebook AI Similarity Search) for approximate nearest-neighbor search.
    FAISS handles millions of fingerprints with sub-10ms query time.
    
    Why FAISS and NOT brute-force cosine similarity:
    Brute force comparison against 100k fingerprints takes ~500ms per query.
    FAISS with IVF index reduces this to <5ms while maintaining 95%+ recall.
    """
    def __init__(self):
        import faiss
        self.index       = faiss.IndexFlatIP(64)   # Inner product = cosine on normalised vectors
        self.fingerprints = {}  # fingerprint_id → {address, label, entity_type}

    def add_fingerprint(self, address: str, fingerprint: np.ndarray,
                        label: str, entity_type: str):
        # Normalise to unit vector for cosine similarity via inner product
        norm_fp = fingerprint / np.linalg.norm(fingerprint)
        self.index.add(norm_fp.reshape(1, -1).astype(np.float32))
        self.fingerprints[self.index.ntotal - 1] = {
            'address': address, 'label': label, 'entity_type': entity_type
        }

    def find_similar(self, query: np.ndarray, top_k: int = 10,
                      min_similarity: float = 0.85) -> list[dict]:
        norm_q = query / np.linalg.norm(query)
        distances, indices = self.index.search(
            norm_q.reshape(1, -1).astype(np.float32), top_k
        )
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0 and dist >= min_similarity:
                result = dict(self.fingerprints[idx])
                result['similarity'] = float(dist)
                results.append(result)
        return results
```

---

## 9. Layer 7 — Multi-Evidence Risk Engine (Production)

### Production Upgrades Over POC

**Upgrade 1 — Calibrated likelihood ratios (empirically validated):**
In the POC, likelihood ratios are set by expert judgment. In production, recalibrate on the validation set (Elliptic + OFAC + WalletExplorer) to ensure that a signal with LR=50 actually corresponds to a 50× probability increase vs. prior. Use Platt scaling on the Bayesian output to calibrate the final probability.

**Upgrade 2 — Behavioral similarity as an additional signal:**
If an address's behavioral fingerprint has cosine similarity > 0.85 to a known OFAC-confirmed cluster, add `BEHAVIORAL_SIMILARITY` as an evidence signal with LR = 8.0. This enables detection of criminal entities that have not yet been flagged by OFAC but behave identically to confirmed criminals.

**Upgrade 3 — Amount correlation validation:**
If the first on-chain transaction to an address matches the amount in a dark web listing for that address (within ±5% for currency conversion noise), add `AMOUNT_CORRELATION` as evidence with LR = 15.0. This is a highly specific signal.

**Upgrade 4 — Ensemble three propagation methods:**
Rather than picking one propagation method, combine all three (taint + label propagation + PPR) into an ensemble with learned weights (from the evaluation comparison). Each method catches different patterns — the ensemble is more robust.

```python
PRODUCTION_LIKELIHOOD_RATIOS = {
    # Core signals (same as POC but empirically calibrated)
    'OFAC_SDN':              1000.0,   # Hardcoded — legally authoritative
    'DARK_WEB_PAYMENT':      50.0,     # Calibrated from validation set
    'TAINT_ENSEMBLE':        25.0,     # Average of 3 propagation methods
    'COMMERCIAL_CONSENSUS':  30.0,     # Only when provenance not circular

    # New production signals
    'AMOUNT_CORRELATION':    15.0,     # DW listing amount = first tx amount
    'BEHAVIORAL_SIMILARITY': 8.0,      # Fingerprint similarity > 0.85 to known criminal
    'DORMANCY_BREAK':        6.0,      # Wallet dormant 300+ days then active
    'CROSS_CHAIN_BRIDGE_PRE': 4.0,     # Received from bridge before criminal tx

    # Exculpatory signals (LR < 1 = reduces probability)
    'VICTIM_CONTEXT':        0.2,
    'EXCHANGE_PASSTHROUGH':  0.05,
    'LIGHTNING_CHANNEL':     0.1,
    'DUST_ATTACK':           0.01,
}
```

---

## 10. Layer 8 — Explainability Engine

**Why explainability is legally required (not just nice-to-have):**
In most jurisdictions, a financial institution that flags an account based on an automated system's output must be able to explain the decision to regulators (under AML regulations such as FATF recommendations, FinCEN guidance, and EU AMLD). A black-box score of 0.73 is legally insufficient. The counterfactual explanation ("this address would not be flagged if the dark web payment context were removed") is what makes the system legally defensible.

**Why counterfactual AND SHAP (both required):**
- SHAP: explains ML model outputs (Isolation Forest, any trained classifier)
- Counterfactual: explains rule-based and Bayesian outputs — "what would need to change?"
- Neither alone is complete: SHAP doesn't work for rule-based systems; counterfactuals don't provide feature importance for ML outputs
- Production uses both, routing to the appropriate explanation method based on which layer produced the decisive score

**Production explainability output format:**
```json
{
  "address": "1CriminalAddressXYZ",
  "category": "BLACKLISTED",
  "score": 0.97,
  "explanation": {
    "decisive_layer": "FAST_PATH_RULE",
    "rule_fired": "OFAC_SDN_CONFIRMED",
    "evidence_chain": [
      {
        "source": "OFAC_SDN",
        "contribution": 0.85,
        "detail": "Listed as SDN on 2024-03-15: Narcotics trafficker",
        "provenance": "DIRECT_OFAC_MATCH",
        "verifiable_at": "https://www.treasury.gov/ofac/..."
      },
      {
        "source": "DARK_WEB_PAYMENT",
        "contribution": 0.08,
        "detail": "Found on payment listing at abc123.onion on 2024-03-10",
        "provenance": "DW_CRAWLER_DIRECT",
        "page_archived": "minio://btc-intel-archive/2024-03-10/page_sha256_xyz.html.gz"
      }
    ],
    "counterfactual": "Score drops to 0.09 (CLEAN) if OFAC_SDN evidence is removed",
    "contradictions": [],
    "confidence_in_explanation": 0.98,
    "analyst_reviewable": true
  }
}
```

---

## 11. Layer 9 — Analyst Feedback Layer

**Why this layer is architecturally required (not optional):**
Without feedback, your false positive patterns accumulate silently. An analyst who reviews a flagged case and determines it's innocent has information the system needs — but without a feedback mechanism, that information is discarded and the same false positive will be generated again next week.

**The retroactive taint correction cascade:**
When an analyst marks address A as `CONFIRMED_INNOCENT`, the system must:
1. Set A's risk_score = 0.0 and category = CLEAN
2. Find all addresses that received taint from A (within 2 hops)
3. Recompute their taint without A's contribution
4. If their taint drops below the WATCHLISTED threshold, reclassify them as CLEAN
5. Emit webhooks for all reclassified addresses (integrating systems need to know)

This cascade is computationally bounded because taint decays with each hop — beyond 3 hops, the contribution from any single address is too small to affect the final category.

```python
@app.post("/feedback/{address}")
async def record_analyst_feedback(
    address:   str,
    verdict:   Literal['CONFIRMED_CRIMINAL', 'CONFIRMED_INNOCENT', 'UNCERTAIN'],
    analyst_id: str,
    notes:     str,
    db:        AsyncSession = Depends(get_db),
    audit_log: AuditLogger  = Depends(get_audit_logger),
):
    """
    Process analyst feedback with full retroactive correction.
    """
    # Immutable audit record first (before any state change)
    await audit_log.record(
        action      = 'ANALYST_FEEDBACK',
        analyst_id  = analyst_id,
        address     = address,
        verdict     = verdict,
        timestamp   = datetime.utcnow(),
        notes       = notes,
    )

    if verdict == 'CONFIRMED_INNOCENT':
        # Update address record
        await db.execute(
            "UPDATE btc_addresses SET risk_category='CLEAN', risk_score=0.0, "
            "analyst_verified=true WHERE address=:addr",
            {'addr': address}
        )

        # Find 1-hop and 2-hop downstream addresses that received taint from this address
        downstream = await get_taint_downstream(address, max_hops=2, db=db)

        # Retroactive taint recomputation for each downstream address
        for downstream_addr in downstream:
            new_score = await recompute_taint_without(downstream_addr, address, db)
            if new_score < WATCHLISTED_THRESHOLD:
                await db.execute(
                    "UPDATE btc_addresses SET risk_category='CLEAN', risk_score=:score "
                    "WHERE address=:addr",
                    {'score': new_score, 'addr': downstream_addr}
                )
                # Emit webhook to notify integrated systems
                await emit_reclassification_webhook(downstream_addr, 'WATCHLISTED', 'CLEAN')

        # Create negative training example for classifier retraining
        await active_learning_queue.add_negative_example(address, notes)

    elif verdict == 'CONFIRMED_CRIMINAL':
        # Strengthen taint for downstream addresses
        downstream = await get_taint_downstream(address, max_hops=2, db=db)
        for downstream_addr in downstream:
            new_score = await recompute_taint_strengthened(downstream_addr, address, db)
            if new_score > BLACKLISTED_THRESHOLD:
                await db.execute(
                    "UPDATE btc_addresses SET risk_category='BLACKLISTED', risk_score=:score "
                    "WHERE address=:addr",
                    {'score': new_score, 'addr': downstream_addr}
                )

    return {'status': 'processed', 'address': address, 'verdict': verdict}
```

---

## 12. Layer 10 — API & Integration Layer

**Why FastAPI and NOT Flask:**
FastAPI provides automatic OpenAPI documentation generation, native async support (critical for the 200ms P99 latency requirement — blocking I/O in Flask would exceed this), Pydantic input validation, and native dependency injection for database sessions. Flask requires third-party packages for all of these. For a production API that law enforcement tools will integrate with, automatic API documentation is required, not optional.

**Why gRPC alongside REST:**
REST with JSON has overhead (~15–20% of CPU budget on high-throughput endpoints) from JSON serialisation. For exchange integrations doing batch screening at 10,000+ addresses/hour, gRPC with Protobuf serialisation reduces this to ~3% overhead. REST is provided for human-readable API use; gRPC is provided for machine-to-machine high-throughput integration.

**Why STIX 2.1 export:**
STIX (Structured Threat Information eXpression) is the ISO standard for threat intelligence sharing. Law enforcement agencies, ISACs (Information Sharing and Analysis Centers), and financial intelligence units (FIUs) expect STIX format. If BTC-Intel produces non-STIX output, it cannot share intelligence with any standardised threat intelligence platform (MISP, OpenCTI, ThreatConnect).

---

## 13. Layer 11 — Threat Intelligence Dashboard (Production)

**Why React + TypeScript and NOT Streamlit (which was fine for POC):**
Streamlit rerenders the entire page on each interaction. For a dashboard used by analysts running complex graph queries, this latency is unacceptable. React's component model allows incremental updates — changing one address's status doesn't reload the entire investigation. TypeScript adds type safety across the frontend codebase, which is required for a multi-developer production team.

**Why Neo4j Bloom and NOT D3.js for graph visualisation:**
D3.js requires building the visualisation layer from scratch. Neo4j Bloom provides an interactive graph explorer with relationship-aware layouts, entity type colouring, and drill-down into node properties — all without custom development. Bloom connects directly to your Neo4j instance and has a cypher passthrough for custom queries.

---

## 14. Infrastructure: Justified Technology Choices

| Layer | POC Choice | Production Choice | Why Upgraded |
|-------|-----------|------------------|--------------|
| Message bus | None (batch) | Apache Kafka | Decouples acquisition from extraction; replay capability; horizontal scaling |
| Blockchain data | BigQuery | Bitcoin Full Node + ElectrumX | Real-time, no API cost, no dependency |
| Crawler | Pre-crawled archive | 6× Tor instances + Splash | Live intelligence, not stale archives |
| Graph DB | Neo4j Community | Neo4j Enterprise | No 4GB heap limit; clustering; RBAC for multi-analyst access |
| Relational DB | PostgreSQL (single) | PostgreSQL (primary + read replicas) | Query load from API doesn't hit the write primary |
| Similarity search | Linear scan | FAISS vector index | <5ms fingerprint search vs. 500ms linear |
| API | Streamlit only | FastAPI (REST) + gRPC | 200ms P99 latency requirement; exchange integrations |
| Frontend | Streamlit | React + TypeScript + Neo4j Bloom | Multi-analyst workspace; production UX |
| Cache | None | Redis | Address lookup cache; reduces PostgreSQL load by ~60% |
| Secrets | Environment variables | HashiCorp Vault | Production secret management; rotation; audit log |
| Monitoring | None | Prometheus + Grafana + PagerDuty | 99.5% uptime SLA requires automated alerting |
| Log management | stdout | ELK Stack (Elasticsearch + Kibana) | Structured log search; anomaly detection on system logs |

---

## 15. Complete Database Schema (Production)

```sql
-- =====================================================
-- CORE TABLES
-- =====================================================

CREATE TABLE btc_addresses (
    address              TEXT PRIMARY KEY,
    address_type         TEXT NOT NULL,   -- P2PKH | P2SH | BECH32 | BECH32M | P2TR
    cluster_id           TEXT,
    cluster_confidence   FLOAT,           -- Multi-heuristic vote confidence
    cluster_version      INTEGER DEFAULT 1, -- Increments on cluster updates
    service_type         TEXT,
    service_confidence   FLOAT,
    risk_category        TEXT NOT NULL DEFAULT 'CLEAN',
    risk_score           FLOAT NOT NULL DEFAULT 0.0,
    risk_version         INTEGER DEFAULT 1,
    first_seen_btc       TIMESTAMPTZ,
    first_seen_dw        TIMESTAMPTZ,
    last_active_btc      TIMESTAMPTZ,
    analyst_verified     BOOLEAN DEFAULT FALSE,
    analyst_verdict      TEXT,   -- CONFIRMED_CRIMINAL | CONFIRMED_INNOCENT | UNCERTAIN
    audit_hash           TEXT,   -- SHA-256 of (address, risk_score, risk_category, timestamp)
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    updated_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_addresses_risk_category ON btc_addresses(risk_category);
CREATE INDEX idx_addresses_cluster ON btc_addresses(cluster_id);
CREATE INDEX idx_addresses_first_seen_dw ON btc_addresses(first_seen_dw);

-- =====================================================
-- PRE-CRIME WATCHLIST
-- =====================================================

CREATE TABLE pre_crime_watchlist (
    address              TEXT PRIMARY KEY REFERENCES btc_addresses(address),
    onion_domain         TEXT NOT NULL,
    page_url             TEXT NOT NULL,
    page_archive_key     TEXT,   -- MinIO object key for archived page
    first_seen_dw        TIMESTAMPTZ NOT NULL,
    dw_confidence        FLOAT NOT NULL,
    pgp_fingerprints     TEXT[],
    aliases              TEXT[],
    page_topic           TEXT,   -- DRUG | WEAPON | FRAUD | COUNTERFEIT | UNKNOWN
    listing_amount_sat   BIGINT, -- Parsed listing price in satoshi (null if not parseable)
    monitoring_status    TEXT NOT NULL DEFAULT 'ACTIVE',
    first_tx_hash        TEXT,   -- Set when first on-chain transaction detected
    first_tx_at          TIMESTAMPTZ,
    first_tx_amount_sat  BIGINT, -- Was it the same as listing_amount? Evidence strength
    amount_match         BOOLEAN, -- first_tx_amount ≈ listing_amount?
    triggered_at         TIMESTAMPTZ,
    expired_at           TIMESTAMPTZ
);

-- =====================================================
-- EVIDENCE TABLES
-- =====================================================

CREATE TABLE evidence (
    id               SERIAL PRIMARY KEY,
    address          TEXT REFERENCES btc_addresses(address),
    evidence_type    TEXT NOT NULL,
    evidence_value   TEXT,
    source           TEXT NOT NULL,
    confidence       FLOAT NOT NULL,
    lr_value         FLOAT,
    lr_contribution  FLOAT,
    provenance_chain TEXT[],  -- Tracks circular dependency
    valid_from       TIMESTAMPTZ DEFAULT NOW(),
    valid_until      TIMESTAMPTZ,  -- Evidence can expire (e.g., 90-day DW retention)
    created_at       TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_evidence_address ON evidence(address);
CREATE INDEX idx_evidence_type ON evidence(evidence_type);

-- =====================================================
-- ENTITY RESOLUTION TABLES
-- =====================================================

CREATE TABLE entities (
    entity_id              TEXT PRIMARY KEY,
    entity_type            TEXT,   -- VENDOR | MARKET | MIXER | INDIVIDUAL | SERVICE
    resolution_confidence  FLOAT NOT NULL,
    first_evidence         TIMESTAMPTZ,
    last_evidence          TIMESTAMPTZ,
    analyst_verified       BOOLEAN DEFAULT FALSE,
    active                 BOOLEAN DEFAULT TRUE
);

CREATE TABLE entity_evidence (
    entity_id      TEXT REFERENCES entities(entity_id),
    evidence_type  TEXT NOT NULL,  -- WALLET | PGP | ALIAS | DOMAIN
    evidence_value TEXT NOT NULL,
    confidence     FLOAT NOT NULL,
    first_seen     TIMESTAMPTZ DEFAULT NOW(),
    last_seen      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (entity_id, evidence_type, evidence_value)
);

CREATE TABLE entity_events (
    id           SERIAL PRIMARY KEY,
    event_type   TEXT NOT NULL,  -- MERGE | SPLIT | KEY_ROTATION | TAKEOVER
    entity_ids   TEXT[] NOT NULL,
    evidence     JSONB,
    confidence   FLOAT NOT NULL,
    occurred_at  TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- BEHAVIORAL ANALYSIS TABLES
-- =====================================================

CREATE TABLE behavioral_features (
    address          TEXT REFERENCES btc_addresses(address),
    computed_at      TIMESTAMPTZ NOT NULL,
    window_days      INTEGER NOT NULL,
    tx_count         INTEGER,
    volume_btc       FLOAT,
    distinct_senders INTEGER,
    distinct_recs    INTEGER,
    anomaly_score    FLOAT,
    fingerprint_vec  FLOAT[],  -- 64-dim behavioral fingerprint
    PRIMARY KEY (address, computed_at, window_days)
);

CREATE TABLE fingerprint_library (
    id              SERIAL PRIMARY KEY,
    address         TEXT REFERENCES btc_addresses(address),
    entity_type     TEXT,
    label           TEXT,   -- OFAC_CONFIRMED | KNOWN_EXCHANGE | UNKNOWN
    fingerprint_vec FLOAT[] NOT NULL,
    computed_at     TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- ANALYST FEEDBACK TABLES
-- =====================================================

CREATE TABLE analyst_feedback (
    id                   SERIAL PRIMARY KEY,
    address              TEXT NOT NULL,
    verdict              TEXT NOT NULL CHECK (verdict IN ('CONFIRMED_CRIMINAL','CONFIRMED_INNOCENT','UNCERTAIN')),
    analyst_id           TEXT NOT NULL,
    notes                TEXT,
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    retroactive_applied  BOOLEAN DEFAULT FALSE,
    cascade_affected     TEXT[],  -- Addresses whose scores were updated due to this feedback
    audit_hash           TEXT NOT NULL  -- Immutable audit record
);

-- =====================================================
-- AUDIT LOG (IMMUTABLE)
-- =====================================================

CREATE TABLE audit_log (
    id           BIGSERIAL PRIMARY KEY,
    action       TEXT NOT NULL,
    actor        TEXT NOT NULL,  -- analyst_id or 'SYSTEM'
    resource     TEXT,           -- address or entity_id
    old_value    JSONB,
    new_value    JSONB,
    timestamp    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sig          TEXT NOT NULL  -- HMAC-SHA256(id||action||actor||resource||timestamp, audit_key)
);

-- Audit log is append-only — no UPDATE or DELETE grants on this table
REVOKE UPDATE, DELETE ON audit_log FROM btc_intel_app;
```

---

## 16. Security, Compliance & Legal Framework

### GDPR Compliance

**Why GDPR matters for BTC-Intel:**
BTC-Intel stores PGP public keys and pseudonymous identifiers (Bitcoin addresses, dark web aliases). The GDPR's position on pseudonymous identifiers (Article 4(1)) is that they constitute personal data if re-identification is possible — which is exactly what BTC-Intel is doing. Academic research under IRB approval provides a legal basis (Article 89), but must be explicitly documented.

**Data minimisation (Article 5(1)(c)):**
- Raw dark web HTML pages: retain 90 days, then delete raw bytes (keep extracted metadata only)
- PGP public keys: retain as long as the associated entity is active in the system
- Bitcoin addresses: no deletion (public blockchain data)
- Analyst feedback: retain indefinitely as part of system quality record

**Data retention configuration:**
```yaml
# config/retention.yml
retention:
  raw_page_bytes: 90  # days
  dark_web_metadata: 365  # days
  evidence_records: 730  # days (2 years)
  analyst_feedback: forever
  audit_log: forever  # Legal requirement
```

### IRB / Ethics Approval

Before crawling dark web sites or processing dark web content in a research context, obtain Institutional Review Board (IRB) approval. The application should document:
- The research is passive observation (no participation in criminal activity)
- No personal data from non-criminal users is collected
- Data minimisation and retention policies
- The research produces a net positive public benefit (reducing criminal finance)

### Audit Log Integrity

The audit log uses HMAC-SHA256 signing to prevent tampering. Each row's signature covers: `id || action || actor || resource || timestamp`, signed with a rotating audit key stored in HashiCorp Vault. If an audit log row is modified, the HMAC check fails and triggers an alert. This is required for legal chain-of-custody admissibility.

---

## 17. Model Versioning & Drift Management

**Why model drift is a production-critical issue:**
Bitcoin usage patterns evolve: CoinJoin adoption increases, new address types emerge (Taproot), Lightning Network grows. A behavioral anomaly detection model trained on 2023 data will have decreasing precision on 2025 data as the "normal" transaction patterns shift.

**Production drift management:**

```python
class ModelVersionManager:
    """
    Tracks model versions, detects precision drift, and triggers retraining.
    """
    def compute_drift_signal(self, model_version: str,
                              recent_fp_rate: float,
                              historical_fp_rate: float) -> str:
        """
        Returns: 'STABLE' | 'DRIFT_WARNING' | 'RETRAIN_REQUIRED'
        """
        drift_ratio = recent_fp_rate / max(historical_fp_rate, 0.001)
        if drift_ratio > 2.0:
            return 'RETRAIN_REQUIRED'    # FP rate doubled — model is stale
        elif drift_ratio > 1.5:
            return 'DRIFT_WARNING'       # 50% degradation — monitor closely
        return 'STABLE'

    def retrain_schedule(self) -> str:
        """
        Retraining trigger conditions:
        1. Automated: FP rate > 2× historical baseline
        2. Scheduled: Quarterly regardless of drift signal
        3. Event-triggered: New major Bitcoin protocol upgrade (Taproot, LN major release)
        """
        return "quarterly_or_drift_triggered"
```

---

## 18. Production Build Roadmap (16 Weeks Post-POC)

| Week | Layer | Milestone | Validates |
|------|-------|-----------|-----------|
| 1–2 | Infrastructure | Kafka + Bitcoin full node + ElectrumX setup | Production data pipeline |
| 3–4 | Layer 1 | Live Tor crawler cluster (6 instances + Splash) | Real-time DW acquisition |
| 5 | Layer 2 | Fine-tuned spaCy + PDF extractor + amount parser | Extraction accuracy |
| 6 | Layer 3 | Temporal entity tracking + entity events | Entity continuity |
| 7 | Layer 4 | UTXO-level clustering + cross-chain bridge detection | Precision improvement |
| 8 | Layer 5 | Service recognition with CIO feedback loop | Pipeline order correctness |
| 9 | Layer 6 | Full temporal features + FAISS fingerprint library | Behavioral analysis |
| 10–11 | Layer 7 | Calibrated Bayesian fusion + ensemble propagation | Evidence quality |
| 11 | Layer 8 | SHAP + counterfactual generator + contradiction detection | Explainability coverage |
| 12 | Layer 9 | Analyst feedback + retroactive correction cascade | Quality improvement loop |
| 13 | Layer 10 | FastAPI REST + gRPC + STIX 2.1 export | Integration readiness |
| 14 | Layer 11 | React dashboard + Neo4j Bloom + audit log viewer | Analyst usability |
| 15 | Security | GDPR compliance audit + IRB documentation + Vault | Legal defensibility |
| 16 | Operations | Prometheus + Grafana + PagerDuty + load testing | SLA validation |

---

## 19. Operational Runbook: What Happens When Things Break

| Failure | Detection | Response | Recovery |
|---------|-----------|----------|----------|
| Bitcoin node falls behind | Grafana: block lag > 2 hours | Alert on-call; switch to Blockchair Pro API | Resync node; switch back when caught up |
| Tor crawler blocked | Grafana: page success rate < 50% | Rotate Tor circuit identities; reduce crawl rate | New Tor exit guard node |
| Kafka consumer lag > 100k messages | Grafana: consumer lag alert | Scale extraction workers horizontally | Lag clears within 30 minutes |
| PostgreSQL primary fails | PgBouncer detects connection failure | Promote read replica to primary | 2–5 minute RTO |
| False positive rate spikes | Analyst feedback rate > 10% in 24 hours | Trigger emergency model evaluation | Roll back to previous model version |
| Audit log HMAC verification fails | Automated HMAC check on every audit insert | Immediate alert to security team | Legal review required before proceeding |
| Neo4j heap exhausted (Enterprise) | JVM OOM alarm | Increase heap allocation; add RAM | 15-minute downtime |

---

*This plan represents the full production target. The POC validates that the algorithms work. This plan validates that the algorithms work at scale, reliably, legally, and with the operational controls required for enterprise deployment. Build the POC first, validate it, then use this document as the specification for the production system.*
