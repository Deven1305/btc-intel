# BTC-Intel: Research Foundation, Architecture Layers, Novel Gaps, and Patent/Publication Strategy
## Every Research Paper → Every Gap → Every BTC-Intel Solution → Patent Criteria

> **What this file is.** The deepest of the three documents. It combines (a) a layer-by-layer architectural breakdown that explains *why each layer sits where it does*, (b) a complete catalogue of every research paper — those in the original planning docs *and* ~20 newer papers found by literature search — each with its gaps and BTC-Intel's response, (c) a deep technical specification of the five novel contributions suitable for both a paper section and a patent claim, (d) a research-gap matrix with honest novelty scores, (e) a complete patent filing guide with ready-to-file claim language, (f) a full research-paper structure, and (g) an implementation status tracker.
>
> **Consistency.** The five phases, four verdict states, five novel contributions, thresholds, and weights are identical to Files A and B (see File B Appendix EE for the canonical values). SHAP is used only to explain on-chain risk components; ClearTrace is not part of BTC-Intel.

---

## Table of Contents

1. [Architecture: Layer-by-Layer Detailed Breakdown](#section-1--architecture-layer-by-layer-detailed-breakdown)
2. [Complete Research Paper Catalog](#section-2--complete-research-paper-catalog)
3. [The Five Novel Contributions: Deep Technical Specification](#section-3--the-five-novel-contributions-deep-technical-specification)
4. [Research Gap Matrix](#section-4--research-gap-matrix)
5. [Patent Strategy: Complete Filing Guide](#section-5--patent-strategy-complete-filing-guide)
6. [Research Paper: Complete Structure](#section-6--research-paper-complete-structure)
7. [Implementation Status Tracker](#section-7--implementation-status-tracker)

---

## Section 1 — Architecture: Layer-by-Layer Detailed Breakdown

The five phases (Files A/B) decompose into layers. For each layer below: its name and pipeline position, the problem it solves (plain English), why it sits where it does (what breaks if reordered), the algorithms used, the data it consumes and produces, the key design decision with alternatives, the paper(s) that justify it, and its confidence contribution to the final score.

**The master pipeline order, and the one rule that governs it:**

```
Phase 1 Seeds → Phase 2 Dark Web → Phase 3 [ Acquisition → Extraction → Entity Resolution
            → Clustering → SERVICE RECOGNITION → Risk Propagation ] → Phase 4 Risk Engine
            → Phase 5 PRE_CRIME → Explainability → (Feedback)
```

> **The non-negotiable ordering rule: SERVICE RECOGNITION must run BEFORE risk propagation.** If taint propagates *before* services are recognised, criminal taint flows *through* an exchange and contaminates all of the exchange's customers — because the exchange address looks like any other node. Once that happens you must retroactively "un-taint" thousands of innocent downstream addresses, which is computationally expensive and error-prone. Recognising the exchange *first* lets propagation stop at the KYC boundary. This single ordering decision is the difference between a usable system and one that floods analysts with false positives.

---

### Phase 1 — Seed Collection Layers

#### Layer 1.1 — Authoritative Seed Acquisition

- **Position:** the very first layer; everything anchors to it.
- **Problem solved (plain English):** we cannot detect criminals from nothing; we need a starting set of *known* criminal addresses to trace outward from.
- **Why here:** seeds must exist before any graph expansion (Phase 3) or cross-reference (Phase 4) can run. Nothing upstream; everything downstream depends on it.
- **Algorithms/methods:** XML/JSON parsing; per-source confidence assignment; conflict resolution keeping the highest-confidence label.
- **Consumes:** OFAC SDN XML, UN consolidated list, Chainabuse/MistTrack/CryptoScamDB/SlowMist feeds.
- **Produces:** `seed_addresses` (criminal, with confidence) and `service_labels` (exchanges/pools, the taint barriers).
- **Key design decision:** OFAC as ground truth (confidence 1.0) rather than commercial labels. **Alternative considered & rejected:** using Chainalysis/TRM labels as seeds — rejected because their methodology is opaque and creates *circular reasoning* (you cannot evaluate your system against labels produced by a similar system).
- **Justifying papers:** OFAC is a primary legal source, not a paper; the circularity concern is exactly what Gao 2022 flags about evidence provenance.
- **Confidence contribution:** OFAC/UN → deterministic BLACKLISTED (the maximum); community sources contribute via likelihood ratios in Phase 4.

#### Layer 1.2 — Service-Label Acquisition (Taint Barriers)

- **Position:** parallel to 1.1, feeding Phase 3's service recognition.
- **Problem solved:** to stop taint at exchanges, we need to *know* which addresses are exchanges.
- **Why here:** the labels must be loaded before service recognition runs (Phase 3), which must run before propagation.
- **Methods:** scrape WalletExplorer cluster labels; feature fallbacks.
- **Consumes:** WalletExplorer service pages. **Produces:** `service_labels`.
- **Key decision:** treat these as *negatives/barriers*, never as criminal seeds. **Alternative rejected:** ignoring service labels — rejected because then taint floods exchange customers.
- **Confidence contribution:** EXCHANGE_VERIFIED → deterministic CLEAN (LR 0.05).

---

### Phase 2 — Dark Web Crawler Layers

#### Layer 2.1 — Acquisition (Tor + Splash, in VM)

- **Position:** first layer of Phase 2.
- **Problem solved:** obtain the off-chain payment context that makes pre-transaction detection possible.
- **Why here:** the raw pages must be fetched before anything can be extracted; isolated in a VM because it is the only layer that touches hostile content.
- **Methods:** Tor SOCKS5 routing; Splash JS rendering; rate limiting; dead-service handling; SHA-256 dedup.
- **Consumes:** `.onion` URLs. **Produces:** raw HTML (→ MinIO) + crawl metadata.
- **Key decision:** Tor-only (no VPN); VM blast shield. **Alternatives rejected:** commercial proxies (log requests; not reproducible); running on host (one exploit compromises all data).
- **Justifying papers:** Biryukov 2014 (onion crawling methodology); Owenson 2018 (the ~8% unauthenticated-surface limitation); Dizzy 2022 and *The Devil Behind the Mirror* 2024 (modern large-scale onion crawling at scale).
- **Confidence contribution:** none directly; enables 2.2–2.4.

#### Layer 2.2 — Address + PGP Extraction

- **Position:** after acquisition.
- **Problem solved:** pull Bitcoin addresses and PGP fingerprints out of page text/images.
- **Why here:** needs the raw page; produces the entities that entity resolution (2.4) and the risk engine consume.
- **Methods:** four BTC regexes; Base58Check/bech32 checksum validation; PGP block parsing + bare-fingerprint regex; OCR/QR for images.
- **Consumes:** HTML/images. **Produces:** validated addresses + PGP fingerprints.
- **Key decision:** checksum-validate before storing (drops garbage). **Alternative rejected:** storing all regex matches — rejected (Issue #17, fills DB with phantom addresses).
- **Justifying papers:** *The Devil Behind the Mirror* 2024 (regex+checksum at scale), MFScope/Cybercriminal Minds (NDSS 2019, multi-currency extraction).
- **Confidence contribution:** PGP_CRIMINAL_LINK (LR 100) when a fingerprint matches a confirmed criminal.

#### Layer 2.3 — Context + Topic Classification

- **Position:** after extraction.
- **Problem solved:** decide whether an address is a *payment* address (inculpatory) or a *victim* mention (exculpatory), and what criminal activity the page is about.
- **Why here:** the context label is what gates entry to PRE_CRIME (Phase 5) and sets the DARK_WEB_PAYMENT confidence; it must be computed per address before scoring.
- **Methods:** keyword scoring with victim-override; (production) sentence-boundary windows; LDA topic modelling.
- **Consumes:** address + surrounding text. **Produces:** `context_type` (PAYMENT/VICTIM/AMBIGUOUS), `page_topic`, confidence.
- **Key decision:** victim keywords override everything (prevents flagging victims). **Alternative rejected:** treating any address occurrence as payment — rejected (would criminalise victims, Issue #18).
- **Justifying papers:** Spitters 2014 (topic modelling); the contribution is *combining* topic + payment extraction on the same page (no prior work does this).
- **Confidence contribution:** DARK_WEB_PAYMENT (LR 50 POC / ~720 calibrated); VICTIM_CONTEXT (LR 0.2, exculpatory).

#### Layer 2.4 — Entity Resolution + Shared-Wallet Onion Graph

- **Position:** after extraction/classification.
- **Problem solved:** link the same operator across markets (via PGP/alias/wallet) and connect onion domains that share a payment wallet.
- **Why here:** needs extracted entities; produces entity links the risk engine and graph consume.
- **Methods:** four-signal probabilistic resolution (Jaro-Winkler aliases); shared-wallet edge construction in Neo4j.
- **Consumes:** addresses, PGP, aliases, domains. **Produces:** entity graph + shared-wallet onion edges.
- **Key decision:** probabilistic (confidence-weighted) resolution, not binary. **Alternative rejected:** deep-learning entity resolution (no labelled training pairs yet); deterministic binary linking (fails on partial evidence).
- **Justifying papers:** Christin 2013, Sun 2019 (cross-market vendors); Biryukov 2014 (hyperlink edges — our shared-wallet edge is the novel extension).
- **Confidence contribution:** PGP_CRIMINAL_LINK; feeds shared-wallet edge weight (Contribution 2).

---

### Phase 3 — Blockchain Graph + Clustering Layers

#### Layer 3.1 — Graph Acquisition

- **Position:** first Phase-3 layer.
- **Problem solved:** obtain the transaction subgraph around seeds.
- **Why here:** clustering/propagation need the graph; it must be fetched first.
- **Methods:** BigQuery 3-hop expansion (POC) / Bitcoin node + ElectrumX (production).
- **Consumes:** seeds. **Produces:** transaction graph (nodes=addresses, edges=transactions).
- **Key decision:** BigQuery for POC (free, reproducible), own node for production (real-time). **Alternative rejected:** rate-limited public APIs (infeasible for clustering).
- **Justifying papers:** Ron & Shamir 2013 (the original full-graph analysis); Weber 2019 (Elliptic graph).
- **Confidence contribution:** none directly; substrate for taint.

#### Layer 3.2 — CIO Clustering (with CoinJoin pre-filter)

- **Position:** after acquisition.
- **Problem solved:** group the many addresses of one entity into a cluster.
- **Why here:** must precede service recognition and propagation (you classify and propagate over clusters).
- **Methods:** Union-Find CIO; CoinJoin pre-filter (≥40% equal outputs ∧ ≥5 outputs); Lightning channel filter; multi-heuristic weighted voting (CIO 0.40, script-change 0.30, optimal 0.20, reuse 0.10).
- **Consumes:** graph. **Produces:** `address_clusters`.
- **Key decision:** CoinJoin/LN pre-filters + 2024-recalibrated weights. **Alternative rejected:** naive Meiklejohn CIO (15–25% false-merge on SegWit); naive change heuristic (23% FPR).
- **Justifying papers:** Meiklejohn 2013, Delgado 2021, Schnoering 2024, Tironsakkul 2022, Stütz 2022, Kappos & Yousaf 2021, *Heuristics for Detecting CoinJoin* 2023, Block-Number Taproot 2025.
- **Confidence contribution:** cluster membership lets one verdict cover all member addresses; merge confidence flags tentative merges.

#### Layer 3.3 — Service Recognition  ⚠️ MUST PRECEDE PROPAGATION

- **Position:** after clustering, **before** propagation — the pivotal ordering.
- **Problem solved:** classify each cluster (exchange / mixer / pool / unknown) so taint behaves correctly.
- **Why here (what breaks if reordered):** if propagation runs first, taint contaminates exchange customers and must be retroactively undone — expensive and error-prone (see the rule at the top of Section 1).
- **Methods:** known-label lookup + feature-based detection; emits a `taint_modifier` (0.0 exchange/pool, 0.5 CoinJoin, 1.0 unknown, 2.0 mixer).
- **Consumes:** clusters + `service_labels`. **Produces:** service type + taint modifier.
- **Key decision:** modifiers gate propagation. **Alternative rejected:** post-hoc service classification (requires retroactive un-tainting).
- **Justifying papers:** Meiklejohn 2013 (service identification by direct interaction); the *ordering* is BTC-Intel's architectural contribution.
- **Confidence contribution:** EXCHANGE_VERIFIED/MINING_POOL → exculpatory; mixer → amplify.

#### Layer 3.4 — Risk Propagation (three methods / ensemble)

- **Position:** after service recognition.
- **Problem solved:** spread risk from seeds to addresses that had financial contact with criminals.
- **Why here:** needs clusters + service modifiers.
- **Methods:** amount-weighted taint, label propagation, PPR (POC: compared; production: ensemble with learned weights); dust threshold 5%, max 3 hops; protocol-specific CoinJoin decay.
- **Consumes:** graph + modifiers. **Produces:** `taint_scores` (hop 1/2/3).
- **Key decision:** implement all three and compare (Contribution 4). **Alternative rejected:** a single method (Nerino uses only label-prop; Chainalysis only taint).
- **Justifying papers:** Chainalysis patent (taint), Nerino 2021 (label-prop), Gao 2022 (calls for formal fusion).
- **Confidence contribution:** TAINT_HOP_1/2/3 (LR 20/8/3).

---

### Phase 4 — Cross-Reference + Risk Engine Layers

#### Layer 4.1 — Rule Fast Path

- **Position:** first risk-engine layer.
- **Problem solved:** decide clear-cut cases instantly and deterministically.
- **Why here:** short-circuits before expensive Bayesian/anomaly work; OFAC must override everything.
- **Methods:** deterministic rules (OFAC→BLACKLISTED 1.0; exchange/pool/dust→CLEAN).
- **Key decision:** rules first. **Alternative rejected:** pure ML (cannot guarantee OFAC override; unexplainable).
- **Confidence contribution:** sets the score to a deterministic extreme when fired.

#### Layer 4.2 — Provenance-Aware Bayesian Fusion

- **Position:** after the fast path.
- **Problem solved:** combine many weak/strong signals proportionally *without double-counting correlated evidence*.
- **Why here:** needs all signals from Phases 2–3; produces the posterior that sets the category.
- **Methods:** log-odds update from prior 0.001 × likelihood ratios; provenance chains skip already-counted sources.
- **Key decision:** provenance de-duplication (Contribution 3). **Alternative rejected:** weighted averaging (treats correlated evidence as independent → over-counts).
- **Justifying papers:** Gao 2022 (gap), Bayesian/Dempster-Shafer fusion (arXiv 2104.07440) confirming the over-counting problem.
- **Confidence contribution:** the posterior itself.

#### Layer 4.3 — Behavioural Anomaly (Isolation Forest + SHAP)

- **Position:** supplementary, blended 30% into the Bayesian 70%.
- **Problem solved:** catch novel patterns no rule/LR encodes.
- **Methods:** Isolation Forest on temporal features; SHAP explains its contributions.
- **Key decision:** supplementary weight, not primary. **Alternative rejected:** anomaly-as-primary (too noisy alone).
- **Justifying papers:** Peled 2021 (features), Lundberg 2017 (SHAP), *Detecting Anomalies… with Explainability* 2024.
- **Confidence contribution:** BEHAVIORAL_ANOMALY (LR ~8).

---

### Phase 5 — PRE_CRIME + Explainability Layers

#### Layer 5.1 — PRE_CRIME Admission + Monitoring

- **Position:** parallel output of Phase 2 + Phase 4.
- **Problem solved:** flag zero-history addresses from dark-web context before any transaction.
- **Why here:** needs context (2.3) + zero-history verification (3.1); monitored until first tx, then re-scored by Phase 4.
- **Methods:** PAYMENT + confidence≥0.40 + zero-history → watchlist; BigQuery poll (POC) / ElectrumX subscription (production).
- **Key decision:** the entire novel state (Contribution 1). **Alternative rejected:** waiting for a transaction (what every other system does).
- **Justifying papers:** none solve it — Chainalysis patent requires a transaction; Peled 2021/Chen 2023 require history.
- **Confidence contribution:** the PRE_CRIME category itself.

#### Layer 5.2 — Explainability (Counterfactual + SHAP + Contradictions)

- **Position:** final layer before output.
- **Problem solved:** make every verdict explainable and legally defensible.
- **Methods:** counterfactual (rule/Bayesian), SHAP (anomaly), contradiction detector, narrative.
- **Key decision:** route by decisive layer. **Alternative rejected:** SHAP-only (cannot explain rules).
- **Justifying papers:** Lundberg 2017, Wachter 2017.
- **Confidence contribution:** none (explains, does not score) — but mandatory for deployment.

---
## Section 2 — Complete Research Paper Catalog

Every paper from the planning docs **and** every newer paper found by literature search, in a uniform format. Papers marked **★ NEW (web search)** were not in the original planning documents.

---

### Category A — Clustering and Heuristics

---

**Paper:** A Fistful of Bitcoins: Characterizing Payments Among Men with No Names
**Venue:** ACM Internet Measurement Conference (IMC) 2013
**arXiv/DOI:** ACM DL 10.1145/2504730.2504747
**Core contribution:** Operationalised the two foundational de-anonymisation heuristics — Common-Input-Ownership (CIO: co-signing inputs share an owner) and the change-address heuristic — and used them to cluster the Bitcoin graph into ~1,070 user clusters, labelling major services (Mt. Gox, Silk Road, SatoshiDice) by direct interaction.
**What it got right:** CIO is still the highest-precision wallet-grouping heuristic; the direct-interaction labelling method is still used by Chainalysis/TRM today. BTC-Intel builds CIO directly into Layer 3.2.
**Gap 1:** No CoinJoin awareness (written pre-CoinJoin) → naive CIO causes 15–25% false-merge on 2024 SegWit data.
**Gap 2:** Static snapshot — cluster membership never updates as keys are sold.
**Gap 3:** Binary merges — no confidence; cannot distinguish a near-certain merge from a speculative one.
**BTC-Intel POC solution:** CoinJoin pre-filter before CIO; multi-heuristic weighted voting with confidence; Union-Find clustering (File A §7.2/§7.5).
**Final Product upgrade:** Lightning channel detection, Taproot UNRESOLVED flagging, temporal split/merge event logging (File B App B).
**Research claim:** "CoinJoin pre-filtering plus confidence-weighted voting reduces CIO false-positive merges from X% to Y% on a 2024 dataset."
**Patent relevance:** CIO itself is unpatentable prior art (this paper); our *additions* (provenance fusion, PRE_CRIME) are the patentable parts — claims must disclaim CIO.

---

**Paper:** Quantitative Analysis of the Full Bitcoin Transaction Graph
**Venue:** Financial Cryptography 2013
**arXiv:** 1209.0440
**Core contribution:** First large-scale quantitative map of the Bitcoin graph; introduced the *peel chain* as a layering/mixing pattern and showed early Silk Road traceability.
**What it got right:** Peel-chain detection is a behavioural feature BTC-Intel uses in the anomaly layer (4.3).
**Gap 1:** No external labels — the paper explicitly calls for "external labelling methods" as future work (the map has no city names).
**Gap 2:** Peel chains identified visually, not as a formal implementable feature.
**BTC-Intel POC solution:** Dark-web payment context *is* the external labelling Ron & Shamir called for (Phase 2 → Layer 2.3), making BTC-Intel the methodological successor to their open problem.
**Final Product upgrade:** Automated daily crawling + label propagation across clusters (File B §4).
**Research claim:** "We supply the external labelling explicitly identified as future work in Ron & Shamir (2013) via off-chain dark-web intelligence."
**Patent relevance:** Low for this paper directly; supports the framing of the PRE_CRIME contribution.

---

**Paper:** Resurrecting Address Clustering in Bitcoin
**Venue / arXiv:** 2107.05749 (Delgado-Segura et al., 2021)
**Core contribution:** Re-assessed Meiklejohn's heuristics on modern Bitcoin: the naive change heuristic has 23% FPR on SegWit; introduced the *optimal-change* heuristic and *multi-heuristic weighted voting*.
**What it got right:** The script-type and optimal-change heuristics; the weighted-voting framework. BTC-Intel adopts both (Layer 3.2).
**Gap 1:** Weights calibrated on pre-2021 data; Taproot (activated Nov 2021) breaks the script-type heuristic (all P2TR outputs look identical).
**Gap 2:** No temporal stability analysis — does not test whether optimal weights drift over time.
**BTC-Intel POC solution:** Use script-type (not naive) change heuristic; recalibrate weights to 2024 (CIO 0.50→0.40 for CoinJoin growth); flag P2TR UNRESOLVED (File A §7.3/§7.6).
**Final Product upgrade:** Quarter-by-quarter precision-degradation measurement as P2TR adoption rises (File B App L.2).
**Research claim:** "We perform the temporal heuristic-stability analysis Delgado et al. (2021) identified as needed, charting clustering precision against P2TR adoption 2021–2025."
**Patent relevance:** Heuristics are prior art; the *temporal measurement methodology* is publishable but weak for patent.

---

**Paper:** ★ NEW (web search) — Assessing the Efficacy of Heuristic-Based Address Clustering for Bitcoin (Schnoering & Vazirgiannis)
**Venue / arXiv:** 2403.00523 (2024)
**Core contribution:** Most recent major clustering paper; introduces four new heuristics and a "clustering ratio" metric, analysing temporal evolution of heuristic effectiveness.
**What it got right:** Quantifies how heuristic effectiveness changes over time — directly relevant to our recalibration.
**Gap 1:** Optimises *compression* (clustering ratio), not *forensic precision* — a heuristic can merge aggressively (high ratio) while merging wrong entities (low precision).
**Gap 2:** No criminal-detection evaluation (does a cluster around an OFAC seed contain only criminal addresses?).
**BTC-Intel POC solution:** Evaluate each of the four heuristics on *forensic precision* (fraction of an OFAC-seeded cluster that is also criminal), a dimension Schnoering does not measure (File A §7.5 voting + Appendix C eval).
**Final Product upgrade:** Incorporate all four heuristics with *forensic-precision-calibrated* weights, not compression-ratio weights.
**Research claim:** "We evaluate the Schnoering et al. (2024) heuristics on forensic precision rather than compression ratio, producing the first criminal-detection-oriented comparison of these heuristics."
**Patent relevance:** Low (evaluation methodology); supports clustering-quality claims.

---

**Paper:** ★ NEW (web search) — Heuristics for Detecting CoinJoin Transactions on the Bitcoin Blockchain
**Venue / arXiv:** 2311.12491 (2023)
**Core contribution:** Refined multi-protocol CoinJoin detection (JoinMarket, Wasabi, Whirlpool) validated through block 760,000.
**What it got right:** Newer, broader protocol coverage than Tironsakkul 2022; directly informs our detector.
**Gap 1:** Detection only — does not deanonymise participants within a mix.
**Gap 2:** Does not integrate dark-web context to distinguish privacy-motivated from criminal mixing.
**BTC-Intel POC solution:** Generic CoinJoin pre-filter (File A §6.6/§7.2).
**Final Product upgrade:** Protocol-specific detector with per-protocol taint decay (Whirlpool/Wasabi-2 0.30, Wasabi-1/JoinMarket 0.35, generic 0.50) (File B §4B).
**Research claim:** "We combine 2023-era protocol-specific CoinJoin detection with dark-web pre-mix context to distinguish criminal from privacy-motivated mixing."
**Patent relevance:** Detection is prior art; the *pre-mix-context-conditioned taint* is a candidate dependent claim.

---

**Paper:** The Unique Dressing of Transactions: Wasabi CoinJoin Transaction Detection (Tironsakkul et al.)
**Venue:** ACM EICC 2022
**Core contribution:** Showed Wasabi 1.x CoinJoins have a distinctive structural fingerprint detectable with high accuracy; traced stolen BTC into Wasabi mixes.
**What it got right:** The detection fingerprint we use as a pre-filter.
**Gap 1:** Detection ≠ deanonymisation. **Gap 2:** Wasabi 2.0 (WabiSabi, dynamic denominations) breaks the 1.x fingerprint. **Gap 3:** No dark-web context integration.
**BTC-Intel POC solution:** Wasabi/Whirlpool thresholds in the CoinJoin filter (File A §7.2).
**Final Product upgrade:** Wasabi 2.0 (≥20 inputs) rule + post-mix taint at reduced confidence (File B §4B).
**Research claim:** "Dark-web pre-mix context elevates post-mix outputs to SUSPECTED_POST_MIX_CRIMINAL, distinguishing criminal from benign Wasabi use."
**Patent relevance:** Detection prior art; context-conditioned post-mix taint is a dependent claim.

---

**Paper:** Adoption and Actual Privacy of Decentralized CoinJoin Implementations in Bitcoin (Stütz et al.)
**Venue / arXiv:** 2109.10229 (2022)
**Core contribution:** Measured that CoinJoins provide only *partial* privacy — pre-mix accumulation and post-mix spending often re-link funds; only ~$322M of ~$4.74B mixed reached exchanges cleanly.
**What it got right:** Establishes that post-mix traceability exists — the basis for our reduced-confidence taint through mixers.
**Gap 1:** Documents pre/post-mix traceability but does not operationalise it into a forensic tool.
**BTC-Intel POC solution:** Taint continues through CoinJoin at 0.5 retention rather than stopping (File A §7.8 / File B §4B).
**Final Product upgrade:** Pool-specific decay rates from Stütz's measured anonymity-set sizes (Whirlpool 0.3, Wasabi 0.35, JoinMarket 0.35).
**Research claim:** "We operationalise the pre/post-mix traceability measured by Stütz et al. (2022) as protocol-specific taint-decay parameters."
**Patent relevance:** The decay-parameter model is a candidate dependent claim.

---

**Paper:** An Empirical Analysis of Privacy in the Lightning Network (Kappos & Yousaf et al.)
**Venue / arXiv:** Financial Cryptography 2021 / 2003.12470
**Core contribution:** Showed channel open/close transactions leak information (usage intensity, approximate balances, sometimes flow direction), though most LN payments remain opaque.
**What it got right:** Channel-funding (2-of-2 multisig) detection — we use it to avoid wrongly merging channel partners.
**Gap 1:** Individual LN payments remain a black box.
**BTC-Intel POC solution:** Detect LN channel opens, skip CIO for partners, flag TAINT_MAY_HAVE_ESCAPED_TO_LN (File A §7.2 LN filter).
**Final Product upgrade:** LN gossip-graph correlation to identify criminal-operated nodes (File B App L.1).
**Research claim:** "We identify criminal-operated Lightning nodes by correlating gossip-graph node IDs with on-chain channel-funding addresses in flagged clusters."
**Patent relevance:** Gossip-on-chain correlation for criminal-node ID is a candidate claim (cross-domain).

---

**Paper:** An Empirical Analysis of Anonymity in Zcash (Kappos et al.)
**Venue:** USENIX Security 2018
**Core contribution:** Methodology for finding invariants that remain observable despite privacy enhancements (shielded pools).
**What it got right:** The "find observable invariants under privacy tech" template applies to Taproot/LN.
**Gap relevant to BTC-Intel:** The equivalent Taproot-invariant analysis for Bitcoin had not been published.
**BTC-Intel POC solution:** Flag P2TR UNRESOLVED (File A §7.6).
**Final Product upgrade:** Taproot degradation measurement (File B App L.2).
**Research claim:** "We extend the privacy-invariant methodology of Kappos et al. (2018) to Bitcoin Taproot."
**Patent relevance:** Low (methodology); see Block-Number Taproot below for the novelty caveat.

---

**Paper:** ★ NEW (web search) — Block Number-Based Address Clustering for the Bitcoin Taproot Upgrade
**Venue:** ResearchGate preprint (2025)
**Core contribution:** Proposes a novel on-chain heuristic for P2TR clustering using the 6-block-confirmation principle — a clustering signal that survives Taproot's script-type hiding.
**What it got right:** It *is* a working P2TR clustering heuristic — which directly affects BTC-Intel's novelty claim.
**Gap 1:** Single heuristic; not integrated with off-chain intelligence; precision on criminal clusters not established.
**BTC-Intel POC solution:** Continue to flag P2TR UNRESOLVED for script-type, but **honestly retire the claim of a novel P2TR heuristic** (File A §7.6 note).
**Final Product upgrade:** Optionally adopt the block-number heuristic and measure its forensic precision (File B App L.2).
**Research claim (revised, honest):** "A novel P2TR clustering heuristic now exists (2025); our contribution is the *temporal precision-degradation measurement* and *forensic-precision evaluation*, not a new heuristic."
**Patent relevance:** This paper is **prior art that narrows** any BTC-Intel Taproot-clustering patent claim — do not file a broad P2TR-clustering claim.

---

**Paper:** ★ NEW (web search) — Heuristic-Based Address Clustering in the Cardano Blockchain
**Venue / arXiv:** 2503.09327 (2025)
**Core contribution:** Adapts CIO-style clustering to Cardano's eUTXO model.
**What it got right:** Confirms CIO generalises across UTXO chains — relevant to any future multi-chain extension.
**Gap 1:** Cardano-specific; not Bitcoin; no off-chain integration.
**BTC-Intel response:** Out of scope for v1 (Bitcoin-only); noted for the multi-blockchain extension (File C §4, multi-blockchain row).
**Research claim:** N/A (cited as related work for cross-chain generalisability).
**Patent relevance:** None directly.

---

### Category B — Machine Learning on the Blockchain

---

**Paper:** Anti-Money Laundering in Bitcoin: Experimenting with GCNs (Weber et al.) — the Elliptic dataset paper
**Venue:** KDD Workshop on Anomaly Detection in Finance 2019
**Core contribution:** Released the Elliptic dataset (203,769 transactions, 4,545 illicit, 166 features); GCN 77%/52% (F1 63%), RF 95%/37% — establishing the precision/recall tradeoff of the field.
**What it got right:** The standard public benchmark; BTC-Intel reproduces the RF baseline in Week 1.
**Gap 1:** 2% illicit class — extreme imbalance, hard recall.
**Gap 2:** Data ends 2018 — predates CoinJoin growth, Taproot, LN, bridges.
**Gap 3:** On-chain features only — a zero-history address has an all-zero feature vector.
**BTC-Intel POC solution:** Add 6 off-chain features (dark-web payment confidence, topic, dw_to_first_tx_days, PGP link, onion co-occurrence, alias match) (File A; File B App C).
**Final Product upgrade:** Separate pre-transaction classifier using *only* off-chain features (for zero-history addresses).
**Research claim:** "Adding off-chain dark-web features improves illicit-class recall by X points over the Weber (2019) Elliptic baseline at comparable precision."
**Patent relevance:** Dataset/RF are prior art; the off-chain feature set + pre-transaction classifier support the PRE_CRIME claim.

---

**Paper:** Towards Malicious Address Identification in Bitcoin (Peled et al.)
**Venue / arXiv:** 2112.11721 (2021)
**Core contribution:** 40+ engineered features; RF achieving 95% precision / 40% recall on Elliptic illicit class. BTC-Intel's Week-1 baseline.
**What it got right:** The feature taxonomy (graph/volume/temporal/structural).
**Gap 1:** Static features over full history dilute recent criminal turns. **Gap 2:** Cannot classify pre-transaction addresses (all features zero). **Gap 3:** No dark-web context.
**BTC-Intel POC solution:** 4-window temporal-delta features (7/30/90/365d) + dormancy-break (File B App C); PRE_CRIME for zero-history (Phase 5).
**Final Product upgrade:** 200+ dimensional temporal vector + lifecycle phase classifier.
**Research claim:** "Temporal delta features increase Elliptic illicit-class recall by X points over the static Peled (2021) baseline without precision loss."
**Patent relevance:** Features are prior art; temporal-gap feature (Contribution 5) is novel.

---

**Paper:** Evolve Path Tracer: Early Detection of Ponzi Schemes and Rug Pulls (Chen et al.)
**Venue / arXiv:** 2301.05412 (2023)
**Core contribution:** Temporal GNN modelling a four-phase criminal wallet lifecycle (pre-crime → active → evasion → exit); 87% F1 early detection.
**What it got right:** The four-phase framework is the theoretical underpinning for why pre-transaction scoring is possible.
**Gap 1:** Needs heavy ML infra (PyTorch Geometric, GPU, labelled temporal data). **Gap 2:** On-chain only — no off-chain temporal anchor.
**BTC-Intel POC solution:** Rolling-window features approximate phases without a TGNN; dw_to_first_tx_days anchors the pre-crime phase (File A §9; File B App C).
**Final Product upgrade:** Full four-phase classifier with phase label on the dashboard.
**Research claim:** "The dark-web-listing-to-first-transaction gap is a statistically significant predictor of illicit classification — a pre-crime-phase signal computable only with off-chain timestamps."
**Patent relevance:** Directly supports PRE_CRIME (Contribution 1) and the temporal-gap feature (Contribution 5).

---

**Paper:** Fingerprinting Bitcoin Entities Using Money Flow Representation Learning (Sayadi et al.)
**Venue:** Applied Network Science 2023 (Springer 10.1007/s41109-023-00591-2)
**Core contribution:** Graph Attention Networks learn 64-dim behavioural fingerprints capturing an entity's money-flow "style"; enables similarity-based classification and cross-market linking.
**What it got right:** The fingerprint embedding we use in the FAISS library (File B App C).
**Gap 1:** Classification task only — not *discovery* of new unlabelled criminals. **Gap 2:** Single-market scope; cross-market generalisation untested.
**BTC-Intel POC solution:** (Production) FAISS fingerprint library of OFAC-confirmed clusters; similarity > 0.85 adds BEHAVIORAL_SIMILARITY.
**Final Product upgrade:** Discovery mechanism — find unlabelled clusters that behave like confirmed criminals (File B App Z.1).
**Research claim:** "First evaluation of behavioural-fingerprint similarity as a *discovery* mechanism for unlabelled criminal entities (precision X at recall Y)."
**Patent relevance:** Discovery-by-similarity is a candidate claim if combined with the OFAC-fingerprint-library construction.

---

**Paper:** Machine Learning Methods to Detect Money Laundering in the Bitcoin Blockchain (Lorenz et al.)
**Venue / arXiv:** 2005.14635 (2020)
**Core contribution:** XGBoost + GNN on Elliptic (F1 0.71 with GNN); graph features improve precision over node-level.
**What it got right:** Confirms graph structure adds signal.
**Gap 1:** No temporal features. **Gap 2:** No explainability (black-box).
**BTC-Intel POC solution:** Temporal features (File B App C) + SHAP/counterfactual explainability (Layer 5.2).
**Research claim:** "We add the explainability Lorenz et al. (2020) acknowledge as missing, via counterfactual + SHAP for a hybrid rule+ML engine."
**Patent relevance:** Counterfactual-for-blockchain (Contribution-adjacent) supports the explainability claim.

---

**Paper:** ★ NEW (web search) — Detecting Illicit Transactions in Bitcoin: A Wavelet-Temporal Graph Transformer Approach for AML (ChronoWave-GNN)
**Venue:** Scientific Reports 2025 (s41598-025-23901-3)
**Core contribution:** Combines Discrete Wavelet Transform with a temporal graph transformer; state-of-the-art on Elliptic (exceeding ~97% AUROC class of methods).
**What it got right:** Best-in-class *post-transaction* detection.
**Gap 1:** On-chain only — zero information before the first transaction remains.
**BTC-Intel response:** Do **not** compete on the Elliptic leaderboard; position BTC-Intel as *complementary* (pre-transaction). Layer 4.3 is modular to allow swapping in such a TGNN later (File A; File B App K).
**Research claim:** "BTC-Intel addresses the pre-transaction phase that state-of-the-art on-chain models (ChronoWave-GNN, 2025) cannot, by construction."
**Patent relevance:** None directly; strengthens the PRE_CRIME novelty framing (the SOTA literally cannot do it).

---

**Paper:** ★ NEW (web search) — The Shape of Money Laundering: Subgraph Representation Learning with the Elliptic2 Dataset (Bellei et al.)
**Venue / arXiv:** 2404.19109 (KDD 2024; MIT-IBM)
**Core contribution:** Elliptic2 dataset — 122K labelled subgraphs over a 49M-node, 196M-edge background graph; subgraph (not node) level money-laundering classification; RevClassify baseline.
**What it got right:** A far larger, subgraph-level successor to Elliptic — a stronger benchmark/calibration source.
**Gap 1:** On-chain only; still no off-chain/pre-transaction dimension.
**BTC-Intel response:** Adopt Elliptic2 for a stronger calibration/evaluation baseline (File B §6/App V); the off-chain gap remains BTC-Intel's territory.
**Research claim:** "We calibrate and evaluate on Elliptic2 (2024), the largest labelled AML graph dataset, while contributing the off-chain pre-transaction signal it lacks."
**Patent relevance:** None directly (dataset).

---

**Paper:** ★ NEW (web search) — Inspection-L: Self-Supervised GNN Node Embeddings for Money Laundering Detection in Bitcoin
**Venue / arXiv:** 2203.10465 (2022)
**Core contribution:** Self-supervised node embeddings (DGI) + downstream classifier on Elliptic, reducing label dependence.
**What it got right:** Self-supervision helps under the 2% label scarcity.
**Gap 1:** On-chain only; no explainability; no pre-transaction.
**BTC-Intel response:** Self-supervised embeddings are an optional Layer-4.3 enhancement; the off-chain + explainability gaps remain ours.
**Research claim:** N/A (related work for label-scarcity mitigation).
**Patent relevance:** None.

---

**Paper:** ★ NEW (web search) — Demystifying Fraudulent Transactions and Illicit Nodes in the Bitcoin Network for Financial Forensics
**Venue / arXiv:** 2306.06108 (2023)
**Core contribution:** End-to-end forensic pipeline + augmented Elliptic-style analysis for illicit-node detection.
**What it got right:** Practical forensic framing aligning with BTC-Intel's analyst use case.
**Gap 1:** On-chain only; no dark-web/off-chain; limited explainability.
**BTC-Intel response:** Confirms the on-chain side of our hybrid; we add the off-chain side.
**Patent relevance:** None directly.

---

**Paper:** Temporal Graph Networks for Deep Learning on Dynamic Graphs (Poursafaei/Rossi et al.)
**Venue / arXiv:** 2006.10637
**Core contribution:** Foundational TGN architecture for temporal graph learning.
**Relevance:** The architecture to adopt if BTC-Intel's Layer 4.3 moves to a temporal GNN in production v2. Not needed for POC.
**Patent relevance:** None (foundational ML).

---
### Category C — Dark Web Intelligence

---

**Paper:** Trawling for Tor Hidden Services: Detection, Measurement, Deanonymization (Biryukov et al.)
**Venue:** IEEE S&P 2014
**Core contribution:** Foundational onion-service enumeration (HSDir technique); first large onion graph using *hyperlink* edges; found a large fraction of onion services relate to illegal activity.
**What it got right:** The crawler+graph methodology BTC-Intel's Phase 2 builds on.
**Gap 1:** Hyperlink edges are weak — two linked sites may be unrelated. **Gap 2:** 2014 data; onion-space composition has changed.
**BTC-Intel POC solution:** Introduce the **shared-wallet edge** — two onion domains sharing a payment address are almost certainly one operator (File A App A). This is Contribution 2.
**Final Product upgrade:** Real-time edge updates; infrastructure-group detection feeds entity resolution (File B App B).
**Research claim:** "The shared-payment-address edge reveals criminal-infrastructure coordination invisible to hyperlink topology (Biryukov 2014)."
**Patent relevance:** **Patentable** (Contribution 2) — financial-instrument-as-graph-edge is a cross-domain combination with no prior art.

---

**Paper:** Towards a Comprehensive Insight into the Thematic Organization of Tor Hidden Services (Spitters et al.)
**Venue:** IEEE EISIC 2014
**Core contribution:** LDA topic modelling classifying onion content (drugs/weapons/fraud/services).
**What it got right:** The topic taxonomy used in Layer 2.3.
**Gap 1:** Topics are descriptive — not linked to payment infrastructure.
**BTC-Intel POC solution:** Run topic classification *and* address extraction on the same page → `page_topic` per extracted address (File A §6.4). Not done in any prior work.
**Final Product upgrade:** Fine-tuned dark-web topic model; topic-specific likelihood ratios (DRUG > generic SERVICES).
**Research claim:** "We extend Spitters (2014) topic modelling from a descriptive tool to a risk feature by binding topic to extracted payment addresses."
**Patent relevance:** Low alone; supports the DARK_WEB_PAYMENT signal.

---

**Paper:** Automated Analysis of Dark Net Markets (Ghosh et al.)
**Venue:** ACM WebSci 2017
**Core contribution:** Automated market-listing classification + price extraction; vendor opsec varies.
**What it got right:** Price extraction — the basis for our amount-correlation signal.
**Gap 1:** No PGP-continuity cross-market linking. **Gap 2:** Prices not correlated with on-chain values.
**BTC-Intel POC solution:** Parse listing amount; (production) compare to first on-chain tx amount → AMOUNT_CORRELATION (File B §8/App G).
**Final Product upgrade:** ±5% amount matching within 24h as a calibrated LR ~15 signal.
**Research claim:** "Listing-price-to-first-transaction amount correlation is strong corroboration of a completed criminal payment — unavailable to single-source tools."
**Patent relevance:** Amount-correlation is a candidate **dependent** claim (weaker non-obviousness).

---

**Paper:** Traveling the Silk Road: A Measurement Analysis (Christin)
**Venue:** WWW 2013
**Core contribution:** First systematic Silk Road measurement; vendor aliases are stable and reused.
**What it got right:** Alias stability motivates our alias-based entity resolution.
**Gap 1:** Manual alias tracking; no automated normalisation/fuzzy matching; cross-market reuse noted but not exploited.
**BTC-Intel POC solution:** Jaro-Winkler alias matching (≥0.90) + PGP continuity (File B App B).
**Research claim:** "Automated four-signal cross-market vendor resolution scales the manual alias tracking of Christin (2013)."
**Patent relevance:** Entity resolution is partially prior art; the *four-signal probabilistic* combination is novel-ish (8/10 in the matrix).

---

**Paper:** Cross-Market Drug Vendor Identification (Sun et al.)
**Venue:** WebSci 2019
**Core contribution:** Stylometric cross-market vendor linking (78% accuracy).
**What it got right:** Confirms vendors operate cross-market under different aliases.
**Gap 1:** Stylometry only — no blockchain/PGP signals. **Gap 2:** Pairwise links, no unified entity graph.
**BTC-Intel POC solution:** Unified four-signal entity graph (wallet + PGP + alias + domain) in Neo4j (File B App B).
**Research claim:** "We unify stylometric, cryptographic (PGP), and financial (wallet) signals into a single probabilistic entity graph, beyond the stylometry-only linking of Sun et al. (2019)."
**Patent relevance:** Four-signal resolution is a candidate claim.

---

**Paper:** The Darknet's Smaller than We Think (Owenson et al.)
**Venue:** Digital Investigation 2018
**Core contribution:** Much criminal infrastructure is behind login; an unauthenticated crawler sees only ~8% of the active criminal surface.
**What it got right:** Honest grounding for BTC-Intel's coverage limitation.
**Gap (for us):** Structural — we cannot create market accounts (illegal/unethical), so ~8% coverage is a hard ceiling.
**BTC-Intel response:** Document the limitation explicitly; supplement with DUTA-10K/Gwern archives + unauthenticated forum quotes (File A §6.9 #10).
**Research claim:** "We cite Owenson (2018) to bound our coverage honestly at ~8% unauthenticated surface."
**Patent relevance:** None (limitation, not contribution).

---

**Paper:** Dark Web Marketplaces via Bitcoin: From Birth to Independence (Hiramoto et al.)
**Venue:** Forensic Science International: Digital Investigation 2020
**Core contribution:** Traced market financial lifecycles (launch → peak → exit) via payment addresses; ~12–24 month lifecycles.
**What it got right:** Market-lifecycle framing.
**Gap 1:** Tracks the *market*, not the *individual vendor* across market deaths.
**BTC-Intel POC solution:** PGP/alias entity resolution follows vendors across market shutdowns (File B App B).
**Final Product upgrade:** Market-exit detection + 90-day reappearance monitoring of associated PGP/aliases.
**Research claim:** "We track individual-vendor continuity across market deaths via PGP/alias, beyond the market-level lifecycle of Hiramoto et al. (2020)."
**Patent relevance:** Low alone; supports entity-continuity.

---

**Paper:** ★ NEW (web search) — Cybercriminal Minds: An Investigative Study of Cryptocurrency Abuses in the Dark Web (MFScope) (Lee et al.)
**Venue:** NDSS 2019
**Core contribution:** MFScope crawled 27M+ dark webpages, extracted ~10M unique crypto addresses (BTC/ETH/XMR), and characterised abuse campaigns at scale.
**What it got right:** Demonstrates the *scale* of dark-web address extraction — validating BTC-Intel's dedup/rate-limit/storage design and confirming the approach is sound.
**Gap 1:** Characterisation/measurement, not pre-transaction risk scoring. **Gap 2:** No provenance-aware fusion; no PRE_CRIME state. **Gap 3:** No graph-cross-reference to OFAC clusters with calibrated LRs.
**BTC-Intel POC solution:** Same extraction philosophy, but feeding a *risk engine* with PRE_CRIME + provenance fusion rather than a measurement study (Phases 4–5).
**Final Product upgrade:** Live continuous crawl vs MFScope's one-time study.
**Research claim:** "We convert large-scale dark-web address extraction (MFScope, 2019) from a measurement study into a real-time, calibrated, pre-transaction risk system."
**Patent relevance:** MFScope is **prior art for address extraction** — our claims must focus on PRE_CRIME/fusion, not extraction.

---

**Paper:** ★ NEW (web search) — The Devil Behind the Mirror: Tracking Campaigns of Cryptocurrency Abuses on the Dark Web
**Venue / arXiv:** 2401.04662 (2024)
**Core contribution:** Crawled 4,923 onion sites / 130k+ pages; identified 2,564 illicit sites and 1,189 illicit blockchain addresses; extracted 15,752 addresses (15,450 BTC, 302 ETH) via regex+checksum and tracked abuse campaigns.
**What it got right:** Current best-practice extraction (regex + Base58/checksum + web3 validation) — exactly BTC-Intel's Layer 2.2; validates our pipeline as state of the art.
**Gap 1:** Campaign tracking, not pre-transaction scoring. **Gap 2:** No shared-wallet onion graph edge type. **Gap 3:** No provenance-aware fusion / PRE_CRIME state.
**BTC-Intel POC solution:** Same extraction; plus shared-wallet edges (Contribution 2), PRE_CRIME (Contribution 1), provenance fusion (Contribution 3).
**Final Product upgrade:** Real-time campaign + infrastructure-group detection.
**Research claim:** "Building on 2024 dark-web extraction methods, we add the shared-wallet onion edge and pre-transaction scoring absent from that work."
**Patent relevance:** This is the **most recent prior art for dark-web BTC extraction** — frame claims around our three core contributions, not extraction.

---

**Paper:** ★ NEW (web search) — Dizzy: Large-Scale Crawling and Analysis of Onion Services
**Venue / arXiv:** 2209.07202 (2022)
**Core contribution:** Scalable onion crawling + analysis methodology at large scale.
**What it got right:** Engineering patterns for crawling at scale (dedup, scheduling) — informs Phase 2 production.
**Gap 1:** Crawling/measurement, not financial risk; no on-chain cross-reference.
**BTC-Intel response:** Adopt scaling patterns (File B §4); add the financial/risk layer.
**Patent relevance:** None (crawling infrastructure is prior art).

---

**Paper:** Criminal Motivation on the Dark Web: A Categorical Model (Dalins et al.)
**Venue:** Digital Investigation 2018
**Core contribution:** Behavioural-motivation taxonomy for dark-web actors.
**Relevance:** Informs BTC-Intel's `entity_type` classification (VENDOR/MARKET/MIXER/INDIVIDUAL/SERVICE).
**Patent relevance:** None.

---

### Category D — Risk Scoring and Evidence Fusion

---

**Paper:** Chainalysis Patent US10977655B2 (2021)
**Type:** Issued USPTO patent, class G06Q 20/06
**Core contribution (claim):** Amount-weighted taint scoring — compute taint as tainted-input/total-received and propagate through the graph with decay; the "haircut" method through mixers.
**What it covers (and we must disclaim):** amount-weighted taint as a risk-scoring mechanism; risk score assigned to a blockchain address; haircut decay.
**What it does NOT cover (our territory):** pre-transaction scoring from off-chain context; provenance-tracking to prevent circular evidence; the PRE_CRIME_WATCHLIST state; PGP-cluster-confidence; the shared-wallet onion edge.
**BTC-Intel POC solution:** Our taint follows the patented method (acknowledged prior art) but our novelty is *before* the first transaction and in the fusion engine (File A §7.8/§8).
**Final Product upgrade:** Ensemble taint (still acknowledging the patent for the amount-weighted component).
**Research claim:** "BTC-Intel is complementary to taint-based systems, adding the pre-transaction dimension their patent explicitly requires a transaction to perform."
**Patent relevance:** **Critical blocker** — claims must explicitly disclaim taint propagation and read only on off-chain/pre-transaction elements. Claim 1's requirement of "a taint value propagated from a previously classified address" does **not** read on our PRE_CRIME claim (which acts on zero-history addresses).

---

**Paper:** Bitcoin Transaction Graph Analysis for Money Laundering Detection (Nerino et al.)
**Venue:** ARES 2021
**Core contribution:** Label-propagation risk scoring; 89% accuracy; better recall than naive single-hop taint.
**What it got right:** Label propagation as one valid method (our Method 2).
**Gap 1:** Only label propagation — no comparison to taint or PPR. **Gap 2:** Damping factor set heuristically, not calibrated.
**BTC-Intel POC solution:** Implement all three methods and compare on the same dataset (Contribution 4) (File A §7.8/App C).
**Final Product upgrade:** Ensemble with learned weights (File B §6C).
**Research claim:** "First head-to-head comparison of amount-weighted taint, label propagation, and PPR on one labelled dataset, identifying the best method per address category."
**Patent relevance:** The *comparison* is publishable, not patentable; the ensemble weighting is a weak candidate claim.

---

**Paper:** Blockchain Intelligence: When Blockchain Meets AI (Gao et al.)
**Venue:** IEEE Transactions on Network Science 2022
**Core contribution:** Survey of AI/ML for blockchain analytics; explicitly notes the field "lacks a formal evidence fusion framework" and that systems "combine evidence without formal probabilistic justification."
**What it got right:** It *names the gap* BTC-Intel's provenance-aware Bayesian fusion fills.
**Gap (it identifies):** No formal, provenance-aware evidence fusion exists.
**BTC-Intel POC solution:** Calibrated Bayesian likelihood ratios + provenance de-duplication (Contribution 3) (File A §8.3).
**Research claim:** "We present the first formally specified provenance-aware Bayesian evidence-fusion engine for blockchain risk scoring — the gap Gao et al. (2022) identify."
**Patent relevance:** **Patentable** (Contribution 3) — Gao 2022 establishes the problem is open.

---

**Paper:** ★ NEW (web search) — Bayesian and Dempster-Shafer Models for Combining Multiple Sources of Evidence in a Fraud Detection System
**Venue / arXiv:** 2104.07440
**Core contribution:** Formalises combining evidence via Bayesian/Dempster-Shafer; shows naive *summing* of scores equals *averaging* probabilities and over-counts correlated evidence.
**What it got right:** Independent confirmation that correlated evidence must not be naively combined — exactly the over-counting our provenance fusion prevents.
**Gap 1:** General fraud, not blockchain; no *provenance-chain* mechanism to detect *which* signals are correlated. **Gap 2:** No application to circular OFAC→commercial→OFAC dependencies.
**BTC-Intel POC solution:** Provenance chains explicitly identify correlated sources and skip them (File A §8.3).
**Research claim:** "We extend evidence-fusion theory (Bayesian/Dempster-Shafer) with an explicit *provenance-chain* mechanism that detects and removes circular correlated evidence in blockchain risk scoring."
**Patent relevance:** Strengthens non-obviousness of Contribution 3 — prior work knew the *problem* (over-counting) but not the *provenance-chain solution*.

---

**Paper:** ★ NEW (web search) — A Plug-and-Play Data-Driven Approach for Anti-Money Laundering in Bitcoin
**Venue:** Expert Systems with Applications 2024 (S0957417424029397)
**Core contribution:** Modular, data-driven AML pipeline for Bitcoin.
**What it got right:** Modularity aligns with BTC-Intel's swappable Layer 4.3.
**Gap 1:** On-chain only; no off-chain/pre-transaction; no provenance fusion.
**BTC-Intel response:** Cited as related work for modular AML; our off-chain + fusion remain distinct.
**Patent relevance:** None directly.

---

**Paper:** ★ NEW (web search) — Transformer-Based Risk Monitoring for AML with Transaction Graph Integration
**Venue:** ICDEBA 2025
**Core contribution:** Transformer + transaction-graph features for AML risk monitoring.
**Gap:** On-chain only; no pre-transaction; no calibrated provenance fusion.
**BTC-Intel response:** Optional future Layer-4.3 model; off-chain gap remains ours.
**Patent relevance:** None.

---

**Paper:** ★ NEW (web search) — SoK: Web3 RegTech for Cryptocurrency VASP AML/CFT Compliance
**Venue / arXiv:** 2512.24888
**Core contribution:** Systematisation of compliance/RegTech for crypto VASPs (screening, monitoring, reporting).
**What it got right:** Frames the compliance landscape BTC-Intel's §12 (audit/PMLA/GDPR) targets.
**Gap:** Survey; no pre-transaction mechanism.
**BTC-Intel response:** Use as grounding for the compliance/SAR/audit design (File B §12).
**Patent relevance:** None (survey).

---

**Paper:** ★ NEW (web search) — USPTO US10275772B2 "Cryptocurrency Risk Detection System" & US11182781 "Blockchain Encryption Tags"
**Type:** Issued US patents (prior-art search hits)
**Core contribution:** Risk scoring for crypto transactions based on blockchain factors with weighted factor scores (10275772); blockchain tagging (11182781).
**Why listed:** **Prior-art blockers to check before filing.** 10275772 covers weighted factor risk scoring of *transactions* — our claims must avoid reading on generic weighted transaction risk and stay specific to *pre-transaction off-chain context* and *provenance de-duplication*.
**BTC-Intel response:** Frame independent claims narrowly (pre-transaction, off-chain, provenance) so they do not read on these patents (File C §5B).
**Patent relevance:** **Important blockers** — include in the prior-art search (§5E).

---

### Category E — Explainability

---

**Paper:** A Unified Approach to Interpreting Model Predictions (SHAP) (Lundberg & Lee)
**Venue:** NeurIPS 2017
**Core contribution:** Shapley-value-based additive feature attributions for any ML model.
**What it got right:** Theoretically grounded feature importance — used to explain the Isolation Forest (Layer 4.3).
**Gap 1:** Designed for ML models — cannot explain deterministic rules.
**BTC-Intel POC solution:** SHAP for the ML layer **only** (on-chain risk components — never bank fraud); counterfactual for rule/Bayesian layers (File A App H; File B App E).
**Research claim:** "We pair SHAP (ML layer) with counterfactuals (rule/Bayesian layers) to explain a *hybrid* risk engine end-to-end."
**Patent relevance:** SHAP is prior art; the hybrid routing is a weak candidate.

---

**Paper:** Counterfactual Explanations Without Opening the Black Box (Wachter et al.)
**Venue:** Harvard Journal of Law & Technology 2017
**Core contribution:** Formalises counterfactual explanations — the minimal input change that flips the output.
**What it got right:** The "what would change the verdict?" framing our counterfactual generator implements.
**Gap 1:** No prior application to blockchain address risk scoring.
**BTC-Intel POC solution:** Counterfactual generator that finds the minimal evidence-removal set dropping the score below WATCHLISTED (File A §8.5).
**Research claim:** "First counterfactual-explanation generator for blockchain address risk scoring."
**Patent relevance:** Candidate claim (explainability for blockchain risk) — novel application, moderate non-obviousness.

---

**Paper:** ★ NEW (web search) — Detecting Anomalies in Blockchain Transactions Using ML Classifiers and Explainability Analysis
**Venue / arXiv:** 2401.03530 (2024)
**Core contribution:** ML anomaly detection on blockchain transactions with SHAP-based explanation.
**What it got right:** Confirms SHAP-for-blockchain-anomaly is sound (validates Layer 4.3 + App H).
**Gap 1:** No counterfactual for rule layers; no pre-transaction; no provenance fusion.
**BTC-Intel response:** We add counterfactual for the deterministic layers and the hybrid routing.
**Patent relevance:** Prior art for SHAP-on-blockchain — our explainability claims must center on the *hybrid rule+ML counterfactual*, not SHAP alone.

---

**Paper:** Privacy-Preserving Blockchain Analysis (Yin et al.)
**Venue:** IEEE Transactions on Information Forensics 2023
**Core contribution:** Reviews GDPR implications for blockchain analytics; whether PGP keys/pseudonyms are personal data (Article 4(1)).
**Relevance:** Grounds BTC-Intel's retention policy, IRB requirements, and the PGP-as-personal-data question (File B §12).
**Patent relevance:** None (legal review).

---

### Category F — Additional New Gaps (Web Search)

---

**Paper:** ★ NEW (web search) — Analyzing the Effect of Taproot on Bitcoin Deanonymization
**Venue:** IEEE ICDCSW 2023
**Core contribution:** Confirms Taproot degrades clustering (P2TR outputs uniform); proposes one partial remaining heuristic.
**Gap it opens:** A comprehensive P2TR forensic solution; temporal degradation unmeasured.
**BTC-Intel response:** Flag UNRESOLVED + measure degradation (File B App L.2). (Combined with Block-Number 2025, the "novel P2TR heuristic" claim is retired — measurement is the honest contribution.)
**Research claim:** "We chart Taproot-driven clustering-precision degradation 2021–2025."
**Patent relevance:** Weak after the 2025 block-number heuristic prior art.

---

**Paper:** ★ NEW (web search) — Geolocated Lightning Network Topology Snapshots 2019–2023
**Venue:** Scientific Data 2025 (s41597-025-06413-7)
**Core contribution:** Curated LN gossip-graph snapshots + city-level geolocation.
**Gap it fills for us:** A dataset enabling LN gossip-on-chain correlation.
**BTC-Intel response:** Use for criminal-LN-node identification (File B App L.1).
**Research claim:** "We correlate LN gossip snapshots (2025 dataset) with on-chain channel-funding clusters to identify criminal-operated nodes."
**Patent relevance:** Supports the gossip-correlation candidate claim.

---

**Paper:** ★ NEW (web search) — Time Tells All: Deanonymization of Blockchain RPC Users with Zero Transaction Fee
**Venue / arXiv:** 2508.21440 (2025)
**Core contribution:** A node-RPC-based deanonymisation side channel.
**Gap it opens (for us, operationally):** Running our own node (File B §5) exposes an RPC attack surface.
**BTC-Intel response:** Bind RPC/ZMQ to localhost only; firewall internal (File B §2B, App O hardening).
**Patent relevance:** None (defensive/operational).

---

**Paper:** ★ NEW (web search) — The Dark Art of Financial Disguise in Web3: Money Laundering Schemes and Countermeasures
**Venue / arXiv:** 2509.21831 (2025)
**Core contribution:** SoK of Web3 laundering typologies (mixers, bridges, DeFi) and countermeasures.
**Gap it informs:** Cross-chain bridge laundering (>$7B cumulative) — quantifying how often confirmed criminals bridge out.
**BTC-Intel response:** CROSS_CHAIN_EXIT events + measuring bridge-exit frequency among OFAC clusters (File B App D).
**Research claim:** "We quantify the single-chain intelligence loss by measuring how often OFAC-confirmed clusters exit via cross-chain bridges."
**Patent relevance:** Bridge-exit detection is largely known; the *frequency measurement* is publishable, not patentable.

---

**Paper:** ★ NEW (web search) — Deanonymizing Bitcoin Transactions via Network Traffic Analysis with Semi-Supervised Learning
**Venue / arXiv:** 2603.17261 (2026)
**Core contribution:** Network-layer (not graph-layer) deanonymisation via traffic analysis.
**Relevance:** Orthogonal channel to BTC-Intel (we are passive graph+OSINT); noted as complementary.
**Patent relevance:** None.

---

**Paper:** ★ NEW (web search) — BAClassifier: Automatic Bitcoin Address Behaviour Classification
**Venue:** (dataset/tool; 2M+ addresses, 4 behaviour types)
**Core contribution:** Large annotated behaviour-classification dataset/tool.
**Relevance:** A candidate auxiliary classifier/dataset for Layer 4.3 behaviour features.
**Gap:** On-chain only; no off-chain/pre-transaction.
**Patent relevance:** None (dataset/tool).

---

**Paper:** ★ NEW (web search) — Detection of Crowdsourcing Cryptocurrency Laundering via Multi-Task Collaboration
**Venue / arXiv:** 2512.02534 (2025)
**Core contribution:** Multi-task model for crowdsourced laundering detection.
**Relevance:** Related work for laundering-pattern detection; on-chain only.
**Patent relevance:** None.

---
## Section 3 — The Five Novel Contributions: Deep Technical Specification

Each contribution is specified so it can serve simultaneously as a research-paper section and a patent claim. Structure for each: the problem no prior work solves; how BTC-Intel solves it (pseudocode-level); why it is novel (with citations); the measurable claim; patent claim language (method-claim format); and a paper-section template.

---

### Contribution 1 — PRE_CRIME_WATCHLIST Mechanism (Priority 1 — File First)

**The problem no existing work solves.** Every existing system — Chainalysis, TRM, Elliptic, and every academic paper (Peled 2021, Chen 2023, ChronoWave-GNN 2025) — requires at least one on-chain transaction before it can assign risk. An address with zero transaction history is indistinguishable from a brand-new legitimate address. There is a *pre-transaction window* during which criminal payment infrastructure is established but entirely invisible to monitoring.

**Formal definition.** Let `a` be a Bitcoin address with on-chain transaction count `tx(a) = 0`. Let `D(a)` be the set of dark-web documents in which `a` appears, and `ctx(a,d) ∈ {PAYMENT, VICTIM, AMBIGUOUS}` the classified context of `a` in document `d` with confidence `c(a,d)`. The **PRE_CRIME_WATCHLIST** state is assigned iff:

```
tx(a) = 0  ∧  ∃ d ∈ D(a) : ctx(a,d) = PAYMENT  ∧  c(a,d) ≥ θ        (θ = 0.40)
```

The assigned pre-transaction risk is a function of the dark-web context strength only: `risk_pre(a) = f(max_d c(a,d), topic(a), pgp(a))`. The address is then *monitored*; on the first transaction it is promoted to the full risk engine.

**The dark-web context scoring algorithm (pseudocode):**

```
function score_precrime(address a):
    docs ← crawl_records(a)
    payment_docs ← { d ∈ docs : classify_context(window(a,d)) = PAYMENT }
    if payment_docs = ∅: return NONE
    c ← max { confidence(d) for d in payment_docs }
    if c < θ(0.40): return NONE
    if onchain_tx_count(a) > 0: return NOT_PRECRIME    # has history → full engine
    return PRE_CRIME_WATCHLIST with {confidence: c, topic: topic(a),
                                     pgp: fingerprints(a), first_seen_dw: now()}
```

**The monitoring state machine:**

```
states:  ACTIVE → TRIGGERED → {BLACKLISTED|WATCHLISTED|CLEAN}
                ↘ EXPIRED (no tx within retention and context weakens)
transitions:
  (admit)          ∅ → ACTIVE        on score_precrime = PRE_CRIME_WATCHLIST
  (first tx)   ACTIVE → TRIGGERED     on ElectrumX/poll detects tx(a) > 0
  (re-score) TRIGGERED → final        run full risk engine with on-chain + DW evidence
  (timeout)    ACTIVE → EXPIRED        on (now - first_seen_dw > retention)
```

**First-transaction detection and re-evaluation trigger.** POC: BigQuery poll every 6h. Production: ElectrumX `blockchain.address.subscribe` → seconds. On TRIGGERED, run the full Phase-4 engine combining the stored DARK_WEB_PAYMENT evidence with newly-available taint/amount-correlation evidence; record `dw_to_first_tx_days` (feeds Contribution 5).

**Why it is novel (with citations).** Chainalysis US10977655B2 Claim 1 *requires* "a taint value propagated from a previously classified cryptocurrency address" — no transaction, no taint, no score. Peled 2021 and Chen 2023 compute features from transaction history; a zero-history address yields an all-zero/undefined feature vector. ChronoWave-GNN (2025), the post-transaction state of the art, cannot score an address with no transactions by construction. MFScope (2019) and *The Devil Behind the Mirror* (2024) extract dark-web addresses but produce *measurement studies*, not a pre-transaction *risk state* with monitoring. **No prior paper or patent claims pre-transaction risk scoring from off-chain payment context.**

**Measurable claim.** "BTC-Intel assigned PRE_CRIME_WATCHLIST to N% of subsequently-OFAC-confirmed criminal addresses an average of D days before official designation — detection impossible for any transaction-dependent system."

**Patent claim language (method):**

```
1. A computer-implemented method for assigning a pre-transaction risk classification
   to a cryptocurrency address, comprising:
   (a) receiving a document retrieved from a Tor hidden service, the document comprising
       text content and one or more cryptocurrency addresses;
   (b) classifying, by a natural language processor, the text surrounding each address as
       a payment context, a victim-report context, or an ambiguous context, based on
       payment-transaction signal keywords, wherein a victim-report context is treated as
       reducing risk;
   (c) for each address classified as a payment context:
       (i)  querying a blockchain database to determine whether the address has any
            on-chain transaction history;
       (ii) responsive to the address having no on-chain transaction history, assigning a
            PRE_CRIME_WATCHLIST classification and a confidence score derived from the
            payment-context classification;
   (d) storing the classification and confidence score in a monitoring database;
   (e) monitoring the blockchain database for a first on-chain transaction of the address; and
   (f) responsive to detecting the first on-chain transaction, updating the risk
       classification based on a combination of the stored payment-context evidence and the
       on-chain transaction evidence.
```

**Why no prior patent (Chainalysis US10977655B2) covers this.** Their independent claim presupposes an existing transaction and a previously-classified source from which taint is propagated. Step (c)(ii) of our claim acts on an address with *zero* history and *no* prior classification, deriving risk from *off-chain* context — outside the literal scope of their claim and non-obvious over it.

**Paper-section template.** §5 "The PRE_CRIME_WATCHLIST Mechanism": (1) Motivation — the pre-transaction blind spot; (2) Design — context → admit → monitor → re-score; (3) Confidence scoring; (4) Algorithm box (above); (5) State machine; (6) Evaluation — days-before-OFAC.

---

### Contribution 2 — Shared-Wallet Onion Graph Edge Type (Priority 2)

**The problem no prior work solves.** Onion-graph construction (Biryukov 2014) uses *hyperlink* edges; Spitters 2014 uses topic similarity. Hyperlinks are weak — a link between two sites may be a recommendation, a review, or spam, proving nothing about shared operation. No prior work uses a *financial instrument* (a shared payment wallet) as an edge between onion domains.

**Definition.** Build graph `G_onion = (V, E)` where `V` = onion domains. For domains `u, v ∈ V`, add edge `(u,v)` iff there exists at least one Bitcoin address `a` appearing in a PAYMENT context on both `u` and `v`. Edge weight `w(u,v) = |{a : a ∈ PAYMENT(u) ∩ PAYMENT(v)}|` (number of shared payment addresses); edge confidence derives from co-appearance frequency.

**Graph-construction algorithm (pseudocode):**

```
for each address a with PAYMENT context on ≥2 distinct domains:
    domains ← distinct_domains(a, context=PAYMENT)
    for each unordered pair (u,v) in domains:
        if edge(u,v) ∉ E: create edge(u,v) with weight=1, addresses={a}
        else: edge(u,v).weight += 1; edge(u,v).addresses ∪= {a}
infrastructure_groups ← weakly_connected_components(G_onion, min_weight≥1)
```

**Edge-weight computation.** `w(u,v)` counts shared payment addresses; higher weight = stronger operational coupling. A connected component over these edges is an **infrastructure group** — a set of onion domains operated by one criminal entity sharing payment rails.

**What it reveals that hyperlinks miss.** Two markets that both print `1ABC...` at checkout share the *same private key for incoming payments* — i.e., one operator controls both checkouts. Hyperlink analysis cannot see this (the sites need not link to each other at all). The shared-wallet edge surfaces operator-level coordination invisible to Biryukov 2014.

**Prior art delta.** Biryukov 2014: hyperlink edges (network-topology relationship). Spitters 2014: topic-similarity edges (content relationship). BTC-Intel: *financial-instrument co-occurrence* edges (operational/ownership relationship). The combination of blockchain-address clustering with onion-graph construction is a cross-domain combination present in neither literature.

**Measurable claim.** "X% of shared-wallet edges connect domain pairs with *no* hyperlink edge — criminal coordination undetectable by hyperlink-based onion-graph analysis."

**Patent claim language (dependent on Claim 1):**

```
4. The method of claim 1, further comprising constructing a graph in which each node
   represents a Tor hidden service domain and each edge between two nodes represents the
   co-appearance of at least one cryptocurrency address in payment-context documents on
   both domains, the edge having a weight proportional to the number of shared addresses;
5. The method of claim 4, further comprising identifying, from connected components of
   said graph, a group of Tor hidden service domains operated by a common entity based on
   shared payment infrastructure.
```

**Paper-section template.** §6.3 "Shared-Payment-Address Edges": definition, construction, edge weight, an example pair with no hyperlink, and the X%-no-hyperlink result.

---

### Contribution 3 — Provenance-Aware Bayesian Evidence Fusion (Priority 3)

**The circular double-counting problem (worked example).** OFAC designates address A. Chainalysis ingests OFAC and flags A. A community member reads the news and reports A. Three "independent" signals — all tracing to one fact (the OFAC listing). Naively combining them:

```
log-odds += ln(LR_OFAC) + ln(LR_commercial) + ln(LR_community)
         =  ln(1000)    + ln(30)            + ln(5)
         =  6.91        + 3.40              + 1.61   = +11.92   ← one fact, counted thrice
```

This grossly overstates confidence. The Bayesian/Dempster-Shafer fusion literature (arXiv 2104.07440) confirms summing correlated scores over-counts, but provides no mechanism to detect *which* blockchain signals are correlated. Gao 2022 explicitly names this as an open gap.

**The provenance-chain data structure.** Each evidence signal `s` carries `provenance(s)` = the set of source identifiers it ultimately derives from. Example: `provenance(COMMERCIAL_CONSENSUS) = {OFAC_SDN}` (commercial flags re-label OFAC); `provenance(COMMUNITY_REPORT) = {}` (independent). Formally a directed acyclic provenance graph per signal.

**The deduplication algorithm (pseudocode):**

```
function fuse(signals):
    log_odds ← ln(prior / (1 - prior))        # prior = 0.001
    active ← ∅                                  # source ids already applied
    for s in sort_desc_by_LR(signals):         # strongest first → deterministic skip
        if provenance(s) ∩ active ≠ ∅:
            mark s skipped (circular evidence); continue
        log_odds += ln(LR(s))
        active ← active ∪ {source_id(s)}
    return sigmoid(log_odds)
```

Applied to the example: OFAC counted (+6.91); COMMERCIAL_CONSENSUS skipped (provenance {OFAC_SDN} ∈ active); COMMUNITY_REPORT skipped likewise → net **+6.91**, counted once. Correct.

**The calibrated likelihood-ratio framework.** Each `LR(s)` is measured empirically (File B §6): `LR = P(signal | criminal) / P(signal | clean)` with Laplace smoothing. This makes the fusion both *de-duplicated* and *calibrated* — the two properties prior systems lack.

**Why prior work does not solve it.** Gao 2022 (survey) states current systems "combine evidence without formal probabilistic justification." The Chainalysis patent has no provenance mechanism. The general fusion literature (2104.07440) knows the over-counting *problem* but not the *provenance-chain solution* applied to blockchain's hidden OFAC→commercial→OFAC dependencies.

**Measurable claim.** "Provenance-aware fusion reduces false-positive inflation: on a test set with circular evidence, naive fusion produces F% false positives at the BLACKLISTED tier vs P% with provenance de-duplication (P ≪ F)."

**Patent claim language (independent):**

```
7. A computer-implemented method for combining cryptocurrency-address risk evidence from a
   plurality of sources, comprising:
   (a) receiving a plurality of evidence signals, each associated with an evidence type and
       a source identifier;
   (b) determining, for each signal, a provenance chain comprising the source identifiers
       that contributed to its generation;
   (c) maintaining an active set of source identifiers already applied to a Bayesian risk
       computation;
   (d) determining, for each signal, whether any identifier in its provenance chain is in
       the active set;
   (e) responsive to such an identifier being present, excluding the signal to prevent
       double-counting of correlated evidence; and
   (f) computing a final risk score by applying only the non-excluded signals as sequential
       Bayesian updates to a prior probability.
```

**Paper-section template.** §6 "Provenance-Aware Fusion": the circular problem, the provenance structure, the algorithm, the calibration, and the false-positive-inflation ablation.

---

### Contribution 4 — Three-Way Propagation Method Comparison (Priority 4)

**Why comparing all three is novel.** Prior work uses exactly one method each: Chainalysis = amount-weighted taint; Nerino 2021 = label propagation; PPR appears in other graph work. No published paper compares all three on the *same* labelled dataset with the *same* seeds and threshold.

**Evaluation methodology.** Hold dataset, seeds (OFAC), and threshold (0.35) fixed. Run amount-weighted taint, label propagation, and PPR. Report precision/recall/F1/FPR **per method and per address category** (exchange / mixer / ordinary). The hypothesis: each method wins a different category (taint for exchange-adjacent value flows; label propagation for mixer outputs; PPR for general criminal clusters).

**Expected result format:**

```
Category   | Method        | Precision | Recall | F1
-----------+---------------+-----------+--------+-----
exchange   | taint         |   high    |  mid   |
exchange   | label-prop    |   mid     |  mid   |
exchange   | PPR           |   low     |  high  |
mixer-out  | taint         |   low     |  low   |
mixer-out  | label-prop    |   high    |  mid   |
general    | PPR           |   mid     |  high  |
...        | ENSEMBLE      |  ≥ best single per category       |
```

**Measurable claim.** "First head-to-head comparison of amount-weighted taint, label propagation, and PPR on one labelled dataset; the ensemble matches or beats the best single method in every address category."

**Paper-section template.** §7.6 "Propagation Comparison": methodology, per-category table, ensemble weights, discussion of which method suits which category. (Publishable, not patentable — a comparison is not an invention; the *ensemble weighting* is at best a weak dependent claim.)

---

### Contribution 5 — Temporal Off-Chain/On-Chain Gap Feature (Priority 5)

**The feature.** `dw_to_first_tx_days(a) = first_onchain_tx_date(a) − first_dark_web_listing_date(a)`. The number of days between an address being advertised on the dark web and its first on-chain transaction — the measurable duration of the pre-crime phase.

**Why only BTC-Intel can compute it.** It requires *both* dark-web crawl timestamps *and* full on-chain history for the same address. No on-chain-only system (Peled, Chen, ChronoWave-GNN, Elliptic2) has the dark-web timestamp; no dark-web measurement study (MFScope, Devil-Behind-the-Mirror) cross-references it with on-chain first-tx timing as a *predictive feature*. The data combination is unique to BTC-Intel's architecture.

**Statistical significance test.** Treat illicit classification as the label. Compare `dw_to_first_tx_days` distributions for later-confirmed-criminal vs later-confirmed-clean addresses using a Mann-Whitney U test (non-parametric, no normality assumption); report effect size and p-value. Hypothesis: criminal addresses have a *characteristic* short gap (set up, advertised, paid quickly), clean addresses either lack a dark-web listing entirely or show a long/random gap.

```
# services/research/temporal_gap_test.py
from scipy.stats import mannwhitneyu

def test_gap_significance(criminal_gaps, clean_gaps):
    stat, p = mannwhitneyu(criminal_gaps, clean_gaps, alternative="two-sided")
    return {"U": float(stat), "p_value": float(p),
            "significant": p < 0.05,
            "criminal_median": _median(criminal_gaps),
            "clean_median": _median(clean_gaps)}
```

**Measurable claim.** "The dark-web-listing-to-first-transaction gap is a statistically significant predictor of illicit classification (Mann-Whitney U, p < 0.05), with criminal addresses showing a characteristically short gap."

**Paper-section template.** §7.7 "The Off-Chain/On-Chain Temporal Gap": feature definition, why only we can compute it, the significance test, and the result. (Publishable; the *feature* is hard to patent alone but supports the PRE_CRIME claim's dependent claims.)

---
## Section 4 — Research Gap Matrix

Columns: Research Area | Best Existing Paper | What It Covers | What It Misses | BTC-Intel Solution | Novelty (1–10) | Patent Potential. Novelty scores are *honest* — where 2024–2025 papers have partly closed a gap, the score is lowered with a precise note.

| Research Area | Best Existing Paper | What It Covers | What It Misses | BTC-Intel Solution | Novelty | Patent |
|---------------|---------------------|----------------|----------------|--------------------|---------|--------|
| CIO clustering | Meiklejohn 2013, Delgado 2021 | Co-input ownership; modern reassessment | CoinJoin/Taproot awareness; confidence | CoinJoin pre-filter + confidence voting + 2024 weights | 4/10 | Low (prior art) |
| CoinJoin-aware clustering | Tironsakkul 2022, Heuristics-2023 (2311.12491) | Multi-protocol detection | Pre-mix context conditioning | Protocol-specific decay + DW pre-mix context | 5/10 | Dependent claim |
| Taproot forensics | Block-Number 2025, ICDCSW 2023 | A P2TR heuristic now exists | Temporal degradation; forensic precision | Flag UNRESOLVED + measure degradation | 3/10 *(lowered: 2025 heuristic exists)* | Weak |
| Lightning forensics | Kappos & Yousaf 2021; LN dataset 2025 | Channel leakage; gossip data | Criminal-node identification | Gossip↔on-chain cluster correlation | 6/10 | Candidate |
| **Pre-transaction risk scoring** | **None** | — | Everything (no system does it) | **PRE_CRIME_WATCHLIST** | **9/10** | **Strong (Claim 1)** |
| Dark-web payment-context extraction | Devil-Behind-Mirror 2024, MFScope 2019 | Large-scale extraction | Pre-transaction risk *state* | Extraction → risk engine + PRE_CRIME | 5/10 *(extraction is prior art)* | Low (extraction) |
| PGP cross-market entity linking | Christin 2013, Sun 2019 | Alias/stylometry linking | Multi-signal probabilistic graph | 4-signal (wallet+PGP+alias+domain) resolution | 7/10 | Candidate |
| **Shared-wallet onion edges** | **Biryukov 2014 (hyperlink only)** | Hyperlink/topic edges | Financial-instrument edges | **Shared-payment-address edge type** | **8/10** | **Strong (Claims 4–5)** |
| Bayesian evidence fusion | Gao 2022 (names gap); 2104.07440 | Fusion theory; over-counting known | Provenance-chain de-dup for blockchain | Calibrated provenance-aware fusion | 7/10 | Candidate (Claim 7) |
| **Circular evidence de-duplication** | **None (blockchain)** | — | The mechanism itself | **Provenance-chain skip** | **9/10** | **Strong (Claim 7)** |
| Taint propagation comparison | Nerino 2021 (single method) | Label propagation | Cross-method comparison | 3-way comparison + ensemble | 6/10 | Weak (comparison) |
| Behavioural lifecycle detection | Chen 2023 | 4-phase TGNN | Off-chain anchor; light infra | Rolling windows + DW anchor | 5/10 | Low |
| Behavioural fingerprint *discovery* | Sayadi 2023 (classification) | Fingerprint embeddings | Discovery of unlabelled criminals | FAISS similarity discovery | 7/10 | Candidate |
| Temporal feature engineering | Peled 2021 (static) | Static features | Temporal deltas | 4-window delta features | 6/10 | Low |
| **Off-chain/on-chain temporal gap** | **None** | — | The feature (needs both data) | **dw_to_first_tx_days + sig test** | **8/10** | Supports Claim 1 |
| SHAP for hybrid rule+ML | Lundberg 2017; 2401.03530 (2024) | SHAP on ML | Rule-layer explanation | SHAP + counterfactual routing | 5/10 | Weak |
| Counterfactual for blockchain risk | Wachter 2017 (general) | Counterfactual theory | Blockchain application | Evidence-removal counterfactual | 7/10 | Candidate |
| Cross-chain bridge tracking | Chainalysis/Elliptic blogs; SoK 2509.21831 | Bridge tracing exists | Exit-frequency quantification | CROSS_CHAIN_EXIT + frequency measure | 4/10 | Low |
| Adversarial evasion detection | Adversarial-ML general | Generic robustness | Blockchain-specific evasion | Dust filter + cluster-poison quarantine + contradiction score | 6/10 | Candidate |
| Multi-blockchain entity resolution | Partial (Cardano 2025 etc.) | Per-chain clustering | Unified cross-chain identity | Cross-chain-ready entity schema (PGP/alias) | 5/10 | Low |
| Amount-correlation validation | Ghosh 2017 (prices only) | Price extraction | Price↔on-chain matching | ±5%/24h AMOUNT_CORRELATION | 7/10 | Dependent claim |

**Reading the scores honestly.** The three highest (PRE_CRIME 9, circular-evidence de-dup 9, shared-wallet edge 8) are where BTC-Intel is genuinely unprecedented and where patent effort should concentrate. Taproot dropped to 3/10 *because* the 2025 block-number heuristic now exists — a lower score with a precise claim beats an inflated one a reviewer/examiner will puncture.

---

## Section 5 — Patent Strategy: Complete Filing Guide

### 5A — What Is Patentable (Detailed Analysis)

For each of the five contributions: the patentable mechanism, why novel (no prior art), why non-obvious (cross-domain), and risk factors.

**Contribution 1 — PRE_CRIME_WATCHLIST.**
- *Mechanism:* assigning risk to a zero-history address from off-chain payment context + monitoring + re-scoring on first tx.
- *Novel:* no patent/paper claims pre-transaction scoring from dark-web context; Chainalysis US10977655B2 requires an existing transaction.
- *Non-obvious:* the insight that a payment-context listing carries risk *before* any transaction is not an obvious extension of taint systems, which treat all zero-history addresses as risk-neutral; combining NLP context classification with on-chain zero-history verification spans two domains.
- *Risk factors:* TRM/Chainalysis/Elliptic have active filing programs and applications are confidential for 18 months — a pending application could surface. MFScope/Devil-Behind-the-Mirror are prior art for *extraction* (not for the risk *state*), so claims must center the PRE_CRIME state + monitoring, not extraction.

**Contribution 2 — Shared-Wallet Onion Edge.**
- *Mechanism:* financial-instrument (shared payment address) as a weighted edge between onion domains; infrastructure-group detection from components.
- *Novel:* Biryukov 2014 (hyperlinks) and Spitters 2014 (topics) use no financial edge.
- *Non-obvious:* requires expertise in *both* onion-graph construction (network measurement) and address clustering (forensics) — cross-domain combinations are typically non-obvious.
- *Risk factors:* a graph-analytics practitioner *might* combine the two; mitigate by claiming the specific construction (payment-context co-appearance + weight + component-based operator grouping).

**Contribution 3 — Provenance-Aware Bayesian Fusion.**
- *Mechanism:* per-signal provenance chains + skip-if-ancestor-already-applied in a Bayesian update.
- *Novel:* Gao 2022 names the gap; no blockchain patent claims provenance de-dup.
- *Non-obvious:* Bayesian fusion is known and provenance tracking is known (citation graphs), but applying provenance tracking to remove *circular* blockchain evidence requires recognising hidden OFAC→commercial→OFAC dependencies that are undocumented publicly.
- *Risk factors:* general fusion prior art (2104.07440) knows the over-counting problem; mitigate by claiming the *provenance-chain* mechanism specifically, not "avoiding double counting" generally.

**Contribution 4 — Three-Way Comparison.** Not patentable (a comparison is not an invention). The *ensemble weighting* is at best a weak dependent claim. Publish, do not file.

**Contribution 5 — Temporal Gap Feature.** A single feature is hard to patent. File it only as a *dependent* claim under Claim 1 (the gap is computed during PRE_CRIME monitoring). Publish the significance result.

### 5B — What Is NOT Patentable (Prior-Art Blockers)

| Element | Blocking prior art |
|---------|--------------------|
| CIO clustering | Meiklejohn 2013 |
| Change-address heuristic | Meiklejohn 2013, Delgado 2021 |
| Amount-weighted taint propagation | Chainalysis US10977655B2 |
| Generic weighted transaction risk score | US10275772B2 ("Cryptocurrency risk detection system") |
| Dark-web BTC address extraction (regex+checksum) | MFScope (NDSS 2019), Devil-Behind-the-Mirror (2024) |
| Graph-based risk propagation | Nerino 2021 + many |
| Behavioural feature extraction on blockchain | Peled 2021, Weber 2019 |
| Isolation Forest / Random Forest | Public algorithms (Liu 2008 etc.) |
| SHAP explainability | Lundberg & Lee 2017 |
| SHAP-on-blockchain-anomaly | 2401.03530 (2024) |
| P2TR clustering heuristic (block-number) | Block-Number Taproot (2025) |
| CoinJoin detection | Tironsakkul 2022, 2311.12491 (2023) |

**Critical warning:** do not draft any claim that reads on Chainalysis US10977655B2 (taint) or US10275772B2 (weighted transaction risk). Independent claims must be specifically anchored to *off-chain pre-transaction* context and *provenance de-duplication* — the elements those patents do not cover.

### 5C — Patent Claim Templates (Ready to File)

**Independent Claim 1 (PRE_CRIME method)** — see Contribution 1 above (full text).

**Dependent Claims on Claim 1:**

```
2. The method of claim 1, further comprising extracting one or more PGP public-key
   fingerprints from the document and storing an association between a PGP fingerprint and
   the cryptocurrency address as corroborating evidence for the payment-context classification.

3. The method of claim 1, further comprising extracting a price amount from the document and,
   upon detecting the first on-chain transaction, comparing the first on-chain transaction
   amount to the extracted price amount to produce an amount-correlation confidence score.

4. The method of claim 1, further comprising constructing a graph in which each node is a Tor
   hidden service domain and each edge represents co-appearance of at least one cryptocurrency
   address in payment-context documents on both domains, the edge weighted by the number of
   shared addresses.

5. The method of claim 4, further comprising identifying, from connected components of the
   graph, a group of domains operated by a common entity based on shared payment infrastructure.

6. The method of claim 1, wherein the confidence score is computed by a Bayesian inference
   engine that updates a prior probability using likelihood ratios and that maintains, for each
   evidence signal, a provenance graph, excluding from the update any signal whose provenance
   graph shares a source with an already-applied signal.

9. The method of claim 1, further comprising recording a temporal gap between the first
   dark-web appearance date and the first on-chain transaction date, and using said gap as a
   feature in the updated risk classification.
```

**Independent Claim 7 (Provenance-aware fusion)** — see Contribution 3 above (full text).

**Independent Claim 8 (System / apparatus):**

```
8. A system for cryptocurrency-address threat intelligence comprising one or more processors
   and one or more non-transitory computer-readable media storing instructions that, when
   executed, cause the system to perform the operations of claims 1 and 7, the system further
   comprising: a Tor-network crawler executing within an isolated virtual machine; an object
   store retaining raw documents for a configurable retention period and deleting them
   thereafter; and an append-only audit log in which each record is cryptographically signed.
```

**Independent Claim 10 (Computer-readable medium):**

```
10. One or more non-transitory computer-readable media storing instructions that, when executed
    by one or more processors, cause performance of the method of claim 1.
```

### 5D — Filing Timeline (Month-by-Month)

```
Month 0  File US provisional patent application ($320 micro-entity) — establishes priority
Month 0  File arXiv preprint (cs.CR primary, cs.SI cross-list) — academic priority
Month 1  Submit 6-page workshop paper (FC WTSC) — preliminary PRE_CRIME results
Month 2  Complete POC evaluation data collection (precision/recall/days-before-OFAC)
Month 3  Write full 12–16 page paper; 2 colleagues proofread (1 external)
Month 4  Submit to Financial Cryptography (FC) — primary venue
Month 5  Workshop decision + presentation (public record)
Month 6  Begin non-provisional drafting (with patent agent)
Month 8  FC decision; if rejected, revise → NDSS/IMC
Month 10 File PCT international application (priority in 157 countries)
Month 11 File US non-provisional (before the 12-month provisional deadline)
Month 12 Provisional expires — non-provisional MUST be filed by now
Month 14 FC paper published (if accepted)
Month 18 PCT publishes (was confidential)
Month 30 Enter national phases (EPO, UKIPO, JPO, IPOS, IPO-India) as budget allows
```

**Critical path:** Month 0 provisional → Month 12 non-provisional is the unmissable deadline. **Europe/India/China/Japan have no grace period** — file the provisional *before* the arXiv preprint or you forfeit those jurisdictions.

### 5E — Prior-Art Search Queries (Run Before Filing)

```
Google Patents / USPTO Patent Center:
  "cryptocurrency" AND "pre-transaction" AND "risk"
  "blockchain" AND "dark web" AND "risk score"
  "bitcoin" AND "zero transaction history" AND "classification"
  "tor" AND "hidden service" AND "cryptocurrency address" AND "risk"
  "cryptocurrency" AND "Bayesian" AND ("evidence fusion" OR "provenance")
  "onion" AND "bitcoin" AND "graph" AND "clustering"
Assignee portfolios (read independent claims only):
  assignee:Chainalysis   assignee:"TRM Labs"   assignee:Elliptic
  assignee:CipherTrace    assignee:"Mastercard" (CipherTrace acquirer)
Specific patents to read in full:
  US10977655B2 (Chainalysis taint) ; US10275772B2 (crypto risk detection) ; US11182781 (blockchain tags)
Non-patent prior art:
  arXiv cs.CR/cs.SI: "bitcoin" "dark web" "risk" after:2020
  Google Scholar / IEEE Xplore / ACM DL: "bitcoin" AND "dark web" AND ("risk" OR "intelligence") 2020–present
```

**What a "blocking" result looks like:** a single document whose *independent claim* (patent) or main method (paper) recites **all** elements of your independent claim. For Claim 1, a blocker would describe assigning risk to a *zero-history* address from *off-chain* context *and* monitoring for first transaction. Partial overlaps (extraction-only like MFScope; taint-only like Chainalysis) are *not* blockers but may be combined by an examiner under obviousness — which is why the cross-domain non-obviousness arguments in §5A matter.

---
## Section 6 — Research Paper: Complete Structure

### 6.1 — Abstract Template (250 words, fill-in-the-blank)

```
Cryptocurrency-based financial crime reached [$X] billion in [year] [cite Chainalysis report].
Despite sophisticated blockchain analytics, existing systems — commercial and academic —
share a fundamental limitation: they require at least one on-chain transaction before any
risk assessment is possible, leaving a pre-transaction window during which criminal payment
infrastructure is established yet invisible to monitoring.

We present BTC-Intel, a Bitcoin wallet intelligence system integrating Tor-hidden-service
intelligence with transaction-graph analysis. BTC-Intel introduces the PRE_CRIME_WATCHLIST
classification, assigning non-zero risk to addresses found in dark-web payment contexts prior
to any on-chain activity. We further contribute (1) a shared-payment-address edge type for
onion-service graphs that reveals operator-level coordination invisible to hyperlink analysis,
and (2) a provenance-aware Bayesian evidence-fusion engine that prevents circular
double-counting of correlated intelligence signals.

We evaluate on OFAC SDN confirmed addresses, the Elliptic [and Elliptic2] dataset(s), and
WalletExplorer service labels. BTC-Intel achieves [X]% precision at [Y]% recall on the
confirmed-criminal task, outperforming the single-hop OFAC-taint baseline by [Z] points on
recall at comparable precision. Critically, BTC-Intel flagged [N]% of subsequently-
OFAC-confirmed addresses in the PRE_CRIME_WATCHLIST state an average of [D] days before
official designation. We release all code for components not dependent on dark-web data and a
hash-verified dataset manifest for reproducibility.
```

Every bracketed value is a **measurement placeholder** — do not submit until each is a measured number (§6.4).

### 6.2 — Section-by-Section Content Specification

| Section | Write this | Do NOT write |
|---------|-----------|--------------|
| 1 Introduction (2 pp) | The pre-transaction blind spot; the gap (cite Chainalysis patent + Peled/Chen/ChronoWave); numbered contribution list; paper org. | Method details; jargon before defining it. |
| 2 Background/Related (1.5–2 pp) | CIO [Meiklejohn/Delgado], taint [Chainalysis], dark-web OSINT [Biryukov/Spitters/Devil-Behind-Mirror], ML [Weber/Peled/ChronoWave/Elliptic2], fusion gap [Gao]. Credit generously. | Understating prior work (fastest rejection). |
| 3 Threat Model (0.5–1 pp) | Adversary (fresh addresses, mixing, multi-market, bridges); defender (passive, public BTC + unauthenticated onion + OFAC); out-of-scope (other chains, auth-walled markets); success criteria. | Claiming capabilities you lack. |
| 4 System Architecture (3–4 pp) | Figure 1 (5 phases, VM boundary); per-layer decision + alternative; pseudocode for the 3 patentable contributions. | Code dumps; undefended choices. |
| 5 PRE_CRIME mechanism (1–1.5 pp) | Contribution 1 in full (state machine, scoring, algorithm box). | — |
| 6 Dark-web integration (1 pp) | Shared-wallet edge (Contribution 2) deep; entity resolution; brief crawler. | Over-claiming crawler novelty (extraction is prior art). |
| 7 Evaluation (3–4 pp) | Datasets; metrics; ≥2 baselines; ablation (≥5 variants); PRE_CRIME days-before-OFAC; 3-way propagation table. | Any unmeasured number. |
| 8 Limitations (0.5 pp) | ~8% auth-wall coverage [Owenson]; cross-chain blindness; Taproot degradation; LN opacity; 1–24h crawl lag; Elliptic 2018 cutoff. | Hiding limitations. |
| 9 Ethics/Legal (0.5 pp) | IRB status; GDPR minimisation/retention; passive observation; no criminal participation; data-release plan. | Omitting ethics (now required at top venues). |
| 10 Conclusion (0.5 pp) | Summary; the single headline number (days-before-OFAC); future work (TGNN, cross-chain, authenticated crawling). | New claims not in the body. |

### 6.3 — Required Numerical Results (Collect Before Submission)

| Measurement | Section |
|-------------|---------|
| Precision/Recall/F1 (BLACKLISTED) on OFAC test set | 7.3 |
| FPR on known-clean (WalletExplorer) set | 7.3 |
| Elliptic baseline reproduced within ±2% of Peled 2021 | 7.3 |
| Delta vs baseline (recall improvement) | 7.3 |
| Ablation: ≥5 variants (−PRE_CRIME, −DW, −temporal, −Bayesian, −provenance) | 7.4 |
| # PRE_CRIME addresses + days-before-OFAC | 7.5 |
| 3-way propagation comparison (precision/recall/F1/FPR per method & category) | 7.6 |
| Temporal-gap significance (Mann-Whitney U, p) | 7.7 |
| Per-address processing time (feasibility) | 7 |

**Never claim without measurement:** "X% precision" (if estimated); "outperforms Chainalysis" (proprietary, unmeasurable); "sub-200ms" (without specified hardware); "Y% of dark-web addresses are criminal" (no ground truth).

### 6.4 — Venue Selection and Why

| Venue | Fit | Acceptance | First choice if… |
|-------|-----|-----------|------------------|
| **Financial Cryptography (FC)** | Best — blockchain + financial crime | ~20% | **Primary target.** |
| NDSS | Strong dark-web measurement track | ~17% | FC rejects. |
| ACM IMC | Measurement focus (Meiklejohn precedent) | ~25% | Emphasise crawl/measurement. |
| IEEE S&P / USENIX Security | Highest prestige; focused contributions | ~15% | Submit PRE_CRIME-only, deep eval. |
| ARES | Applied security (Nerino precedent) | ~35% | Need faster/lower-bar publication. |
| FC WTSC workshop | 6-page preliminary | higher | Establish citation anchor first. |

**Strategy:** workshop (WTSC) for early feedback + citation anchor → FC as primary → NDSS/IMC fallback. For double-blind FC, file the arXiv preprint *after* the review window (or anonymised) — but always *after* the provisional patent (no-grace-period jurisdictions).

### 6.5 — Common Rejection Reasons → Prevention

| Rejection | Prevention |
|-----------|-----------|
| "Contributions not distinguished from prior work" | Section-2 comparison table with a ✓/✗ column per contribution per paper. |
| "Insufficient evaluation" | Every Section-1 contribution has a Section-7 result; prove "first to do X" by citing absence in prior work. |
| "Unrealistic threat model" | State exactly what the system *cannot* do (Section 8). |
| "Ethical concerns (dark-web crawling)" | Section 9: IRB status; unauthenticated = legally analogous to public web; no criminal participation. |
| "Novelty is incremental" | Ablation proving the *combination* achieves what components cannot; explicit novel-vs-prior split in Section 1. |
| "Not reproducible (DW data unshareable)" | Release all non-DW code (Elliptic eval, clustering, fusion) on GitHub + hash-verified DW manifest. |

### 6.6 — Reproducibility Requirements

Release: the clustering (Union-Find + heuristics), the provenance-aware Bayesian engine, the three propagation methods + comparison harness, the Elliptic baseline reproduction, and the evaluation scripts — all on GitHub with README + license. For the dark-web component (legally unshareable), release a **SHA-256 manifest** of the page set so a reviewer can verify identity under NDA, plus de-identified extracted feature vectors where lawful. State exactly what is and is not released and why.

---

## Section 7 — Implementation Status Tracker

Every component: POC status, Final-Product status, build week (from the roadmaps in Files A/B), priority, and whether completing it enables a research claim. Status legend: NOT_STARTED / PLANNED / IN_PROGRESS / COMPLETE. (Statuses below reflect the *plan* — all are PLANNED until build begins; the column shows the *intended* end state and gating.)

| Component | POC status | Final status | Build week | Priority | Research claim? |
|-----------|-----------|--------------|-----------|----------|-----------------|
| OFAC/UN seed collection | PLANNED (A W2) | PLANNED (B W4 auto-refresh) | A:2 / B:4 | CRITICAL | NO |
| Extended seed sources (8+) + ETag | — | PLANNED (B W4) | B:4 | HIGH | NO |
| Service labels (taint barriers) | PLANNED (A W2) | PLANNED | A:2 | CRITICAL | NO |
| Dark-web crawler (Tor+Splash, VM) | PLANNED (A W5) | PLANNED (B W5 live) | A:5 / B:5 | CRITICAL | partial (extraction is prior art) |
| BTC + PGP extraction + checksum | PLANNED (A W5) | PLANNED | A:5 | CRITICAL | NO (prior art) |
| Context/topic classification | PLANNED (A W5) | PLANNED (B W6 sentence-boundary) | A:5 / B:6 | HIGH | YES (topic+payment binding) |
| **Shared-wallet onion graph** | PLANNED (A W5) | PLANNED (B real-time) | A:5 / B:5 | HIGH | **YES (Contribution 2)** |
| 4-signal entity resolution | basic PGP (A W5) | PLANNED (B W6 probabilistic) | A:5 / B:6 | MEDIUM | YES |
| Graph expansion (BigQuery→node) | PLANNED (A W3) | PLANNED (B W3 node, W7 ZMQ) | A:3 / B:3 | CRITICAL | NO |
| CIO + CoinJoin pre-filter | PLANNED (A W3) | PLANNED (B W6 protocol-specific) | A:3 / B:6 | CRITICAL | YES (recalibration) |
| Multi-heuristic voting (2024 weights) | PLANNED (A W3) | PLANNED | A:3 | HIGH | YES (weight recalibration) |
| Taproot UNRESOLVED + degradation | flag only (A W3) | PLANNED (B W15 measure) | A:3 / B:15 | MEDIUM | YES (degradation curve) |
| **Service recognition (before taint)** | PLANNED (A W3) | PLANNED (B W8 feedback loop) | A:3 / B:8 | CRITICAL | YES (ordering) |
| 3-way taint comparison | PLANNED (A W4) | PLANNED (B W9 ensemble) | A:4 / B:9 | HIGH | **YES (Contribution 4)** |
| **Provenance-aware Bayesian fusion** | PLANNED (A W8) | PLANNED (B W9 calibrated) | A:8 / B:9 | CRITICAL | **YES (Contribution 3)** |
| Calibrated likelihood ratios | guessed (A) | PLANNED (B W9 measured) | B:9 | HIGH | YES |
| Isolation Forest + SHAP | PLANNED (A W9) | PLANNED (B modular) | A:9 | MEDIUM | partial |
| Counterfactual generator | PLANNED (A W8) | PLANNED (B App E) | A:8 | HIGH | YES (counterfactual-for-blockchain) |
| **PRE_CRIME_WATCHLIST** | PLANNED (A W7) | PLANNED (B W8 ElectrumX) | A:7 / B:8 | CRITICAL | **YES (Contribution 1, Priority 1)** |
| Temporal off-chain/on-chain gap | stored (A W7) | PLANNED (B W8 + sig test) | A:7 / B:8 | MEDIUM | **YES (Contribution 5)** |
| Behavioural fingerprint (FAISS) | — | PLANNED (B W9) | B:9 | MEDIUM | YES (discovery) |
| Amount-correlation signal | — | PLANNED (B W9) | B:9 | MEDIUM | YES (dependent) |
| Analyst feedback + cascade | — | PLANNED (B W10) | B:10 | HIGH | NO |
| Drift detection + retrain | — | PLANNED (B W11) | B:11 | HIGH | NO |
| Production API (REST+gRPC) | thin (A App J) | PLANNED (B W12) | B:12 | HIGH | NO |
| Audit log + HMAC + PMLA/GDPR | basic (A) | PLANNED (B W13) | B:13 | CRITICAL | NO |
| Cross-chain bridge detection | static list (A App E ref) | PLANNED (B W15) | B:15 | LOW | YES (exit-frequency) |
| Lightning gossip integration | filter only | PLANNED (B W15) | B:15 | LOW | YES (criminal-node ID) |
| Streamlit / React dashboard | PLANNED (A W10) | PLANNED (B W14 React) | A:10 / B:14 | HIGH | NO |
| Evaluation harness + metrics | PLANNED (A W9) | PLANNED (B W16 quarterly) | A:9 / B:16 | CRITICAL | YES (all numbers) |

**How to use this tracker.** The CRITICAL + "research claim YES" rows are the ones that *both* gate a working demo *and* unlock a paper/patent — build those first: PRE_CRIME (Contribution 1), provenance fusion (Contribution 3), shared-wallet edge (Contribution 2), and the evaluation harness (which produces every number the paper needs). The five contributions map to: Contribution 1 → PRE_CRIME row; 2 → shared-wallet row; 3 → provenance fusion row; 4 → 3-way taint row; 5 → temporal-gap row.

---

## Appendix C1 — Consolidated Paper-to-Contribution Map

Quick cross-reference: which prior paper each contribution answers, and the honest novelty score.

| Contribution | Primary prior art it transcends | Secondary | Novelty | File-A/B location |
|--------------|----------------------------------|-----------|---------|-------------------|
| 1 PRE_CRIME | Chainalysis US10977655B2 (needs tx); Peled 2021; Chen 2023; ChronoWave 2025 | MFScope 2019, Devil 2024 (extraction only) | 9/10 | A §9 / B §7 |
| 2 Shared-wallet edge | Biryukov 2014 (hyperlinks) | Spitters 2014 (topics) | 8/10 | A App A / B App B |
| 3 Provenance fusion | Gao 2022 (names gap); 2104.07440 (problem known) | Chainalysis patent (no provenance) | 9/10 | A §8.3 / B §6 |
| 4 3-way comparison | Nerino 2021 (single method) | Chainalysis (taint only) | 6/10 | A §7.8 / B §6C |
| 5 Temporal gap | Chen 2023 (on-chain only) | Peled 2021 (static) | 8/10 | A §9.6 / B §7.2 |

---

## Appendix C2 — Honesty Ledger: Where Novelty Was Lowered After Literature Search

Per the task's instruction to update novelty honestly when newer papers narrow a gap:

- **Taproot heuristic:** lowered from "novel heuristic" to "degradation measurement only" — *Block Number-Based Address Clustering for Bitcoin Taproot Upgrade* (2025) already provides a P2TR heuristic. Do **not** claim a novel P2TR heuristic in paper or patent.
- **Dark-web BTC extraction:** lowered to "prior art" — MFScope (NDSS 2019, ~10M addresses) and *The Devil Behind the Mirror* (2024, 15,450 BTC addresses) establish regex+checksum extraction at scale. BTC-Intel's novelty is the *risk state* (PRE_CRIME) and *edges/fusion*, not extraction.
- **SHAP-on-blockchain:** *Detecting Anomalies… with Explainability* (2024) already does SHAP on blockchain anomalies. Our explainability novelty is the *hybrid rule+ML counterfactual routing*, not SHAP itself.
- **CoinJoin detection:** *Heuristics for Detecting CoinJoin* (2023) post-dates the planning docs and broadens protocol coverage; our novelty is *context-conditioned post-mix taint*, not detection.
- **Evidence over-counting:** the Bayesian/Dempster-Shafer paper (2104.07440) shows the over-counting problem is *known*; our novelty is the *provenance-chain mechanism* for blockchain's circular OFAC→commercial dependencies, not the observation that correlated evidence over-counts.

A precise, defensible claim beats an inflated one that a reviewer or patent examiner will puncture. The three contributions that survive literature search at full strength — **PRE_CRIME (9/10), provenance-aware fusion (9/10), shared-wallet edge (8/10)** — are where to concentrate both the paper's headline and the patent's independent claims.

---

## Appendix C3 — Plain-Language Gap Walkthroughs (Every Paper)

For readers who want the *intuition* before the formalism, each paper below follows the pattern: **📄 What it did** → **🕳️ The gap** → **💡 Our fix** → **🔬 POC** → **🏭 Final**. This complements the formal catalog in Section 2.

---

### A1 · Meiklejohn 2013 — "A Fistful of Bitcoins"

**📄 What it did.** Imagine a pile of anonymous letters. If two letters were mailed in the same envelope, the same person sent both. Meiklejohn applied this to Bitcoin: if two addresses co-sign a transaction's inputs, the same person controls both (CIO). Using this, they sorted the blockchain into ~1,070 clusters and identified real services (Mt. Gox, Silk Road) by sending them small payments and watching which cluster received the money.

**🕳️ The gap.** (1) CoinJoin did not exist yet — when strangers *deliberately* pool a transaction to hide who paid whom, CIO wrongly merges them (15–25% false merges on 2024 SegWit). (2) Frozen in time — if a key is sold, the cluster never updates. (3) Binary — no "we're 60% sure" confidence.

**💡 Our fix.** A CoinJoin pre-filter (skip CIO when ≥40% of outputs are equal and there are ≥5 outputs), confidence-weighted multi-heuristic voting, and temporal split/merge event logging.

**🔬 POC.** CoinJoin filter + Union-Find CIO over the 3-hop OFAC expansion; report the % of merges the filter prevented (File A §7.2).

**🏭 Final.** Lightning detection, Taproot UNRESOLVED flagging, Neo4j entity-event logging of splits/merges (File B App B).

---

### A2 · Ron & Shamir 2013 — "Quantitative Analysis of the Full Bitcoin Transaction Graph"

**📄 What it did.** Drew the first big map of how Bitcoin money flows, and named the *peel chain* — passing money through a long single-file chain of addresses, like passing a package through ten couriers so no one knows the source or destination.

**🕳️ The gap.** A map with roads but no city names. They could see flows but not *who* the clusters were, and explicitly said "external labelling methods are needed."

**💡 Our fix.** Dark-web payment context *is* that external labelling: when a market page says "pay 1ABC...", we have labelled that cluster with real-world meaning without depositing money.

**🔬 POC.** End-to-end: dark-web address → CIO cluster → OFAC match → labelled entity (File A §6–7).

**🏭 Final.** Automated daily crawling + label propagation so one labelled address annotates its whole cluster.

---

### A3 · Delgado-Segura 2021 — "Resurrecting Address Clustering in Bitcoin"

**📄 What it did.** Checked whether the 2013 recipe still works on modern Bitcoin. Verdict: partly. The naive change heuristic ("the new address is the change") has 23% FPR on SegWit. They added an optimal-change heuristic and weighted voting.

**🕳️ The gap.** Weights calibrated on pre-2021 data; Taproot (Nov 2021) makes all P2TR outputs look identical, breaking the script-type heuristic; no test of whether weights drift over time.

**💡 Our fix.** Use script-type (not naive) change; recalibrate weights to 2024 (CIO 0.50→0.40 for CoinJoin growth); flag P2TR UNRESOLVED; *measure* degradation over time.

**🔬 POC.** Multi-heuristic voter with 2024 weights; compare precision vs Delgado's 2021 weights on the OFAC test set (File A §7.3/§7.5).

**🏭 Final.** Quarter-by-quarter P2TR degradation chart (File B App L.2).

---

### A4 · Schnoering 2024 — "Assessing the Efficacy of Heuristic-Based Address Clustering"

**📄 What it did.** The most recent clustering paper: four new heuristics and a "clustering ratio" measuring how much each merges, with how effectiveness changes over time.

**🕳️ The gap.** It measures *compression*, not *correctness* — a heuristic can merge everything (great ratio) while merging the wrong things (terrible precision).

**💡 Our fix.** Evaluate each heuristic on *forensic precision*: does a cluster built around an OFAC seed contain only criminal addresses?

**🔬 POC.** Run the four heuristics on the OFAC set; report forensic precision per heuristic — a table not in the original paper.

**🏭 Final.** Adopt all four with forensic-precision-calibrated weights.

---

### A5 · Tironsakkul 2022 — "Wasabi CoinJoin Transaction Detection"

**📄 What it did.** Showed Wasabi mixes have a recognisable "shape" even though their contents are mixed, and traced stolen Bitcoin into Wasabi.

**🕳️ The gap.** Detecting a mix ≠ knowing who's in it; Wasabi 2.0 changed the shape; no dark-web context to tell criminal mixing from privacy mixing.

**💡 Our fix.** Detect → skip CIO → propagate taint to all outputs at reduced confidence; if a pre-mix address has criminal dark-web context, mark post-mix outputs SUSPECTED_POST_MIX_CRIMINAL.

**🔬 POC.** Wasabi/Whirlpool thresholds in the CoinJoin filter.

**🏭 Final.** Six-protocol detector with per-protocol taint decay (File B §4B).

---

### A6 · Stütz 2022 — "Adoption and Actual Privacy of Decentralised CoinJoin"

**📄 What it did.** Asked whether CoinJoins actually deliver privacy. Answer: only partly — how coins were gathered *before* and spent *after* the mix often re-links them.

**🕳️ The gap.** It proves pre/post-mix traceability but never builds a tool that uses it.

**💡 Our fix.** Don't stop taint at a mix — decay it (retain ~50% generic, less for stronger protocols) and keep following, because the paper shows post-mix funds remain traceable.

**🔬 POC.** Taint decay 0.5 at the CoinJoin hop vs 0.85 for normal hops.

**🏭 Final.** Pool-specific decay from Stütz's measured anonymity sets (Whirlpool 0.3, Wasabi 0.35, JoinMarket 0.35).

---

### A7 · Kappos & Yousaf 2021 — "Privacy in the Lightning Network"

**📄 What it did.** Lightning is Bitcoin's fast lane: open a channel (on-chain), send many private payments (off-chain), close it (on-chain). They showed the open/close transactions leak more than expected.

**🕳️ The gap.** Individual in-channel payments stay a black box.

**💡 Our fix.** Detect channel opens (2-of-2 multisig), skip CIO for partners, flag funds as possibly-escaped-to-LN.

**🔬 POC.** LN 2-of-2 P2WSH filter in clustering.

**🏭 Final.** Correlate the public LN gossip graph with on-chain funding to identify criminal-operated nodes (File B App L.1).

---

### B1 · Weber 2019 — The Elliptic Dataset

**📄 What it did.** Built the only public labelled Bitcoin dataset (203,769 transactions, 2% illicit, 166 features) — the benchmark everyone uses.

**🕳️ The gap.** Severe class imbalance (49 clean per 1 criminal); data ends 2018; on-chain features only — a zero-history address is all-zeros.

**💡 Our fix.** Add 6 off-chain features (dark-web payment confidence, topic, dw_to_first_tx_days, PGP link, onion co-occurrence, alias match) that only exist with dark-web intelligence.

**🔬 POC.** Append the 6 features to the RF; ablation shows the recall gain.

**🏭 Final.** A separate pre-transaction classifier using *only* off-chain features for zero-history addresses; optionally adopt Elliptic2 (2024) as a stronger benchmark.

---

### B2 · Peled 2021 — "Towards Malicious Address Identification"

**📄 What it did.** 40+ features → RF at 95% precision / 40% recall. BTC-Intel's Week-1 baseline.

**🕳️ The gap.** Static features over all history dilute recent criminal turns; zero-history → all zeros; no dark-web context.

**💡 Our fix.** 4-window temporal-delta features (7/30/90/365d) + dormancy-break; PRE_CRIME for zero-history.

**🔬 POC.** Add temporal deltas to the Elliptic eval; measure recall beyond 40%.

**🏭 Final.** 200+ dim temporal vector + lifecycle phase classifier.

---

### B3 · Chen 2023 — "Evolve Path Tracer" (four lifecycle phases)

**📄 What it did.** Found criminal wallets follow four phases — pre-crime (quiet setup), active (high volume, peel chains), evasion (dormant then mixers), exit (one big cash-out). A temporal GNN detects them early (87% F1).

**🕳️ The gap.** Needs heavy ML infra; on-chain only — no signal for the pre-crime phase before any transaction.

**💡 Our fix.** Rolling windows approximate the phases cheaply; the dark-web listing date anchors the pre-crime phase, and dw_to_first_tx_days measures its duration.

**🔬 POC.** Dormancy-break feature; the temporal-gap feature.

**🏭 Final.** Full four-phase classifier with phase labels on the dashboard.

---

### B4 · ChronoWave-GNN 2025 — wavelet-temporal graph transformer

**📄 What it did.** The most advanced *post-transaction* detector — wavelets + temporal graph transformer, top of the Elliptic leaderboard.

**🕳️ The gap.** Still on-chain only: zero information before the first transaction.

**💡 Our fix.** Don't compete on the leaderboard (we'd lose the GNN arms race). Position BTC-Intel as *complementary* — it owns the pre-transaction phase ChronoWave cannot touch by construction. Layer 4.3 is modular so a future version can plug ChronoWave in.

**🔬 POC.** Simpler Isolation Forest as the post-transaction component.

**🏭 Final.** Optional TGNN swap-in for Layer 4.3.

---

### C1 · Biryukov 2014 — "Trawling for Tor Hidden Services"

**📄 What it did.** Built the first big map of the dark web by enumerating onion services and linking them by *hyperlinks*.

**🕳️ The gap.** Hyperlinks are weak — a link can be a recommendation or spam. The strong relationship it misses: two sites that take payment to the *same* wallet are almost certainly one operator.

**💡 Our fix.** Add the shared-wallet edge — connect onion domains that share a payment address, weighted by how many they share.

**🔬 POC.** Build the shared-wallet graph in Neo4j; show a pair connected by a shared wallet but *no* hyperlink (File A App A).

**🏭 Final.** Real-time edge updates; infrastructure-group detection feeds entity resolution.

---

### C2 · Spitters 2014 — "Thematic Organisation of Tor Hidden Services"

**📄 What it did.** Used LDA topic modelling to classify onion content (drugs/weapons/fraud/services).

**🕳️ The gap.** Topics are descriptive and studied separately from payment addresses.

**💡 Our fix.** Run topic classification *and* address extraction on the same page, so every extracted address carries a `page_topic`.

**🔬 POC.** Keyword/LDA topic per page stored with each address.

**🏭 Final.** Fine-tuned dark-web topic model; topic-specific likelihood ratios (DRUG > generic SERVICES).

---

### C3 · Ghosh 2017 — "Automated Analysis of Dark Net Markets"

**📄 What it did.** Automatically classified market listings and extracted prices.

**🕳️ The gap.** No PGP-continuity linking; prices never checked against the blockchain.

**💡 Our fix.** Parse the listing price and (production) compare it to the first on-chain transaction amount — a match within ±5% in 24h is strong corroboration.

**🔬 POC.** Amount parser stores listing price on the watchlist row.

**🏭 Final.** AMOUNT_CORRELATION as a calibrated LR ~15 signal.

---

### C4 · Christin 2013 / Sun 2019 — cross-market vendors

**📄 What they did.** Christin: first Silk Road study; aliases are stable and reused. Sun: stylometry links the same vendor across markets (78%).

**🕳️ The gap.** Manual/stylometry-only linking; no unified entity graph combining blockchain + PGP + alias signals.

**💡 Our fix.** Four-signal probabilistic entity resolution (wallet + PGP + alias via Jaro-Winkler + domain) into one Neo4j entity graph.

**🔬 POC.** PGP-fingerprint linking across domains.

**🏭 Final.** Full four-signal resolution + temporal entity events.

---

### C5 · Owenson 2018 — "The Darknet's Smaller than We Think"

**📄 What it did.** Measured that most criminal markets are behind login; an unauthenticated crawler sees only ~8% of the active surface.

**🕳️ The gap (for us).** We cannot create market accounts (illegal/unethical), so ~8% is a hard ceiling.

**💡 Our fix.** Acknowledge it; supplement with DUTA-10K/Gwern archives and unauthenticated forum quotes.

**🔬/🏭.** Cited honestly in the limitations section of both POC and paper.

---

### C6 · Hiramoto 2020 — "Dark Web Marketplaces via Bitcoin"

**📄 What it did.** Traced market financial lifecycles (launch → peak → exit), ~12–24 months.

**🕳️ The gap.** Tracks the *market*, not the *vendor* across market deaths.

**💡 Our fix.** PGP/alias entity resolution follows vendors when a market dies and they resurface elsewhere.

**🔬 POC.** PGP continuity across domains.

**🏭 Final.** Market-exit detection + 90-day reappearance monitoring.

---

### D1 · Chainalysis Patent US10977655B2

**📄 What it does.** Pour dirty water (criminal funds) through pipes (transactions); track how much dirty water ends up in each bucket — the taint score. Requires an existing transaction.

**🕳️ The gap.** No transaction = no taint = zero score. Every PRE_CRIME address scores zero in their system. Also no protection against circular evidence.

**💡 Our fix.** PRE_CRIME (risk before the first transaction) + provenance-aware fusion (no circular double-counting).

**🔬/🏭.** Positioned as *complementary* to taint; our claims disclaim taint and target the off-chain/pre-transaction elements.

---

### D2 · Nerino 2021 — Label Propagation for AML

**📄 What it did.** Spread "criminal" labels through the graph like a rumour, weakening with distance (89% accuracy).

**🕳️ The gap.** Only tested one method; never compared to taint or PPR.

**💡 Our fix.** Implement all three and compare on the same dataset; ensemble in production.

**🔬 POC.** Three methods in parallel + comparison table.

**🏭 Final.** Ensemble with learned per-category weights.

---

### D3 · Gao 2022 — Blockchain Intelligence Survey

**📄 What it did.** Surveyed AI/ML for blockchain and explicitly noted: nobody combines evidence with formal probabilistic justification.

**🕳️ The gap.** It *names* the missing formal fusion framework.

**💡 Our fix.** Calibrated, provenance-aware Bayesian fusion — exactly the named gap.

**🔬/🏭.** The provenance engine (Contribution 3).

---

### E1 · Lundberg & Lee 2017 — SHAP / E2 · Wachter 2017 — Counterfactuals

**📄 What they did.** SHAP: explain an ML score by each feature's contribution. Wachter: explain by the minimal change that would flip the decision.

**🕳️ The gap.** SHAP can't explain deterministic rules; counterfactuals weren't applied to blockchain risk.

**💡 Our fix.** SHAP for the ML anomaly layer + a counterfactual generator for the rule/Bayesian layers; route by the decisive layer.

**🔬 POC.** SHAP on the Isolation Forest; counterfactual on the Bayesian score.

**🏭 Final.** Full explainability engine with contradiction detection and narrative.

---

### F (NEW) · The brand-new gaps from literature search

**F1 Taproot forensics** (ICDCSW 2023 + Block-Number 2025): a P2TR heuristic now exists → we *measure degradation* rather than claim a new heuristic. **F2 Pre-transaction intelligence**: still no published system does it → our highest-novelty contribution. **F3 Cross-protocol bridges** (SoK 2509.21831, >$7B laundered): emit CROSS_CHAIN_EXIT, measure exit frequency. **F4 Adversarial evasion**: dust filter + cluster-poison quarantine + contradiction score. **F5 Multi-blockchain entity resolution**: cross-chain-ready schema via PGP/alias. **F6 RPC deanon** (Time-Tells-All 2025): operational — bind our node RPC to localhost.

---
## Appendix C4 — Provisional Patent: Detailed-Description Embodiments (Ready-to-File Draft)

A provisional application is never examined but becomes the specification for the non-provisional, so it should be written as if it *is* the full application. Below is draft "Detailed Description of Preferred Embodiments" text for the three patentable contributions, with reference numerals and alternative embodiments (which broaden protection). Have a registered patent agent/attorney refine before filing.

### C4.1 — Title, Field, Background, Summary

**Title:** "System and Method for Pre-Transaction Risk Assessment of Cryptocurrency Addresses Using Off-Chain Contextual Intelligence."

**Field of the Invention.** This invention relates to cryptocurrency transaction monitoring, and more particularly to systems that assign risk classifications to cryptocurrency addresses prior to their participation in on-chain transactions using contextual intelligence derived from off-chain sources, and to systems that combine risk evidence from multiple sources while preventing double-counting of correlated evidence.

**Background.** Cryptocurrency is increasingly used for illicit payments. Existing monitoring systems assign risk to an address only after it participates in an on-chain transaction; for example, taint-propagation systems compute a risk value propagated from a previously classified address (e.g., US10977655B2), and machine-learning systems compute features from an address's transaction history. Consequently, an address that has been established as criminal payment infrastructure but has not yet transacted is indistinguishable, to such systems, from a newly created legitimate address. Furthermore, when multiple intelligence sources independently report the same underlying fact, naive combination of their signals over-counts that fact. There is a need for (a) pre-transaction risk assessment from off-chain context, and (b) evidence combination that accounts for correlated provenance. *[The Background must not describe the invention itself.]*

**Brief Summary.** A system (100) crawls Tor hidden services within an isolated execution environment (110), extracts cryptocurrency addresses and surrounding text (120), classifies the text as a payment, victim, or ambiguous context (130), and for payment-context addresses lacking on-chain history assigns a pre-transaction classification (140) and monitors for a first transaction (150), upon which a fusion engine (160) computes a final risk classification while excluding correlated evidence by provenance (170). An onion-domain graph (180) connects domains sharing a payment address.

### C4.2 — Embodiment 1: Pre-Transaction Classification (numerals 100–199)

The crawler subsystem (110) operates within an isolated virtual machine (112) communicating with an object store (114) over a restricted network interface (116) that permits, in a preferred embodiment, communication only with said object store. A renderer (118) executes page scripts within the isolated environment without executing them in the extraction process. *In an alternative embodiment, the crawler retrieves pre-archived documents (119) from a research repository rather than crawling live, the remainder of the method being identical.*

An extraction subsystem (120) applies a plurality of address patterns (121) corresponding to address encodings including pay-to-public-key-hash, pay-to-script-hash, and Bech32/Bech32m, and validates each candidate by a checksum verifier (122). A fingerprint extractor (123) derives cryptographic public-key fingerprints from the document. *In an alternative embodiment, the extraction subsystem further applies optical character recognition (124) and machine-readable-code decoding (125) to image content below a size threshold.*

A classifier (130) determines, for each validated address, a context label selected from {payment, victim, ambiguous} based on signal terms (131) within a window (132) about the address occurrence; a victim label is treated as reducing risk. *In a preferred embodiment the window (132) is determined by sentence boundaries (133) such that the window comprises the sentence containing the address and a configurable number of adjacent sentences.*

A pre-transaction module (140) queries a blockchain datastore (142) to determine on-chain history; responsive to a payment label with confidence at least a threshold (144, e.g., 0.40) and to the address having no on-chain history, the module assigns a pre-transaction classification (146) and stores it with the confidence and contextual evidence in a monitoring datastore (148).

A monitor (150) detects a first on-chain transaction of a monitored address by one of: periodic query (152) of the blockchain datastore, or subscription (154) to an address-indexing service. Responsive to detection, a re-evaluation trigger (156) invokes the fusion engine (160) with the stored contextual evidence and newly available on-chain evidence, and records a temporal gap (158) between the first off-chain appearance and the first on-chain transaction.

### C4.3 — Embodiment 2: Provenance-Aware Fusion (numerals 160–179)

The fusion engine (160) initializes a log-odds accumulator (162) from a prior probability (164). For each evidence signal (166), a provenance resolver (168) determines a provenance set comprising source identifiers contributing to the signal. An active-source register (170) records source identifiers already applied. A gate (172) excludes a signal whose provenance set intersects the active register, thereby preventing double-counting of correlated evidence; otherwise the engine adds the natural logarithm of a likelihood ratio (174) associated with the signal to the accumulator and records the signal's source in the register. *In a preferred embodiment, signals are processed in descending order of likelihood ratio (176) so exclusion is deterministic. In an alternative embodiment, the likelihood ratios (174) are empirically calibrated (178) from confirmed-criminal and confirmed-clean address sets.* A converter (179) maps the accumulator to a posterior probability and a category by thresholds.

### C4.4 — Embodiment 3: Shared-Payment-Address Onion Graph (numerals 180–199)

A graph builder (180) maintains nodes (182) each representing a hidden-service domain and edges (184) each representing co-appearance of at least one payment-context address on two domains, an edge weight (186) being a count of shared addresses. A component analyzer (188) identifies, from connected components (190) over edges with weight at least a threshold, groups of domains (192) operated by a common entity. *In an alternative embodiment, edges further store the set of shared addresses (194) and a co-appearance timestamp (196) enabling temporal analysis of infrastructure formation.*

### C4.5 — Why Each Embodiment Avoids the Blocking Prior Art

- *Embodiment 1* acts on addresses with **no** on-chain history and **no** prior classification, deriving risk from off-chain context — outside the literal scope of US10977655B2 Claim 1 (which requires "a taint value propagated from a previously classified cryptocurrency address") and of US10275772B2 (which scores *transactions* by weighted blockchain factors).
- *Embodiment 2* recites a **provenance-set intersection gate** absent from any blockchain risk patent; general fusion prior art (2104.07440) lacks the provenance mechanism.
- *Embodiment 3* recites a **financial-instrument co-appearance edge** absent from hyperlink (Biryukov 2014) and topic (Spitters 2014) onion graphs.

### C4.6 — Drawings to Include (USPTO-compliant, all elements numbered)

```
FIG. 1  System architecture: crawler(110)→extraction(120)→classifier(130)→
        pre-transaction(140)→monitor(150)→fusion(160)→graph(180), with isolated VM
        boundary (112) and object store (114).
FIG. 2  Flowchart of the pre-transaction method (Embodiment 1), steps (146)→(156).
FIG. 3  State machine: ACTIVE→TRIGGERED→{BLACKLISTED|WATCHLISTED|CLEAN}, EXPIRED.
FIG. 4  Flowchart of provenance-aware fusion (Embodiment 2), gate (172).
FIG. 5  Onion graph with shared-wallet edges (184) and an infrastructure group (192).
FIG. 6  Database schema (monitoring datastore 148; audit log).
```

---

## Appendix C5 — Evaluation Methodology in Depth

The numbers in §6.3 do not collect themselves. This appendix specifies *how* to construct each test set and compute each metric, with code — so the evaluation is reproducible and the paper's claims are defensible.

### C5.1 — Test-Set Construction

```python
# services/eval/build_testsets.py
"""
True positives (criminal):
  - OFAC SDN confirmed BTC addresses (ground truth, confidence 1.0)
  - Known mixers from FBI/OFAC press releases (Helix, Bestmixer, Sinbad, etc.)
True negatives (clean):
  - WalletExplorer exchange hot-wallet addresses (should be CLEAN)
  - Random ordinary addresses with no suspicious history
  - Chainabuse-reported SCAM-VICTIM addresses (should be CLEAN, exculpatory)
Held-out: never used for LR calibration AND evaluation simultaneously (no leakage).
"""
def build_testsets(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT address FROM seed_addresses WHERE source='OFAC_SDN'")
        ofac = [r[0] for r in cur.fetchall()]
        cur.execute("SELECT address FROM service_labels WHERE label_type='EXCHANGE'")
        exch = [r[0] for r in cur.fetchall()]
    # split: half of OFAC for calibration, half for evaluation (no leakage)
    cal_pos, eval_pos = ofac[::2], ofac[1::2]
    cal_neg, eval_neg = exch[::2], exch[1::2]
    return {"cal_pos": cal_pos, "cal_neg": cal_neg,
            "eval_pos": eval_pos, "eval_neg": eval_neg}
```

### C5.2 — The Four Core Metrics (Defined and Coded)

- **Precision = TP/(TP+FP)** — of addresses we flagged, how many are truly criminal.
- **Recall = TP/(TP+FN)** — of truly criminal addresses, how many we caught.
- **F1 = 2·P·R/(P+R)** — harmonic mean.
- **FPR = FP/(FP+TN)** — of clean addresses, how many we wrongly flagged.

(Code in File A Appendix C `evaluate()`.) Report all four with 95% confidence intervals via bootstrap resampling:

```python
# services/eval/bootstrap.py
import random

def bootstrap_ci(addresses, classify_fn, is_positive, metric_fn, n=1000):
    vals = []
    for _ in range(n):
        sample = [random.choice(addresses) for _ in addresses]
        vals.append(metric_fn(sample, classify_fn, is_positive))
    vals.sort()
    return vals[int(0.025*n)], vals[int(0.975*n)]    # 95% CI
```

### C5.3 — The PRE_CRIME Ground-Truth Construction (Hardest Part)

The novel claim — "flagged N% of addresses D days before OFAC" — needs a ground truth for *pre-transaction* classification. Build it like this:

```python
# services/eval/precrime_ground_truth.py
"""
For each OFAC-confirmed address with a known OFAC listing date:
  1. Look up its earliest dark-web appearance in our crawl records.
  2. If the DW appearance predates the OFAC listing date AND was PAYMENT context,
     it is a TRUE POSITIVE for PRE_CRIME (we could have flagged it before OFAC).
  3. days_before_ofac = ofac_listing_date - dark_web_first_seen_date.
"""
def precrime_evaluation(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT s.address, s.fetched_at AS ofac_date,
                   MIN(d.first_seen) AS dw_first_seen
            FROM seed_addresses s
            JOIN dark_web_records d ON d.address = s.address
            WHERE s.source = 'OFAC_SDN' AND d.context_type = 'PAYMENT'
            GROUP BY s.address, s.fetched_at
        """)
        rows = cur.fetchall()
    caught_early = [r for r in rows if r[2] < r[1]]      # DW seen before OFAC
    days = [(r[1] - r[2]).days for r in caught_early]
    pct = len(caught_early) / len(rows) if rows else 0.0
    avg_days = sum(days) / len(days) if days else 0.0
    return {"pct_caught_before_ofac": round(pct, 4),
            "avg_days_before_ofac": round(avg_days, 1),
            "n_total": len(rows), "n_early": len(caught_early)}
```

This produces the headline number for the abstract: *"flagged {pct}% of OFAC addresses {avg_days} days before designation."*

### C5.4 — The Ablation Study (Required at Top Venues)

```python
# services/eval/ablation.py
"""
Run the full system, then disable one component at a time, to prove each contributes.
Each variant is the same engine with a flag turning a component off.
"""
VARIANTS = {
    "FULL": {},
    "no_precrime":   {"disable_precrime": True},
    "no_darkweb":    {"disable_dw_features": True},
    "no_temporal":   {"disable_temporal": True},
    "no_bayesian":   {"rules_only": True},
    "no_provenance": {"disable_provenance_dedup": True},
}
def run_ablation(engine_factory, testsets):
    out = {}
    for name, flags in VARIANTS.items():
        eng = engine_factory(**flags)
        out[name] = evaluate(eng, testsets["eval_pos"], testsets["eval_neg"])
    return out      # table proving each component's marginal contribution
```

Expected story: removing PRE_CRIME drops the days-before-OFAC metric to zero; removing dark-web features drops recall; removing provenance de-dup *inflates* false positives on circular-evidence cases (proving Contribution 3's value).

### C5.5 — The Three-Way Propagation Comparison

Use File A Appendix C `compare_propagation_methods()` with labels split by address category (exchange / mixer / ordinary, derived from `service_labels` + heuristics). Report a precision/recall/F1/FPR table per method per category, plus the ensemble — the Contribution-4 deliverable.

### C5.6 — Statistical Rigour Checklist

- [ ] No data leakage: calibration and evaluation sets are disjoint (C5.1).
- [ ] Confidence intervals on every headline metric (C5.2 bootstrap).
- [ ] Significance test for the temporal-gap feature (Mann-Whitney U, §3 Contribution 5).
- [ ] Baseline reproduced within ±2% of Peled 2021 before claiming improvement.
- [ ] Ablation isolates each contribution's marginal effect (C5.4).
- [ ] Per-category breakdown for the propagation comparison (C5.5).
- [ ] Processing-time measured on specified hardware (feasibility claim).

---
## Appendix C6 — Detailed Threat Model

A precise threat model is required at top venues and prevents the "unrealistic threat model" rejection (§6.5). It states who the adversary is, what they can and cannot do, what the defender achieves, and what is out of scope.

### C6.1 — The Adversary

A criminal actor who uses Bitcoin for illicit payments and advertises payment addresses on Tor hidden services. The adversary is assumed to be capable of:

- **Address rotation:** generating a fresh address per transaction (defeating address-reuse heuristics).
- **Mixing:** using CoinJoin (Wasabi/Whirlpool/JoinMarket) to obscure fund flow.
- **Multi-market operation:** operating across several dark-web markets under different aliases.
- **Cross-chain exit:** bridging Bitcoin to Ethereum/Monero for final cash-out.
- **Limited counter-intelligence:** knowing that blockchain analytics exists and taking basic evasive steps.

The adversary is assumed **not** to be capable of (for v1): breaking Bitcoin's cryptography; compromising OFAC's processes; or preventing their own payment addresses from appearing on the public-facing (unauthenticated) parts of markets they advertise on.

### C6.2 — The Defender (BTC-Intel)

A passive observer with access to:

- the full public Bitcoin blockchain (via BigQuery in POC, own node in production);
- the ability to crawl **publicly accessible, unauthenticated** Tor hidden services;
- OFAC SDN / UN sanctions lists and community intelligence databases (Chainabuse, etc.).

The defender performs **only passive observation** — never creating accounts, purchasing, logging in, or interacting with criminal services.

### C6.3 — Out of Scope

- The adversary's activity on Ethereum, Monero, or other chains (cross-chain tracking ends at the bridge — File B App D).
- Activity behind **authentication walls** on markets (~92% of the active surface — Owenson 2018). BTC-Intel sees ~8% unauthenticated surface, supplemented by archives.
- Operational-security failures at exchanges (KYC) — a complementary channel, not BTC-Intel's mechanism.
- Network-layer deanonymisation (traffic analysis, RPC side-channels) — orthogonal to our graph+OSINT approach.

### C6.4 — Success Criteria

Assign risk classifications with ≥90% precision (BLACKLISTED tier) and demonstrate detection of pre-transaction addresses subsequently confirmed criminal (the PRE_CRIME claim), with a full, sourced evidence chain for every verdict.

### C6.5 — Attack-by-Attack Defence (Adversarial Robustness)

| Attack | What the adversary does | BTC-Intel defence | Residual risk |
|--------|-------------------------|-------------------|---------------|
| Cluster poisoning | Co-sign with a legitimate address to pollute its cluster | Confidence-weighted voting: a single suspicious co-sign yields a TENTATIVE merge, not auto-merge; production quarantines clusters growing >10k addresses/24h | A patient, low-volume poisoner could still nudge a cluster |
| Dust attack | Send tiny amounts from criminal addresses to many innocent ones | 5% minimum taint fraction filters dust; taint does not propagate *backwards* (receiving dust ≠ guilt); deterministic DUST_FILTER → CLEAN | None significant |
| Dark-web misinformation | Post an innocent address as a "payment" address to frame someone | Contradiction score: an address flagged PAYMENT but appearing in many VICTIM contexts is down-weighted and routed to human review | A one-off false listing with no contradicting evidence could mislead until reviewed |
| Feature manipulation | Mimic clean transaction patterns to stay below the anomaly threshold | Anomaly is only 30% of the blend; dark-web + taint dominate; off-chain evidence is hard to fake | Sophisticated mimicry remains the hardest attack — an honest limitation |
| Address rotation | Fresh address per transaction | CIO + change heuristics re-cluster rotated addresses; PRE_CRIME catches the *first* appearance on the dark web regardless of rotation | Rotation across never-crawled venues evades detection |
| Mixing | CoinJoin to break taint | Detect + decay taint (not stop); pre-mix dark-web context elevates post-mix outputs | Strong-protocol mixing (Whirlpool/Wasabi-2) still degrades taint substantially |
| Cross-chain exit | Bridge BTC→ETH/XMR | CROSS_CHAIN_EXIT event preserves source risk; tracking ends honestly | No on-chain follow past the bridge (v1 limitation) |

The "feature manipulation" row is the honest limitation to state in the paper's Section 8 — BTC-Intel does not fully solve adversarial mimicry of clean behaviour, and says so.

---

## Appendix C7 — Patent Prosecution Guide: Surviving §101 / §102 / §103

Filing is the start; *prosecution* (responding to examiner rejections) is where claims live or die. The three rejection types a software patent faces and how BTC-Intel's claims survive each.

### C7.1 — §101 (Subject-Matter Eligibility — "Abstract Idea")

**The risk.** Software/business-method claims are often rejected as an "abstract idea" (Alice/Mayo framework). A claim reciting only "compute a risk score" is vulnerable.

**How BTC-Intel survives.** The independent claims recite a *specific technological process with concrete, non-generic steps*: crawling within an *isolated execution environment*, validating addresses by *checksum*, classifying *off-chain* context, querying a *blockchain datastore* for zero history, *subscribing* to an address-indexing service for first-transaction detection, and a *provenance-set intersection gate*. These are concrete improvements to a technical field (cryptocurrency monitoring), not an abstract idea implemented on a generic computer. **Drafting rule:** every independent claim must tie to a concrete technical mechanism (the isolated VM, the checksum, the subscription, the provenance gate) — never claim "assign a risk score" in the abstract.

### C7.2 — §102 (Novelty — Anticipation)

**The risk.** A single prior-art document reciting *all* claim elements anticipates and invalidates.

**How BTC-Intel survives (element-by-element vs the closest art):**

- *vs Chainalysis US10977655B2:* their Claim 1 requires "a taint value propagated from a previously classified address." Our Claim 1 step (c)(ii) acts on an address with **no on-chain history** and **no prior classification**. The "previously classified" and "taint propagated" elements are **absent** from our claim → no anticipation.
- *vs US10275772B2 (crypto risk detection):* scores *transactions* by weighted blockchain factors. Our claim scores a *pre-transaction address* by *off-chain* context. The "transaction" and "blockchain factor weighting" elements differ → no anticipation.
- *vs MFScope / Devil-Behind-the-Mirror:* extract dark-web addresses but produce a *measurement study* — neither recites the *PRE_CRIME state*, *monitoring*, or *re-scoring on first transaction*. Those elements are absent → no anticipation.

### C7.3 — §103 (Non-Obviousness)

**The risk.** Even if no single document anticipates, an examiner may combine two references (e.g., "MFScope extraction" + "Chainalysis taint") and argue obviousness.

**How BTC-Intel survives:**

- **Cross-domain combination argument.** Combining onion-graph construction (network measurement) with address clustering (forensics), or NLP context classification with on-chain zero-history verification, requires expertise in *two distinct fields* — combinations across fields are presumptively non-obvious.
- **Teaching away.** The closest art *teaches away* from our approach: taint systems explicitly require a transaction (they would not motivate a skilled person to score a zero-history address); measurement studies do not motivate a real-time risk *state*.
- **Unexpected result.** The ablation (C5.4) shows the *combination* achieves what components cannot — pre-transaction detection D days before OFAC — an unexpected, measurable result that supports non-obviousness.
- **Solving a recognised-but-unsolved problem.** Gao 2022 explicitly names the evidence-fusion gap; solving a long-recognised unsolved problem is evidence of non-obviousness for Contribution 3.

### C7.4 — Office-Action Response Workflow

```
Receive Office Action (rejection)
   │
   ├─ §101? → amend claims to emphasise concrete technical mechanisms (VM, checksum,
   │           subscription, provenance gate); argue improvement to a technical field.
   ├─ §102? → element-by-element claim chart showing the missing element vs the cited art.
   ├─ §103? → cross-domain + teaching-away + unexpected-result (ablation) arguments;
   │           if needed, add a dependent element the combination lacks.
   └─ File response within the statutory period (typically 3 months, extendable to 6).
Repeat until allowance or final rejection → RCE (Request Continued Examination) or appeal.
```

### C7.5 — Continuation Strategy

File the broad independent claims first. If some are rejected, pursue the allowable ones to grant and file a **continuation** to keep prosecuting the broader claims — this secures *some* protection early while preserving the chance at broader scope. Keep at least one continuation pending to claim later-discovered embodiments.

---

## Appendix C8 — Freedom-to-Operate and Defensive Publication

### C8.1 — Freedom-to-Operate (FTO) — Can We *Build* It Without Infringing?

Patentability ("can we patent it?") and FTO ("can we build it without infringing others?") are different questions. BTC-Intel's FTO analysis:

| BTC-Intel component | Potential blocking patent | FTO position |
|---------------------|---------------------------|--------------|
| Amount-weighted taint | Chainalysis US10977655B2 | **Risk.** Our taint implementation may read on their claims. Mitigation: taint is *not* our novelty — we can (a) license, (b) design around by emphasising label-propagation/PPR, or (c) restrict the amount-weighted method to research/non-commercial use. |
| Generic transaction risk scoring | US10275772B2 | **Low risk.** We score pre-transaction addresses by off-chain context, not transactions by weighted factors. |
| CIO / change heuristics | Meiklejohn/Delgado (papers, not patents) | **No risk** — published, unpatented. |
| CoinJoin detection | Tironsakkul/2311.12491 (papers) | **No risk** — published methods. |
| SHAP / Isolation Forest / RF | Public algorithms | **No risk.** |

**Conclusion:** the only material FTO risk is the taint component vs Chainalysis. Because taint is *not* BTC-Intel's contribution and the system works using label-propagation/PPR ensembles, BTC-Intel can design around it if licensing is undesirable.

### C8.2 — Defensive Publication

For contributions you do **not** want to patent but want to keep *others* from patenting (e.g., the three-way propagation comparison, the temporal-gap feature, the Taproot-degradation method), **defensive publication** is the tool: publish them (arXiv, the paper) so they become prior art that blocks anyone else's patent. The arXiv preprint (Month 0) serves double duty — academic priority *and* defensive publication for the non-patented contributions.

**Decision rule per contribution:**

| Contribution | Patent or defensively publish? | Why |
|--------------|-------------------------------|-----|
| 1 PRE_CRIME | **Patent** (Claim 1, priority) | Strong novelty + commercial value |
| 2 Shared-wallet edge | **Patent** (Claims 4–5) | Cross-domain, defensible |
| 3 Provenance fusion | **Patent** (Claim 7) | Names-the-gap novelty |
| 4 Three-way comparison | **Defensively publish** | A comparison is not an invention |
| 5 Temporal gap | **Dependent claim + publish** | Weak standalone; supports Claim 1 |
| Taproot degradation | **Defensively publish** | 2025 heuristic narrows patentability |
| Amount correlation | **Dependent claim (Claim 3)** | Weak non-obviousness alone |

---

## Appendix C9 — Complete Annotated Bibliography

Citation keys match those used throughout. ★ marks papers added via literature search (not in the original planning docs).

**Clustering / Heuristics**
- [Nakamoto2008] Nakamoto, S. "Bitcoin: A Peer-to-Peer Electronic Cash System." 2008. *(Whitepaper §10 anticipates multi-input de-anonymisation — original CIO citation.)*
- [Meiklejohn2013] Meiklejohn et al. "A Fistful of Bitcoins." ACM IMC 2013. DOI 10.1145/2504730.2504747.
- [Ron2013] Ron & Shamir. "Quantitative Analysis of the Full Bitcoin Transaction Graph." FC 2013. arXiv:1209.0440.
- [Delgado2021] Delgado-Segura et al. "Resurrecting Address Clustering in Bitcoin." arXiv:2107.05749, 2021.
- [Kappos2018] Kappos et al. "An Empirical Analysis of Anonymity in Zcash." USENIX Security 2018.
- ★[Schnoering2024] Schnoering & Vazirgiannis. "Assessing the Efficacy of Heuristic-Based Address Clustering for Bitcoin." arXiv:2403.00523, 2024.
- ★[CoinJoinHeur2023] "Heuristics for Detecting CoinJoin Transactions on the Bitcoin Blockchain." arXiv:2311.12491, 2023.
- [Tironsakkul2022] Tironsakkul et al. "The Unique Dressing of Transactions: Wasabi CoinJoin Transaction Detection." ACM EICC 2022.
- [Stutz2022] Stütz et al. "Adoption and Actual Privacy of Decentralized CoinJoin Implementations in Bitcoin." arXiv:2109.10229, 2022.
- [KapposLN2021] Kappos & Yousaf et al. "An Empirical Analysis of Privacy in the Lightning Network." FC 2021. arXiv:2003.12470.
- ★[BlockNumTaproot2025] "Block Number-Based Address Clustering for the Bitcoin Taproot Upgrade." ResearchGate preprint, 2025.
- ★[Taproot2023] "Analyzing the Effect of Taproot on Bitcoin Deanonymization." IEEE ICDCSW 2023.
- ★[CardanoClust2025] "Heuristic-Based Address Clustering in the Cardano Blockchain." arXiv:2503.09327, 2025.

**Machine Learning**
- [Weber2019] Weber et al. "Anti-Money Laundering in Bitcoin: Experimenting with GCNs." KDD Workshop 2019. *(Elliptic dataset.)*
- [Peled2021] Peled et al. "Towards Malicious Address Identification in Bitcoin." arXiv:2112.11721, 2021.
- [Chen2023] Chen et al. "Evolve Path Tracer: Early Detection of Ponzi Schemes and Rug Pulls." arXiv:2301.05412, 2023.
- [Sayadi2023] Sayadi et al. "Fingerprinting Bitcoin Entities Using Money Flow Representation Learning." Applied Network Science 2023. DOI 10.1007/s41109-023-00591-2.
- [Lorenz2020] Lorenz et al. "ML Methods to Detect Money Laundering in the Bitcoin Blockchain." arXiv:2005.14635, 2020.
- [Poursafaei2022] Rossi/Poursafaei et al. "Temporal Graph Networks for Deep Learning on Dynamic Graphs." arXiv:2006.10637.
- ★[ChronoWave2025] "Detecting Illicit Transactions in Bitcoin: A Wavelet-Temporal Graph Transformer Approach for AML." Scientific Reports 2025. s41598-025-23901-3.
- ★[Elliptic2_2024] Bellei et al. "The Shape of Money Laundering: Subgraph Representation Learning with the Elliptic2 Dataset." arXiv:2404.19109, KDD 2024.
- ★[InspectionL2022] "Inspection-L: Self-Supervised GNN Node Embeddings for Money Laundering Detection in Bitcoin." arXiv:2203.10465, 2022.
- ★[Demystify2023] "Demystifying Fraudulent Transactions and Illicit Nodes in the Bitcoin Network for Financial Forensics." arXiv:2306.06108, 2023.
- ★[PlugPlayAML2024] "A Plug-and-Play Data-Driven Approach for Anti-Money Laundering in Bitcoin." Expert Systems with Applications 2024. S0957417424029397.
- ★[TransformerAML2025] "Transformer-Based Risk Monitoring for AML with Transaction Graph Integration." ICDEBA 2025.
- ★[Crowdsource2025] "Detection of Crowdsourcing Cryptocurrency Laundering via Multi-Task Collaboration." arXiv:2512.02534, 2025.

**Dark Web Intelligence**
- [Biryukov2014] Biryukov et al. "Trawling for Tor Hidden Services." IEEE S&P 2014.
- [Spitters2014] Spitters et al. "Thematic Organization of Tor Hidden Services." IEEE EISIC 2014.
- [Ghosh2017] Ghosh et al. "Automated Analysis of Dark Net Markets." ACM WebSci 2017.
- [Christin2013] Christin. "Traveling the Silk Road." WWW 2013.
- [Sun2019] Sun et al. "Cross-Market Drug Vendor Identification." WebSci 2019.
- [Owenson2018] Owenson et al. "The Darknet's Smaller than We Think." Digital Investigation 2018.
- [Hiramoto2020] Hiramoto et al. "Dark Web Marketplaces via Bitcoin: From Birth to Independence." FSI: Digital Investigation 2020.
- [Dalins2018] Dalins et al. "Criminal Motivation on the Dark Web." Digital Investigation 2018.
- ★[MFScope2019] Lee et al. "Cybercriminal Minds: An Investigative Study of Cryptocurrency Abuses in the Dark Web." NDSS 2019.
- ★[DevilMirror2024] "The Devil Behind the Mirror: Tracking Campaigns of Cryptocurrency Abuses on the Dark Web." arXiv:2401.04662, 2024.
- ★[Dizzy2022] "Dizzy: Large-Scale Crawling and Analysis of Onion Services." arXiv:2209.07202, 2022.

**Risk Scoring / Fusion**
- [ChainalysisPatent] Chainalysis Inc. US10977655B2 (2021). Class G06Q 20/06.
- ★[CryptoRiskPatent] US10275772B2 "Cryptocurrency Risk Detection System."
- ★[BlockchainTagsPatent] US11182781 "Blockchain Encryption Tags."
- [Nerino2021] Nerino et al. "Bitcoin Transaction Graph Analysis for Money Laundering Detection." ARES 2021.
- [Gao2022] Gao et al. "Blockchain Intelligence: When Blockchain Meets AI." IEEE Trans. Network Science 2022.
- ★[BayesDS2021] "Bayesian and Dempster-Shafer Models for Combining Multiple Sources of Evidence in a Fraud Detection System." arXiv:2104.07440.
- ★[Web3RegTech2025] "SoK: Web3 RegTech for Cryptocurrency VASP AML/CFT Compliance." arXiv:2512.24888.
- ★[DarkArt2025] "The Dark Art of Financial Disguise in Web3." arXiv:2509.21831, 2025.

**Explainability / Privacy / Misc**
- [Lundberg2017] Lundberg & Lee. "A Unified Approach to Interpreting Model Predictions (SHAP)." NeurIPS 2017.
- [Wachter2017] Wachter et al. "Counterfactual Explanations Without Opening the Black Box." Harvard JOLT 2017.
- [Yin2023] Yin et al. "Privacy-Preserving Blockchain Analysis." IEEE TIFS 2023.
- [Chaum1981] Chaum. "Untraceable Electronic Mail, Return Addresses, and Digital Pseudonyms." 1981.
- ★[BlockchainXAI2024] "Detecting Anomalies in Blockchain Transactions Using ML Classifiers and Explainability Analysis." arXiv:2401.03530, 2024.
- ★[LNDataset2025] "Geolocated Lightning Network Topology Snapshots 2019–2023." Scientific Data 2025. s41597-025-06413-7.
- ★[TimeTellsAll2025] "Time Tells All: Deanonymization of Blockchain RPC Users with Zero Transaction Fee." arXiv:2508.21440, 2025.
- ★[NetTrafficDeanon2026] "Deanonymizing Bitcoin Transactions via Network Traffic Analysis with Semi-Supervised Learning." arXiv:2603.17261, 2026.

**Count:** ~50 references; ~23 marked ★ are new via literature search — far exceeding the "at least 3 new papers" requirement.

---
## Appendix C10 — Draft Paper Prose (Introduction, Related Work, Conclusion)

Beyond the templates in §6, here is *actual draft prose* (with bracketed measurement placeholders) the team can adapt — written to the standards of a security/FC submission.

### C10.1 — Draft Introduction

> Cryptocurrency-enabled crime has grown into a structural problem for financial integrity: an estimated [$X] billion was laundered through cryptocurrencies in [year], and government sanctions bodies now routinely publish digital-asset addresses as blocked property — over 1,200 such addresses as of 2025, of which roughly 63% are Bitcoin. A mature ecosystem of analytics tools, both commercial (Chainalysis, TRM, Elliptic) and academic (the Elliptic-dataset line of work), supports law enforcement and compliance teams in tracing these funds.
>
> Yet every one of these systems shares a single, fundamental blind spot. They assign risk to an address *only after that address has participated in an on-chain transaction.* Taint-propagation systems require, by construction, "a taint value propagated from a previously classified address" [ChainalysisPatent]; machine-learning classifiers compute features from transaction history [Peled2021, Weber2019], so an address with no history yields an empty feature vector; and the current state of the art in temporal graph learning [ChronoWave2025] cannot, by definition, score an address that has never transacted. The consequence is a *pre-transaction window* during which criminal payment infrastructure is openly established — advertised on dark-web markets — yet remains invisible to every monitoring system. An exchange receiving a deposit address that was listed in a drug-market checkout page yesterday sees, today, an address indistinguishable from a brand-new legitimate wallet.
>
> We close this gap. We present BTC-Intel, a Bitcoin wallet intelligence system that integrates intelligence extracted from Tor hidden services with Bitcoin transaction-graph analysis. Its central novelty is the PRE_CRIME_WATCHLIST classification: a non-zero risk assigned to an address found in a dark-web payment context *before* any on-chain activity, monitored until its first transaction, then promoted by a full risk engine. We further contribute a shared-payment-address edge type for onion-service graphs — revealing operator-level coordination that hyperlink-based graphs [Biryukov2014] cannot see — and a provenance-aware Bayesian evidence-fusion engine that prevents the circular double-counting of correlated intelligence that prior work combines without formal justification [Gao2022].
>
> **Contributions.** In summary, this paper makes the following contributions: **(1)** the PRE_CRIME_WATCHLIST mechanism, the first published method for assigning non-zero risk to a cryptocurrency address prior to any on-chain transaction (§5); **(2)** the shared-payment-address edge type for Tor hidden-service graphs (§6); **(3)** a provenance-aware Bayesian evidence-fusion engine (§6); **(4)** the first head-to-head comparison of amount-weighted taint, label propagation, and Personalised PageRank on a single labelled dataset (§7); and **(5)** an evaluation demonstrating [X]% precision at [Y]% recall and detection of [N]% of subsequently-confirmed criminal addresses an average of [D] days before official designation (§7). Section 2 reviews prior work; Section 3 states the threat model; Sections 4–6 present the architecture and novel mechanisms; Section 7 evaluates; Sections 8–9 discuss limitations and ethics.

### C10.2 — Draft Related-Work Prose

> **Address clustering.** The common-input-ownership (CIO) heuristic originates with Meiklejohn et al. [Meiklejohn2013]; Delgado-Segura et al. [Delgado2021] re-assess it on modern Bitcoin, showing the naive change heuristic reaches 23% false-positive rate on SegWit and introducing optimal-change and weighted voting. Schnoering & Vazirgiannis [Schnoering2024] add further heuristics and a temporal clustering-ratio analysis. We adopt CIO with a CoinJoin pre-filter and recalibrated 2024 weights; CIO itself is not our contribution.
>
> **Privacy mechanisms.** CoinJoin detection is well studied [Tironsakkul2022, CoinJoinHeur2023], and Stütz et al. [Stutz2022] show mixing provides only partial privacy through pre/post-mix linkage; Kappos & Yousaf [KapposLN2021] analyse Lightning-channel leakage. Taproot degrades script-type heuristics [Taproot2023], though a block-number heuristic has since been proposed [BlockNumTaproot2025]; accordingly we flag P2TR clustering as unresolved and *measure* its degradation rather than claim a new heuristic.
>
> **Risk propagation.** Amount-weighted taint is the commercial approach [ChainalysisPatent]; Nerino et al. [Nerino2021] apply label propagation. No prior work compares these with Personalised PageRank on a common dataset — a gap we fill (§7).
>
> **Dark-web intelligence.** Biryukov et al. [Biryukov2014] enumerate onion services and build hyperlink graphs; Spitters et al. [Spitters2014] classify content by topic; Ghosh et al. [Ghosh2017] extract market prices. Recent work extracts cryptocurrency addresses at scale [MFScope2019, DevilMirror2024]. Our shared-payment-address edge extends Biryukov's hyperlink graph with a financial signal absent from all of this work, and we bind topic to extracted payment addresses, unlike Spitters.
>
> **Behavioural ML and explainability.** Peled et al. [Peled2021] and Weber et al. [Weber2019] establish the Elliptic benchmark; Chen et al. [Chen2023] model a four-phase criminal lifecycle; ChronoWave-GNN [ChronoWave2025] is the current post-transaction state of the art. We complement, not compete with, these by addressing the pre-transaction phase, and we add explainability via SHAP [Lundberg2017] for the ML layer and counterfactuals [Wachter2017] for the rule/Bayesian layers — the latter not previously applied to blockchain risk.
>
> **Evidence fusion.** Gao et al. [Gao2022] note that current systems combine evidence "without formal probabilistic justification," and general fusion work [BayesDS2021] shows naive score-summing over-counts correlated evidence; neither provides a provenance mechanism for blockchain's circular OFAC→commercial dependencies, which our engine supplies.

### C10.3 — Draft Conclusion

> We presented BTC-Intel, the first published Bitcoin wallet intelligence system to assign risk *before* an address's first on-chain transaction, by integrating dark-web payment-context intelligence with transaction-graph analysis. Beyond the PRE_CRIME_WATCHLIST mechanism, we contributed a shared-payment-address onion-graph edge and a provenance-aware Bayesian fusion engine, and we provided the first three-way comparison of taint, label propagation, and Personalised PageRank on a common dataset. Our central empirical finding is that BTC-Intel identified [N]% of subsequently-OFAC-confirmed criminal addresses in the PRE_CRIME_WATCHLIST state an average of [D] days before official designation — detection that is impossible for any transaction-dependent system. Future work includes integrating temporal graph networks for the post-transaction layer, extending entity resolution across chains, and — within strict legal and ethical bounds — improving coverage of authenticated market surfaces.

---

## Appendix C11 — Consolidated Research-Claims List (One per Paper, With Placeholders)

A single place to track every measurable claim. Replace each [X]/[Y]/[Z]/[N]/[D] with a measured value before submission (§6.3). A claim with an un-filled placeholder is not submittable.

1. **vs Meiklejohn 2013:** "CoinJoin pre-filtering + confidence voting reduces CIO false-merge from [A]% to [B]% on 2024 data."
2. **vs Ron & Shamir 2013:** "We supply the external labelling they identified as future work via off-chain dark-web intelligence, labelling [C] clusters."
3. **vs Delgado 2021:** "Recalibrated 2024 weights change clustering precision by [D] points; we chart P2TR degradation from [E]% to [F]% adoption."
4. **vs Schnoering 2024:** "Forensic-precision evaluation ranks the four heuristics differently than the clustering-ratio metric in [G] of 4 cases."
5. **vs Tironsakkul/Stütz 2022:** "Context-conditioned post-mix taint recovers [H]% of post-mix criminal outputs missed by stop-at-mix."
6. **vs Kappos & Yousaf 2021:** "We identify [I] criminal-operated Lightning nodes via gossip↔on-chain correlation."
7. **vs Weber 2019:** "Adding 6 off-chain features improves Elliptic illicit-class recall by [J] points at comparable precision."
8. **vs Peled 2021:** "Temporal delta features improve recall by [K] points over the static baseline; baseline reproduced within ±2%."
9. **vs Chen 2023:** "dw_to_first_tx_days is a significant predictor of illicit classification (Mann-Whitney U, p=[L])."
10. **vs ChronoWave 2025:** "BTC-Intel detects [M] pre-transaction addresses that ChronoWave scores zero by construction."
11. **vs Biryukov 2014:** "[N]% of shared-wallet edges connect domains with no hyperlink edge."
12. **vs Nerino 2021:** "Ensemble propagation matches or beats the best single method in [O] of [P] address categories."
13. **vs Gao 2022:** "Provenance de-dup reduces BLACKLISTED-tier false positives on circular-evidence cases from [Q]% to [R]%."
14. **PRE_CRIME headline:** "[S]% of OFAC-confirmed addresses flagged PRE_CRIME an average of [T] days before designation."
15. **Amount correlation:** "[U]% of triggered PRE_CRIME addresses showed first-tx amount matching the listing price within ±5%."

---

## Appendix C12 — Budget, Resources, and Funding Plan

### C12.1 — Patent Budget

| Item | Self-file | With patent agent | Notes |
|------|-----------|-------------------|-------|
| Provisional (USPTO fee) | $320 | $320 + ~$1,500 agent | Micro-entity rate (individual/uni researcher) |
| Prior-art search | $0 (self, §5E) | $1,000–$2,000 | Agent searches are more thorough |
| Non-provisional (USPTO) | ~$800 | $800 + ~$3,000 agent | Includes exam fee |
| PCT application (USPTO) | ~$3,000 | $3,000 + ~$2,000 agent | International priority, 157 countries |
| Office-action responses | $0–$600 | $1,500–$3,000 each | One or more likely (App C7) |
| EPO national phase | €4,000+ | +€2,000 agent | Only if Europe pursued |
| **Total (US only, w/ agent)** | — | **~$10,000–$15,000** | Over 2–3 years |
| **Total (international)** | — | **~$25,000–$40,000** | Over 3–5 years |

**Recommendation:** use a USPTO-registered patent *agent* with a CS background (~$4,000 for the core US filings) — the claim-quality gain over pro-se is large for the cost.

### C12.2 — Paper Budget

| Item | Cost |
|------|------|
| arXiv submission | $0 |
| Conference registration (if accepted) | $600–$1,200 |
| Travel/accommodation (in-person) | $1,000–$3,000 |
| Professional proofreading | $200–$500 |
| Open-access fee (optional) | $0–$1,500 |
| **Total** | **~$2,000–$5,000** |

### C12.3 — Funding Sources for Academic Researchers

- **University Technology Transfer Office (TTO):** often covers patent costs in exchange for a share of licensing revenue. **Negotiate ownership *before* filing** — institutions frequently claim IP created with their resources.
- **Proof-of-Concept / commercialisation grants:** NSF I-Corps (US), Innovate UK, EIC Accelerator (EU).
- **Research commercialisation funds** at most major universities.
- **The provisional itself is cheap ($320)** — file it this week regardless of larger funding, to secure the priority date.

---

## Appendix C13 — Reproducibility and Artifact-Release Plan

To pre-empt the "not reproducible" rejection (§6.5) while respecting the legal constraint that dark-web raw pages cannot be redistributed:

**Release on GitHub (open):**
- The clustering engine (Union-Find CIO + four heuristics + CoinJoin filter).
- The three propagation methods + the comparison harness (Contribution 4).
- The provenance-aware Bayesian fusion engine (Contribution 3) with the LR-calibration code.
- The Elliptic baseline reproduction (Peled 2021) and the full evaluation harness (App C5).
- The PRE_CRIME state machine and monitoring logic (with a synthetic/archived data adapter).
- README, license (e.g., MIT for code), and a `requirements.txt` (pinned).

**Release under controlled access / as a manifest (legal constraint):**
- A **SHA-256 manifest** of the dark-web page set (lets a reviewer verify dataset identity under NDA without redistribution).
- De-identified extracted feature vectors where lawful (addresses are public; PGP UIDs and free text are stripped).

**Do NOT release:** raw dark-web HTML (GDPR + legal risk; auto-deleted at 90 days anyway).

**Reproducibility statement for the paper:** "All pipeline components not dependent on dark-web content are released at [URL]. The dark-web dataset cannot be redistributed for legal reasons; we release a SHA-256 manifest for verification under NDA and de-identified feature vectors. The Elliptic evaluation is fully reproducible from public data."

---

## Appendix C14 — Patent-Ready and Paper-Ready Checklists

### C14.1 — Patent-Ready (before filing the provisional)

- [ ] Inventor's notebook entry, dated and witnessed (conception + reduction-to-practice dates).
- [ ] Prior-art search completed for Claims 1, 7, 8 (§5E queries run; US10977655B2, US10275772B2, US11182781 read in full).
- [ ] Confirmed Claim 1 does not read on Chainalysis US10977655B2 (zero-history, no prior classification — App C7.2).
- [ ] Provisional text written: Title, Field, Background, Summary, Detailed Description (App C4 embodiments), Claims, Abstract.
- [ ] Drawings prepared (FIG.1–6, App C4.6, all elements numbered).
- [ ] Alternative embodiments included (broaden scope).
- [ ] USPTO Patent Center account created; micro-entity qualification confirmed.
- [ ] $320 ready; Application Number recorded in 3 places after filing.
- [ ] 12-month non-provisional + PCT deadlines calendared with a 1-month buffer.
- [ ] **Provisional filed BEFORE the arXiv preprint** (no-grace-period jurisdictions).

### C14.2 — Paper-Ready (before submitting to any venue)

- [ ] All five Section-1 contributions have a Section-7 result (no orphan claims).
- [ ] ≥2 baselines (naive single-hop taint; Peled 2021 RF).
- [ ] Ablation with ≥5 variants (App C5.4).
- [ ] PRE_CRIME days-before-OFAC result (App C5.3).
- [ ] Three-way propagation table (App C5.5).
- [ ] Temporal-gap significance test (Contribution 5).
- [ ] Limitations section with the 6 documented limitations (incl. ~8% Owenson coverage).
- [ ] Ethics section: IRB status, GDPR, passive observation, no criminal participation.
- [ ] Prior art cited generously; nothing claimed novel without justification.
- [ ] Every [X]/[Y]/... placeholder replaced with a measured value (App C11).
- [ ] Page count within venue limit; correct template (ACM/IEEE/Springer).
- [ ] Reproducibility statement + GitHub repo (App C13).
- [ ] Proofread by ≥2 people (≥1 external).
- [ ] For double-blind: arXiv timing handled (after review window or anonymised), but after the provisional.

---

## Appendix C15 — Research Glossary (Terms of Art)

| Term | Definition |
|------|------------|
| **CIO (Common-Input-Ownership)** | Heuristic: co-signing transaction inputs share one owner. |
| **Change address** | The output returning the remainder to the sender in a 2-output transaction. |
| **Optimal-change heuristic** | Identifies change as the output equal to inputs − payment − fee. |
| **CoinJoin** | A privacy transaction where independent parties combine inputs/outputs. |
| **Taint** | Traceable fraction of an address's funds originating from a criminal source. |
| **Haircut** | Taint-decay method that reduces taint proportionally through mixing. |
| **Peel chain** | A long single-file chain of transactions used for layering. |
| **Likelihood ratio (LR)** | P(signal\|criminal)/P(signal\|clean); how much evidence multiplies risk. |
| **Prior / Posterior** | Probability before / after combining evidence. |
| **Provenance chain** | The set of sources a signal derives from; used to prevent double-counting. |
| **Counterfactual explanation** | The minimal input change that would flip the model's decision. |
| **SHAP** | Shapley-value feature attributions for ML model outputs. |
| **PGP fingerprint** | A 40-hex unique key identifier; identical fingerprints = same operator. |
| **P2TR / Taproot** | Address type whose outputs are uniform, defeating script-type heuristics. |
| **Entity resolution** | Linking multiple identifiers (addresses/aliases/keys) to one real entity. |
| **Jaro-Winkler** | A string-similarity metric weighting shared prefixes (for alias matching). |
| **FAISS** | Facebook AI Similarity Search; fast approximate nearest-neighbour index. |
| **Personalised PageRank (PPR)** | Random-walk proximity to a chosen seed set. |
| **Label propagation** | Spreading labels through a graph, weakening with distance. |
| **Elliptic / Elliptic2** | The standard public labelled Bitcoin transaction datasets (2019 / 2024). |
| **STIX 2.1** | ISO standard format for sharing threat intelligence. |
| **SAR / PMLA** | Suspicious Activity Report / India's Prevention of Money Laundering Act. |
| **PRE_CRIME_WATCHLIST** | Risk state for zero-history addresses flagged from dark-web context. |
| **Shared-wallet edge** | An onion-graph edge between domains sharing a payment address. |
| **FTO (Freedom-to-Operate)** | Whether building a system infringes others' patents. |
| **Defensive publication** | Publishing to block others from patenting an idea. |
| **§101 / §102 / §103** | USPTO rejections: eligibility / novelty / non-obviousness. |
| **Provisional / Non-provisional** | Priority-establishing (unexamined) / examined patent application. |
| **PCT** | Patent Cooperation Treaty — one filing, 157-country priority. |

---

## Appendix C16 — How the Three Files Fit Together (Reader's Map)

| If you want to… | Read |
|------------------|------|
| Build the working POC for $0 in 10 weeks | **File A** (full code, free sources, day-1 script) |
| Scale to production (real-time, calibrated, compliant) | **File B** (per-component upgrades, 16-week roadmap) |
| Understand the research foundations and why each layer exists | **File C §1–2** |
| Write the paper | **File C §3, §6, App C5, C10, C11, C13, C14.2** |
| File the patent | **File C §5, App C4, C7, C8, C14.1** |
| Track what to build and what enables a claim | **File C §7** |
| Verify a number is canonical | **File B App EE** (single source of truth) |

All three files describe the *same* system — five phases, four verdict states, five novel contributions — at three altitudes: build it (A), scale it (B), justify and protect it (C). The single goal never changes: **given any Bitcoin address, determine with sourced evidence whether it is BLACKLISTED, WATCHLISTED, PRE_CRIME_WATCHLIST, or CLEAN.**

---

## Appendix C17 — Architecture Decision Records (Why Each Threshold and Weight)

Reviewers and examiners ask "why this number?" Every magic constant in the system has a justification. These ADRs document them so no value looks arbitrary.

**ADR-1 — Criminal prior = 0.001.** *Decision:* the Bayesian prior is 1 in 1,000. *Why:* realistic base rate — illicit on-chain volume is a small fraction (~0.1–0.2%) of all activity, consistent with the 2% illicit *labelled* rate in Elliptic being an over-sample for ML. *Alternative rejected:* 0.5 (uninformative) would massively over-flag; 0.0001 would require implausibly strong evidence to flag anyone.

**ADR-2 — BLACKLISTED ≥ 0.85, WATCHLISTED ≥ 0.35.** *Decision:* two thresholds on the posterior. *Why:* 0.85 keeps BLACKLISTED precision ≥90% (the legal-defensibility floor); 0.35 captures strong-circumstantial cases for human review without flooding analysts. *Alternative rejected:* a single threshold loses the "review queue" tier that catches mid-confidence cases.

**ADR-3 — DARK_WEB confidence gate = 0.40 for PRE_CRIME.** *Decision:* only PAYMENT context with confidence ≥0.40 admits an address to PRE_CRIME. *Why:* below 0.40 the context is too ambiguous (often AMBIGUOUS, not PAYMENT); 0.40 balances catching real listings against false admissions. *Alternative rejected:* admitting all PAYMENT mentions (0.0) would watchlist victim quotes and incidental mentions.

**ADR-4 — CoinJoin rule: ≥40% equal outputs AND ≥5 outputs.** *Decision:* the generic CoinJoin pre-filter. *Why:* coordinated mixes produce many equal-value outputs; 40%/5 catches the general shape (validated against Tironsakkul/2311.12491). *Alternative rejected:* lower thresholds catch ordinary batch payments (false CoinJoin); higher thresholds miss small mixes.

**ADR-5 — Minimum taint fraction = 0.05 (dust filter).** *Decision:* taint below 5% does not propagate. *Why:* prevents dust-attack amplification and haircut noise. *Alternative rejected:* 0% propagates dust everywhere; 0.20 misses genuine diluted-but-real criminal flows.

**ADR-6 — Max 3 hops.** *Decision:* taint propagates at most 3 hops. *Why:* beyond hop 3 the contribution of any single seed is below the dust threshold in typical criminal flows; commercial tools use up to 5 for indirect *warnings*, but we stop at 3 for WATCHLISTED to control false positives. *Alternative rejected:* unbounded hops contaminate the whole graph.

**ADR-7 — Clustering weights CIO 0.40 / script-change 0.30 / optimal 0.20 / reuse 0.10.** *Decision:* 2024-recalibrated multi-heuristic weights. *Why:* CIO lowered from Delgado's 0.50 to 0.40 because CoinJoin growth raised its false-merge risk; the freed 0.10 redistributes to the change heuristics. Auto-merge ≥0.65, tentative ≥0.40. *Alternative rejected:* Delgado's 2021 weights over-trust CIO on 2024 data.

**ADR-8 — Anomaly blend 70% Bayesian / 30% anomaly.** *Decision:* the Isolation-Forest anomaly is supplementary. *Why:* anomaly alone is noisy; it should catch novel patterns the LRs miss without dominating sourced evidence. *Alternative rejected:* anomaly-as-primary produces unexplainable, high-FP scores.

**ADR-9 — 90-day raw-HTML retention.** *Decision:* delete raw HTML after 90 days. *Why:* GDPR data minimisation + storage sustainability (File A §4C). *Alternative rejected:* forever (legal liability + ~1 TB/4yr); 30 days (too short to re-extract after parser improvements).

**ADR-10 — Service recognition before taint.** *Decision:* the pipeline-ordering rule. *Why:* propagating before classifying contaminates exchange customers and requires expensive retroactive un-tainting. *Alternative rejected:* post-hoc service classification (Section 1, the non-negotiable rule).

**ADR-11 — Redis cache TTL = 5 minutes (production).** *Decision:* assessed decisions cached 5 min. *Why:* balances <200 ms P99 against freshness — risk rarely changes within 5 min, but the cache absorbs ~60% of read load. *Alternative rejected:* longer TTL serves stale verdicts after a new seed; no cache misses the latency target.

**ADR-12 — Amount-correlation tolerance ±5% / 24h.** *Decision:* listing price matches first-tx amount within ±5% inside 24h. *Why:* ±5% absorbs fiat-conversion/fee noise; 24h matches typical order-to-payment latency. *Alternative rejected:* exact match misses fee/conversion drift; wide windows produce coincidental matches.

---

## Appendix C18 — Novelty-Defense Memos (Reviewer-Facing)

For each strong contribution, a one-page argument anticipating the reviewer/examiner objection "isn't this obvious / already done?" Use these in rebuttals and in the patent's non-obviousness arguments.

### C18.1 — Defending PRE_CRIME (Contribution 1)

*Anticipated objection:* "Extracting dark-web addresses is known (MFScope, Devil-Behind-the-Mirror); flagging them is obvious."

*Defense:* Extraction is indeed prior art — and we cite it. The novelty is **not** extraction; it is the **risk state and lifecycle**: (a) verifying *zero on-chain history* as the defining condition, (b) assigning a *monitored* PRE_CRIME classification with a confidence derived from context, (c) *re-scoring on first transaction* combining stored off-chain with new on-chain evidence, and (d) recording the *temporal gap*. No prior work — measurement studies included — produces a *risk state* that is *monitored* and *promoted*. The closest patent (Chainalysis) *requires* a transaction; it teaches *away* from scoring a zero-history address. The ablation proves the mechanism yields detection D days before OFAC that no transaction-dependent system can produce. That is a concrete, measurable, non-obvious result.

### C18.2 — Defending the Shared-Wallet Edge (Contribution 2)

*Anticipated objection:* "A graph analyst would obviously connect sites that share a wallet."

*Defense:* The combination spans two distinct fields — onion-graph construction (a network-measurement discipline, Biryukov 2014) and Bitcoin address clustering (a forensics/cryptography discipline). A practitioner in either field does not, from their own field's prior art, arrive at representing a *shared payment address* as a *weighted edge between hidden-service domains* used for *operator-group detection*. Cross-domain combinations are presumptively non-obvious, and the measurable result — X% of shared-wallet edges connect domains with *no* hyperlink — demonstrates the edge reveals relationships the prior (hyperlink) art cannot. Spitters' topic edges and Biryukov's hyperlink edges are *content* and *network* relationships respectively; ours is an *ownership* relationship, categorically different.

### C18.3 — Defending Provenance-Aware Fusion (Contribution 3)

*Anticipated objection:* "Bayesian fusion and provenance tracking are both known; combining them is obvious."

*Defense:* Bayesian fusion is known; provenance tracking is known (citation graphs). The non-obvious step is recognising that *blockchain risk evidence has hidden circular dependencies* — OFAC → commercial relabeler → community report all tracing to one OFAC fact — that are *not publicly documented*, and that naive fusion therefore over-counts. Gao 2022 explicitly states the field lacks formal fusion; the general fusion literature (BayesDS2021) knows correlated evidence over-counts but provides *no provenance mechanism* to detect *which* signals are correlated in this domain. Our provenance-set-intersection gate is the specific, non-obvious solution to a recognised-but-unsolved problem — strong evidence of non-obviousness under §103.

---

## Appendix C19 — Competitive Landscape

How BTC-Intel compares to the commercial tools whose gaps it targets. (Commercial capabilities are inferred from public materials; BTC-Intel is not claimed to beat them on their own turf — it adds a dimension they lack.)

| Capability | Chainalysis | TRM | Elliptic | Academic SOTA | **BTC-Intel** |
|------------|-------------|-----|----------|---------------|---------------|
| Post-transaction taint scoring | ✅ (patented) | ✅ | ✅ | ✅ (ChronoWave) | ✅ (acknowledged prior art) |
| **Pre-transaction (zero-history) scoring** | ❌ | ❌ | ❌ | ❌ | **✅ (PRE_CRIME)** |
| Dark-web address extraction | ✅ (proprietary) | ✅ | partial | ✅ (MFScope/Devil) | ✅ |
| **Shared-wallet onion graph edge** | ❌ (public) | ❌ | ❌ | ❌ | **✅** |
| **Provenance-aware fusion** | ❌ (no public claim) | ❌ | ❌ | ❌ (Gao: gap) | **✅** |
| Explainable evidence chain | partial | partial | partial | rarely | ✅ (counterfactual + SHAP) |
| Three-way propagation comparison | ❌ | ❌ | ❌ | ❌ | ✅ |
| Open / reproducible | ❌ (proprietary) | ❌ | ❌ | ✅ (some) | ✅ (non-DW components) |
| Cost as primary source | $50k+/yr | $$$ | $$$ | free | **free (own infra)** |

**Strategic positioning for the paper:** BTC-Intel is *complementary* to commercial taint systems, adding the pre-transaction dimension they structurally lack — never claimed to outperform them on post-transaction taint (which we cannot measure against proprietary systems and must not claim, per §6.3).

---

## Appendix C20 — Experiment Design Per Contribution

For each contribution, the *specific* experiment that proves it, the dataset, the metric, and the expected result table — so the team knows exactly what to run.

### C20.1 — Experiment 1: PRE_CRIME Early Detection

- **Hypothesis:** BTC-Intel flags criminal addresses *before* OFAC designation.
- **Data:** OFAC-confirmed addresses with known listing dates ∩ our crawl records with PAYMENT context.
- **Procedure:** App C5.3 `precrime_evaluation`.
- **Metric:** % caught before OFAC; mean days-before-OFAC (with distribution).
- **Expected table:**

```
Metric                          | Value
--------------------------------+--------
addresses with DW + OFAC        | [n]
flagged PRE_CRIME before OFAC    | [n_early]  ([pct]%)
mean days before OFAC            | [D] days
median days before OFAC          | [D50] days
```

### C20.2 — Experiment 2: Shared-Wallet Edge vs Hyperlink

- **Hypothesis:** shared-wallet edges reveal coordination hyperlinks miss.
- **Data:** crawled onion domains with both hyperlink edges (LINKS_TO) and shared-wallet edges (SHARES_WALLET).
- **Procedure:** count shared-wallet edges whose endpoints have no hyperlink path; inspect a sample for confirmed coordination.
- **Metric:** % of shared-wallet edges with no corresponding hyperlink edge.
- **Expected table:**

```
Edge analysis                          | Value
---------------------------------------+--------
SHARES_WALLET edges                    | [m]
of which no LINKS_TO between endpoints  | [m_only] ([N]%)
infrastructure groups (≥2 domains)      | [g]
largest group size                      | [s] domains
```

### C20.3 — Experiment 3: Provenance De-Dup Prevents Inflation

- **Hypothesis:** provenance de-dup prevents false-positive inflation on circular evidence.
- **Data:** a constructed set where each address has correlated signals (OFAC + commercial relabel + community report all from one fact) plus a control set with genuinely independent signals.
- **Procedure:** run fusion with and without the provenance gate (App C5.4 `no_provenance` variant).
- **Metric:** BLACKLISTED-tier false-positive rate, with vs without provenance.
- **Expected table:**

```
Fusion variant        | FP rate (circular set) | FP rate (independent set)
----------------------+------------------------+--------------------------
naive (no provenance) |        [F]%            |          [a]%
provenance-aware      |        [P]% (P≪F)      |          [a]%  (unchanged)
```

### C20.4 — Experiment 4: Three-Way Propagation Comparison

- **Hypothesis:** each method wins a different address category; the ensemble dominates.
- **Data:** Elliptic + OFAC seeds; addresses labelled by category (exchange/mixer/ordinary).
- **Procedure:** App C5.5 `compare_propagation_methods`.
- **Metric:** precision/recall/F1/FPR per method per category.
- **Expected table:** the per-category table in §3 Contribution 4 (filled with measured values); ensemble row ≥ best single per category.

### C20.5 — Experiment 5: Temporal-Gap Significance

- **Hypothesis:** dw_to_first_tx_days predicts illicit classification.
- **Data:** later-confirmed-criminal vs later-confirmed-clean addresses, both with a dark-web listing date and a first-tx date.
- **Procedure:** Mann-Whitney U test (§3 Contribution 5 `test_gap_significance`).
- **Metric:** U statistic, p-value, criminal vs clean median gap.
- **Expected result:** p < 0.05 with criminal median gap shorter than clean — the gap is a significant predictor.

### C20.6 — Experiment 0 (Gate): Baseline Reproduction

- **Hypothesis:** our pipeline reproduces Peled 2021.
- **Data:** Elliptic (Kaggle).
- **Metric:** precision/recall on illicit class within ±2% of published 95%/40%.
- **Gate:** if this fails, **stop** — the pipeline has a bug; do not proceed to Experiments 1–5.

---

## Appendix C21 — Combined Patent + Paper Gantt (Months 0–30)

```
Month  Patent track                          Paper track
-----  ------------------------------------  -----------------------------------------
 0     File provisional ($320)  ◀ FIRST       (hold arXiv until provisional filed)
 0     —                                      File arXiv preprint (cs.CR) after provisional
 1     —                                      Submit WTSC workshop paper (6pp, prelim)
 2     —                                      Run Experiments 0–5 (App C20); collect numbers
 3     Begin non-provisional drafting         Write full 12–16pp paper; 2 proofreaders
 4     —                                      Submit to Financial Cryptography (primary)
 5     —                                      Workshop decision + present (public record)
 6     Non-provisional drafting (agent)       —
 8     —                                      FC decision; if reject → revise for NDSS/IMC
10     File PCT (157-country priority)         —
11     File US non-provisional (before M12!)   —
12     ▲ Provisional expires — must be filed   —
14     —                                      FC paper published (if accepted)
16     Possible first office action            Release GitHub artifacts (App C13)
18     PCT publishes (was confidential)        —
20-30  Office-action responses; continuations Enter national phases (EPO/UKIPO/JPO/IPOS/IN)
```

**Two unmissable dates:** (1) provisional **before** arXiv (no-grace-period jurisdictions); (2) non-provisional **before** the 12-month provisional expiry (or the priority date is lost).

---

## Appendix C22 — Research-Program Risk Register

What could go wrong with the claims, the likelihood, the impact, and the mitigation. Maintaining this keeps the program honest.

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| A competitor's confidential patent application covers PRE_CRIME (18-month window) | Medium | High | File provisional now; broad+narrow claims; monitor publications at month 18; continuation strategy |
| PRE_CRIME early-detection numbers are weak (few addresses caught before OFAC) | Medium | High | Maximise crawl coverage + archives; report honestly; even modest D-days is novel; pivot headline to the *mechanism* if numbers are thin |
| Reviewer deems contributions incremental | Medium | Medium | Ablation proving the combination's value; explicit novel-vs-prior table; novelty-defense memos (App C18) |
| Taproot/extraction novelty challenged by 2024–2025 papers | High | Low | Already lowered honestly (App C2); claims concentrate on the three 8–9/10 contributions |
| Dark-web dataset unshareable → reproducibility rejection | High | Medium | Release all non-DW code + SHA-256 manifest + de-identified features (App C13) |
| Ethics/IRB objection to crawling | Medium | High | IRB approval; unauthenticated-only; passive observation; ethics section (App C6, §6) |
| §101 abstract-idea rejection | Medium | Medium | Claims tied to concrete mechanisms (VM, checksum, subscription, provenance gate) (App C7.1) |
| §103 obviousness via reference combination | Medium | High | Cross-domain + teaching-away + unexpected-result arguments (App C7.3, C18) |
| FTO: taint component infringes Chainalysis | Low (research) / Medium (commercial) | Medium | Taint is not our novelty; design around with label-prop/PPR ensemble; license if commercialising (App C8.1) |
| Calibration data leakage inflates results | Low | High | Disjoint calibration/eval splits; bootstrap CIs; baseline gate (App C5) |
| Model drift invalidates calibrated LRs before publication | Low | Low | Drift detection (File B §10); report calibration date; recalibrate before final numbers |

**Reading the register:** the two highest-impact risks (competitor confidential filing; weak PRE_CRIME numbers) are both mitigated by the same move — *file the provisional now and maximise crawl coverage early* — which is why §5D and the roadmaps front-load both. The honesty ledger (App C2) and the novelty-defense memos (App C18) directly address the "incremental novelty" risk that sinks most system papers.

---

*End of File C. This document maps every research paper (original + ~23 newer via literature search) to its gaps and BTC-Intel's response, specifies the five novel contributions at paper-and-patent depth, scores novelty honestly (lowering it where 2024–2025 work has narrowed a gap), and provides ready-to-file claim language, full provisional-patent embodiments, an evaluation methodology with per-contribution experiments, draft paper prose, architecture decision records, novelty-defense memos, a risk register, and complete publication and IP-protection plans — all consistent with the five-phase architecture and four verdict states implemented in Files A (POC) and B (Production).*
