# BTC-Intel: POC / MVP Implementation Plan
## Proof-of-Concept → Working Demonstrable Model
### Layer-Wise Architecture with Full Justification

> **Document Purpose:** This is the first of two implementation plans. This plan covers the POC (Proof of Concept) — a working, demonstrable model that can be presented to professors, investors, or collaborators as evidence the system works. It is NOT a production system. Every architectural choice is justified and contrasted against alternatives that were considered and rejected.

---

## Table of Contents

1. [POC Philosophy: What "Working Model" Actually Means](#1-poc-philosophy)
2. [High-Level POC Architecture](#2-high-level-poc-architecture)
3. [Layer 0 — Baseline Validation (Week 1)](#3-layer-0--baseline-validation)
4. [Layer 1 — Data Acquisition Layer (Weeks 1–2)](#4-layer-1--data-acquisition-layer)
5. [Layer 2 — Address Clustering Layer (Weeks 2–3)](#5-layer-2--address-clustering-layer)
6. [Layer 3 — Service Recognition Layer (Week 3)](#6-layer-3--service-recognition-layer)
7. [Layer 4 — Risk Propagation Layer (Week 4)](#7-layer-4--risk-propagation-layer)
8. [Layer 5 — Pre-Crime Intelligence Layer (Weeks 5–6)](#8-layer-5--pre-crime-intelligence-layer)
9. [Layer 6 — Risk Engine (Weeks 7–8)](#9-layer-6--risk-engine)
10. [Layer 7 — Evaluation Framework (Week 9)](#10-layer-7--evaluation-framework)
11. [Layer 8 — Dashboard (Week 10)](#11-layer-8--dashboard)
12. [POC Tech Stack: Justified Choices](#12-poc-tech-stack-justified-choices)
13. [Database Schema (POC Version)](#13-database-schema-poc-version)
14. [POC Evaluation Targets and Success Criteria](#14-poc-evaluation-targets-and-success-criteria)
15. [What the POC Does NOT Solve (By Design)](#15-what-the-poc-does-not-solve-by-design)

---

## 1. POC Philosophy: What "Working Model" Actually Means

A POC is not a production system. It is not even an MVP. It is the **minimum working demonstration** that proves the core hypothesis: that combining dark web intelligence with blockchain graph analysis produces a meaningful improvement over existing single-source approaches.

The POC needs to answer exactly three questions:

**Question 1:** Can you extract Bitcoin addresses from dark web content and link them to OFAC-confirmed criminal entities through blockchain graph analysis?  
**Question 2:** Does this dark web + blockchain combination produce higher precision or better recall than single-hop OFAC taint alone (the naive baseline)?  
**Question 3:** Can you demonstrate a wallet being classified as PRE_CRIME (flagged via dark web before its first transaction) and then confirmed as BLACKLISTED (after its first criminal transaction)?

If the POC answers these three questions with measured, defensible numbers, it is sufficient to present at a research level and to build the MVP on top of.

**POC Scope Boundaries:**
- Analyzes 50–100 OFAC seed addresses and their 3-hop clusters (not the full Bitcoin graph)
- Uses BigQuery for blockchain data (no Bitcoin full node required)
- Dark web component processes a small pre-crawled sample (not a live crawler in the POC)
- Dashboard is Streamlit (not a production web application)
- No real-time monitoring; batch processing only
- Evaluation is on a labeled test set, not live data

---

## 2. High-Level POC Architecture

```
┌─────────────────────────────────────────────────────────┐
│              DATA LAYER (Static for POC)                 │
│  OFAC SDN XML     │  BigQuery Bitcoin Dataset            │
│  Elliptic Dataset │  WalletExplorer Labels               │
│  Pre-crawled DW   │  Chainabuse API                      │
│  sample pages     │                                       │
└──────────┬──────────────────────┬────────────────────────┘
           │                      │
┌──────────▼──────────────────────▼────────────────────────┐
│              PROCESSING LAYER                             │
│  ┌─────────────────────┐  ┌────────────────────────────┐ │
│  │  ADDRESS CLUSTERER   │  │  DARK WEB EXTRACTOR        │ │
│  │  CIO + CoinJoin      │  │  BTC address extraction    │ │
│  │  filter + LN filter  │  │  PGP extraction            │ │
│  │  NetworkX union-find │  │  Context classification    │ │
│  └──────────┬──────────┘  └────────────┬───────────────┘ │
│             │                           │                  │
│  ┌──────────▼───────────────────────────▼──────────────┐  │
│  │           ENTITY RESOLUTION                          │  │
│  │  PGP → Wallet linkage                               │  │
│  │  Alias normalisation (Jaro-Winkler)                 │  │
│  │  Neo4j entity graph                                 │  │
│  └───────────────────────────┬──────────────────────────┘  │
│                               │                              │
│  ┌────────────────────────────▼──────────────────────────┐  │
│  │           SERVICE RECOGNITION                          │  │
│  │  ExchangeDetector │ MixerDetector │ PoolDetector      │  │
│  └───────────────────────────┬──────────────────────────┘  │
│                               │                              │
│  ┌────────────────────────────▼──────────────────────────┐  │
│  │           RISK ENGINE (3-Layer)                       │  │
│  │  Layer 1: Rule-based fast path                        │  │
│  │  Layer 2: Bayesian fusion (calibrated LRs)            │  │
│  │  Layer 3: Isolation Forest anomaly detection          │  │
│  └───────────────────────────┬──────────────────────────┘  │
└─────────────────────────────┬────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────┐
│              OUTPUT LAYER                                 │
│  PostgreSQL (risk scores, evidence)                       │
│  Neo4j (entity graph)                                     │
│  Streamlit Dashboard                                      │
│  Evaluation Report (precision/recall/F1/FPR)             │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Layer 0 — Baseline Validation (Week 1)

**Purpose:** Reproduce a published result before building anything new. This is not optional. If you cannot reproduce a published baseline, your methodology has a bug.

**What to do:**
Reproduce the Random Forest classifier from Peled et al. (2021) on the Elliptic Bitcoin Dataset (available on Kaggle). The published result is 95% precision at 40% recall on the illicit class.

**Why this layer first (before any other work):**
- If your implementation of the pipeline cannot match published results on a known dataset, something is fundamentally wrong
- This step validates your Python environment, your feature engineering code, and your data loading pipeline
- The reproduced baseline IS your comparison baseline for the entire project — you need it before you can claim your system improves on it
- This takes 1 week, not more — the Elliptic dataset and a Random Forest are straightforward

**Why Elliptic Dataset and NOT something else:**
- It is the only publicly available labeled Bitcoin transaction dataset with academic credibility
- Used in 50+ published papers, so any reviewer knows it
- Contains 166 pre-computed features per transaction — you don't need BigQuery for this step
- The 2% illicit class is realistic (real-world class imbalance) and tests your system under the same conditions as production

**Why NOT start with BigQuery directly:**
BigQuery clustering takes longer to set up and debug. The Elliptic dataset lets you validate your ML pipeline in isolation before adding the data acquisition complexity.

**Deliverable for Week 1:**
```
results/elliptic_baseline.json:
{
  "model": "RandomForestClassifier",
  "precision_illicit": 0.95,
  "recall_illicit": 0.40,
  "f1_illicit": 0.57,
  "auc_roc": 0.98,
  "published_precision": 0.95,
  "match": true
}
```

---

## 4. Layer 1 — Data Acquisition Layer (Weeks 1–2)

**Purpose:** Establish the ground truth seed set and blockchain data access.

### Sub-Layer 1A: OFAC SDN XML Parser

**What it does:**
Downloads and parses the OFAC Specially Designated Nationals (SDN) XML file to extract all confirmed cryptocurrency addresses.

```python
import xml.etree.ElementTree as ET
import requests

def fetch_ofac_btc_addresses() -> list[dict]:
    """
    Downloads OFAC SDN XML and extracts all Bitcoin addresses.
    Free, no API key. Updated by OFAC irregularly.
    """
    url = "https://www.treasury.gov/ofac/downloads/sdn.xml"
    response = requests.get(url, timeout=60)
    root = ET.fromstring(response.content)

    ns = {'ofac': 'http://tempuri.org/sdnList.xsd'}
    addresses = []

    for entity in root.findall('.//ofac:sdnEntry', ns):
        name = entity.findtext('ofac:lastName', namespaces=ns)
        for feature in entity.findall('.//ofac:feature', ns):
            if feature.findtext('ofac:featureType', namespaces=ns) == 'Digital Currency Address':
                addr_val = feature.findtext('.//ofac:value', namespaces=ns)
                if addr_val:
                    addresses.append({
                        'address': addr_val.strip(),
                        'entity_name': name,
                        'source': 'OFAC_SDN',
                        'confidence': 1.0  # OFAC is ground truth
                    })
    return addresses
```

**Why OFAC and not community databases (Chainabuse, etc.) as primary:**
OFAC addresses are legally authoritative. They are confirmed by U.S. government enforcement actions with public legal basis. Community databases have no verification mechanism — a fraudster can file a report against any address. OFAC is the only indisputable ground truth for the seed set.

**Why NOT use Chainalysis or TRM labels as seeds:**
These are commercial labels with unknown methodology. Using them as ground truth introduces circular reasoning — you cannot evaluate your system against labels that may have been produced by a similar system.

---

### Sub-Layer 1B: BigQuery Bitcoin Data Access

**What it does:**
Queries Google BigQuery's `bigquery-public-data.crypto_bitcoin` dataset for all transactions involving OFAC seed addresses and their clusters.

**Why BigQuery and NOT a local Bitcoin node:**
For the POC, a Bitcoin full node takes 620GB of disk and 3–7 days to sync. BigQuery gives the same data coverage via SQL in minutes. BigQuery is also perfectly reproducible — anyone with a Google account can run the same query and get the same result, which is essential for a research paper.

**Why NOT Blockstream API or Mempool.space:**
Both APIs have rate limits that make historical clustering infeasible. Blockstream: ~0.5 req/sec sustainable; a cluster of 5,000 addresses with 10 transactions each = 50,000 API calls = 100,000 seconds = 28 hours per cluster. Unacceptable for a research POC.

**Core BigQuery queries:**

```sql
-- Query 1: Find all transactions where an OFAC address appears as input
-- (Establishes outbound transaction graph from OFAC addresses)
WITH ofac_addrs AS (
    SELECT addr FROM UNNEST(@ofac_seed_list) AS addr
),
seed_txns AS (
    SELECT DISTINCT i.spent_transaction_hash AS txn_hash, i.addresses[OFFSET(0)] AS seed_addr
    FROM `bigquery-public-data.crypto_bitcoin.inputs` i
    WHERE i.addresses[OFFSET(0)] IN (SELECT addr FROM ofac_addrs)
)
SELECT st.txn_hash, st.seed_addr,
       o.addresses[OFFSET(0)] AS recipient_addr,
       o.value AS value_satoshi
FROM seed_txns st
JOIN `bigquery-public-data.crypto_bitcoin.outputs` o
  ON o.transaction_hash = st.txn_hash
LIMIT 100000;

-- Query 2: CIO expansion (1 hop) — find all co-input addresses
WITH seed_txns AS (
    SELECT DISTINCT spent_transaction_hash AS txn_hash
    FROM `bigquery-public-data.crypto_bitcoin.inputs`
    WHERE addresses[OFFSET(0)] IN UNNEST(@ofac_seed_list)
),
co_inputs AS (
    SELECT DISTINCT i2.addresses[OFFSET(0)] AS co_address
    FROM seed_txns st
    JOIN `bigquery-public-data.crypto_bitcoin.inputs` i2
      ON i2.spent_transaction_hash = st.txn_hash
    WHERE i2.addresses[OFFSET(0)] NOT IN UNNEST(@ofac_seed_list)
)
SELECT co_address FROM co_inputs;
```

**Estimated BigQuery cost for POC:**
- 50 OFAC seed addresses, 3-hop CIO expansion: ~200–400GB processed
- Free tier: 1TB/month — sufficient for POC
- Beyond free tier: $5/TB = $1–2 for this workload

---

### Sub-Layer 1C: Dark Web Sample Acquisition (POC Simplified Version)

**POC approach:** For the POC, use a **pre-crawled static sample** rather than a live Tor crawler. This eliminates Tor dependency, speeds up development, and allows reproducible evaluation.

**Sources for pre-crawled dark web data:**
- The Gwern dark web market archives (publicly available, archived historical market data)
- The DUTA dataset (Dark web URLs and Text for Academic Research)
- Cached pages from known market snapshots available in academic repositories

**Why NOT a live Tor crawler for the POC:**
Live Tor crawling adds significant complexity: Tor circuit management, rate limiting, JavaScript rendering (Splash or Selenium), page deduplication, storage management. For a POC, this complexity obscures whether your core algorithms work. The POC should prove the pipeline; the MVP adds the live crawler.

**What the sample must contain:**
At minimum, a set of dark web pages that contain Bitcoin addresses known to the OFAC list, to demonstrate end-to-end linkage from dark web content to confirmed criminal address.

---

## 5. Layer 2 — Address Clustering Layer (Weeks 2–3)

**Purpose:** Group Bitcoin addresses that belong to the same entity using CIO and change address heuristics, with protective filters.

**Why this layer exists:**
A single Bitcoin entity (criminal or legitimate) typically controls thousands of addresses, generating a new address for each transaction for privacy. Clustering groups these addresses into wallets. Without clustering, your analysis treats each address as a separate entity — like treating each phone call a criminal makes as a different criminal.

**Why CIO and NOT other approaches:**
CIO is the only heuristic with cryptographic basis: addresses that co-sign a transaction provably share private key material (they signed with the same key or a key held by the same entity). Other heuristics (change address, address reuse) are probabilistic. CIO is deterministic. Start with the deterministic signal.

**Why NOT use a commercial clustering service:**
Chainalysis and TRM provide clustering as a service but their cluster memberships are opaque proprietary outputs that cannot be cited in a research paper without revealing commercial dependencies. For research reproducibility, you must be able to show your clustering algorithm.

### Implementation

```python
from collections import defaultdict
from collections import Counter
from dataclasses import dataclass

@dataclass
class Transaction:
    txid: str
    inputs: list   # list of {address, value}
    outputs: list  # list of {address, value}
    timestamp: int

class AddressClusterer:
    """
    CIO clustering with three protective filters.
    Uses Union-Find (disjoint set) data structure for O(α(n)) merge time.
    """

    COINJOIN_THRESHOLD = 0.40  # ≥40% identical output values = likely CoinJoin
    MAX_CLUSTER_SIZE = 10_000  # Clusters > 10k addresses flagged for review
    LN_MULTISIG_PATTERNS = [
        'OP_2 {} {} OP_2 OP_CHECKMULTISIG',  # P2MS Lightning channel
    ]

    def __init__(self):
        self.parent = {}   # Union-Find parent map
        self.rank   = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x]   = 0
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1

    def is_coinjoin(self, tx: Transaction) -> bool:
        """
        Equal-output detection: if ≥40% of outputs have the same satoshi value
        AND there are ≥5 outputs, this is likely a CoinJoin coordination.
        Wasabi uses 0.1 BTC denominations; JoinMarket uses variable amounts.
        The 40% threshold comes from the AddressClusterer paper (2403.00523).
        """
        if len(tx.outputs) < 5:
            return False
        values     = [o['value'] for o in tx.outputs]
        max_freq   = Counter(values).most_common(1)[0][1]
        return max_freq / len(values) >= self.COINJOIN_THRESHOLD

    def is_lightning_channel(self, tx: Transaction) -> bool:
        """
        Lightning Network channel funding transactions use 2-of-2 multisig.
        These look like criminal co-signing to CIO but are NOT — the two
        parties are independent channel partners, not the same entity.
        Filter: 2-of-2 multisig input = skip CIO.
        """
        for inp in tx.inputs:
            script = inp.get('script_asm', '')
            if 'OP_2' in script and 'OP_CHECKMULTISIG' in script:
                return True
            # P2WSH Lightning (modern): OP_0 <hash> — 32-byte push in witness
            if inp.get('witness_script_type') == 'p2wsh_2of2':
                return True
        return False

    def cio_cluster(self, tx: Transaction) -> None:
        """Apply CIO heuristic: merge all input addresses into one cluster."""
        if len(tx.inputs) < 2:
            return  # Single-input: no co-ownership signal

        if self.is_coinjoin(tx):
            return  # CoinJoin: inputs are NOT co-owned

        if self.is_lightning_channel(tx):
            return  # LN channel: participants are NOT co-owned

        input_addrs = [inp['address'] for inp in tx.inputs if inp.get('address')]
        if len(input_addrs) < 2:
            return

        # Merge all input addresses into one cluster
        for i in range(1, len(input_addrs)):
            self.union(input_addrs[0], input_addrs[i])

    def change_address_heuristic(self, tx: Transaction) -> str | None:
        """
        Script-type variant ONLY (lowest false positive rate per Delgado 2021).
        
        Why script-type and NOT naive (odd amount to new address):
        The naive heuristic has 23% FPR on SegWit transactions because SegWit
        addresses look structurally different from P2PKH regardless of amount.
        Script-type matching asks: "which output has the same script type as
        the inputs?" — this is invariant to amount and much more precise.
        
        We do NOT use the naive variant. We do NOT apply this to Taproot (P2TR)
        transactions — Taproot hiding makes script-type inference unreliable.
        """
        if len(tx.outputs) != 2:
            return None  # Only apply to 2-output transactions

        # Determine dominant input script type
        script_types = [inp.get('script_type') for inp in tx.inputs if inp.get('script_type')]
        if not script_types:
            return None

        dominant_type = Counter(script_types).most_common(1)[0][0]
        if dominant_type == 'witness_v1_taproot':
            return None  # Taproot: heuristic is unreliable, skip

        # Find change candidates: same script type as inputs + fresh address
        change_candidates = [
            o['address'] for o in tx.outputs
            if o.get('script_type') == dominant_type
            and self.find(o['address']) == o['address']  # Not yet clustered = fresh
        ]

        return change_candidates[0] if len(change_candidates) == 1 else None

    def get_clusters(self) -> dict[str, list[str]]:
        """Returns map of cluster_root → list of member addresses."""
        clusters = defaultdict(list)
        for addr in self.parent:
            clusters[self.find(addr)].append(addr)
        return dict(clusters)
```

**Why Union-Find and NOT graph database clustering:**
Clustering is an offline batch algorithm. Union-Find runs in near-O(n) time for n addresses. Doing the same operation in Neo4j via Cypher MATCH/MERGE would be orders of magnitude slower because every merge requires a graph write transaction. The rule is: **compute clusters in Python, store results in Neo4j.**

**Why NOT hierarchical agglomerative clustering (HAC):**
HAC is designed for continuous similarity metrics. CIO merging is a binary decision — either two addresses co-signed or they didn't. Union-Find is the correct data structure for binary equivalence merging.

---

## 6. Layer 3 — Service Recognition Layer (Week 3)

**Purpose:** Classify each identified cluster as a type of Bitcoin service before risk propagation. This step is non-negotiable in the pipeline order.

**Why BEFORE risk propagation (critical pipeline order):**
Taint propagates differently through different service types:
- **Exchange:** Breaks taint chain (KYC/AML boundary). A criminal depositing to Binance does not contaminate all Binance customers.
- **Mixer/CoinJoin:** Amplifies taint to all outputs (the entire purpose is to mix criminal and clean funds).
- **Mining pool:** Origin-clean (creates new Bitcoin, receives no tainted input by definition).

If you run risk propagation before service recognition, all three service types are treated identically — this produces incorrect taint scores for the majority of flagged addresses.

**Why NOT defer service recognition to a later post-processing step:**
If taint has already propagated through an exchange before you classify it, you'd need to retroactively "untaint" all downstream addresses. This retroactive correction is computationally expensive and error-prone. Getting the pipeline order right is architecturally cheaper than fixing it afterward.

```python
class ServiceClassifier:
    """
    Two-stage: fast known-label lookup, then feature-based detection.
    """

    KNOWN_EXCHANGE_CLUSTERS = {}  # Loaded from WalletExplorer labels
    KNOWN_POOL_ADDRESSES    = set()

    def classify(self, cluster_root: str, cluster_addrs: list[str],
                 cluster_stats: dict) -> dict:
        """
        Returns: {service_type: str, confidence: float, taint_modifier: float}
        taint_modifier:
          0.0 = exchange (breaks chain)
          0.5 = CoinJoin coordinator (pass-through with reduced confidence)
          1.0 = criminal service / unknown (full taint propagation)
          2.0 = mixer (amplifies — all outputs receive full taint)
        """
        # Stage 1: Known label lookup (100% confidence when matched)
        if any(addr in self.KNOWN_EXCHANGE_CLUSTERS for addr in cluster_addrs):
            return {'service_type': 'EXCHANGE', 'confidence': 1.0, 'taint_modifier': 0.0}

        if any(addr in self.KNOWN_POOL_ADDRESSES for addr in cluster_addrs):
            return {'service_type': 'MINING_POOL', 'confidence': 1.0, 'taint_modifier': 0.0}

        # Stage 2: Feature-based detection
        exchange_prob = self._exchange_probability(cluster_stats)
        mixer_signals = self._mixer_signals(cluster_stats)
        pool_prob     = self._pool_probability(cluster_stats)

        if exchange_prob > 0.7:
            return {'service_type': 'EXCHANGE', 'confidence': exchange_prob, 'taint_modifier': 0.0}
        if mixer_signals.get('coinjoin_pattern') and mixer_signals.get('fixed_denomination'):
            return {'service_type': 'COINJOIN_COORDINATOR', 'confidence': 0.85, 'taint_modifier': 0.5}
        if pool_prob > 0.9:
            return {'service_type': 'MINING_POOL', 'confidence': pool_prob, 'taint_modifier': 0.0}

        return {'service_type': 'UNKNOWN', 'confidence': 0.5, 'taint_modifier': 1.0}

    def _exchange_probability(self, stats: dict) -> float:
        score = 0.0
        if stats.get('distinct_senders_90d', 0) > 10_000:   score += 0.30
        elif stats.get('distinct_senders_90d', 0) > 1_000:  score += 0.15
        if stats.get('distinct_recipients_90d', 0) > 10_000: score += 0.25
        if stats.get('has_public_label', False):              score += 0.30
        if stats.get('avg_outputs_per_tx', 0) > 20:          score += 0.10
        return min(score, 1.0)

    def _pool_probability(self, stats: dict) -> float:
        """Mining pools: all input transactions are coinbase (null input hash)."""
        coinbase_fraction = stats.get('coinbase_input_fraction', 0)
        return coinbase_fraction  # If 90%+ inputs are coinbase, it's a pool

    def _mixer_signals(self, stats: dict) -> dict:
        signals = {}
        if stats.get('equal_output_fraction', 0) > 0.40:
            signals['coinjoin_pattern'] = True
        if stats.get('fixed_denomination_fraction', 0) > 0.30:
            signals['fixed_denomination'] = True
        if stats.get('many_in_many_out_fraction', 0) > 0.50:
            signals['many_in_many_out'] = True
        return signals
```

---

## 7. Layer 4 — Risk Propagation Layer (Week 4)

**Purpose:** Propagate risk scores from OFAC seed addresses through the transaction graph to identify addresses that have had financial contact with confirmed criminals.

**Why implement THREE propagation methods:**
This is one of BTC-Intel's publishable contributions (Contribution D from the research paper document). The three-way comparison of taint vs. label propagation vs. PPR on the same dataset fills a documented gap in the literature (Nerino 2021 uses only label propagation; Chainalysis uses only taint). The comparison result — which method is best for which address category — is the measurable output.

```python
import math
import networkx as nx

class RiskPropagator:

    def propagate_taint(self, graph: nx.DiGraph, seed_scores: dict,
                        service_types: dict, max_hops: int = 3) -> dict:
        """
        Amount-weighted taint propagation (Chainalysis method).
        taint(recipient) = taint(sender) × (tainted_value / total_received_value)
        
        Protective thresholds applied:
        - Minimum taint fraction: 5% (below this = dust, ignore)
        - Exchange passthrough: taint_modifier from service classification applied
        - Max hops: 3 (taint decays to noise by hop 3 in most criminal flows)
        """
        taint_scores = dict(seed_scores)  # OFAC seeds start at 1.0

        for hop in range(max_hops):
            new_scores = {}
            for edge in graph.edges(data=True):
                sender, recipient, data = edge
                sender_taint = taint_scores.get(sender, 0.0)
                if sender_taint < 0.05:
                    continue  # Below dust threshold

                # Apply service type modifier
                svc = service_types.get(recipient, {})
                taint_mod = svc.get('taint_modifier', 1.0)
                if taint_mod == 0.0:
                    continue  # Exchange: breaks chain

                tainted_value = data.get('value_satoshi', 0) * sender_taint
                total_received = data.get('total_received_satoshi', data.get('value_satoshi', 1))
                taint_fraction = tainted_value / max(total_received, 1)

                if taint_fraction >= 0.05:  # 5% minimum threshold
                    propagated = taint_fraction * taint_mod
                    new_scores[recipient] = max(new_scores.get(recipient, 0), propagated)

            taint_scores.update(new_scores)

        return taint_scores

    def propagate_label(self, graph: nx.DiGraph, seed_scores: dict,
                        damping: float = 0.85) -> dict:
        """
        Label propagation — propagates both forward (to recipients) and backward
        (to senders). More appropriate for identifying full criminal infrastructure.
        Unlike taint, propagates in both directions.
        """
        scores = dict(seed_scores)
        for _ in range(10):  # 10 iterations = typical convergence
            new_scores = {}
            for node in graph.nodes():
                neighbor_score = 0.0
                for neighbor in list(graph.predecessors(node)) + list(graph.successors(node)):
                    neighbor_score += scores.get(neighbor, 0.0)
                degree = max(graph.degree(node), 1)
                new_scores[node] = (1 - damping) * scores.get(node, 0.0) + \
                                    damping * (neighbor_score / degree)
            scores = new_scores
        return scores

    def propagate_ppr(self, graph: nx.DiGraph, seed_nodes: list,
                       alpha: float = 0.85, iterations: int = 20) -> dict:
        """
        Personalised PageRank from OFAC seed nodes.
        PPR score = structural proximity to criminal seeds (not value-based).
        Less susceptible to dust/haircut problem than taint because it measures
        graph proximity, not value flow.
        """
        personalization = {n: 1.0/len(seed_nodes) for n in seed_nodes}
        # Set all non-seed nodes to 0 in personalization
        for node in graph.nodes():
            if node not in personalization:
                personalization[node] = 0.0
        return nx.pagerank(graph, alpha=alpha, personalization=personalization,
                           max_iter=iterations)
```

---

## 8. Layer 5 — Pre-Crime Intelligence Layer (Weeks 5–6)

**Purpose:** Process dark web content to identify addresses that are listed in payment contexts BEFORE any on-chain transaction. This is the core novel contribution.

**Why this layer is novel:**
Every existing system (Chainalysis, TRM, Elliptic, all academic papers) can only flag an address AFTER it has participated in a suspicious transaction. BTC-Intel is the first system to assign a non-zero risk score to an address with zero transaction history, based solely on its appearance in a dark web payment context.

**Why this matters operationally:**
A cryptocurrency exchange performing KYC/AML checks receives a deposit address before the customer transacts. If BTC-Intel has already identified that deposit address in a dark web drug listing, the exchange can flag the account BEFORE the transaction is confirmed, not after.

```python
import re
import pgpy
from dataclasses import dataclass, field
from datetime import datetime

# Bitcoin address regex patterns
BTC_PATTERNS = {
    'P2PKH':   re.compile(r'\b(1[a-km-zA-HJ-NP-Z1-9]{25,34})\b'),
    'P2SH':    re.compile(r'\b(3[a-km-zA-HJ-NP-Z1-9]{25,34})\b'),
    'BECH32':  re.compile(r'\b(bc1[a-z0-9]{6,87})\b', re.IGNORECASE),
    'BECH32M':  re.compile(r'\b(bc1p[a-z0-9]{6,87})\b', re.IGNORECASE),
}

PAYMENT_CONTEXT_KEYWORDS = {
    'high':   ['send', 'payment', 'pay', 'deposit', 'bitcoin', 'btc', 'wallet',
                'address', 'transfer', 'escrow', 'price', 'checkout', 'order'],
    'medium': ['contact', 'pgp', 'encrypted', 'transaction'],
    'low':    ['bitcoin', 'btc', 'crypto'],
    'exclude': ['victim', 'scam', 'scammer', 'fraud', 'warning', 'reported',
                'stolen', 'hacked', 'phishing']
}

@dataclass
class DarkWebIntelRecord:
    address:          str
    context_type:     str        # PAYMENT | AMBIGUOUS | VICTIM_REPORT
    context_window:   str        # 500-char surrounding text
    pgp_fingerprints: list[str]  # PGP keys found on same page
    aliases:          list[str]  # Vendor/market aliases on same page
    onion_domain:     str
    page_url:         str
    first_seen:       datetime
    confidence:       float      # 0.0–1.0 based on context signals
    page_topic:       str        # From topic classification: DRUG | WEAPON | FRAUD | UNKNOWN

class DarkWebAddressExtractor:

    def extract_from_page(self, html: str, page_url: str,
                          onion_domain: str) -> list[DarkWebIntelRecord]:
        records = []
        # Find all Bitcoin addresses in the page
        all_addrs = {}
        for addr_type, pattern in BTC_PATTERNS.items():
            for match in pattern.finditer(html):
                addr = match.group(0)
                if addr_type in ('BECH32', 'BECH32M'):
                    addr = addr.lower()  # Normalise bech32 to lowercase
                if self._verify_checksum(addr):
                    all_addrs[addr] = match.start()

        for addr, position in all_addrs.items():
            context_text = html[max(0, position-250):position+250]
            context_type, confidence = self._classify_context(context_text)
            pgp_keys    = self._extract_pgp_fingerprints(html)
            aliases     = self._extract_aliases(html)

            records.append(DarkWebIntelRecord(
                address          = addr,
                context_type     = context_type,
                context_window   = context_text,
                pgp_fingerprints = pgp_keys,
                aliases          = aliases,
                onion_domain     = onion_domain,
                page_url         = page_url,
                first_seen       = datetime.utcnow(),
                confidence       = confidence,
                page_topic       = self._classify_topic(html),
            ))

        return records

    def _classify_context(self, context: str) -> tuple[str, float]:
        """
        Classify the context type of a Bitcoin address occurrence.
        Returns (context_type, confidence).
        """
        context_lower = context.lower()

        # Check for victim/scam context first (negating signal)
        if any(kw in context_lower for kw in PAYMENT_CONTEXT_KEYWORDS['exclude']):
            return 'VICTIM_REPORT', 0.1  # Low confidence in criminal classification

        # Count payment context signals
        high_signals   = sum(1 for kw in PAYMENT_CONTEXT_KEYWORDS['high']   if kw in context_lower)
        medium_signals = sum(1 for kw in PAYMENT_CONTEXT_KEYWORDS['medium'] if kw in context_lower)

        if high_signals >= 3:
            return 'PAYMENT', min(0.50 + 0.10 * high_signals, 0.95)
        elif high_signals >= 1:
            return 'PAYMENT', 0.40 + 0.10 * high_signals
        elif medium_signals >= 2:
            return 'AMBIGUOUS', 0.30
        else:
            return 'AMBIGUOUS', 0.15

class PreCrimeWatchlist:
    """
    The novel component: assigns non-zero risk to addresses with zero on-chain history.
    """

    def add_to_watchlist(self, record: DarkWebIntelRecord) -> dict:
        if record.context_type != 'PAYMENT':
            return None  # Only PAYMENT context addresses enter PRE_CRIME_WATCHLIST

        return {
            'address':     record.address,
            'status':      'PRE_CRIME_WATCHLIST',
            'confidence':  record.confidence,
            'evidence': {
                'dark_web_source':  record.onion_domain,
                'page_url':         record.page_url,
                'first_seen_dw':    record.first_seen.isoformat(),
                'pgp_fingerprints': record.pgp_fingerprints,
                'aliases':          record.aliases,
                'topic':            record.page_topic,
            },
            'monitoring':  'ACTIVE',  # Monitor for first on-chain transaction
        }
```

---

## 9. Layer 6 — Risk Engine (Weeks 7–8)

**Purpose:** Combine all signals from previous layers into a final risk classification with full evidence chain.

**Why three layers and NOT just rules:**
A pure rule system (14 hard-coded rules) cannot generalise to new criminal patterns. A pure ML system (black box) cannot explain why a score was assigned, which is legally required for law enforcement use. The three-layer hybrid handles clear cases (rules), ambiguous cases (Bayesian), and novel patterns (anomaly detection).

**Why Bayesian and NOT just weighted averaging:**
Weighted averaging treats all evidence as independent. In practice, OFAC designations and Chainalysis flags share provenance (Chainalysis feeds OFAC and vice versa). Treating them as independent doubles-counts correlated evidence. The Bayesian framework with provenance tracking prevents this.

```python
import math
from dataclasses import dataclass

@dataclass
class RiskDecision:
    address:         str
    category:        str     # CLEAN | WATCHLISTED | BLACKLISTED | PRE_CRIME_WATCHLIST
    final_score:     float   # 0.0–1.0
    evidence:        list[dict]
    counterfactual:  str
    contradictions:  list[str]

class ThreeLayerRiskEngine:

    # --- Layer 1: Rules ---
    def fast_path(self, address: str, signals: dict) -> RiskDecision | None:
        if signals.get('ofac_confirmed'):
            return RiskDecision(address, 'BLACKLISTED', 1.0,
                                [{'source': 'OFAC_SDN', 'contribution': 1.0}],
                                'N/A — deterministic rule', [])
        if signals.get('dust_attack'):
            return RiskDecision(address, 'CLEAN', 0.0,
                                [{'source': 'DUST_FILTER', 'contribution': -1.0}],
                                'N/A — deterministic rule', [])
        if signals.get('exchange_confirmed'):
            return RiskDecision(address, 'CLEAN', 0.05,
                                [{'source': 'EXCHANGE_PASSTHROUGH', 'contribution': -0.95}],
                                'N/A — known exchange', [])
        return None  # No fast path match; go to Layer 2

    # --- Layer 2: Bayesian Fusion ---
    PRIOR_CRIMINAL = 0.001  # 1 in 1000 addresses is criminal (realistic prior)

    LIKELIHOOD_RATIOS = {
        'OFAC_SDN':              1000.0,
        'DARK_WEB_PAYMENT':      50.0,
        'TAINT_HOP_1':           20.0,
        'COMMERCIAL_CONSENSUS':  30.0,
        'VICTIM_CONTEXT':        0.2,    # Exculpatory — reduces probability
        'BEHAVIORAL_ANOMALY':    8.0,
        'COMMUNITY_REPORTS':     5.0,
        'TAINT_HOP_3':           3.0,
    }

    PROVENANCE_CHAINS = {
        # Maps evidence type to its ultimate source(s)
        # Prevents double-counting: if OFAC_SDN is already applied, skip
        # Chainalysis/TRM flags that merely repeat OFAC data
        'COMMERCIAL_TRM':      ['OFAC_SDN'],    # TRM re-labels OFAC addresses
        'COMMERCIAL_CHAINALY': ['OFAC_SDN'],    # Chainalysis re-labels OFAC
    }

    def bayesian_fusion(self, signals: dict) -> tuple[float, list[dict]]:
        """
        Provenance-aware Bayesian update.
        Provenance tracking: if evidence X is derived from evidence Y, and
        Y is already in the active evidence set, skip X to prevent double-counting.
        """
        log_odds = math.log(self.PRIOR_CRIMINAL / (1 - self.PRIOR_CRIMINAL))
        active_sources = set()
        contributions  = []

        # Sort signals by likelihood ratio (apply strongest first for log-odds stability)
        sorted_signals = sorted(signals.items(),
                                key=lambda x: self.LIKELIHOOD_RATIOS.get(x[0], 1.0),
                                reverse=True)

        for sig_type, sig_value in sorted_signals:
            if not sig_value:
                continue

            # Provenance check: skip if this evidence's source is already counted
            provenance = self.PROVENANCE_CHAINS.get(sig_type, [])
            if any(parent in active_sources for parent in provenance):
                continue  # Circular evidence detected, skip

            lr = self.LIKELIHOOD_RATIOS.get(sig_type)
            if lr is None:
                continue

            contribution = math.log(lr)
            log_odds    += contribution
            active_sources.add(sig_type)
            contributions.append({
                'source':       sig_type,
                'lr':           lr,
                'contribution': contribution,
                'log_odds_after': log_odds,
            })

        posterior = 1 / (1 + math.exp(-log_odds))
        return posterior, contributions

    # --- Layer 3: Anomaly Detection ---
    def anomaly_score(self, feature_vector) -> float:
        """
        Isolation Forest anomaly detection.
        Trained on known-clean addresses (WalletExplorer exchange addresses).
        High anomaly score = unusual relative to clean population = suspicious.
        """
        # In POC: use pre-trained model loaded from disk
        raw = self.isolation_forest.decision_function([feature_vector])[0]
        return 1 - (raw - self.isolation_forest.offset_) / (1 - self.isolation_forest.offset_)

    def classify(self, address: str, signals: dict) -> RiskDecision:
        # Layer 1: Fast path
        fast = self.fast_path(address, signals)
        if fast:
            return fast

        # Layer 2: Bayesian
        bayes_score, contributions = self.bayesian_fusion(signals)

        # Layer 3: Anomaly
        if signals.get('feature_vector') is not None:
            anomaly = self.anomaly_score(signals['feature_vector'])
            # Blend anomaly into Bayesian score (anomaly is supplementary, not primary)
            final_score = 0.70 * bayes_score + 0.30 * anomaly
        else:
            final_score = bayes_score

        # Categorise
        if final_score >= 0.85:
            category = 'BLACKLISTED'
        elif final_score >= 0.35:
            category = 'WATCHLISTED'
        elif signals.get('pre_crime_watchlist'):
            category = 'PRE_CRIME_WATCHLIST'
        else:
            category = 'CLEAN'

        # Generate counterfactual
        counterfactual = self._generate_counterfactual(
            address, final_score, contributions, threshold=0.35
        )

        # Detect contradictions
        contradictions = []
        if signals.get('victim_context') and final_score > 0.5:
            contradictions.append(
                f"Victim context classifier flagged as potential victim "
                f"(reduces score by {abs(math.log(0.2)):.2f} log-odds units)"
            )

        return RiskDecision(address, category, final_score, contributions,
                            counterfactual, contradictions)

    def _generate_counterfactual(self, address, score, contributions, threshold) -> str:
        if score <= threshold:
            return f"Address is below WATCHLISTED threshold ({threshold}) — no counterfactual needed."
        cumulative = score
        removal_set = []
        sorted_contribs = sorted(contributions, key=lambda c: abs(c['contribution']), reverse=True)
        for c in sorted_contribs:
            cumulative -= c['contribution'] / (math.log(10))  # Approximate de-contribution
            removal_set.append(c['source'])
            if cumulative <= threshold:
                break
        return (f"Score drops to {cumulative:.2f} (below WATCHLISTED) if these evidence "
                f"sources are removed: {', '.join(removal_set)}")
```

---

## 10. Layer 7 — Evaluation Framework (Week 9)

**Purpose:** Produce the three numbers that make this research defensible: precision, recall, and false positive rate.

**Why this is not optional:**
A POC without evaluation is a demo, not research. Your professor's first question is "how do you know it works?" The evaluation layer is what separates "I built something" from "I built something that demonstrably works at X precision."

**Evaluation test set construction:**

```python
EVALUATION_SET = {
    'true_positives': {
        'ofac_confirmed': 50,   # From OFAC SDN XML — ground truth positives
        'known_mixers':   20,   # From FBI/OFAC press releases (Helix, BestMixer)
    },
    'true_negatives': {
        'exchange_hot_wallets':  50,  # From WalletExplorer labels — should be CLEAN
        'random_ordinary':       50,  # Random addresses with no suspicious history
        'chainabuse_victims':    20,  # Scam victims — should be CLEAN
    }
}

def evaluate(system, test_set) -> dict:
    tp = fp = tn = fn = 0
    for addr in test_set['true_positives']['ofac_confirmed']:
        result = system.classify(addr)
        if result.category in ('BLACKLISTED', 'WATCHLISTED'):
            tp += 1
        else:
            fn += 1

    for addr in test_set['true_negatives']['exchange_hot_wallets']:
        result = system.classify(addr)
        if result.category == 'CLEAN':
            tn += 1
        else:
            fp += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    fpr       = fp / (fp + tn) if (fp + tn) > 0 else 0

    return {'precision': precision, 'recall': recall, 'f1': f1, 'fpr': fpr,
            'tp': tp, 'fp': fp, 'tn': tn, 'fn': fn}
```

---

## 11. Layer 8 — Dashboard (Week 10)

**What it provides:**
A Streamlit-based analyst dashboard that provides:
- Address lookup: enter any Bitcoin address and see its risk classification and evidence chain
- Graph visualisation: Neo4j Browser embedded via iframe showing the entity relationship graph
- PRE_CRIME_WATCHLIST monitor: live list of watchlisted addresses with monitoring status
- Evaluation metrics display: real-time precision/recall/F1 on the evaluation set

**Why Streamlit and NOT a custom web app:**
Streamlit produces a fully functional data application in ~100 lines of Python. For a POC, the purpose of the dashboard is to demonstrate the system works — not to build production UI. A custom React/Flask application would take 4–6 weeks for the same visual output.

**Why NOT just Jupyter notebooks:**
Jupyter notebooks require Python environment setup on the evaluator's machine. Streamlit runs as a web server — evaluators access it via browser. For demonstration purposes (professor evaluation, investor demo), browser-accessible is significantly better.

---

## 12. POC Tech Stack: Justified Choices

| Component | Choice | Why This | Why NOT Alternatives |
|-----------|--------|----------|---------------------|
| Blockchain data | Google BigQuery | Full coverage, no setup, SQL-queryable, free tier sufficient, reproducible | Full node: 620GB, 7-day sync. Blockstream: rate limits infeasible for clustering |
| Clustering algorithm | NetworkX Union-Find | O(α(n)) time, native Python, handles 10M+ addresses in memory | Neo4j Cypher: slow for bulk merge operations |
| Graph storage | Neo4j Community | Cypher query language, strong Python driver, excellent visualisation | TigerGraph: steep learning curve. NetworkX: fails >10M nodes |
| ML baseline | scikit-learn RandomForest | Reproduces Peled 2021 baseline, standard Python, no GPU required | PyTorch GNN: week 1 should validate pipeline, not push ML frontier |
| Anomaly detection | scikit-learn IsolationForest | No labeled negative class needed, well-understood, interpretable | Autoencoder: needs GPU, more tuning, harder to explain |
| Relational DB | PostgreSQL | ACID, full-text search, JSON support, robust Python driver (psycopg2) | SQLite: no concurrent writes. MySQL: worse JSON support |
| Dashboard | Streamlit | Working UI in <100 lines Python, browser-accessible, no frontend code | React: 4+ weeks. Jupyter: local Python required |
| Dark web data (POC) | Pre-crawled archive | Reproducible, no Tor dependency, fast to work with | Live Tor crawler: adds 2 weeks of infrastructure complexity to POC |
| Explainability | SHAP + custom counterfactual | SHAP for ML layer, counterfactual for rule layer, both required | LIME: less theoretically sound than SHAP. Feature importance only: insufficient for analyst use |

---

## 13. Database Schema (POC Version)

```sql
-- Core addresses table
CREATE TABLE btc_addresses (
    address         TEXT PRIMARY KEY,
    address_type    TEXT,           -- P2PKH | P2SH | BECH32 | BECH32M | P2TR
    cluster_id      TEXT,           -- Union-Find cluster root address
    service_type    TEXT,           -- EXCHANGE | MIXER | POOL | MARKET | UNKNOWN
    service_conf    FLOAT,
    risk_category   TEXT,           -- CLEAN | WATCHLISTED | BLACKLISTED | PRE_CRIME_WATCHLIST
    risk_score      FLOAT,
    first_seen_btc  TIMESTAMPTZ,    -- First on-chain transaction date
    first_seen_dw   TIMESTAMPTZ,    -- First dark web appearance (null if unknown)
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Evidence records
CREATE TABLE evidence (
    id              SERIAL PRIMARY KEY,
    address         TEXT REFERENCES btc_addresses(address),
    evidence_type   TEXT,  -- OFAC_SDN | DARK_WEB_PAYMENT | TAINT_HOP | BEHAVIORAL | ANOMALY
    evidence_value  TEXT,  -- The specific evidence value
    source          TEXT,  -- Data source identifier
    confidence      FLOAT,
    lr_contribution FLOAT, -- Log-odds contribution to Bayesian fusion
    provenance_chain TEXT[], -- List of parent evidence sources
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- PRE_CRIME watchlist
CREATE TABLE pre_crime_watchlist (
    address          TEXT PRIMARY KEY REFERENCES btc_addresses(address),
    onion_domain     TEXT,
    page_url         TEXT,
    first_seen_dw    TIMESTAMPTZ,
    dw_confidence    FLOAT,
    pgp_fingerprints TEXT[],
    aliases          TEXT[],
    page_topic       TEXT,
    monitoring       TEXT DEFAULT 'ACTIVE',  -- ACTIVE | TRIGGERED | EXPIRED
    first_tx_hash    TEXT,  -- Set when first on-chain transaction detected
    first_tx_at      TIMESTAMPTZ
);

-- Evaluation results
CREATE TABLE evaluation_results (
    run_id          TEXT,
    run_at          TIMESTAMPTZ DEFAULT NOW(),
    precision       FLOAT,
    recall          FLOAT,
    f1              FLOAT,
    fpr             FLOAT,
    tp_count        INTEGER,
    fp_count        INTEGER,
    tn_count        INTEGER,
    fn_count        INTEGER,
    dataset         TEXT,  -- 'OFAC+ELLIPTIC+WALLETEXPLORER'
    notes           TEXT
);
```

---

## 14. POC Evaluation Targets and Success Criteria

The POC is a success if ALL of the following are met:

| Metric | Target | Why This Threshold |
|--------|--------|--------------------|
| Precision (BLACKLISTED tier) | ≥ 0.90 | <90% means 1 in 10 flagged addresses is innocent — unacceptable for enforcement use |
| Recall (OFAC addresses found) | ≥ 0.80 | >20% miss rate means significant criminal infrastructure uncovered |
| F1 score | ≥ 0.85 | Harmonic mean; ensures precision and recall are both reasonable |
| False Positive Rate (clean wallets flagged) | < 0.05 | <5% of exchange/ordinary wallets incorrectly flagged |
| Elliptic baseline reproduced | Within ±2% of published | Validates pipeline correctness |
| At least 1 PRE_CRIME_WATCHLIST address demonstrated | Must exist | The core novel contribution must be demonstrated live |
| Counterfactual explanation generated for each BLACKLISTED address | 100% coverage | Non-negotiable for legal defensibility |

---

## 15. What the POC Does NOT Solve (By Design)

The following gaps are acknowledged and deferred to the Final Product plan:

| Gap | Why Deferred |
|-----|-------------|
| Live Tor crawler | POC uses pre-crawled archive; live crawler adds 3+ weeks of infrastructure |
| Cross-chain intelligence (Ethereum, Monero) | Out of scope for POC; would require separate blockchain indexers |
| Taproot (P2TR) clustering | CIO blind to Taproot; research gap noted, fix deferred to MVP |
| Lightning Network full support | Channel detection filter added; full LN graph tracking deferred |
| Real-time monitoring | POC is batch; real-time adds message queue + streaming pipeline |
| Analyst feedback loop | Schema includes table; retroactive taint correction deferred to MVP |
| Model drift detection | POC uses static trained models; versioning deferred to production |
| GDPR compliance layer | Data retention policy noted; formal compliance framework deferred |

---

## 16. Week-by-Week POC Timeline

| Week | Focus | Deliverable | Validates |
|------|-------|-------------|-----------|
| 1 | Layer 0: Elliptic baseline | Reproduce Peled 2021 RF on Elliptic dataset | Pipeline works |
| 2 | Layers 1A+1B: OFAC + BigQuery | 3-hop CIO expansion from 50 OFAC seeds | Data acquisition works |
| 3 | Layers 2+3: Clustering + Service | Clusters with service classification | Clustering correct |
| 4 | Layer 4: Risk propagation | All 3 methods (taint, LP, PPR) running, comparison metrics | Propagation correct |
| 5–6 | Layer 5: Pre-crime intelligence | DW sample processed, PRE_CRIME_WATCHLIST populated | Novel contribution live |
| 7–8 | Layer 6: Risk engine | Full 3-layer engine producing RiskDecision objects | End-to-end scoring |
| 9 | Layer 7: Evaluation | Precision/recall/F1/FPR on full test set | Research defensibility |
| 10 | Layer 8: Dashboard | Streamlit dashboard live | Demonstrability |

---

*This POC plan is designed to produce a demonstrable, defensible working model in 10 weeks. Every architectural choice is justified by research constraints and contrasted against alternatives. The POC is complete when the three core questions in Section 1 can be answered with measured numbers.*
