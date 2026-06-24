# BTC-Intel: Research Papers, Gaps, and How We Solve Them
## A Plain-Language Guide for Every Researcher, Reviewer, and Builder

> **Who this document is for:** Anyone who wants to understand WHAT the existing research says, WHERE it falls short, and HOW BTC-Intel's POC and Final Product specifically fills those gaps — without needing to read 20+ papers to get there. Every gap is explained in plain English first, then technically for those who want it.

---

## How to Read This Document

Each section follows the same simple pattern:

```
📄 PAPER    →  What it did (plain language)
🕳️ GAP      →  What it missed or couldn't do
💡 OUR FIX  →  Exactly how BTC-Intel solves it
🔬 POC      →  What we built in the POC to address it
🏭 FINAL    →  What the production system adds on top
```

This pattern repeats for every paper and every gap. If you understand it for one paper, you understand the format for all.

---

## Table of Contents

**Category A — Clustering & How Bitcoin Wallets Are Grouped**
- A1. Meiklejohn 2013 — The Original "Group Wallets Together" Paper
- A2. Ron & Shamir 2013 — The First Big Map of Criminal Bitcoin Flows
- A3. Delgado-Segura 2021 — "Wait, The Grouping Rules Are Broken for Modern Bitcoin"
- A4. Schnoering et al. 2024 — Four New Heuristics and a Better Measuring Stick
- A5. Tironsakkul et al. 2022 (Wasabi CoinJoin Detection) — The Privacy Tool That Breaks Clustering
- A6. Stütz et al. 2022 (CoinJoin Privacy Study) — How Much Did Privacy Tools Actually Help Criminals?
- A7. Kappos & Yousaf 2021 (Lightning Network Privacy) — The Off-Chain Blind Spot

**Category B — Machine Learning on the Blockchain**
- B1. Weber et al. 2019 — The Elliptic Dataset: The Benchmark Everyone Uses
- B2. Peled et al. 2021 — 40+ Features and a Strong Random Forest Baseline
- B3. Lorenz et al. 2020 — XGBoost and Graph Networks on Elliptic
- B4. Chen et al. 2023 — Criminal Wallets Have a Lifecycle (Four Phases)
- B5. ChronoWave-GNN 2025 — The Newest Temporal Graph Model
- B6. GCN-GRU Hybrid 2025 — Combining Structural and Sequential Features

**Category C — Dark Web Intelligence**
- C1. Biryukov et al. 2014 — How to Map the Tor Hidden Service Network
- C2. Spitters et al. 2014 — Topic Classification of the Dark Web
- C3. Ghosh et al. 2017 — Automated Market Analysis
- C4. Christin 2013 — The First Silk Road Study
- C5. Owenson et al. 2018 — "The Dark Web Is Smaller Than We Think"
- C6. Hiramoto et al. 2020 — Dark Market Lifecycle via Bitcoin Transactions

**Category D — Risk Scoring and Evidence Combination**
- D1. Chainalysis Patent US10977655B2 — The Commercial Gold Standard
- D2. Nerino et al. 2021 — Graph Label Propagation for AML
- D3. Gao et al. 2022 — Survey That Proves Nobody Combines Evidence Properly

**Category E — Explainability**
- E1. Lundberg & Lee 2017 — SHAP: Making ML Explainable
- E2. Wachter et al. 2017 — Counterfactual Explanations

**Category F — Brand New Gaps (Not in Prior Document)**
- F1. The Taproot Forensics Gap (Confirmed by 2023 IEEE Paper)
- F2. The Pre-Transaction Intelligence Gap (No Paper Exists)
- F3. The Cross-Protocol Bridge Gap
- F4. The Adversarial Evasion Gap
- F5. The Multi-Blockchain Entity Resolution Gap

---

## CATEGORY A — Clustering and How Bitcoin Wallets Are Grouped

---

### A1. Meiklejohn et al. 2013 — "A Fistful of Bitcoins"
**Published:** ACM Internet Measurement Conference 2013 ✅ REAL PAPER

#### 📄 What it did (plain language)

Imagine you have a stack of anonymous letters. You notice that two letters use the same handwriting style. You conclude they came from the same person. Meiklejohn's paper does the exact same thing with Bitcoin.

The key observation: **If two Bitcoin addresses both sign the same transaction as inputs (paying together), they must both be controlled by the same person** — because only someone who holds both private keys can authorise both. This is called **Common-Input-Ownership (CIO)**.

The paper used this observation to group 1,070 distinct Bitcoin user clusters from the entire blockchain — like sorting those anonymous letters into piles by author — and then identified real services (Mt. Gox, Silk Road) by sending a small amount of Bitcoin to known addresses and watching which cluster it came back from.

**Why this was a big deal:** It proved that Bitcoin is NOT anonymous. It is pseudonymous at best. The paper kicked off the entire field of blockchain analytics.

#### 🕳️ Gap 1 — CoinJoin Transactions Break Everything

The paper assumes that anyone who co-signs a transaction as an input is the same person. **But what if strangers deliberately pool their transactions together to hide who paid whom?**

That is exactly what CoinJoin does. In a CoinJoin transaction, Alice, Bob, and Charlie all put their coins in together and get them back mixed — so no outside observer can tell which input belonged to which output. The problem: all three of them are "co-signing inputs," so Meiklejohn's rule says Alice, Bob, and Charlie are the same person. They are not.

**Consequence:** On 2024 data, applying CIO naively causes a 15–25% false positive cluster merge rate on SegWit transactions. This means roughly 1 in 5 cluster merges in a naively applied system would be wrong.

#### 🕳️ Gap 2 — Frozen in Time

The paper analyses a snapshot. If a criminal sells their private key to someone else next month, the cluster still says the original criminal owns all those addresses. The system does not update.

#### 🕳️ Gap 3 — Binary Yes/No, No Confidence

Either two addresses are merged or they are not. There is no "we are 60% sure these belong to the same entity." This means you cannot distinguish a slam-dunk merge from a speculative one.

#### 💡 How BTC-Intel Solves It

**Gap 1 Fix — CoinJoin Pre-Filter:**
Before applying CIO, BTC-Intel checks if a transaction looks like a CoinJoin. The test: if 40% or more of the outputs have identical satoshi values AND there are 5 or more outputs — that is almost certainly a CoinJoin coordination. We skip CIO entirely for those transactions.

**Gap 2 Fix — Temporal Cluster Tracking:**
BTC-Intel logs cluster membership changes over time. When an address that was previously in Cluster A starts appearing in completely different transactions from Cluster A's normal pattern, the system flags this as a potential key-sale event and creates a "cluster split" entity event.

**Gap 3 Fix — Confidence-Weighted Voting:**
Instead of a binary merge decision, BTC-Intel uses four heuristics that vote with weights. The final merge confidence is the weighted sum of votes. A merge with confidence 0.90 (three heuristics agree) is treated differently from a merge with confidence 0.42 (only one weak heuristic).

#### 🔬 POC Implementation
```python
# The CoinJoin pre-filter in action
def is_coinjoin(tx):
    if len(tx.outputs) < 5:
        return False  # Too few outputs to be a coordinated mix
    values = [o['value'] for o in tx.outputs]
    max_freq = Counter(values).most_common(1)[0][1]
    return max_freq / len(values) >= 0.40  # 40%+ identical = CoinJoin
    
# CIO is only applied AFTER this check passes as False
def cio_cluster(tx, clusterer):
    if is_coinjoin(tx): return   # SKIP — do not merge these addresses
    if is_lightning_channel(tx): return  # SKIP — LN partners ≠ same entity
    # Only now: merge all input addresses into one cluster
    input_addrs = [inp['address'] for inp in tx.inputs if inp.get('address')]
    for i in range(1, len(input_addrs)):
        clusterer.union(input_addrs[0], input_addrs[i])
```
The POC applies this filter to the 3-hop expansion from OFAC seed addresses pulled from BigQuery. The filter is measurable: we report the % of transactions that would have been incorrectly merged without the filter.

#### 🏭 Final Product Addition
Production adds Lightning Network channel detection (2-of-2 P2WSH multisig), Taproot gap flagging (P2TR transactions are not clustered via script-type heuristic — flagged as UNRESOLVED), and the temporal split/merge event logger with Neo4j entity events.

---

### A2. Ron & Shamir 2013 — "Quantitative Analysis of the Full Bitcoin Transaction Graph"
**Published:** Financial Cryptography 2013 ✅ REAL PAPER

#### 📄 What it did (plain language)

If Meiklejohn's paper said "here is how to group addresses," Ron & Shamir's paper said "here is what the full map of Bitcoin looks like when you do." They analysed every Bitcoin transaction ever made up to that point and produced the first large-scale map of how money flows.

Key discovery: **Peeling chains** — a pattern where criminal money is moved through a long sequence of single hops (A → B → C → D → E...) to make tracing harder. This is the digital equivalent of passing a package through 10 couriers so no one knows who started or ended the chain.

They also discovered that most Bitcoin at the time was controlled by a small number of large clusters — evidence that services (exchanges, Silk Road) dominated the network.

#### 🕳️ Gap — The Map Has No Labels

Ron & Shamir produced a beautifully detailed map, but it was like a map with roads and no city names. They could see money flowing, but they could not say WHO the clusters were without manually depositing Bitcoin into services to test. The paper explicitly says: "external labelling methods are needed as future work."

**This is the exact gap BTC-Intel's dark web intelligence fills.**

#### 💡 How BTC-Intel Solves It

The "external labelling" called for in this paper is exactly what BTC-Intel's dark web acquisition layer provides. When a dark web page says "send payment to 1ABC..." and BTC-Intel identifies that address, it has labelled that cluster with real-world context (drug market payment, ransomware demand, etc.) — without needing to deposit money into the service.

#### 🔬 POC Implementation
The POC demonstrates end-to-end labelling: take an address from a pre-crawled dark web page → match it to a cluster via CIO → match that cluster against OFAC SDN list → produce a labelled entity. This flow directly validates the gap Ron & Shamir identified.

#### 🏭 Final Product Addition
Production adds automated daily crawling of dark web payment pages, PGP-fingerprint-assisted cluster labelling, and a label propagation pass that spreads the dark web context label to all addresses within the same cluster (so if one address in a cluster is a dark web drug payment, all 5,000 addresses in that cluster are annotated as such).

---

### A3. Delgado-Segura et al. 2021 — "Resurrecting Address Clustering in Bitcoin"
**arXiv:** 2107.05749 ✅ REAL PAPER

#### 📄 What it did (plain language)

Imagine you used a great recipe in 2013, but by 2021 the ingredients had changed significantly. Delgado-Segura's paper asks: "Does the old Bitcoin clustering recipe still work on modern Bitcoin?" The answer was: **partially, but some key heuristics are now broken or much weaker.**

Specifically, the "naive change address heuristic" — which says "when a transaction has two outputs, the output going to a brand-new address is probably the change address going back to the sender" — had a **23% false positive rate on modern SegWit transactions**. That means nearly 1 in 4 detections is wrong.

The paper introduced better heuristics and a **weighted voting system**: instead of each heuristic independently deciding, they all vote and you take the weighted result.

#### 🕳️ Gap 1 — Taproot Came After This Paper

The paper was written in 2021, and its weights were calibrated on 2020 data. Taproot (P2TR addresses, which all look identical regardless of whether they are single-signature, multisig, or a complex script) was activated in November 2021 and has been growing since. The script-type change address heuristic — which was the paper's improvement — **does not work for Taproot** because all P2TR outputs look the same.

#### 🕳️ Gap 2 — Weights Drift Over Time

The paper sets heuristic weights once. But as the Bitcoin ecosystem evolves (CoinJoin adoption up, Taproot adoption up, Lightning usage up), the optimal weights change. No published paper has tracked how heuristic performance changes quarter by quarter.

#### 💡 How BTC-Intel Solves It

**Gap 1 Fix:** BTC-Intel explicitly flags all Taproot (P2TR) transactions as having an UNRESOLVED clustering status. We do not apply script-type heuristics to them. We document this as a known limitation and as a research gap that needs a new heuristic specifically designed for P2TR.

**Gap 2 Fix:** The POC recalibrates heuristic weights on 2024 BigQuery data and measures the change vs. the 2021 weights. This is the exact type of temporal drift analysis the paper says is needed. Reporting "CIO weight dropped from 0.50 to 0.40 for 2024 data due to CoinJoin adoption increase" is a publishable contribution in itself.

#### 🔬 POC Implementation
The multi-heuristic weighted voter is built in Week 2–3 of the POC. The weights used are:
- CIO: 0.40 (reduced from Delgado's 0.50 for 2024)
- Script-type change: 0.30 (not applied to P2TR)
- Optimal change (exact remainder): 0.20
- Address reuse: 0.10 (very precise, very rare)

The POC measures precision with these weights vs. the Delgado 2021 weights on the same test set. The difference is our novel measurement.

#### 🏭 Final Product Addition
Production adds a Taproot-specific research module that tries alternative clustering approaches for P2TR: temporal co-activity (two P2TR addresses that are always active within the same 10-minute window), amount fingerprinting (P2TR addresses that always receive the same denominations), and cross-reference with known P2TR-adopting services (exchanges that migrated to P2TR first are identifiable by their announcement dates).

---

### A4. Schnoering et al. 2024 — "Assessing the Efficacy of Heuristic-Based Address Clustering for Bitcoin"
**arXiv:** 2403.00523 ✅ REAL PAPER (verified from search results)

#### 📄 What it did (plain language)

This is the most recent major clustering paper (March 2024). It introduces **four new heuristics** and a new metric called the **clustering ratio** — which measures how much each heuristic reduces the number of separate entities (a good heuristic should merge many addresses into fewer clusters; a bad one barely merges anything or merges wrong addresses together).

Crucially, the paper analyses the **temporal evolution** of these ratios — showing that some heuristics that worked well in 2015 barely do anything today, while others have become more effective.

#### 🕳️ Gap — The Paper Does Not Evaluate Criminal Detection Precision

The clustering ratio tells you how much the heuristic groups addresses. It does NOT tell you whether the groups formed are actually correct. A heuristic could have a very high clustering ratio (merges everything into a few big clusters) while having terrible precision (merging completely unrelated entities together). The paper optimises for compression, not for forensic accuracy.

#### 💡 How BTC-Intel Solves It

BTC-Intel evaluates each heuristic not just on clustering ratio but on forensic precision — specifically, what fraction of a cluster formed by heuristic X that contains one OFAC-confirmed address also contains OTHER OFAC-confirmed addresses? If the answer is high, the heuristic is good for criminal cluster identification.

This is a novel evaluation dimension that Schnoering does not measure.

#### 🔬 POC Implementation
The POC runs each of the four Schnoering heuristics on the OFAC test set and measures cluster precision (how often does the cluster formed around an OFAC seed address contain only criminal addresses, not legitimate ones?). This table — heuristic vs. forensic precision — is not in any prior paper.

#### 🏭 Final Product Addition
Production incorporates all four Schnoering heuristics into the multi-heuristic voter with forensic-precision-calibrated weights (not Schnoering's compression-ratio weights). This is an explicit improvement over the 2024 state of the art.

---

### A5. Tironsakkul et al. 2022 — "Wasabi CoinJoin Transaction Detection"
**Published:** ACM EICC 2022 ✅ REAL PAPER (verified from search results)

#### 📄 What it did (plain language)

Wasabi Wallet is one of the most popular Bitcoin privacy tools. It works by mixing many people's transactions together (CoinJoin) so that nobody — not even the mixing service — can tell which input went to which output. This paper asks: **even though Wasabi mixes transactions, can we still detect WHICH transactions are Wasabi mixes?**

Answer: **yes, with very high accuracy.** The paper found that Wasabi's mixing mechanism has a distinctive "fingerprint" (specific output denominations, specific numbers of inputs and outputs) that makes Wasabi CoinJoins identifiable even if the contents are mixed. They also tested this on known cryptocurrency theft incidents and found stolen Bitcoin flowing into Wasabi mixes.

#### 🕳️ Gap 1 — Detection Works, Deanonymisation Does Not

Detecting that a transaction is a Wasabi CoinJoin is not the same as knowing who participated. The paper correctly identifies the mixing transaction but cannot attribute individual inputs to individual criminals within it.

#### 🕳️ Gap 2 — Wasabi 2.0 Changed the Pattern

The paper covers Wasabi 1.0/1.1. Wasabi 2.0 (WabiSabi protocol, released 2022) uses dynamic denominations instead of fixed ones — meaning the old Wasabi fingerprint does not apply directly. The paper acknowledges this limitation.

#### 🕳️ Gap 3 — No Integration with Dark Web Context

The paper does not check whether the stolen Bitcoin that enters Wasabi mixes also appears in dark web payment contexts — which would confirm criminal intent before the mixing step.

#### 💡 How BTC-Intel Solves It

**Gap 1 Partial Fix:** BTC-Intel applies the Wasabi/Whirlpool detection algorithm from this paper as a pre-filter. When a transaction is detected as a CoinJoin, we: (a) skip CIO merging to avoid false cluster merges, (b) label the transaction as PRIVACY_TOOL_USED, and (c) apply taint to ALL outputs from the mix at reduced confidence (because we cannot tell which output is criminal, we treat all outputs as potentially tainted, with a reduced multiplier).

**Gap 3 Fix:** If a pre-mix address appears in a dark web payment context, BTC-Intel marks the post-mix outputs with SUSPECTED_POST_MIX_CRIMINAL at elevated confidence — because the pre-mix criminal context provides evidence that the mixing was not for legitimate privacy reasons.

#### 🔬 POC Implementation
The CoinJoin detection filter in the POC uses the Tironsakkul threshold (40% equal outputs, 5+ outputs for general detection; the Wasabi-specific denominator check for Wasabi 1.x). In the evaluation, we measure how many transactions from the OFAC cluster expansion would have been incorrectly CIO-merged without this filter.

#### 🏭 Final Product Addition
Production adds the 6-check CoinJoin detection engine covering JoinMarket, Wasabi 1.0, Wasabi 1.1, Wasabi 2.0 (≥20 inputs rule), Whirlpool, and unattributed CoinJoins, based on the Schnoering/Vazirgiannis 2023 methodology. Each identified CoinJoin output receives a TAINT_DILUTION flag indicating that post-mix addresses share taint with reduced confidence.

---

### A6. Stütz et al. 2022 — "Adoption and Actual Privacy of Decentralised CoinJoin in Bitcoin"
**arXiv:** 2109.10229 ✅ REAL PAPER (verified from search results)

#### 📄 What it did (plain language)

This is the companion paper to Tironsakkul — but instead of asking "can we detect these mixes," it asks "do these mixes actually provide privacy?" The answer was sobering for criminals: **even well-designed CoinJoins only partially protect privacy.** The paper found that:

- Pre-mixing behaviour (how coins were accumulated before mixing) often identifies the mixer
- Post-mixing behaviour (how coins are spent after mixing) often re-links them to their criminal source
- Only ~322M USD out of 4.74B USD mixed via Wasabi/Samourai ended up at exchanges — most money is still traceable through pre/post mix analysis

The paper also confirmed that the pre-mixing and post-mixing windows significantly narrow the anonymity set.

#### 🕳️ Gap — Pre-Mix and Post-Mix Windows Are Not Exploited in Forensics Tools

The paper shows that pre-mix and post-mix transaction patterns are traceable — but does not build a practical tool that uses this finding for criminal detection. The insight is documented but not operationalised.

#### 💡 How BTC-Intel Solves It

BTC-Intel's risk propagation system exploits exactly this gap. When a cluster receives a taint score and then sends to a detected CoinJoin transaction, we do NOT stop propagating taint. We follow the post-mix addresses and apply taint at reduced confidence, based on the finding from this paper that post-mix traceability exists. The reduced confidence (vs. normal propagation) reflects the privacy gain from the mix.

#### 🔬 POC Implementation
Risk propagation in the POC explicitly tracks "pre-mix" → "CoinJoin" → "post-mix" hops. The taint decay rate at the CoinJoin hop is set to 0.5 (50% confidence retention) rather than the normal 0.85 (85% retention for ordinary hops). This models the partial privacy gain while preserving evidence of criminal origin.

#### 🏭 Final Product Addition
Production adds a pool-specific taint decay model: Wasabi 2.0 gets lower taint retention (0.3) than Whirlpool (0.4) and JoinMarket (0.35), reflecting their different anonymity set sizes measured by Stütz et al.

---

### A7. Kappos & Yousaf 2021 — "An Empirical Analysis of Privacy in the Lightning Network"
**Published:** Financial Cryptography 2021 ✅ REAL PAPER (verified from search results)

#### 📄 What it did (plain language)

Lightning Network is Bitcoin's "fast lane." Instead of recording every small payment on the main blockchain, two parties open a "payment channel" (which IS recorded on-chain), send many payments back and forth privately (NOT recorded on-chain), and then close the channel (recorded on-chain). The idea is that only the opening and closing transactions are public; the individual payments within the channel are hidden.

This paper asks: **can we infer what happened inside the channel from the opening and closing transactions?** Surprisingly, yes — quite a lot. The paper identified heuristics that reveal whether a channel was used for many payments vs. few, the approximate balance at closure, and in some cases, the direction of payment flow.

#### 🕳️ Gap — Lightning Transactions Are Still a Black Box for Forensics

Even with these heuristics, the paper acknowledges that the vast majority of Lightning payments are opaque. If a criminal uses Lightning Network, existing forensics tools — including BTC-Intel — cannot trace individual payments. They can only see channel open/close events.

#### 💡 How BTC-Intel Solves It (Partial)

BTC-Intel detects Lightning channel openings (2-of-2 multisig transactions) and labels them as LIGHTNING_CHANNEL_OPEN. This does two things: (a) prevents incorrect CIO merging of the two channel participants, and (b) flags the UTXO as having "off-chain activity potential" — meaning taint entering a Lightning channel is flagged as TAINT_MAY_HAVE_ESCAPED_TO_LN.

What BTC-Intel cannot do: trace payments within the channel. This is an explicit limitation documented in the system.

#### 🔬 POC Implementation
The Lightning channel filter checks input scripts for 2-of-2 P2WSH patterns during CIO clustering. Detected LN channels are logged to the database with a LIGHTNING_CHANNEL entity type and skipped in the risk propagation taint pass.

#### 🏭 Final Product Addition
Production adds Lightning Network gossip graph integration — the LN gossip protocol broadcasts node identities and channel capacities publicly. By correlating gossip graph node IDs with on-chain channel funding transactions, BTC-Intel can identify which Lightning nodes are operated by known criminal entities (if their channel funding addresses are in a flagged cluster). This does not reveal payment contents but does reveal criminal infrastructure.

---

## CATEGORY B — Machine Learning on the Blockchain

---

### B1. Weber et al. 2019 — The Elliptic Dataset Paper
**Published:** KDD Workshop on Anomaly Detection 2019 ✅ REAL PAPER

#### 📄 What it did (plain language)

To train any machine learning model, you need labelled examples. For blockchain crime detection, you need: "here are 1,000 criminal transactions" and "here are 10,000 legitimate transactions." The problem: nobody had built this dataset before.

Weber et al. partnered with Elliptic (a blockchain analytics company) to create the first public labelled dataset of Bitcoin transactions — 203,769 transactions, of which 4,545 are labelled as illicit and 42,019 as licit. The rest are unlabelled. They then tested Graph Convolutional Networks (GCN) and Random Forests on this data.

**This dataset is still the ONLY public, peer-reviewed, labelled Bitcoin transaction dataset. Every ML paper in blockchain forensics uses it.**

#### 🕳️ Gap 1 — Only 2% of Transactions Are Labelled as Illicit

In the real world, the percentage of criminal Bitcoin transactions is small — and this dataset reflects that. But 2% illicit means the model sees 49 legitimate examples for every 1 criminal example. This "class imbalance" makes models biased toward predicting "clean" (because being wrong only costs 2% of examples). Getting high recall (catching most criminals) is very hard.

#### 🕳️ Gap 2 — The Dataset Ends in 2018

The Elliptic dataset covers 2013–2018. Criminal Bitcoin behaviour has changed dramatically since then: CoinJoin adoption, Taproot, Lightning Network, cross-chain bridges, DeFi-based laundering. Models trained on 2018 data may not generalise to 2024 criminal patterns.

#### 🕳️ Gap 3 — No Off-Chain Features

All 166 features in the dataset come from on-chain data. No dark web context, no PGP linkage, no alias correlation. A criminal address that has not yet transacted but is listed on a dark web market has ZERO features in this dataset — it is indistinguishable from a brand new legitimate address.

#### 💡 How BTC-Intel Solves It

**Gap 3 Fix (the critical one):** BTC-Intel adds 6 new off-chain features derived from dark web intelligence:
1. `dw_payment_context_confidence` — How confident are we that this address appears in a payment context on a dark web page?
2. `dw_topic_label` — What category of dark web page (DRUG / WEAPON / FRAUD / UNKNOWN)?
3. `dw_to_first_tx_days` — How many days passed between dark web listing and first on-chain transaction?
4. `pgp_fingerprint_linked` — Does this address share a PGP fingerprint with a known criminal entity?
5. `onion_cooccurrence_count` — How many dark web domains co-list this address?
6. `alias_criminal_match` — Does a vendor alias on the same page match a known criminal alias?

These 6 features are not in the Elliptic dataset and cannot be added to it (the underlying data is proprietary). They are ONLY available if you have dark web intelligence — which is BTC-Intel's key advantage.

#### 🔬 POC Implementation
The POC adds these 6 features to the Random Forest trained on the Elliptic dataset. We use train/test split on Elliptic, but evaluation addresses (the ones we actually classify) have the dark web features appended from our pre-crawled dark web sample. The ablation study shows the recall improvement from adding these 6 features.

#### 🏭 Final Product Addition
Production trains a separate "pre-transaction classifier" that uses ONLY the 6 off-chain features (since pre-transaction addresses have no on-chain features at all). This classifier is trained on addresses that were later confirmed as criminal (post-confirmation labels from OFAC, applied retroactively to addresses from the dark web sample that appeared before the OFAC confirmation date).

---

### B2. Peled et al. 2021 — "Towards Malicious Address Identification in Bitcoin"
**arXiv:** 2112.11721 ✅ REAL PAPER

#### 📄 What it did (plain language)

This is the paper BTC-Intel reproduces as its baseline in Week 1 of the POC. Peled et al. built the most thorough feature engineering study for Bitcoin criminal address classification. They designed 40+ features grouped into:

- **Graph features:** How many addresses sent to this address? How many did it send to?
- **Volume features:** How much Bitcoin total? What was the average transaction size?
- **Temporal features:** How long was the wallet active? How many days between transactions?
- **Structural features:** Does the wallet participate in peeling chains? What fraction of transactions are consolidations?

Using these features, they trained a Random Forest achieving **95% precision at 40% recall** on the illicit class of the Elliptic dataset. This means: when it says "this is criminal," it is right 95% of the time — but it only finds 40% of all actual criminals. Very precise, but misses a lot.

#### 🕳️ Gap 1 — All Features Are Static

Every feature is computed over the wallet's ENTIRE transaction history. A wallet that spent 2 years as a legitimate business and then switched to criminal activity would have mostly-clean historical features. The static classifier would not detect it because the historical average dilutes the recent criminal pattern.

#### 🕳️ Gap 2 — Cannot Classify Pre-Transaction Addresses

If an address has never made a transaction, ALL 40+ features are zero or undefined. The classifier returns "unknown." Pre-crime detection is impossible.

#### 🕳️ Gap 3 — No Dark Web Context

Features are purely on-chain. No external intelligence is integrated.

#### 💡 How BTC-Intel Solves It

**Gap 1 Fix — Temporal Delta Features:**
Instead of computing features over all history, BTC-Intel computes them over FOUR time windows: 7 days, 30 days, 90 days, and 365 days. Then we add "delta features" — the CHANGE in each feature between windows. For example:
- `volume_7d` vs. `volume_365d_avg_per_week` — is the recent week unusually high?
- `dormancy_break_score` — was the wallet inactive for 300+ days and then suddenly active?
- `sender_growth_rate_7d_vs_90d` — is the number of senders growing much faster than the 90-day baseline?

A wallet that was legitimate for 2 years but just started receiving from criminal sources would have a high `dormancy_break_score` and a spike in `volume_7d` vs. `volume_365d` — patterns the static classifier misses entirely.

**Gap 2 Fix — PRE_CRIME_WATCHLIST:**
This is BTC-Intel's primary novel contribution. By using dark web payment context as the signal INSTEAD of on-chain features, we can classify a pre-transaction address. The confidence comes from how certain we are that the dark web listing is a payment context, not from any on-chain behaviour.

#### 🔬 POC Implementation
The POC adds the 4-window temporal feature computation to the Elliptic evaluation. The delta features are computed from the Elliptic dataset's time-step structure (the Elliptic dataset has 49 time steps, each roughly 2 weeks). We measure whether adding temporal deltas improves recall beyond Peled's 40% baseline.

#### 🏭 Final Product Addition
Production adds a full 200+ dimensional temporal feature vector with all four time windows, all delta features, and the 6 off-chain features. A separate lightweight neural network (2-layer MLP) is trained on this full feature set for the anomaly scoring layer of the risk engine.

---

### B3. Chen et al. 2023 — "Evolve Path Tracer: Early Detection of Ponzi Schemes"
**arXiv:** 2301.05412 ✅ REAL PAPER

#### 📄 What it did (plain language)

This paper discovered something crucial: **criminal wallets follow a predictable lifecycle with four phases.** Think of it like watching a criminal setup unfold in stages:

1. **Pre-crime phase:** The wallet is new and quiet. Small test transactions, setting up infrastructure.
2. **Active crime phase:** High volume, rapid transactions, peeling chains — criminal activity is ongoing.
3. **Evasion phase:** The wallet goes quiet (dormancy) then suddenly activates and sends to mixers.
4. **Exit phase:** One large consolidation to an exchange, then silence — the criminal cashed out.

The paper used a Temporal Graph Neural Network to learn these phase transitions and achieved 87% F1 in detecting them BEFORE the scheme collapsed (i.e., early detection).

#### 🕳️ Gap 1 — Requires Heavy ML Infrastructure

A Temporal Graph Neural Network requires PyTorch Geometric, GPU compute, and a large labelled temporal training set. This is beyond a research POC's 10-week timeline.

#### 🕳️ Gap 2 — On-Chain Only

The paper does not use dark web data as a temporal anchor. If we know when an address FIRST appeared on a dark web market (the dark web listing timestamp), that IS the start of the pre-crime phase — before any on-chain activity. The paper cannot detect pre-crime because it does not have this signal.

#### 💡 How BTC-Intel Solves It

**Gap 1 Fix (POC Approximation):** BTC-Intel's 4-window rolling feature system approximates the TGNN phase detection without the heavy infrastructure. Each time window captures a different lifecycle phase:
- 7-day window = detecting active/evasion phases
- 365-day window = detecting dormancy (pre-evasion)
- The delta between them = detecting phase transitions

**Gap 2 Fix (Novel Contribution):** The `dw_to_first_tx_days` feature measures the exact time gap between a dark web listing and the first on-chain transaction. This IS the pre-crime phase duration — measurable only if you have dark web timestamps. No existing paper computes or uses this feature.

#### 🔬 POC Implementation
The dormancy detection feature (`dormancy_break_score = 1 if tx_count_7d > 5 AND tx_count_365d < 3 else 0`) is computed in Week 6 of the POC as part of the behavioral feature set.

#### 🏭 Final Product Addition
Production adds the full four-phase classifier. For each address with sufficient transaction history, the system assigns a lifecycle phase (PRE_CRIME / ACTIVE / EVASION / EXIT) based on the rolling window features. The phase label is included in the risk output and the analyst dashboard.

---

### B4. ChronoWave-GNN 2025 — "Detecting Illicit Bitcoin Transactions: A Wavelet-Temporal Graph Approach"
**Published:** Scientific Reports, 2025 ✅ REAL PAPER (verified from search results)

#### 📄 What it did (plain language)

This is the most advanced temporal graph model for Bitcoin forensics published to date. It combines two powerful ideas:
- **Discrete Wavelet Transform (DWT):** Converts transaction time-series into frequency components, allowing the model to detect both fast-changing patterns (sudden spikes) and slow patterns (gradual drift)
- **Temporal Graph Neural Network:** Models how the transaction graph evolves over time

The result (ChronoWave-GNN) achieved state-of-the-art results on the Elliptic dataset, outperforming simpler temporal models.

#### 🕳️ Gap — Complexity Without Off-Chain Context

Even this state-of-the-art model uses only on-chain features. It is solving a harder version of a hard problem (detecting illicit transactions from on-chain data alone) with more sophisticated tools. But the fundamental limitation — zero information before the first transaction — remains.

#### 💡 How BTC-Intel Positions Against This

BTC-Intel does NOT try to compete with ChronoWave-GNN on the Elliptic leaderboard (that is a GNN arms race where we would lose). Instead, BTC-Intel's unique value is the PRE_TRANSACTION phase — which ChronoWave-GNN literally cannot address because it has no features for an address with no transactions.

In the research paper, we acknowledge ChronoWave-GNN as the current state of the art on post-transaction detection and position BTC-Intel as the complementary system for pre-transaction intelligence.

#### 🔬 POC Implementation
The POC's Isolation Forest anomaly detection (on on-chain behavioral features) is the "post-transaction" component. It is deliberately simpler than ChronoWave-GNN. Its purpose is to catch the cases where dark web intelligence AND taint propagation both miss something anomalous.

#### 🏭 Final Product Addition
Production v2 (not v1) could integrate ChronoWave-GNN or similar temporal GNN as a replacement for the Isolation Forest in the risk engine's third layer. The architecture is designed to allow this swap — Layer 3 of the risk engine is modular.

---

## CATEGORY C — Dark Web Intelligence

---

### C1. Biryukov et al. 2014 — "Trawling for Tor Hidden Services"
**Published:** IEEE S&P 2014 ✅ REAL PAPER

#### 📄 What it did (plain language)

Before this paper, nobody knew how many Tor hidden services (onion sites) existed or what they contained. Biryukov's team built the first large-scale crawler that could enumerate onion services by exploiting the Tor HSDir (Hidden Service Directory) protocol. They built a graph of these services using hyperlinks (Site A links to Site B → put an edge between them).

Think of it like the first attempt to build a map of the dark web — not by knowing addresses in advance, but by systematically cataloguing everything that was publicly reachable.

#### 🕳️ Gap — Hyperlinks Are Weak Relationships

Two onion sites that link to each other might be completely unrelated (a dark web forum linking to a market is just a recommendation, not proof of shared operation). The paper's graph edges — based purely on hyperlinks — are too weak to identify coordinated criminal infrastructure.

**There is a much stronger relationship that the paper misses completely: two onion sites that accept payment to the SAME Bitcoin wallet are almost certainly operated by the same person.**

#### 💡 How BTC-Intel Solves It

BTC-Intel introduces the **shared-wallet edge type** in the onion graph. When two onion domains both have a page containing the same Bitcoin payment address, BTC-Intel draws an edge between those domains with edge weight equal to the number of shared addresses. This edge is a much stronger relationship than a hyperlink — it means the same entity controls both sites' payment infrastructure.

This is one of BTC-Intel's three primary novel contributions.

#### 🔬 POC Implementation
The POC builds a small onion graph from the pre-crawled dark web sample. Nodes are onion domains. Edges are added when two domains share one or more extracted Bitcoin addresses. The graph is stored in Neo4j and visualised in the Streamlit dashboard. We demonstrate that two sites connected by a shared-wallet edge that are NOT connected by a hyperlink edge reveal criminal coordination invisible to Biryukov's methodology.

#### 🏭 Final Product Addition
Production adds automated daily graph expansion as the live crawler discovers new pages. Edge weights are updated in real-time. Cluster analysis on the shared-wallet graph identifies "infrastructure groups" — sets of onion domains operated by the same criminal entity — which become new labels in the entity resolution layer.

---

### C2. Spitters et al. 2014 — "Thematic Organisation of Tor Hidden Services"
**Published:** IEEE EISIC 2014 ✅ REAL PAPER

#### 📄 What it did (plain language)

Instead of mapping the dark web by links, Spitters asked: "what is each site about?" Using Latent Dirichlet Allocation (LDA) — a topic modelling algorithm — the paper classified dark web sites into thematic groups: drugs, weapons, fraud, services, etc.

This was the first systematic content classification of the dark web at scale.

#### 🕳️ Gap — The Topics Are Descriptive, Not Operational

Knowing that a page is "drug-related" is useful, but it does not tell you which payment addresses on that page are active, legitimate, or connected to confirmed criminal entities. Topic classification and payment infrastructure are studied in separate silos.

#### 💡 How BTC-Intel Solves It

BTC-Intel runs topic classification (using the same LDA approach as Spitters) on every crawled dark web page AND extracts payment addresses from the same page. This creates the `page_topic` label in the DarkWebIntelRecord — so every extracted address is tagged with what type of criminal activity it was associated with. A payment address tagged `DRUG` has a different risk profile than one tagged `FRAUD` or `WEAPONS`.

This combination — topic + payment address — is not in any prior paper.

#### 🔬 POC Implementation
Topic classification runs on the pre-crawled sample using a lightweight LDA model (gensim, 5 topics: DRUG / WEAPON / FRAUD / SERVICES / OTHER). The `page_topic` field is stored with each extracted address and included as a feature in the risk engine.

#### 🏭 Final Product Addition
Production fine-tunes the topic classifier on a dark web-specific corpus (Gwern archives + DUTA dataset) to improve from ~70% to ~85% topic accuracy. Topic-specific likelihood ratios are calibrated: addresses from DRUG pages get LR=60 in the Bayesian engine vs. LR=35 for generic SERVICES pages.

---

### C3. Owenson et al. 2018 — "The Darknet's Smaller Than We Think"
**Published:** Digital Investigation 2018 ✅ REAL PAPER

#### 📄 What it did (plain language)

A sobering counterpoint to optimistic claims about dark web intelligence. This paper systematically measured what fraction of dark web criminal infrastructure is actually reachable by a crawler. Their finding: **because most serious criminal markets require login and authentication, a crawler without credentials only sees ~8% of the active criminal surface.**

The other 92% is behind login walls — you need an account, sometimes requiring referrals or drug purchases, to access it.

#### 🕳️ Gap This Creates For BTC-Intel

BTC-Intel's crawler cannot create accounts on dark web markets (this would involve purchasing illegal goods, which is a criminal act regardless of research intent). This means BTC-Intel has a structural 8% coverage limitation that cannot be eliminated without either (a) law enforcement credentials sharing, or (b) covert accounts (legally and ethically off-limits).

#### 💡 How BTC-Intel Handles This

BTC-Intel acknowledges this limitation explicitly. The 8% coverage is not a failure of the system — it is a fundamental constraint of operating legally and ethically. The Owenson paper provides the academic justification for stating this limitation.

What BTC-Intel does to maximise coverage within legal bounds:
- Crawls all unauthenticated pages (product previews often show partial listings before login)
- Monitors forum posts that quote market payment addresses (forums are often unauthenticated)
- Processes archived market data from research repositories (Gwern, DUTA)
- Crawls known public-facing market pages (many markets have a public "about" page with payment instructions)

#### 🔬 POC and Final Product
Both POC and Final Product cite Owenson 2018 in the limitations section and document the 8% coverage number as part of the evaluation context. This prevents reviewers from asking "why didn't you find more addresses?" — the answer is already justified academically.

---

### C4. Hiramoto et al. 2020 — "Dark Web Marketplaces via Bitcoin: From Birth to Independence"
**Published:** Forensic Science International: Digital Investigation ✅ REAL PAPER (verified from search results)

#### 📄 What it did (plain language)

This paper traced the full lifecycle of dark web markets by following their Bitcoin payment addresses — from a market's launch (first payment address appears on-chain) to its peak (high transaction volume) to its exit (final consolidation before site shutdown). They studied multiple markets and found that most have a predictable financial lifecycle of 12–24 months.

#### 🕳️ Gap — Market Lifecycle ≠ Individual Criminal Lifecycle

The paper tracks the market (the platform) not the individual criminals using it. A vendor active on multiple markets, or a vendor who moves from one shuttered market to another, is not tracked. The individual criminal's continuity across market deaths is invisible.

#### 💡 How BTC-Intel Solves It

BTC-Intel's entity resolution layer — specifically the PGP fingerprint and alias tracking — follows individual vendors across market lifecycles. When Market A shuts down and a vendor reappears on Market B with the same PGP key, BTC-Intel connects these as the same entity. The market payment addresses change, but the vendor identity is continuous.

#### 🔬 POC Implementation
The entity resolution module in Week 5–6 of the POC tracks PGP fingerprints across multiple dark web domains. A vendor appearing on two domains with the same fingerprint is resolved to a single entity in Neo4j.

#### 🏭 Final Product Addition
Production adds market shutdown detection: when a domain's crawl starts returning 404 errors or a "market retired" page, the system triggers a "market exit event" and begins monitoring for reappearance of associated PGP keys and aliases on new domains within 90 days.

---

## CATEGORY D — Risk Scoring and Evidence Combination

---

### D1. Chainalysis Patent US10977655B2 (2021)
**Status:** Issued US Patent ✅ VERIFIED REAL PATENT

#### 📄 What it does (plain language)

Imagine you have a bucket of dirty water (criminal Bitcoin). You pour it through a series of pipes (transactions). Some water from the dirty bucket mixes with clean water at each pipe junction. Chainalysis's patent describes a system for tracking how much "dirty water" ends up in each bucket at the end.

Formally: for each Bitcoin address, calculate what fraction of all Bitcoin it ever received came (directly or indirectly) from a confirmed criminal source. This fraction is the "taint score." A taint score of 0.10 means 10% of an address's received funds are traceable to criminal sources.

#### 🕳️ Gap — Taint Requires a Transaction to Exist

The patent's core mechanism literally requires: "computing a taint value propagated from a previously classified cryptocurrency address." You need an existing transaction. No transaction = no taint = no risk score.

**Every address in BTC-Intel's PRE_CRIME_WATCHLIST would receive a taint score of zero from Chainalysis's system — indistinguishable from a brand new legitimate address.**

#### 🕳️ Gap 2 — No Circular Evidence Protection

If OFAC designates an address and Chainalysis flags it, then Chainalysis's flag is used as additional evidence for the OFAC designation, which strengthens the Chainalysis flag — this is circular. The patent has no provenance tracking to prevent this.

#### 💡 How BTC-Intel Solves Both

**Gap 1:** The PRE_CRIME_WATCHLIST — assigning risk before the first transaction using dark web payment context as the signal.

**Gap 2:** The provenance-aware Bayesian fusion engine — each evidence signal has a documented provenance chain, and signals that derive from an already-counted source are excluded from the Bayesian update.

#### 🔬 POC and Final Product
Both are described extensively in the implementation plans. The key point here: BTC-Intel's taint propagation system is explicitly positioned as COMPLEMENTARY to Chainalysis (not a replacement), adding the pre-transaction dimension that Chainalysis's patent does not cover.

---

### D2. Nerino et al. 2021 — "Bitcoin Transaction Graph Analysis for AML"
**Published:** ARES 2021 ✅ REAL PAPER

#### 📄 What it did (plain language)

Instead of Chainalysis's "how much dirty water" approach (amount-weighted taint), this paper asked: "can we just ask the GRAPH who is suspicious, without tracking exact amounts?"

They used **Label Propagation** — a graph algorithm that spreads "criminal" labels from confirmed criminal nodes to nearby nodes, with the label getting weaker the farther it travels. Think of it like a rumour spreading through a social network: people close to the source are very likely to have heard it; people far away are less likely.

Result: 89% accuracy on detecting money laundering. Better than naive taint for recall; slightly worse for precision.

#### 🕳️ Gap — Only Tested One Propagation Method

The paper only tests label propagation. It does not compare it to amount-weighted taint or to Personalised PageRank. A forensics practitioner cannot know from this paper which method to use without the comparison.

#### 💡 How BTC-Intel Solves It

BTC-Intel implements ALL THREE propagation methods and produces a head-to-head comparison table on the same dataset. This three-way comparison is the research contribution that fills this gap.

#### 🔬 POC Implementation
Week 4 of the POC runs all three methods in parallel: `propagate_taint()`, `propagate_label()`, and `propagate_ppr()`. The comparison table (precision/recall/F1 per method) is the evaluation output of Week 4.

#### 🏭 Final Product Addition
Production uses an ensemble of all three, with weights learned from the comparison evaluation: the ensemble outperforms any single method, and the learned weights reflect which method is best for which address category (taint is best for exchange addresses; label propagation is best for mixer outputs; PPR is best for general criminal clusters).

---

## CATEGORY E — Explainability

---

### E1. Lundberg & Lee 2017 — SHAP
**Published:** NeurIPS 2017 ✅ REAL PAPER

#### 📄 What it did (plain language)

When a machine learning model says "this address is 73% likely to be criminal," an analyst naturally asks: "WHY?" SHAP answers this by computing how much each feature contributed to the score. For example: "dark_web_payment_confidence contributed +28 points, taint_hop_1 contributed +22 points, dormancy_break contributed +15 points, exchange_passthrough contributed -12 points."

SHAP has solid mathematical backing (Shapley values from cooperative game theory) and works for any ML model.

#### 🕳️ Gap — Does Not Explain Rule-Based Decisions

SHAP works for ML models. BTC-Intel's fast-path layer uses deterministic rules (if OFAC = confirmed, then BLACKLISTED, period). There is no "feature importance" for a deterministic rule — it either fired or it did not.

#### 💡 How BTC-Intel Solves It

BTC-Intel uses SHAP for the ML components (Isolation Forest anomaly detection, behavioral classifier) and a **counterfactual explanation generator** for the rule-based and Bayesian components. The counterfactual says: "this address would fall below the WATCHLISTED threshold if [specific evidence] were removed." This is actionable for an analyst: it tells them exactly what evidence is carrying the score.

#### 🔬 POC Implementation
The Isolation Forest anomaly score output is explained using SHAP TreeExplainer (Week 7). Each SHAP output is formatted into an analyst-readable contribution table ranked by |impact|.

#### 🏭 Final Product Addition
Production adds the counterfactual generator for the Bayesian layer: implemented as an iterative evidence removal algorithm that finds the minimum set of evidence signals whose removal would push the score below the WATCHLISTED threshold. This counterfactual is included in every WATCHLISTED and BLACKLISTED decision output.

---

## CATEGORY F — BRAND NEW GAPS (Not in Prior Document)

These gaps were identified from the verified research literature search done for this document. They are not covered in the earlier research gap analysis (Document 03) and represent additional novel contributions.

---

### F1. The Taproot Forensics Gap
**Supporting paper:** "Analyzing the Effect of Taproot on Bitcoin Deanonymization" — IEEE ICDCSW 2023 ✅ REAL PAPER (verified)

#### 🕳️ The Gap (In Plain Language)

In November 2021, Bitcoin activated Taproot, which introduced a new address type: P2TR. Here is the forensics problem Taproot creates:

**Before Taproot:** If Alice uses a multisig wallet (multiple people required to authorise transactions), her addresses look different from Bob's single-key wallet. A forensics analyst can tell: "that address is multisig, so it is probably a business or exchange."

**After Taproot:** Whether Alice is using a single key, a 100-of-100 multisig, or a complex smart contract — the on-chain address looks IDENTICAL. All P2TR outputs look the same. The script-type change address heuristic — which was the best improvement in Delgado 2021 — becomes useless for Taproot.

The 2023 IEEE paper confirms this and proposes one partial heuristic that remains applicable. But no comprehensive forensics solution for P2TR exists.

#### 💡 How BTC-Intel Addresses This New Gap

**What we do:** Flag all P2TR transactions as CLUSTERING_UNRESOLVED. Do not apply script-type heuristics. Still apply CIO (which remains valid — if two P2TR addresses co-sign, they are still co-owned, even if we cannot tell their script type).

**The novel research contribution:** Document the precision degradation from Taproot adoption quarter by quarter. As Taproot adoption grows from X% to Y% of all Bitcoin transactions, heuristic precision drops by Z points. This is the temporal stability analysis that Delgado 2021 called for but never did.

**The patent-worthy finding:** Any new heuristic that extracts clustering signal from Taproot transactions (e.g., using transaction timing patterns, amount fingerprinting for P2TR outputs, or gossip network correlation) would be a novel contribution with no prior art.

#### 🔬 POC Implementation
The POC measures what percentage of 2024 Bitcoin transactions in the OFAC cluster expansion are P2TR. For those, clustering is flagged as UNRESOLVED. The evaluation reports separately: precision for P2PKH+SegWit transactions vs. P2TR transactions (expected to show significant precision drop for P2TR).

#### 🏭 Final Product Addition
Production v1 documents the gap. Production v2 implements experimental Taproot-specific heuristics including: P2TR-to-P2TR same-wallet same-session (timing analysis) and P2TR address-book pattern (addresses that always appear together in outputs regardless of type similarity).

---

### F2. The Pre-Transaction Intelligence Gap
**Status:** NO PUBLISHED PAPER EXISTS ⭐ HIGHEST NOVELTY

#### 🕳️ The Gap (In Plain Language)

Here is the problem no paper has solved: **Every existing system waits for a criminal to do something before flagging them.**

It is like a bank that only locks the vault AFTER the robber walks in, takes the money, and walks out. By the time the alarm triggers, the damage is done.

In Bitcoin terms: a drug dealer sets up a new wallet on Monday. On Tuesday, they list that wallet address on a dark web market. On Wednesday, they start receiving payment. On Thursday, the FBI notices the unusual transactions. By Friday, they might get OFAC-designated — weeks after the criminal operation began.

BTC-Intel says: **we can flag the wallet on Tuesday — before any transaction — because the wallet address is publicly posted on the dark web market's payment page.** The dark web page IS the evidence of criminal intent.

#### 💡 The Complete BTC-Intel Solution

This is the PRE_CRIME_WATCHLIST — covered extensively in implementation plans. The key point here is confirming that **no academic paper and no commercial patent has claimed this mechanism**. Chainalysis's patent requires transactions. Every ML paper requires transaction features. This gap is genuinely unaddressed in published literature.

The evidence chain for a PRE_CRIME_WATCHLIST address:
1. Crawler finds page on `xyz.onion` classified as drug market
2. Extractor finds Bitcoin address `1ABC...` in payment context on that page
3. Blockchain check: `1ABC...` has zero transaction history
4. → Assigned: `PRE_CRIME_WATCHLIST`, confidence = 0.68 (from dark web context strength)
5. Monitoring: any first transaction to `1ABC...` triggers immediate re-evaluation

#### 🔬 POC Implementation
Week 5–6 builds this. Demonstrated with at least one address that: (a) appeared in the pre-crawled dark web sample, (b) had zero blockchain history at crawl time, (c) later received a first on-chain transaction (verifiable in BigQuery). This end-to-end demonstration — dark web appearance → pre-crime classification → confirmed first transaction — is the core POC deliverable.

#### 🏭 Final Product Addition
Production adds real-time monitoring via ElectrumX's address subscription API. As soon as a new transaction appears for any PRE_CRIME_WATCHLIST address, the system: (a) re-evaluates with full risk engine, (b) sends webhook notification to integrated systems, (c) logs the time gap between dark web first appearance and first on-chain transaction as a research data point.

---

### F3. The Cross-Protocol Bridge Gap
**Supporting context:** DeFi/bridge literature; confirmed gap in blockchain analytics

#### 🕳️ The Gap (In Plain Language)

Criminals have discovered that blockchain analytics tools are good at tracking Bitcoin — but only Bitcoin. So they convert their Bitcoin to a different cryptocurrency (Ethereum, Monero, Zcash) using a cross-chain bridge, and then do their criminal activity on the other chain where they are harder to track.

Known bridges criminals use:
- **WBTC (Wrapped Bitcoin):** Converts BTC → WBTC (an Ethereum token representing Bitcoin). Once on Ethereum, funds flow through DeFi mixers like Tornado Cash.
- **RenBridge:** Similar BTC → ETH conversion
- **THORChain:** Decentralised exchange supporting BTC → any chain swaps
- **Atomic swaps:** Direct BTC → XMR (Monero) swaps with no central intermediary

**The gap:** When BTC-Intel tracks a criminal address and finds it sent funds to a WBTC bridge, our tracking stops. The criminal is now on Ethereum. No Bitcoin analytics tool can follow them.

#### 💡 How BTC-Intel Handles This

**What we can do today:** Detect the cross-chain bridge exit event. When funds flow to a known bridge address (WBTC custodian, RenBridge gateway, THORChain vault), BTC-Intel emits a `CROSS_CHAIN_EXIT` event with the bridge name and amount. The risk score of the originating address is not reduced — the criminal context remains — but the monitoring note says "tracking ends here."

**What would require future research:** A cross-chain intelligence system that correlates BTC→ETH bridge entries with Ethereum transaction outputs. This is a multi-blockchain analytics problem that is a research area in itself. BTC-Intel v1 does not attempt this; it is explicitly flagged as a known limitation.

**Novel contribution for the paper:** Measuring how frequently OFAC-confirmed criminal addresses use cross-chain bridges before cash-out. If X% of confirmed criminal clusters exit via bridges, this quantifies the intelligence loss from single-chain analytics — a number that does not appear in any published paper.

#### 🔬 POC Implementation
The POC includes a static list of known bridge addresses (WBTC custodians, RenBridge, THORChain vaults — all publicly known from their documentation). When a taint propagation step hits one of these addresses, it logs a CROSS_CHAIN_EXIT event and stops taint propagation at that address.

#### 🏭 Final Product Addition
Production maintains an auto-updated bridge address registry (scraping bridge protocol announcements and on-chain deployment records). When a new bridge address is detected in the wild, it is added to the registry and a batch re-evaluation of all connected clusters is triggered.

---

### F4. The Adversarial Evasion Gap
**Supporting context:** Adversarial ML literature; no specific blockchain evasion paper from verified search

#### 🕳️ The Gap (In Plain Language)

A sophisticated criminal who knows BTC-Intel exists can try to evade it deliberately. For example:
- **Cluster poisoning:** Intentionally co-sign a transaction with a legitimate address to pollute the legitimate address's cluster with criminal addresses, causing false positives in BTC-Intel
- **Dust attack:** Send tiny amounts (dust) from criminal addresses to thousands of legitimate addresses, making those addresses "tainted" by association, causing mass false positives that overwhelm the system
- **Feature manipulation:** Deliberately create transaction patterns that look like clean behaviour (normal amounts, normal timing, normal counterparties) to stay below the anomaly detection threshold
- **Dark web misinformation:** Post legitimate addresses as payment addresses on dark web pages to frame innocent people

#### 💡 How BTC-Intel Handles This

**Dust attack protection:** Transactions where BTC-Intel's system itself would be the victim of dust (receiving tiny outputs from criminal addresses) are filtered. The minimum taint fraction threshold (5%) prevents dust amounts from triggering taint propagation. Additionally, taint propagation does not work backwards — receiving dust from a criminal address does not make you criminal.

**Cluster poisoning protection:** The confidence weighting in the multi-heuristic voter means a single suspicious co-sign does not automatically create a high-confidence merge. The merge is tagged as TENTATIVE if confidence is below 0.65.

**Misinformation protection:** BTC-Intel computes a `contradiction_score` for each address. If an address is flagged as PAYMENT context by dark web extraction BUT also appears in many VICTIM_REPORT contexts on abuse databases, the contradicting evidence reduces confidence and flags for human review.

**Feature manipulation:** This is the hardest adversarial attack and BTC-Intel does not fully solve it. This is an honest limitation for the paper.

#### 🔬 POC Implementation
The POC includes the dust filter and the contradiction detector. The VICTIM_CONTEXT likelihood ratio (LR = 0.2) reduces Bayesian posterior for addresses flagged as victims.

#### 🏭 Final Product Addition
Production adds an explicit adversarial detection module that flags statistical anomalies in cluster formation: a cluster that grew by more than 10,000 addresses in 24 hours is almost certainly the victim of a deliberate cluster poisoning attack and is quarantined for manual review.

---

### F5. The Multi-Blockchain Entity Resolution Gap
**Status:** Partially addressed in academic literature; no complete solution exists

#### 🕳️ The Gap (In Plain Language)

The same criminal might use Bitcoin, Ethereum, Monero, and dark web marketplaces simultaneously. Each analytical system (BTC-Intel for Bitcoin, other tools for Ethereum) identifies them independently but cannot say "the Bitcoin criminal in Cluster A is the same person as the Ethereum criminal in Cluster B."

How do we know it is the same person? Common signals:
- Same PGP fingerprint used in dark web communications for both
- Same alias ("DarkDealer42") mentioned on pages that list both BTC and ETH addresses
- Amount correlation: a payment made on the BTC side matches an identical amount on the ETH side 24 hours later (bridge transfer)
- IP linkage (if available from law enforcement)

#### 💡 How BTC-Intel Addresses This

BTC-Intel's entity resolution layer is designed to receive signals from multiple blockchains. The PGP fingerprint and alias matching work regardless of which blockchain the payment addresses are on. The entity graph in Neo4j can contain nodes for BTC addresses, ETH addresses, and dark web entities — with cross-chain entity links when evidence warrants.

What is NOT implemented in v1: BTC-Intel does not crawl Ethereum data or Monero data. But the entity resolution SCHEMA is cross-chain ready — when an external source (law enforcement data, partner analytics) provides Ethereum address mappings, BTC-Intel can integrate them via the entity graph.

#### 🔬 POC Implementation
The POC's Neo4j schema has an `address_type` field that supports non-Bitcoin chains. The entity resolution module is designed to accept entity links from external sources without requiring BTC-Intel itself to crawl those chains.

#### 🏭 Final Product Addition
Production v2 adds Ethereum address import via Chainalysis API (if licensed) or etherscan.io public labels. Cross-chain entity links are created when the same PGP key or alias appears in association with both a BTC and an ETH address. This is a genuine novel capability that no current tool offers as an integrated, explainable system.

---

## Summary: The Complete Gap-to-Solution Map

| Paper / Gap | Gap | BTC-Intel Solution | POC | Final Product |
|-------------|-----|-------------------|-----|---------------|
| Meiklejohn 2013 | No CoinJoin awareness, binary clustering | CoinJoin pre-filter + confidence voting | ✅ Week 2–3 | + LN detection + Taproot flagging |
| Ron & Shamir 2013 | No external labels for clusters | Dark web payment context as cluster label | ✅ Week 5–6 | + Live crawler + daily label updates |
| Delgado 2021 | 2020 weights, no Taproot handling | Recalibrated 2024 weights, P2TR gap flagged | ✅ Evaluation Week 9 | + Taproot-specific heuristics research |
| Schnoering 2024 | Optimises compression, not forensic precision | Forensic precision evaluation of 4 new heuristics | ✅ Evaluation Week 9 | + Full production voting with forensic weights |
| Tironsakkul 2022 | Detection works, deanonymisation does not | Post-mix taint with dilution modifier | ✅ Week 4 taint | + 6-protocol CoinJoin detection engine |
| Stütz 2022 | Pre/post mix windows not operationalised | 0.5 taint retention at CoinJoin hop | ✅ Week 4 taint | + Pool-specific decay model |
| Kappos & Yousaf 2021 | LN payments are opaque | Channel funding detection, gossip graph integration | ✅ Week 3 filter | + LN node criminal identification |
| Weber 2019 (Elliptic) | No off-chain features, data ends 2018 | 6 new off-chain features; pre-transaction classifier | ✅ Week 7–8 | + Full 200-feature temporal vector |
| Peled 2021 | Static features miss lifecycle phases | 4-window temporal rolling features + delta features | ✅ Week 6 | + Full lifecycle phase classifier |
| Chen 2023 | TGNN needs GPU; no off-chain temporal anchor | Rolling windows approximate phases; `dw_to_first_tx_days` | ✅ Week 6 | + Phase label in analyst dashboard |
| ChronoWave-GNN 2025 | On-chain only; no pre-transaction coverage | Complementary positioning; modular layer 3 | ✅ Isolation Forest substitute | + Optional TGNN integration in v2 |
| Biryukov 2014 | Hyperlink edges only | Shared-wallet edge type in onion graph | ✅ Week 5 | + Real-time graph expansion |
| Spitters 2014 | Topic classification only, no payment linking | Topic + payment address on same page | ✅ Week 5 | + Fine-tuned dark web topic model |
| Owenson 2018 | 8% unauthenticated surface only | Acknowledged limitation; forum + archive supplementation | ✅ Documented | + Auto-supplement from archives |
| Hiramoto 2020 | Market lifecycle ≠ vendor continuity | PGP + alias tracking across market shutdowns | ✅ Week 5–6 | + Market exit event detection |
| Chainalysis Patent | Requires transactions; no circular evidence guard | PRE_CRIME_WATCHLIST + provenance deduplication | ✅ Week 7–8 | + Full retroactive correction cascade |
| Nerino 2021 | Single propagation method only | Three-way comparison (taint/LP/PPR) | ✅ Week 4 | + Ensemble propagation with learned weights |
| Gao 2022 Survey | No formal evidence fusion framework | Calibrated Bayesian LRs + provenance tracking | ✅ Week 7–8 | + Empirically calibrated LR values |
| Lundberg & Lee 2017 | SHAP does not explain rules | SHAP for ML + counterfactual for rules | ✅ Week 7 | + Analyst narrative generator |
| **NEW: Taproot Gap** | No forensics heuristic for P2TR | Flag as UNRESOLVED; measure precision degradation | ✅ Flagging only | + Taproot-specific heuristic research |
| **NEW: Pre-Transaction Gap** | No system flags pre-transaction addresses | PRE_CRIME_WATCHLIST — the primary novel contribution | ✅ Core POC | + Real-time monitoring via ElectrumX |
| **NEW: Bridge Gap** | Tracking ends at cross-chain bridges | Emit CROSS_CHAIN_EXIT event; stop taint propagation | ✅ Static bridge list | + Auto-updated bridge registry |
| **NEW: Adversarial Gap** | Criminals can deliberately evade | Dust filter + contradiction scorer + quarantine | ✅ Basic filters | + Adversarial cluster growth detector |
| **NEW: Multi-Blockchain Gap** | Same criminal invisible across chains | Cross-chain entity schema ready; PGP/alias cross-chain | ✅ Schema only | + ETH import via Chainalysis/etherscan |

---

## One-Paragraph Summary for Presentations

> "Every existing blockchain forensics system — academic and commercial — shares two fundamental limitations: they can only flag a Bitcoin address after it has participated in suspicious transactions, and they have no way to determine that a brand-new address is criminal before its first payment arrives. BTC-Intel fills this gap by combining intelligence extracted from Tor hidden services with Bitcoin graph analysis. When a payment address appears on a dark web drug market before any transaction has occurred, BTC-Intel flags it immediately as PRE_CRIME_WATCHLIST. When that address later receives its first criminal payment, the system confirms the classification with full evidence chain. Additionally, BTC-Intel introduces two new research contributions not in any prior paper: a shared-wallet edge type in onion service graphs that reveals criminal coordination invisible to hyperlink analysis, and a provenance-aware Bayesian evidence fusion engine that prevents the circular double-counting of correlated intelligence signals that plagues existing multi-source risk systems."

---

*This document should be read alongside Documents 01 (POC Plan), 02 (Final Product Plan), 03 (Technical Gap Analysis), and 04 (Patent/Paper Filing Guide) for the complete BTC-Intel research and implementation package.*
