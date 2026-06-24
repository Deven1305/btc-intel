# BTC-Intel: Master Prompt for Claude Opus via Claude Code
## Give this entire file as your first message in a Claude Code session

---

## BEFORE YOU START — READ THIS (For the Teammate Using Claude Code)

**Model to use:** Claude Opus (latest available — claude-opus-4-6 or higher in Claude Code)

**How to use this prompt:**
1. Clone the repository (repo name suggested below)
2. Open Claude Code in the repo directory: `claude` in terminal
3. Paste this ENTIRE file as your first message
4. Let Opus run — it will read all MD files, search the web for papers, and produce 3 output files
5. Do NOT interrupt mid-run — Opus works autonomously on complex tasks
6. Expected runtime: 20–40 minutes for the full output

**Why Opus for this task:**
Opus 4.6+ has adaptive thinking (thinks longer on hard problems automatically),
superior long-context performance (handles all 7 MD files simultaneously),
and sustained effort on complex synthesis tasks without losing coherence.
It also has web search capability in Claude Code — use it to find new research papers.

**Repo name suggestion:** `btc-intel-research` or `wallet-blacklist-intelligence`

**What goes in the repo before cloning:**
```
btc-intel-research/
├── docs/
│   ├── 01_POC_Implementation_Plan.md
│   ├── 02_Final_Product_Implementation_Plan.md
│   ├── 03_Research_Papers_Gap_Analysis.md
│   ├── 04_Patent_and_Research_Paper_Guide.md
│   ├── 05_Research_Gaps_Explained_Simply.md
│   ├── 06_BTC_Intel_POC_Plan.md
│   └── 07_BTC_Intel_Final_Product_Plan.md
├── output/
│   └── (empty — Opus writes here)
└── MASTER_PROMPT_FOR_CLAUDE_OPUS.md  ← this file
```

---

## THE PROMPT (Everything below this line is for Claude Opus)

---

# Your Mission: Synthesize BTC-Intel Into 3 Definitive Documents

You are working on **BTC-Intel** — a Bitcoin wallet blacklist intelligence system.
The single goal of BTC-Intel is: **given any Bitcoin address, determine with evidence
whether it is BLACKLISTED, WATCHLISTED, PRE_CRIME_WATCHLIST, or CLEAN.**

You have access to 7 existing research and planning documents in the `docs/` folder.
Read ALL of them completely before writing anything.
Then search the web for additional research papers to fill gaps.
Then produce exactly 3 output files in `output/`.

---

## STEP 1 — READ ALL 7 EXISTING DOCUMENTS

Read these files in this order. Do not skip any.

```
docs/01_POC_Implementation_Plan.md
docs/02_Final_Product_Implementation_Plan.md
docs/03_Research_Papers_Gap_Analysis.md
docs/04_Patent_and_Research_Paper_Guide.md
docs/05_Research_Gaps_Explained_Simply.md
docs/06_BTC_Intel_POC_Plan.md
docs/07_BTC_Intel_Final_Product_Plan.md
```

As you read, build a mental model of:
- The 5-phase architecture (Seed Collection → Dark Web Crawler → Blockchain Graph → Cross-Reference → PRE_CRIME Watchlist)
- Every research paper mentioned and what gap it fills
- Every novel contribution claimed (PRE_CRIME_WATCHLIST, shared-wallet onion graph edge, provenance-aware Bayesian fusion)
- Every free data source identified (OFAC, BigQuery, DUTA-10K, Elliptic, etc.)
- The college server + VM crawler setup
- The risk classification states and how they are computed
- What ClearTrace was (bank fraud detection — NOT part of the core architecture)
- The 21 dark web crawling issues and their solutions

---

## STEP 2 — WEB SEARCH FOR ADDITIONAL RESEARCH PAPERS

After reading all documents, search the web for research papers that were
NOT already covered in the existing docs or that have newer findings.

Search for ALL of the following (use web search for each query):

```
Search 1: "Bitcoin address clustering" 2023 2024 2025 research paper heuristics
Search 2: "CoinJoin detection" Bitcoin privacy mixing paper 2023 2024
Search 3: "dark web Bitcoin forensics" 2023 2024 research paper address extraction
Search 4: "pre-transaction risk scoring" cryptocurrency blockchain intelligence
Search 5: "Taproot P2TR" Bitcoin clustering forensics research 2024 2025
Search 6: "Lightning Network privacy" Bitcoin forensics 2023 2024
Search 7: "blockchain AML" anti-money laundering machine learning 2024 2025
Search 8: "temporal graph neural network" Bitcoin illicit transaction 2024
Search 9: "onion service graph" Tor dark web cryptocurrency 2023 2024
Search 10: "OFAC sanctions Bitcoin" cryptocurrency compliance 2024 2025
Search 11: "behavioral fingerprint" cryptocurrency wallet clustering entity resolution
Search 12: "cross-chain bridge" Bitcoin forensics Ethereum money laundering
Search 13: "provenance tracking" evidence fusion risk scoring financial crime
Search 14: "explainability blockchain" SHAP counterfactual cryptocurrency forensics
Search 15: "Elliptic dataset" benchmark Bitcoin ML classification 2024
```

For each search result that finds a paper NOT already in the existing docs:
- Note the paper title, venue, year, arXiv ID if available
- Note what it contributes
- Note what gap it leaves that BTC-Intel fills
- Add it to your research gap section

---

## STEP 3 — PRODUCE THREE OUTPUT FILES

Write all three files. Do not write placeholder text. Every section must be complete.
Each file goes in `output/` directory.

---

### OUTPUT FILE 1: `output/A_POC_Architecture_and_Implementation.md`

**Title:** BTC-Intel POC: Complete Architecture, Implementation and Technical Flow
**Subtitle:** "Is This Bitcoin Wallet Criminal?" — Working Proof of Concept

**Tone:** Detailed but readable. Explain every technical decision in plain English
first, then show the code/config. Use analogies. Someone who has read nothing else
about BTC-Intel should be able to understand and implement it from this document alone.

**This file must cover ALL of the following sections in this order:**

---

#### Section 1 — What BTC-Intel Does (Plain Language, No Jargon)

Write 3 paragraphs maximum. Cover:
- The single goal: is this Bitcoin wallet criminal?
- The four classification states: BLACKLISTED / WATCHLISTED / PRE_CRIME_WATCHLIST / CLEAN
- What "evidence chain" means and why it matters (not just a score — every claim is sourced)
- One concrete end-to-end example: user enters `1ABCxyz...` → system outputs verdict + evidence

Do NOT mention ClearTrace, SHAP for bank fraud, XGBoost on PaySim, or any financial
transaction fraud detection. Those are separate projects. BTC-Intel is Bitcoin wallet
intelligence only.

---

#### Section 2 — What is 100% Free for the POC

A table with every free data source, free tool, and free service used.
For each, specify: what it provides, the URL, the free tier limit, and any signup required.

Key free sources to cover (add more from web search findings):
- OFAC SDN XML (treasury.gov/ofac/downloads/sdn.xml) — confirmed criminal BTC addresses
- UN Consolidated Sanctions List (scsanctions.un.org) — international sanctions
- Chainabuse API (chainabuse.com) — community fraud reports, 100/day free
- MistTrack (misttrack.io) — 100 queries/day free, APAC coverage
- Google BigQuery crypto_bitcoin dataset — 1TB/month free, full Bitcoin history
- Elliptic Dataset (Kaggle) — 203k labeled transactions, free for research
- WalletExplorer (walletexplorer.com) — exchange cluster labels, free scrape
- DUTA-10K dataset — pre-crawled dark web pages, academic request
- Cryptoscamdb (github.com/cryptoscamdb) — open source scam wallet list
- Slowmist blockchain-blacklist (github.com) — security firm maintained
- Anthropic Claude API — free trial credits (~$5) for investigation briefs

Confirm: nothing in the POC costs money if you use the free tiers carefully.

---

#### Section 3 — POC Architecture Diagram (ASCII)

Draw the complete system architecture as a detailed ASCII diagram.
Show all 5 phases as boxes. Show data flow between them with arrows.
Show what goes into each phase and what comes out.
Show the VM boundary (crawler lives inside VM on college server).
Show the database layer (PostgreSQL, Neo4j, MinIO, Redis).
Show the output (Streamlit dashboard + Claude API brief).

---

#### Section 4 — College Server + VM Setup (Answering Safety Questions)

Explain completely:

**4A — Why a VM is mandatory (not optional)**
Explain the blast shield concept with an example: "if a dark web page exploits the
crawler, it damages the VM — restore from snapshot in 2 minutes, server is untouched."

**4B — Tor: VPN or not?**
State clearly: use Tor ONLY, no VPN. Explain why (VPN adds a trusted third party
that sees your traffic; Tor alone is correct for this research use case).
Explain what each party sees: dark web server sees Tor exit node IP, ISP sees
encrypted Tor traffic, your server sees nothing (all inside VM).

**4C — Where HTML is saved and for how long**
Complete flow: crawler (inside VM) → gzip compress → SHA-256 hash →
write to MinIO on college server → extract metadata to PostgreSQL → 
raw HTML auto-deleted after 90 days (MinIO lifecycle policy).
Explain WHY 90 days: GDPR data minimisation + storage sustainability.

**4D — College server hardware and software requirements**
Minimum specs for POC (and why each spec is needed).
Complete software installation commands (Ubuntu 22.04 LTS).
What runs on the server (PostgreSQL, Neo4j, MinIO, Redis, FastAPI, Streamlit).
What runs ONLY inside the VM (Tor, Splash, Python crawler).

---

#### Section 5 — Phase 1: Seed Collection (Working Code)

Explain what seeds are and why they are the foundation.
Analogy: "seeds are like a starting address book of confirmed criminals — we then
trace who they sent money to, who sent money to them, and so on outward."

Provide complete working Python code for:
- OFAC SDN XML parser (extract all BTC addresses with entity names)
- UN Consolidated List parser
- Chainabuse API fetcher
- WalletExplorer service label scraper
- PostgreSQL storage with conflict handling

Explain the confidence levels: OFAC = 1.0 (ground truth), Chainabuse = 0.6
(community report, not government verified), and why this distinction matters.

---

#### Section 6 — Phase 2: Dark Web Crawler (Working Code + Safety)

Explain the crawler's role: finding Bitcoin addresses in PAYMENT contexts on dark web
pages BEFORE any on-chain transaction exists.

Cover with working code:
- The 4 Bitcoin address regex patterns (P2PKH, P2SH, BECH32, BECH32M)
- PGP fingerprint extraction (and WHY PGP matters: same fingerprint = same person, 100% certainty)
- Context classification: PAYMENT vs VICTIM_REPORT vs AMBIGUOUS
  (explain with examples: "send BTC to 1ABC..." = PAYMENT; "WARNING: 1ABC... scammer" = VICTIM)
- Page topic classification: DRUG / WEAPON / FRAUD / UNKNOWN
- Alias extraction from vendor pages
- CoinJoin detection for correct cluster handling
- Deduplication via SHA-256 page hash in Redis
- Rate limiting: 30 seconds between requests per Tor circuit (polite crawling)
- Dead service handling: 3 failures → mark DEAD, retry in 30 days
- MinIO archiving of raw HTML

Address ALL 21 issues from the word document (include a table mapping each issue to
its specific code-level solution).

---

#### Section 7 — Phase 3: Blockchain Graph + Clustering (Working Code)

Explain using a clear analogy: "one criminal uses 1,000 addresses for privacy —
clustering is like figuring out all 1,000 letters in a pile came from the same author."

Cover with working code:
- BigQuery queries for 3-hop transaction expansion from OFAC seeds
  (include actual SQL with cost estimates — stays within 1TB free tier)
- CIO Union-Find implementation with CoinJoin pre-filter
  (explain WHY CoinJoin breaks CIO and what the filter checks: ≥40% equal outputs AND ≥5 outputs)
- Script-type change address heuristic
  (explain WHY script-type is better than naive: 5% vs 23% false positive rate)
- Optimal-change heuristic
- Multi-heuristic weighted voting (weights: CIO 0.40, script-change 0.30, optimal 0.20, reuse 0.10)
  (explain why 2024 weights differ from Delgado 2021 weights — CoinJoin adoption increased)
- Taproot (P2TR) gap: flag as UNRESOLVED, explain why (all P2TR outputs look identical)
- Service classification: exchange / mixer / pool / unknown
  (explain why this MUST run BEFORE taint propagation — taint stops at exchanges)
- Three taint propagation methods: amount-weighted (Chainalysis), label propagation, PPR
  (explain each in plain English with an analogy for each)
- Why comparing all three methods is a novel research contribution

---

#### Section 8 — Phase 4: Cross-Reference + Risk Engine (Working Code)

Explain Bayesian fusion in plain English first:
"We start with a prior belief: 1 in 1000 Bitcoin addresses is criminal.
Each piece of evidence MULTIPLIES this probability up or down.
OFAC confirmation multiplies it 1000x. Dark web payment context multiplies it 50x.
Evidence that the address belongs to an exchange DIVIDES it by 20."

Cover with complete working code:
- The three classification layers:
  Layer 1: Fast deterministic rules (OFAC → instant BLACKLISTED)
  Layer 2: Bayesian fusion with provenance-aware deduplication
  Layer 3: Behavioral anomaly check
- Complete likelihood ratio table with plain-English explanation of each LR value
- The provenance rule with worked example:
  "OFAC designates address A. Chainalysis also flags it. Community reports it.
   All three trace to ONE fact: the OFAC listing.
   Without provenance tracking: 3x the log-odds for one underlying fact.
   With provenance: OFAC counted once, others skipped."
- The counterfactual generator: "score drops below WATCHLISTED if X evidence is removed"
- Complete RiskDecision dataclass with all fields

---

#### Section 9 — Phase 5: PRE_CRIME_WATCHLIST (Working Code + Why This Is Novel)

This section needs extra emphasis because it is BTC-Intel's most important novel contribution.

Open with: "Every existing system — Chainalysis, TRM, Elliptic, every academic paper — requires
at least one Bitcoin transaction before it can classify an address. A new wallet with zero
transaction history gets a risk score of ZERO from every commercial system.
BTC-Intel flags it the moment it appears on a dark web payment page."

Cover:
- Complete working code for PRE_CRIME_WATCHLIST entry (with confidence threshold check)
- How on-chain history is verified via BigQuery before entering watchlist
- The monitoring mechanism: BigQuery polling every 6 hours
- The first-transaction trigger: when polling detects a transaction, run full risk engine
- A concrete example timeline:
  Day 1: Criminal creates wallet 1ABC... for drug market
  Day 2: Lists it on abc.onion → BTC-Intel finds it → PRE_CRIME_WATCHLIST (zero history)
  Day 3: First customer pays → BigQuery polling detects → promoted to WATCHLISTED/BLACKLISTED
  → BTC-Intel detected this 24 hours before any commercial system could
- Database schema for the watchlist table

---

#### Section 10 — Claude API Investigation Brief (Working Code)

Explain the grounded prompting design:
"Claude receives ONLY computed evidence: the evidence list, scores, category, counterfactual.
Claude's job is to NARRATE these findings, not invent new ones.
This prevents hallucination — Claude cannot add a risk factor that wasn't computed first."

Provide complete working code for the brief generator with the full grounded system prompt.

---

#### Section 11 — Streamlit POC Dashboard (Working Code)

Complete working Streamlit app covering:
- Address lookup with risk score + colour-coded category
- Evidence chain display with contribution arrows
- Counterfactual display
- PRE_CRIME_WATCHLIST live table
- Evaluation metrics display (precision/recall vs baseline)
- Claude brief generation button

---

#### Section 12 — Database Schema

Complete PostgreSQL schema for all tables:
seed_addresses, dark_web_records, pre_crime_watchlist, risk_decisions, 
address_clusters, crawl_queue, audit_log (immutable), reassessment_queue

---

#### Section 13 — Week-by-Week Build Schedule

10-week schedule. For each week:
- What gets built (specific components)
- What can be demonstrated at the end of that week
- What validates (what does this prove works?)

---

#### Section 14 — Exactly What to Run on Day 1

Complete bash script for college server setup.
Complete .env template.
Complete requirements.txt.
Exactly what command starts the dashboard.
Expected output after first successful run.

---

#### Section 15 — POC Success Criteria

Table of 8 demo scenarios, each with:
- What to show
- What it proves
- Expected output

Target metrics:
- Precision (BLACKLISTED tier): ≥ 90%
- Recall on OFAC test set: ≥ 80%
- FPR on known exchange addresses: < 5%
- At least 1 PRE_CRIME_WATCHLIST address demonstrated

---

### OUTPUT FILE 2: `output/B_Final_Product_Architecture_and_Implementation.md`

**Title:** BTC-Intel Final Product: Production-Grade Architecture and Implementation
**Subtitle:** From Working POC to Enterprise Bitcoin Wallet Intelligence

**Tone:** Same as File 1 — detailed, readable, plain English first then technical.
Explicitly state at the start of every section: what the POC did, what production needs,
and exactly why the upgrade is necessary.

**This file must cover ALL of the following sections:**

---

#### Section 1 — The Difference: POC vs Production (Summary Table)

A comparison table covering every major component.
Columns: Component | POC Approach | Production Approach | Why the Upgrade Matters.

At minimum cover: data sources, crawler, blockchain data, graph database, risk engine LRs,
monitoring, API, dashboard, storage, security, compliance, feedback loop.

---

#### Section 2 — College Server Final Product Setup

**2A — Full hardware specification** with justification for each spec:
- CPU: 8 cores minimum — which processes need which cores
- RAM: 32GB — breakdown of how each service uses RAM (Neo4j 8GB, PostgreSQL 4GB, etc.)
- SSD: 2TB NVMe — breakdown: Bitcoin full node 620GB, Neo4j 350GB, PostgreSQL 200GB, etc.
- Network: campus LAN specs

**2B — Network isolation for crawler VM**
Full iptables configuration: VM can reach MinIO on server (port 9000) but nothing else.
Firewall rules for external access: dashboard and API visible on campus, databases internal only.
SSL certificate setup (Let's Encrypt, free).

**2C — Daily crawler VM routine**
The full bash script: snapshot → crawl → integrity check → report.
How to restore from snapshot if VM is compromised (< 2 minutes).

**2D — Getting IT department permission**
What to tell the IT department about what the system does.
What it does NOT do (not a live attack system, purely passive research observation).
Data retention and privacy policy to present to IT.

---

#### Section 3 — Phase 1 Production: Auto-Refreshing Seed Collection

**What changes:** POC loaded seeds once. Production auto-refreshes every 4 hours using HTTP ETags.

Explain ETag checking with analogy: "instead of downloading the full 40MB OFAC file every 4 hours
to check for changes, we first ask the server 'has this file changed?' (a tiny 1KB request).
If nothing changed, we skip the download entirely. If it changed, we download and process."

Provide complete working code for:
- ETag-based OFAC refresh (HEAD request → compare ETag → download only if changed)
- New seed detection and downstream re-evaluation trigger
- Extended source list (8+ sources): OFAC, UN, Chainabuse, MistTrack, Cryptoscamdb,
  Slowmist, CDA, WalletExplorer — with confidence weights for each
- Automatic re-assessment of all addresses within 3 hops of new seeds
  (new OFAC designation → find 3-hop neighbors → queue for re-evaluation)

---

#### Section 4 — Phase 2 Production: Live Dark Web Crawler

**4A — Sentence-boundary context extraction**
Explain the POC problem: fixed 500-char window misses payment context sentences
that are far from the address in the page text.
Show the production solution: NLTK sent_tokenize → find address-containing sentence →
expand 3 sentences in each direction → score the expanded window.
Working code with before/after comparison.

**4B — Protocol-specific CoinJoin detection**
Complete working code detecting: Wasabi 1.x (0.1 BTC denomination),
Wasabi 2.0 (≥20 inputs), Whirlpool (exactly 5 equal outputs), JoinMarket, generic.
Explain why each protocol needs its own rule.
Show the taint decay rates for each: Whirlpool 0.3, Wasabi 0.35, JoinMarket 0.35.

**4C — Image OCR and QR code extraction**
Working code using Tesseract + pyzbar.
When it applies: images < 2MB only (larger images = product photos, not address images).
Integration into the extraction pipeline.

**4D — Domain recrawl scheduling**
Complete recrawl schedule table: active markets = 3 days, forums = 7 days,
paste sites = 1 day, static info = 14 days, dead = 30 days.
Working code for the scheduler.

---

#### Section 5 — Phase 3 Production: Bitcoin Full Node + Real-Time

**5A — Why switch from BigQuery**
Explain with a concrete latency example:
"Exchange is about to process withdrawal to 1ABC... 
BigQuery: data is 24 hours old → you miss yesterday's OFAC addition.
Your own Bitcoin node: data is 10 minutes old → you catch today's OFAC addition."

**5B — Bitcoin Core + ElectrumX setup**
Hardware requirements and why (620GB non-pruned, ElectrumX needs 350GB index).
bitcoin.conf configuration (txindex=1, ZMQ settings, RPC settings).
ElectrumX configuration.
Initial sync timeline: 5-7 days (start this on Week 3 of production roadmap).

**5C — ZMQ real-time block monitoring**
Working code for ZMQ subscriber.
Explain ZMQ vs polling: "ZMQ is event-driven — Bitcoin Core pushes a notification
the moment a new block arrives. Polling is 'any new blocks? no. any? no.' — wasteful."
How new transactions trigger risk assessment for known addresses.

**5D — BigQuery's continued role in production**
What BigQuery is still useful for: historical analysis, research queries, backup verification.
Rule: real-time screening → own node. Historical/research → BigQuery.

---

#### Section 6 — Phase 4 Production: Calibrated Risk Engine

**6A — Why calibrated LRs matter (worked example)**
POC guessed: DARK_WEB_PAYMENT LR = 50.
After measuring on real data (720/1000 DW payment addresses later confirmed criminal):
Measured LR = 720.
Show the math: posterior with LR=50 vs LR=720 for the same address.
"A wallet that scored 0.45 (WATCHLISTED) with guessed LR scores 0.94 (BLACKLISTED) with calibrated LR."

Complete calibration code using OFAC confirmed addresses as positives and WalletExplorer
exchange addresses as negatives.

**6B — Ensemble taint propagation**
Working code combining all three methods (taint + label prop + PPR) with learned weights.
How the ensemble outperforms any single method.

**6C — Feedback-driven LR updates**
How analyst feedback (Section 10) flows back into LR calibration.
How often to recalibrate: quarterly baseline + drift-triggered.

---

#### Section 7 — Phase 5 Production: ElectrumX Real-Time Watchlist Monitoring

**What changes:** POC polls BigQuery every 6 hours. Production uses ElectrumX WebSocket
subscriptions for second-level detection.

Concrete latency comparison:
"POC: address enters watchlist at 10am → first transaction at 11am →
 detected at 4pm (6-hour polling gap).
Production: address enters watchlist at 10am → ElectrumX subscription created immediately →
first transaction at 11am → notified within seconds → full risk engine runs by 11:01am."

Complete working async Python code for ElectrumX subscription monitor.
The re-classification flow: PRE_CRIME → TRIGGERED → full risk engine → new category.

---

#### Section 8 — Calibrated Likelihood Ratios (Full Production Table)

A complete table of all LR values in the production system.
For each signal: signal name, guessed LR (POC), measured LR (production), measurement basis.

Include all signals: OFAC_SDN, UN_SANCTIONS, DARK_WEB_PAYMENT, PGP_CRIMINAL_LINK,
TAINT_HOP_1/2/3, COMMUNITY_REPORT, BEHAVIORAL_ANOMALY, VICTIM_CONTEXT, EXCHANGE_VERIFIED,
MINING_POOL, AMOUNT_CORRELATION (dark web listing price matches first on-chain tx amount).

Full calibration methodology code.

---

#### Section 9 — Analyst Feedback Loop

Complete working API endpoint for feedback submission.
Retroactive correction cascade (with code):
- Mark address as CLEAN
- Find all addresses within 2 hops that received taint from this address
- Recompute their taint excluding the corrected address
- If new score < 0.35: reclassify as CLEAN automatically
- Emit notifications for all reclassified addresses
Immutable audit trail for all feedback actions.

---

#### Section 10 — Model Drift Detection

Explain drift with an analogy:
"Your risk scores were calibrated on 2024 data. By 2025, criminals changed tactics —
more Taproot addresses, different structuring amounts. The model silently becomes less accurate.
Drift detection notices this before it causes real damage."

Complete working code for:
- LR drift detection: compare current analyst-confirmed precision to baseline precision
- Kolmogorov-Smirnov test on feature distributions
- Automatic retrain trigger when FP rate doubles
- Quarterly retrain schedule regardless of drift signal

---

#### Section 11 — Production API

Complete FastAPI application with:
- Single address assessment endpoint (< 200ms P99 target)
- Batch endpoint (up to 1000 addresses per request)
- PRE_CRIME watchlist query endpoint
- Feedback submission endpoint
- JWT authentication with tenant isolation
- Redis caching (5-minute TTL)
- Rate limiting
- Complete OpenAPI documentation via FastAPI autodocs

---

#### Section 12 — Audit Log and PMLA/Legal Compliance

Complete PostgreSQL audit log schema (immutable — REVOKE UPDATE, DELETE).
SHA-256 hash-based tamper detection for each record.
GDPR data retention enforcement (90-day raw HTML auto-delete).
PMLA (India) SAR draft generator based on risk decision output.

---

#### Section 13 — Production Dashboard (Capability Specification)

What changes from Streamlit POC to production React app.
Specific features needed:
- Alert queue with PMLA 60-day deadline tracker per alert
- PRE_CRIME live feed (WebSocket, shows new entries in real-time)
- Evidence timeline view (when each signal was first seen for an address)
- Audit log explorer with tamper detection display
- Analyst feedback workspace (mark decisions + retroactive correction status)
- Model performance dashboard (precision/recall over time, drift indicators)

---

#### Section 14 — All 21 Issues: Upgraded Solutions

A table comparing POC solution vs Final Product solution for each of the 21 crawling issues.
For each: what the POC did, what production upgrades, why this matters at scale.

---

#### Section 15 — 16-Week Production Roadmap

Week-by-week breakdown. For each week:
- What gets built
- What changes from the POC version
- What milestone can be demonstrated
- Dependencies (what must be done first)

---

### OUTPUT FILE 3: `output/C_Research_Gaps_Architecture_Patent_Guide.md`

**Title:** BTC-Intel: Research Foundation, Architecture Layers, Novel Gaps, and Patent/Publication Strategy
**Subtitle:** Every Research Paper → Every Gap → Every BTC-Intel Solution → Patent Criteria

**This is the most detailed file. It combines research depth with implementation detail.**

---

#### Section 1 — Architecture: Layer-by-Layer Detailed Breakdown

For EACH of the 5 phases, provide a detailed layer breakdown covering:

**For each layer:**
1. Name and position in the overall pipeline
2. What problem it solves (plain English)
3. Why it is in this position in the pipeline (what would break if the order changed)
4. The specific algorithms/methods used
5. The data it consumes and the data it produces
6. The key design decision and why (with alternatives considered)
7. What research paper or papers justify this approach
8. The confidence contribution to the final risk score

The pipeline order is critical — explain why SERVICE RECOGNITION must run BEFORE
taint propagation (if taint propagates through an exchange first, it incorrectly
contaminates all the exchange's customers).

---

#### Section 2 — Complete Research Paper Catalog

For EVERY paper in the existing docs AND every paper found via web search:

**Format for each paper:**
```
Paper: [Title]
Venue: [Conference/Journal, Year]
arXiv/DOI: [identifier]
Core contribution: [2-3 sentences, plain English]
What it got right: [why BTC-Intel builds on it]
Gap 1: [specific gap with explanation]
Gap 2: [specific gap with explanation]
Gap 3: [if any]
BTC-Intel POC solution: [exactly what we implement in response to this gap]
BTC-Intel Final Product upgrade: [what the production system adds]
Research claim: [the specific claim we can make in a paper based on this gap]
Patent relevance: [can any of our solutions be patented? why?]
```

Cover ALL of these papers plus any new ones from web search:

**Category A — Clustering and Heuristics:**
- Meiklejohn et al. 2013 (A Fistful of Bitcoins)
- Ron & Shamir 2013 (Quantitative Analysis of Bitcoin Transaction Graph)
- Delgado-Segura et al. 2021 (Resurrecting Address Clustering)
- Schnoering et al. 2024 (Assessing Efficacy of Heuristic-Based Address Clustering)
- Tironsakkul et al. 2022 (Wasabi CoinJoin Detection)
- Stütz et al. 2022 (Adoption and Actual Privacy of CoinJoin)
- Kappos & Yousaf 2021 (Lightning Network Privacy Analysis)

**Category B — Machine Learning:**
- Weber et al. 2019 (Elliptic Dataset)
- Peled et al. 2021 (Malicious Address Identification)
- Lorenz et al. 2020 (XGBoost and GNN on Elliptic)
- Chen et al. 2023 (Evolve Path Tracer — Four Lifecycle Phases)
- Any 2024-2025 papers found via web search

**Category C — Dark Web Intelligence:**
- Biryukov et al. 2014 (Trawling for Tor Hidden Services)
- Spitters et al. 2014 (Thematic Organisation of Tor Hidden Services)
- Ghosh et al. 2017 (Automated Analysis of Dark Net Markets)
- Christin 2013 (Traveling the Silk Road)
- Owenson et al. 2018 (The Darknet's Smaller Than We Think)
- Hiramoto et al. 2020 (Dark Market Lifecycle via Bitcoin)

**Category D — Risk Scoring:**
- Chainalysis Patent US10977655B2
- Nerino et al. 2021 (Label Propagation for AML)
- Gao et al. 2022 (Blockchain Intelligence Survey)

**Category E — Explainability:**
- Lundberg & Lee 2017 (SHAP)
- Wachter et al. 2017 (Counterfactual Explanations)

**Category F — New Gaps (from web search findings)**
For every new paper found: same format as above.

---

#### Section 3 — The Five Novel Contributions: Deep Technical Specification

For each of BTC-Intel's five novel contributions, provide a complete specification that
could serve as a research paper section AND a patent claim:

**Contribution 1 — PRE_CRIME_WATCHLIST Mechanism**

Structure each contribution with:
- What the problem is (that no existing work solves)
- How BTC-Intel solves it (technical specification at pseudocode level)
- Why this is novel (what prior work lacks, with citations)
- The measurable claim: "We demonstrate X% improvement / Y% earlier detection vs baseline"
- Patent claim language (method claim format)
- Research paper section template

For PRE_CRIME_WATCHLIST specifically:
- Formal definition of the mechanism
- The dark web context scoring algorithm
- The monitoring state machine (states and transitions)
- The first-transaction detection and re-evaluation trigger
- Why no prior patent (Chainalysis US10977655B2) covers this
- The specific claim: "pre-transaction risk scoring based on off-chain contextual intelligence"

**Contribution 2 — Shared-Wallet Onion Graph Edge Type**
- Definition: co-appearance of Bitcoin address in payment contexts on two different onion domains
- Graph construction algorithm
- Edge weight computation
- What criminal coordination relationships this reveals that hyperlink edges miss
- Prior art: Biryukov 2014 hyperlink edges (what they capture vs what our edge captures)
- Research claim format for a paper
- Patent claim language

**Contribution 3 — Provenance-Aware Bayesian Evidence Fusion**
- The circular double-counting problem with worked example
- The provenance chain data structure
- The deduplication algorithm
- Why prior work (Gao 2022 survey) explicitly identifies this as unsolved
- The calibrated likelihood ratio framework
- Research claim: "first formally specified provenance-aware Bayesian evidence fusion for blockchain risk scoring"
- Patent claim language

**Contribution 4 — Three-Way Propagation Method Comparison**
- Why comparing all three methods is novel (prior work uses only one each)
- The evaluation methodology (same dataset, same seeds, same threshold)
- Expected result format (precision/recall table by method and address category)
- Research claim: "first head-to-head comparison of taint, label propagation, and PPR on same dataset"

**Contribution 5 — Temporal Off-Chain/On-Chain Gap Feature**
- The feature: days between dark web listing date and first on-chain transaction
- Why only BTC-Intel can compute this (requires both DW timestamps AND blockchain data)
- Statistical significance test for this feature's predictive power
- Research claim: "we demonstrate that DW listing date is a statistically significant predictor of illicit classification"

---

#### Section 4 — Research Gap Matrix

A comprehensive matrix table covering all research areas:

Columns: Research Area | Best Existing Paper | What It Covers | What It Misses | BTC-Intel Solution | Novelty Score (1-10) | Patent Potential

Rows (at minimum, add more from web search):
- CIO clustering
- CoinJoin-aware clustering
- Taproot forensics
- Lightning Network forensics
- Pre-transaction risk scoring
- Dark web payment context extraction
- PGP cross-market entity linking
- Shared-wallet onion graph edges
- Bayesian evidence fusion
- Circular evidence deduplication
- Taint propagation comparison
- Behavioral lifecycle detection
- Temporal feature engineering
- Off-chain/on-chain temporal gap feature
- SHAP explainability for hybrid rule+ML systems
- Counterfactual explanation for blockchain risk
- Cross-chain bridge tracking
- Adversarial evasion detection
- Multi-blockchain entity resolution
- Amount correlation validation

---

#### Section 5 — Patent Strategy: Complete Filing Guide

**5A — What Is Patentable (Detailed Analysis)**

For each of the 5 novel contributions:
- The specific mechanism that is patentable
- Why it is novel (no prior art found in USPTO search)
- Why it is non-obvious (cross-domain combination argument)
- Risk factors (what prior art might partially block it)

**5B — What Is NOT Patentable (Prior Art Blockers)**

A table of components that cannot be patented with citation of blocking prior art.
This prevents wasting money on rejected claims.

**5C — Patent Claim Templates (Ready to File)**

Full drafted patent claims for all 5 contributions in USPTO format:
- Independent claims (broadest scope)
- Dependent claims (adding specific elements)
- System claims (apparatus version of method claims)

These should be close to the actual language used in a provisional application.

**5D — Filing Timeline**

A month-by-month filing timeline from today:
Month 0: File provisional patent application ($320 USPTO fee)
Month 0: File arXiv preprint (cs.CR category)
Month 1: Submit workshop paper to Financial Cryptography workshop
Month 2: Complete POC evaluation data collection
Month 3: Write full paper
Month 4: Submit to Financial Cryptography (FC) primary venue
...through to Month 16: Enter EPO and PCT national phases

**5E — Prior Art Search Queries**

Complete list of USPTO Patent Center and Google Patents search queries to run
before filing, with guidance on what a "blocking" result looks like.
Include queries for Chainalysis, TRM Labs, Elliptic assignee portfolios.

---

#### Section 6 — Research Paper: Complete Structure

A complete paper outline with:
- Abstract template (250 words, fill-in-the-blank with actual measurement placeholders)
- Section-by-section content specification (what goes in each section, what to NOT write)
- What numerical results are required before submission (precision, recall, F1, days-before-OFAC)
- Which venue to target first and why (Financial Cryptography, IEEE S&P, ACM IMC)
- Common rejection reasons and how to prevent each one
- Reproducibility requirements (what code and data to release)

---

#### Section 7 — Implementation Status Tracker

A table showing:
- Every component in the system
- POC status: NOT_STARTED / IN_PROGRESS / COMPLETE
- Final Product status: NOT_STARTED / PLANNED / IN_PROGRESS / COMPLETE
- Week it gets built (from the roadmap)
- Priority: CRITICAL / HIGH / MEDIUM / LOW
- Research contribution: YES/NO (does completing this enable a research claim?)

This gives a complete view of what needs to be built and what is already planned.

---

## CRITICAL INSTRUCTIONS FOR OPUS

**Before writing a single word of output, confirm you have:**
1. Read all 7 documents in docs/ folder
2. Completed all 15 web searches
3. Found at least 3 new papers not in the existing docs (there will be many more)

**Writing standards:**
- Every technical concept must be explained in plain English FIRST, then technically
- Every code block must be complete and working (no `# TODO` placeholders, no `...` truncation)
- Every claim about novelty must cite the specific gap in the specific prior work
- Every section must stand alone — someone reading just Section 6 of File 1 should not
  need to read File 3 to understand the taint propagation code
- Use consistent terminology throughout all 3 files
- Never mention ClearTrace as part of BTC-Intel's architecture (it is a separate project)
- SHAP in BTC-Intel is used ONLY to explain risk score component contributions
  (not to explain bank fraud predictions — that was ClearTrace only)

**Things to check before finalising each file:**
- Does every code block have complete imports and dependencies?
- Does every database schema have all columns and all indexes?
- Does every architecture diagram include the VM boundary?
- Does every evidence explanation trace back to a specific data source?
- Do the three output files have consistent architecture across them?
  (the same 5 phases should appear in all three files with consistent naming)

**On web search results:**
- If you find a new paper published in 2024 or 2025 that directly addresses one of
  BTC-Intel's claimed novel contributions, update the novelty assessment honestly.
  A lower novelty score with a more precise claim is better than an inflated claim
  that gets rejected at a conference.
- If you find a new paper that opens a NEW gap BTC-Intel could address,
  add it to the gap matrix and suggest the implementation approach.

**Output files must be:**
- `output/A_POC_Architecture_and_Implementation.md` — minimum 3,000 lines
- `output/B_Final_Product_Architecture_and_Implementation.md` — minimum 2,500 lines
- `output/C_Research_Gaps_Architecture_Patent_Guide.md` — minimum 3,500 lines

Start by reading the docs, then searching the web, then writing. Do not output
anything until you have completed Steps 1 and 2. This is a long autonomous task —
commit to it fully without asking for clarification mid-way.

Begin now.
